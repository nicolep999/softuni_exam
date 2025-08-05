"""
Test data factories for creating test objects.
"""

import factory
from django.contrib.auth.models import User
from movies.models import Movie, Genre, Director, Actor, Watchlist
from reviews.models import Review, Comment


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User objects."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class StaffUserFactory(UserFactory):
    """Factory for creating staff User objects."""

    is_staff = True


class SuperUserFactory(UserFactory):
    """Factory for creating superuser User objects."""

    is_superuser = True


class ProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating Profile objects."""

    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    bio = factory.Faker("text", max_nb_chars=200)
    location = factory.Faker("city")


class GenreFactory(factory.django.DjangoModelFactory):
    """Factory for creating Genre objects."""

    class Meta:
        model = Genre

    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=100)


class DirectorFactory(factory.django.DjangoModelFactory):
    """Factory for creating Director objects."""

    class Meta:
        model = Director

    name = factory.Faker("name")
    bio = factory.Faker("text", max_nb_chars=300)
    birth_date = factory.Faker("date_of_birth", minimum_age=25, maximum_age=80)


class ActorFactory(factory.django.DjangoModelFactory):
    """Factory for creating Actor objects."""

    class Meta:
        model = Actor

    name = factory.Faker("name")
    bio = factory.Faker("text", max_nb_chars=300)
    birth_date = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)


class MovieFactory(factory.django.DjangoModelFactory):
    """Factory for creating Movie objects."""

    class Meta:
        model = Movie

    title = factory.Faker("sentence", nb_words=3)
    release_year = factory.Faker("year")
    plot = factory.Faker("text", max_nb_chars=500)
    director = factory.SubFactory(DirectorFactory)
    imdb_rating = factory.Faker(
        "pydecimal", left_digits=1, right_digits=1, min_value=1, max_value=10
    )

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for genre in extracted:
                self.genres.add(genre)
        else:
            # Add a default genre if none provided
            genre = GenreFactory()
            self.genres.add(genre)

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for actor in extracted:
                self.actors.add(actor)
        else:
            # Add a default actor if none provided
            actor = ActorFactory()
            self.actors.add(actor)


class ReviewFactory(factory.django.DjangoModelFactory):
    """Factory for creating Review objects."""

    class Meta:
        model = Review

    movie = factory.SubFactory(MovieFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Faker("random_int", min=1, max=10)
    title = factory.Faker("sentence", nb_words=4)
    content = factory.Faker("text", max_nb_chars=300)


class CommentFactory(factory.django.DjangoModelFactory):
    """Factory for creating Comment objects."""

    class Meta:
        model = Comment

    review = factory.SubFactory(ReviewFactory)
    user = factory.SubFactory(UserFactory)
    content = factory.Faker("text", max_nb_chars=200)


class WatchlistFactory(factory.django.DjangoModelFactory):
    """Factory for creating Watchlist objects."""

    class Meta:
        model = Watchlist

    user = factory.SubFactory(UserFactory)
    movie = factory.SubFactory(MovieFactory)
