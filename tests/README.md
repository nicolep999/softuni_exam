# Moodie Test Suite

This directory contains the comprehensive test suite for the Moodie movie review application.

## Test Structure

```
tests/
├── __init__.py              # Makes tests a Python package
├── conftest.py              # Pytest configuration and fixtures
├── factories.py             # Test data factories
├── README.md               # This file
├── unit/                   # Unit tests
│   ├── __init__.py
│   ├── test_accounts.py    # Account-related tests
│   ├── test_admin.py       # Admin functionality tests
│   ├── test_movies.py      # Movie-related tests
│   └── test_reviews.py     # Review-related tests
├── integration/            # Integration tests (future)
│   └── __init__.py
└── e2e/                   # End-to-end tests (future)
    └── __init__.py
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **test_accounts.py**: User registration, login, profile management
- **test_admin.py**: Admin dashboard, CRUD operations for content
- **test_movies.py**: Movie models, views, forms, watchlist functionality
- **test_reviews.py**: Review models, views, forms, comments

### Integration Tests (`tests/integration/`)
- Cross-app functionality tests
- API integration tests
- Database transaction tests

### End-to-End Tests (`tests/e2e/`)
- Full user workflow tests
- Browser automation tests (future)

## Running Tests

### Using the Central Test Runner

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --e2e

# Run with coverage
python run_tests.py --coverage

# Run system checks only
python run_tests.py --check

# Run specific test file
python run_tests.py tests/unit/test_accounts.py

# Verbose output
python run_tests.py --verbose
```

### Using Django's Test Runner

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test movies
python manage.py test reviews

# Run specific test class
python manage.py test accounts.tests.ProfileModelTest

# Run specific test method
python manage.py test accounts.tests.ProfileModelTest.test_profile_creation

# Verbose output
python manage.py test -v 2

# Parallel execution
python manage.py test --parallel
```

### Using Pytest

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_accounts.py

# Run tests with markers
pytest -m "unit"
pytest -m "admin"
pytest -m "not slow"

# Verbose output
pytest -v

# Coverage
pytest --cov=. --cov-report=html
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `client`: Django test client
- `user`: Regular user
- `staff_user`: Staff user
- `superuser`: Superuser
- `genre`, `director`, `actor`: Test data objects
- `movie`: Movie with related objects
- `review`: Review with related objects
- `authenticated_client`, `staff_client`, `admin_client`: Pre-authenticated clients

## Test Factories

Test data factories are available in `factories.py`:

- `UserFactory`: Create test users
- `MovieFactory`: Create test movies
- `ReviewFactory`: Create test reviews
- `GenreFactory`, `DirectorFactory`, `ActorFactory`: Create test entities

## Writing Tests

### Django TestCase Style

```python
from django.test import TestCase
from django.urls import reverse

class MyModelTest(TestCase):
    def setUp(self):
        # Setup test data
        pass
    
    def test_something(self):
        # Test logic
        self.assertEqual(1, 1)
```

### Pytest Style with Fixtures

```python
import pytest
from django.urls import reverse

def test_something(client, user):
    # Test logic using fixtures
    response = client.get(reverse('some_url'))
    assert response.status_code == 200
```

### Using Factories

```python
from tests.factories import MovieFactory, UserFactory

def test_with_factories():
    movie = MovieFactory()
    user = UserFactory()
    # Test logic
```

## Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_function():
    pass

@pytest.mark.slow
def test_slow_function():
    pass
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests in this pattern
4. **Use Fixtures**: Leverage pytest fixtures for common setup
5. **Test Edge Cases**: Include tests for error conditions
6. **Keep Tests Fast**: Avoid slow operations in unit tests
7. **Use Factories**: Use factories for creating test data
8. **Test Permissions**: Always test permission requirements

## Coverage

To generate coverage reports:

```bash
# Using the test runner
python run_tests.py --coverage

# Using pytest directly
pytest --cov=. --cov-report=html --cov-report=term

# Using Django
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

- All tests should pass before merging
- Coverage reports are generated automatically
- System checks are run as part of the test suite
- Migration checks ensure database consistency 