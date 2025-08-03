from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View

from .forms import CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile
from movies.models import Watchlist

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('movies:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in after registration
        login(self.request, self.object)
        messages.success(self.request, f"Welcome to Moodie, {self.object.username}! Your account has been created.")
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)

class LogoutView(View):
    def get(self, request):
        # Show confirmation page
        return render(request, 'accounts/logout_confirm.html')
    
    def post(self, request):
        # Perform logout
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('movies:home')

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['watchlist'] = Watchlist.objects.filter(user=self.request.user)
        context['reviews'] = self.request.user.reviews.all()
        return context

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
            context['profile_form'] = ProfileUpdateForm(
                self.request.POST, 
                self.request.FILES, 
                instance=self.request.user.profile
            )
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
            context['profile_form'] = ProfileUpdateForm(instance=self.request.user.profile)
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')

        return self.render_to_response(
            self.get_context_data(
                user_form=user_form,
                profile_form=profile_form
            )
        )
