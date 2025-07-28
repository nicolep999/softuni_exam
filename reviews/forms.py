from django import forms
from .models import Review, Comment

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.movie = kwargs.pop('movie', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        # If this is a new review (not an update), check if user already reviewed this movie
        if not self.instance.pk and Review.objects.filter(user=self.user, movie=self.movie).exists():
            raise forms.ValidationError("You have already reviewed this movie.")
        return cleaned_data
    
    def save(self, commit=True):
        review = super().save(commit=False)
        if not review.pk:  # Only set these on new reviews
            review.user = self.user
            review.movie = self.movie
        if commit:
            review.save()
        return review

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Add a comment...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.review = kwargs.pop('review', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        comment = super().save(commit=False)
        comment.user = self.user
        comment.review = self.review
        if commit:
            comment.save()
        return comment