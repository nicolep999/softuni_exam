from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import Movie
from reviews.models import Review


class Command(BaseCommand):
    help = "Create sample reviews for movies"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reviews-per-movie",
            type=int,
            default=3,
            help="Number of reviews to create per movie (default: 3)",
        )

    def handle(self, *args, **options):
        reviews_per_movie = options["reviews_per_movie"]

        users = list(User.objects.all())
        movies = list(Movie.objects.all())

        if not movies:
            self.stdout.write(self.style.ERROR("No movies found in database"))
            return

        if not users:
            self.stdout.write(self.style.ERROR("No users found in database"))
            return

        total_created = 0

        for movie in movies:
            # Select random users for this movie
            movie_reviewers = random.sample(users, min(reviews_per_movie, len(users)))

            for user in movie_reviewers:
                # Check if user already reviewed this movie
                if Review.objects.filter(user=user, movie=movie).exists():
                    continue

                # Generate contextually appropriate review based on IMDB rating
                review_data = self.generate_contextual_review(movie)

                # Create review
                review = Review.objects.create(
                    user=user,
                    movie=movie,
                    title=review_data["title"],
                    content=review_data["content"],
                    rating=review_data["rating"],
                )

                total_created += 1

            self.stdout.write(
                self.style.SUCCESS(f'✅ Created {len(movie_reviewers)} reviews for "{movie.title}"')
            )

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully created {total_created} reviews!"))

    def generate_contextual_review(self, movie):
        """Generate contextually appropriate review based on movie rating and genre"""

        # Get movie rating (default to 5.0 if no IMDB rating)
        imdb_rating = movie.imdb_rating if movie.imdb_rating else 5.0
        genres = [genre.name.lower() for genre in movie.genres.all()]

        # Determine rating category
        if imdb_rating >= 8.5:
            rating_category = "excellent"
            rating_range = (8, 10)
        elif imdb_rating >= 7.5:
            rating_category = "very_good"
            rating_range = (7, 9)
        elif imdb_rating >= 6.5:
            rating_category = "good"
            rating_range = (6, 8)
        elif imdb_rating >= 5.5:
            rating_category = "average"
            rating_range = (5, 7)
        else:
            rating_category = "poor"
            rating_range = (3, 6)

        # Generate rating within appropriate range
        rating = random.randint(rating_range[0], rating_range[1])

        # Get genre-specific review content
        review_data = self.get_genre_specific_review(
            rating_category, genres, movie.title, imdb_rating
        )

        return {"title": review_data["title"], "content": review_data["content"], "rating": rating}

    def get_genre_specific_review(self, rating_category, genres, movie_title, imdb_rating):
        """Generate genre-specific review content"""

        # Excellent movies (8.5+)
        if rating_category == "excellent":
            titles = [
                "A true masterpiece!",
                "Absolutely brilliant!",
                "Cinematic perfection!",
                "Outstanding achievement",
                "A work of art",
                "Exceptional filmmaking",
                "Pure cinematic magic",
                "A masterpiece of storytelling",
                "Incredible film",
                "A defining moment in cinema",
            ]

            contents = [
                f"'{movie_title}' is nothing short of a masterpiece. Every aspect of this film is crafted with precision and care, from the stunning cinematography to the outstanding performances. This is the kind of movie that reminds us why we love cinema.",
                f"What an incredible achievement! '{movie_title}' delivers on every level - the direction is masterful, the acting is superb, and the story is both engaging and meaningful. This is cinema at its finest.",
                f"A true work of art that transcends its genre. '{movie_title}' is beautifully crafted with exceptional attention to detail. The emotional depth and storytelling are simply outstanding.",
                f"This film is pure cinematic magic. '{movie_title}' showcases the very best of what movies can achieve. The performances are authentic, the visuals are stunning, and the story is unforgettable.",
                f"An exceptional film that deserves all the praise it receives. '{movie_title}' is masterfully directed with outstanding performances and a story that resonates deeply. A true masterpiece.",
            ]

        # Very good movies (7.5-8.4)
        elif rating_category == "very_good":
            titles = [
                "Great film!",
                "Highly recommended!",
                "Excellent movie!",
                "Really enjoyed this",
                "Well-crafted film",
                "Strong performances",
                "Engaging story",
                "Quality filmmaking",
                "Worth watching",
                "Impressive work",
            ]

            contents = [
                f"'{movie_title}' is a really solid film with strong performances and an engaging story. The direction is confident and the pacing keeps you invested throughout. Definitely worth your time.",
                f"I thoroughly enjoyed '{movie_title}'. The film has a good balance of entertainment and substance, with quality acting and a well-crafted narrative. Recommended for sure.",
                f"This is a well-made film that delivers on its promises. '{movie_title}' features strong performances and an engaging plot that keeps you interested from start to finish.",
                f"'{movie_title}' is a quality piece of filmmaking with good performances and an interesting story. The film manages to be both entertaining and meaningful.",
                f"A solid film that showcases good storytelling and acting. '{movie_title}' is well-paced and engaging, making for an enjoyable viewing experience.",
            ]

        # Good movies (6.5-7.4)
        elif rating_category == "good":
            titles = [
                "Good movie",
                "Enjoyable watch",
                "Decent film",
                "Worth a look",
                "Not bad",
                "Has its moments",
                "Pretty good",
                "Decent entertainment",
                "Okay film",
                "Fairly enjoyable",
            ]

            contents = [
                f"'{movie_title}' is a decent film with some good moments. While it's not groundbreaking, it's entertaining enough and has some solid performances. Worth watching if you're interested in the genre.",
                f"This is a fairly enjoyable movie with some good elements. '{movie_title}' has its strengths, though it's not without flaws. It's a decent way to spend a couple of hours.",
                f"'{movie_title}' is okay - it has some good parts and some weaker moments. The acting is generally decent and the story is passable, though nothing particularly memorable.",
                f"A reasonably good film that does what it sets out to do. '{movie_title}' is entertaining enough, though it won't blow you away. Decent for what it is.",
                f"This movie has its moments and some good performances. '{movie_title}' is watchable and reasonably entertaining, though it's not going to be anyone's favorite film.",
            ]

        # Average movies (5.5-6.4)
        elif rating_category == "average":
            titles = [
                "Mediocre",
                "Average at best",
                "Nothing special",
                "Forgettable",
                "Meh",
                "Could be better",
                "Not great",
                "Disappointing",
                "Lacks substance",
                "Underwhelming",
            ]

            contents = [
                f"'{movie_title}' is pretty mediocre. The film has some okay moments but overall feels forgettable. The acting is passable but the story lacks real engagement.",
                f"This movie is average at best. '{movie_title}' doesn't really excel in any particular area - the acting is okay, the story is predictable, and it's just not very memorable.",
                f"'{movie_title}' is disappointing. While it's not terrible, it's not particularly good either. The film feels like it could have been much better with better execution.",
                f"A forgettable film that doesn't leave much of an impression. '{movie_title}' has some decent elements but overall feels underwhelming and lacks real substance.",
                f"This movie is just okay - nothing special. '{movie_title}' has its moments but overall feels like a missed opportunity. It's watchable but not particularly engaging.",
            ]

        # Poor movies (below 5.5)
        else:
            titles = [
                "Not good",
                "Poor quality",
                "Waste of time",
                "Terrible",
                "Bad film",
                "Avoid this",
                "Disappointing",
                "Awful",
                "Boring",
                "Hard to watch",
            ]

            contents = [
                f"'{movie_title}' is not a good film. The acting is poor, the story is weak, and the overall quality is disappointing. I wouldn't recommend wasting your time on this one.",
                f"This movie is pretty bad. '{movie_title}' has poor acting, a weak plot, and feels like a waste of time. There are much better films out there to watch instead.",
                f"'{movie_title}' is disappointing and poorly made. The film lacks any real quality - bad acting, weak story, and overall poor execution. Avoid this one.",
                f"A terrible film that's hard to watch. '{movie_title}' has almost no redeeming qualities. The acting is bad, the story is boring, and it's just not worth your time.",
                f"This is an awful movie. '{movie_title}' is poorly made with bad acting and a weak story. It's boring and feels like a complete waste of time.",
            ]

        # Add genre-specific elements
        if "action" in genres:
            if rating_category in ["excellent", "very_good"]:
                contents.append(
                    f"'{movie_title}' delivers fantastic action sequences with great choreography and impressive stunts. The action scenes are well-shot and genuinely exciting."
                )
            elif rating_category in ["good", "average"]:
                contents.append(
                    f"The action in '{movie_title}' is decent enough, though nothing particularly groundbreaking. The fight scenes are okay but could have been better executed."
                )
            else:
                contents.append(
                    f"The action in '{movie_title}' is poorly choreographed and unconvincing. The fight scenes are boring and lack any real excitement."
                )

        if "comedy" in genres:
            if rating_category in ["excellent", "very_good"]:
                contents.append(
                    f"'{movie_title}' is genuinely funny with clever humor and great comedic timing. The jokes land well and the comedy feels natural and entertaining."
                )
            elif rating_category in ["good", "average"]:
                contents.append(
                    f"The comedy in '{movie_title}' has some funny moments, though not all jokes land. There are some decent laughs but it's inconsistent."
                )
            else:
                contents.append(
                    f"The humor in '{movie_title}' falls flat. The jokes are unfunny and the comedy feels forced and awkward."
                )

        if "drama" in genres:
            if rating_category in ["excellent", "very_good"]:
                contents.append(
                    f"'{movie_title}' delivers powerful dramatic moments with emotional depth and strong character development. The dramatic elements are well-handled and moving."
                )
            elif rating_category in ["good", "average"]:
                contents.append(
                    f"The dramatic elements in '{movie_title}' are handled reasonably well, though they could have been more impactful. The emotional moments are okay but not particularly moving."
                )
            else:
                contents.append(
                    f"The dramatic elements in '{movie_title}' feel forced and unconvincing. The emotional moments lack authenticity and fail to engage."
                )

        if "horror" in genres:
            if rating_category in ["excellent", "very_good"]:
                contents.append(
                    f"'{movie_title}' creates genuine tension and scares with effective atmosphere and well-crafted horror elements. The film is genuinely frightening and well-executed."
                )
            elif rating_category in ["good", "average"]:
                contents.append(
                    f"The horror elements in '{movie_title}' are decent, with some effective scares and atmosphere. It's not particularly frightening but has its moments."
                )
            else:
                contents.append(
                    f"The horror in '{movie_title}' is ineffective and not scary at all. The scares are predictable and the atmosphere is lacking."
                )

        return {"title": random.choice(titles), "content": random.choice(contents)}
