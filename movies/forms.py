from django import forms
from .models import Movie, Genre, Director, Actor


# Utility functions for common form widgets
def get_text_input_widget(placeholder, **kwargs):
    """Get a standardized text input widget"""
    attrs = {"class": "form-input", "placeholder": placeholder, **kwargs}
    return forms.TextInput(attrs=attrs)


def get_textarea_widget(placeholder, rows=3, **kwargs):
    """Get a standardized textarea widget"""
    attrs = {"class": "form-input", "placeholder": placeholder, "rows": rows, **kwargs}
    return forms.Textarea(attrs=attrs)


def get_date_input_widget(**kwargs):
    """Get a standardized date input widget"""
    attrs = {"class": "form-input", "type": "date", **kwargs}
    return forms.DateInput(attrs=attrs)


class MovieForm(forms.ModelForm):
    # Fields for creating new entities if they don't exist
    new_genre_name = forms.CharField(
        required=False,
        max_length=100,
        widget=get_text_input_widget("Enter new genre name"),
        help_text="Add a new genre if it doesn't exist",
    )

    new_director_name = forms.CharField(
        required=False,
        max_length=200,
        widget=get_text_input_widget("Enter new director name"),
        help_text="Add a new director if they don't exist",
    )

    new_actor_name = forms.CharField(
        required=False,
        max_length=200,
        widget=get_text_input_widget("Enter new actor name"),
        help_text="Add a new actor if they don't exist",
    )

    class Meta:
        model = Movie
        fields = [
            "title",
            "release_year",
            "plot",
            "poster",
            "trailer_url",
            "genres",
            "director",
            "actors",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Enter movie title"}
            ),
            "release_year": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "e.g., 2024"}
            ),
            "plot": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 5,
                    "placeholder": "Enter movie plot summary...",
                }
            ),
            "trailer_url": forms.URLInput(
                attrs={"class": "form-input", "placeholder": "https://www.youtube.com/watch?v=..."}
            ),
            "genres": forms.CheckboxSelectMultiple(attrs={"class": "genre-checkboxes"}),
            "director": forms.Select(attrs={"class": "form-input"}),
            "actors": forms.SelectMultiple(attrs={"class": "form-input"}),
        }

    def clean_release_year(self):
        year = self.cleaned_data.get("release_year")
        if year < 1888 or year > 2030:  # First film was in 1888, limit future films to 2030
            raise forms.ValidationError("Please enter a valid release year between 1888 and 2030.")
        return year

    def save(self, commit=True):
        movie = super().save(commit=False)

        if commit:
            # Create new genre if provided
            new_genre_name = self.cleaned_data.get("new_genre_name")
            if new_genre_name:
                genre, created = Genre.objects.get_or_create(
                    name=new_genre_name.strip(),
                    defaults={"description": f"Genre for {new_genre_name}"},
                )
                if created:
                    # Add the new genre to the movie's genres
                    movie.save()
                    movie.genres.add(genre)

            # Create new director if provided
            new_director_name = self.cleaned_data.get("new_director_name")
            if new_director_name and not movie.director:
                director, created = Director.objects.get_or_create(
                    name=new_director_name.strip(),
                    defaults={"bio": f"Director: {new_director_name}"},
                )
                movie.director = director

            # Create new actor if provided
            new_actor_name = self.cleaned_data.get("new_actor_name")
            if new_actor_name:
                actor, created = Actor.objects.get_or_create(
                    name=new_actor_name.strip(), defaults={"bio": f"Actor: {new_actor_name}"}
                )
                if created:
                    # Add the new actor to the movie's actors
                    movie.save()
                    movie.actors.add(actor)

            movie.save()
            self.save_m2m()

        return movie


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ["name", "description"]
        widgets = {
            "name": get_text_input_widget("Enter genre name"),
            "description": get_textarea_widget("Enter genre description..."),
        }


class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ["name", "bio", "birth_date", "photo"]
        widgets = {
            "name": get_text_input_widget("Enter director name"),
            "bio": get_textarea_widget("Enter director biography..."),
            "birth_date": get_date_input_widget(),
        }


class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ["name", "bio", "birth_date", "photo"]
        widgets = {
            "name": get_text_input_widget("Enter actor name"),
            "bio": get_textarea_widget("Enter actor biography..."),
            "birth_date": get_date_input_widget(),
        }


class MovieSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=get_text_input_widget("Search movies..."),
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label="All Genres",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    year_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-input", "placeholder": "From year"}),
    )
    year_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-input", "placeholder": "To year"}),
    )
