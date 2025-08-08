
# Moodie - Movie Review Platform

**Live Demo**: [https://moodie.up.railway.app/](https://moodie.up.railway.app/)

---

---

## 📚 Table of Contents

- [🎬 Project Overview](#-project-overview)
- [✨ Key Features](#-key-features)
- [📸 App in Action](#-app-in-action)
- [⚙️ Tech Stack](#-tech-stack)
- [✅ How It Meets Exam Requirements](#-how-it-meets-exam-requirements)
- [🔐 Authentication & Permissions](#-authentication--permissions)
- [🛡 Security & Validation](#-security--validation)
- [📊 Admin Dashboard Features](#-admin-dashboard-features)
- [🧪 Testing](#-testing)
- [🚀 Deployment Details](#-deployment-details)
- [🔎 Extra Features](#-extra-features)
- [🧠 Code Structure & Best Practices](#-code-structure--best-practices)
- [📈 Project Stats](#-project-stats)
- [🛠 Getting Started](#-getting-started)
- [✅ Running Tests](#-running-tests)
- [🏁 Final Notes](#-final-notes)
- [🔮 Future Plans](#-future-plans)


## 🎬 Project Overview

**Moodie** is a Django-based web app for people who love movies - whether that means rating what you've just seen, planning what to watch next, or simply discovering something new.

The app lets users browse thousands of movies, read and write reviews, manage personal watchlists, and connect through shared movie interests. Admins and staff have access to tools for content moderation and management via a custom dashboard.

The interface is responsive and built with Tailwind CSS. Behind the scenes, Moodie uses PostgreSQL in production and pulls its movie data from TMDB's API. It's also packed with features like image uploads, role-based access, and full CRUD functionality for core models.

---

## ✨ Key Features

Moodie is built around a few core experiences:

- **Movie Browsing** - Explore detailed movie pages with posters, ratings, and metadata.
- **Review System** - Rate and review any movie (1-10 scale) and read others' opinions.
- **Watchlists** - Add movies to your personal list to watch later or track favorites.
- **User Profiles** - Upload an avatar, set your favorite genres, and manage your reviews.
- **Admin Dashboard** - Role-based admin views for managing users, movies, reviews, etc.
- **Role-Based Access** - Permissions vary by user type (guest, user, staff, admin).
- **Responsive UI** - Clean layout that adapts across mobile and desktop devices.

---

## 📸 App in Action

A few quick looks at how Moodie works in the browser:

**Homepage & Movie Browsing**  
Browse recent movies, open a detail page, and view reviews.  

![Homepage](assets/homepage.gif)

---

**Writing a Review**  
Logged-in users can rate movies and share quick thoughts.  

![Write Review](assets/review-posting.gif)

---

**Watchlist Management**  
Add or remove movies to your personal watchlist instantly.  

![Watchlist](assets/watchlist.gif)

---

**Admin Dashboard**  
Admins get access to a custom dashboard for managing users, movies, and reviews. They can also edit directors and actors. 

![Admin Dashboard](assets/admin-dashboard.gif)


## ⚙️ Tech Stack

Moodie is built with the following tools:


- ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
  **Backend** – Handles core logic and routing.

- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
  **Database** – PostgreSQL in production, SQLite in development.

- ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat&logo=tailwind-css&logoColor=white)
  ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
  ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
  **Frontend** – Built with Tailwind, HTML, and a bit of JS.

- ![TMDB](https://img.shields.io/badge/TMDB-01B4E4?style=flat&logo=themoviedatabase&logoColor=white)
  ![OMDb](https://img.shields.io/badge/OMDb-FF4500?style=flat)
  **External APIs** – Movie data from TMDB, IMDb ratings from OMDb.

- ![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=flat&logo=railway&logoColor=white)
  **Deployment** – Deployed with Railway.

- ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)
  ![Django](https://img.shields.io/badge/Django%20TestCase-092E20?style=flat&logo=django&logoColor=white)
  **Testing** – Pytest and Django’s built-in testing tools.

---

## ✅ How It Meets Exam Requirements

### Django Pages & Views

Moodie includes 25+ unique pages and covers both class-based and function-based views:

#### Class-Based Views (Examples)
- `HomeView` - Homepage with recent movies and reviews
- `MovieListView`, `MovieDetailView`, `MovieCreateView`, etc.
- `ReviewCreateView`, `ReviewUpdateView`, `ReviewDeleteView`
- `ProfileView`, `WatchlistView`, `AdminDashboardView` and more

#### Function-Based Views
- `register` - New user sign-up
- `logout` - Log out
- `add_to_watchlist`, `remove_from_watchlist`

### Models

Moodie uses 8 models (1 built-in + 7 custom):

- `User` - Django's built-in auth model
- `Profile` - Extended user details
- `Movie`, `Genre`, `Director`, `Actor` - Core movie metadata
- `Review`, `Comment`, `Watchlist` - User-generated content

### Forms

Custom forms are used for:

- User registration and profile updates
- Password change
- Movie, review, and comment submission
- Movie search

Total: 8 custom forms.

### Templates

There are 20+ templates organized by function, using a shared base layout:

- `base.html`, `home.html`, `movie_detail.html`, `profile.html`, etc.
- Admin-specific templates: `admin_dashboard.html`, `admin_movies.html`, etc.

---

## 🔐 Authentication & Permissions

- **Public users**: Can view movies, read reviews, browse genres, register/login
- **Authenticated users**: Can add/edit/delete their own reviews and comments, manage watchlist, update profiles
- **Staff**: Can manage content in admin views
- **Superusers**: Have full access to all models and admin features

Permissions are handled using Django's mixins:
- `LoginRequiredMixin`
- `UserPassesTestMixin`
- `Custom AdminPermissionMixin`

---

## 🛡 Security & Validation

### Server-Side Protections

- Form and model validation
- Custom `clean()` methods in forms
- Input sanitization (e.g. `strip_tags`, regex cleanup)
- CSRF protection enabled site-wide
- All database operations handled through Django ORM

### Client-Side

- HTML5 validation on all forms
- JavaScript-based instant feedback for form errors

### Custom Error Handling

- 404 and 500 pages with custom templates
- Graceful handling of missing data
- Meaningful error messages

---

## 📊 Admin Dashboard Features

Admins and staff users have access to a full content management system:

- Manage movies, genres, actors, directors, reviews, and users
- Search, filters, and bulk actions for efficient workflows
- Upload and validate media files (e.g. posters, avatars)
- Dashboard statistics and activity logs

---

## 🧪 Testing

Tests cover both unit and integration levels:

```text
tests/
├── unit/
│   ├── test_accounts.py
│   ├── test_admin.py
│   ├── test_movies.py
│   └── test_reviews.py
├── integration/
└── e2e/
```

- Written using Django's `TestCase` and extended with `pytest`
- Factory pattern for generating test data
- Mocks for external API calls
- Coverage reports available for CI pipelines

---

## 🚀 Deployment Details

The project is deployed on **Railway** with:

- Environment-specific settings
- SSL enforcement and security headers
- Automatic migrations on deploy
- Static/media file handling for production

---

## 🔎 Extra Features

- **Search & Filtering** - Search movies by title, filter by genre or rating
- **Comments** - Users can comment on reviews
- **Watchlist UI** - Easy add/remove buttons and personalized movie list
- **Image Handling** - External image URLs from TMDB + local media uploads

---

## 🧠 Code Structure & Best Practices

- Follows Django's **MVT** architecture strictly
- Code follows **SOLID** principles where applicable
- Modular app-based layout
- Models are documented and use type hints
- Views are DRY and class-based where possible
- Query optimization with `select_related()` / `prefetch_related()`

---

## 📈 Project Stats

- 8 models
- 25+ views
- 8 forms
- 20+ templates
- Fully custom admin area
- Extensive test coverage
- Full permission system

---

## 🛠 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Setup

```bash
git clone <repo-url>
cd moodie

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your own DB settings and secrets

python manage.py migrate
python manage.py createsuperuser
python run_tests.py
python manage.py runserver
```

---

## ✅ Running Tests

```bash
# Run all tests
python run_tests.py

# Run with coverage
pytest --cov

# Run unit-only
pytest tests/unit

# Run integration
pytest tests/integration
```

---

## 🏁 Final Notes

Moodie was built as part of an advanced Django project challenge, but more than that - it was a personal dive into full-stack development. It covers everything from frontend responsiveness to backend validation, admin tools, security, and testing.

It's meant to be both a polished product and a learning experience - and it's still growing.

---

## 🔮 Future Plans


- 🎭 **User Messaging** – Let users chat directly about movies they’ve both seen.
- 📺 **TV Shows Support** – Add shows with seasons, episodes, and tracking.
- 🧠 **Smart Recommendations** – Suggest movies based on your ratings and reviews.
- 🎨 **Dark Mode** – Optional dark theme for better late-night browsing.
- 🗂 **Better Discovery** – Combine filters to find exactly what you’re in the mood for.
- 💬 **Reactions on Comments** – Add quick likes/dislikes to keep the good stuff visible.
- 🏆 **User Badges** – Small achievements for activity like reviewing or watchlisting.

Always open to ideas and feedback!
