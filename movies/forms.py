from django import forms
from .models import Movie, Genre, Director, Actor, Watchlist

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'release_year', 'plot', 'poster', 'trailer_url', 'genres', 'director', 'actors']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-input'}),
            'plot': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
            'trailer_url': forms.URLInput(attrs={'class': 'form-input'}),
            'genres': forms.SelectMultiple(attrs={'class': 'form-input'}),
            'director': forms.Select(attrs={'class': 'form-input'}),
            'actors': forms.SelectMultiple(attrs={'class': 'form-input'}),
        }
    
    def clean_release_year(self):
        year = self.cleaned_data.get('release_year')
        if year < 1888 or year > 2030:  # First film was in 1888, limit future films to 2030
            raise forms.ValidationError("Please enter a valid release year between 1888 and 2030.")
        return year

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ['name', 'bio', 'birth_date', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ['name', 'bio', 'birth_date', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class MovieSearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Search movies...'}),
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label="All Genres",
        widget=forms.Select(attrs={'class': 'form-input'}),
    )
    year_from = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'From year'}),
    )
    year_to = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'To year'}),
    )