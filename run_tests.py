#!/usr/bin/env python
"""
Central test runner for Moodie project.
This script provides a unified way to run tests with different configurations.
"""
import sys
import os
import argparse
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def run_django_tests(test_path=None, verbosity=2, parallel=None, coverage=False):
    """Run Django tests with specified options."""
    command_parts = ["python", "manage.py", "test"]

    if test_path:
        command_parts.append(test_path)

    if verbosity:
        command_parts.extend(["-v", str(verbosity)])

    if parallel:
        command_parts.extend(["--parallel", str(parallel)])

    command = " ".join(command_parts)
    return run_command(command, "Django Tests")


def run_pytest_tests(test_path=None, verbose=False, coverage=False):
    """Run pytest tests with specified options."""
    command_parts = ["pytest"]

    if test_path:
        command_parts.append(test_path)
    else:
        command_parts.append("tests/")

    if verbose:
        command_parts.append("-v")

    if coverage:
        command_parts.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])

    command = " ".join(command_parts)
    return run_command(command, "Pytest Tests")


def run_system_check():
    """Run Django system check."""
    command = "python manage.py check"
    return run_command(command, "Django System Check")


def run_migrations_check():
    """Check for pending migrations."""
    command = "python manage.py makemigrations --check --dry-run"
    return run_command(command, "Migration Check")


def run_linting():
    """Run code linting (if flake8 is available)."""
    try:
        # Use UTF-8 encoding to avoid Windows encoding issues
        command = "flake8 . --exclude=.venv,__pycache__,migrations --max-line-length=120"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        if result.returncode == 0:
            print(result.stdout)
            print(f"\n✅ Code Linting (flake8) completed successfully!")
            return True
        else:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            print(f"\n❌ Code Linting (flake8) failed with exit code {result.returncode}")
            return False
    except (ImportError, UnicodeDecodeError, FileNotFoundError):
        print("\n⚠️  flake8 not available or encoding issues. Skipping linting.")
        return True


def main():
    """Main function to handle command line arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Moodie Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --django           # Run only Django tests
  python run_tests.py --pytest           # Run only pytest tests
  python run_tests.py --unit             # Run only unit tests
  python run_tests.py --coverage         # Run tests with coverage
  python run_tests.py --check            # Run system checks only
  python run_tests.py tests/unit/        # Run specific test path
        """,
    )

    parser.add_argument(
        "test_path", nargs="?", help="Specific test path to run (e.g., tests/unit/test_accounts.py)"
    )

    parser.add_argument("--django", action="store_true", help="Run Django tests only")

    parser.add_argument("--pytest", action="store_true", help="Run pytest tests only")

    parser.add_argument("--unit", action="store_true", help="Run unit tests only")

    parser.add_argument("--integration", action="store_true", help="Run integration tests only")

    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")

    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage reporting")

    parser.add_argument("--check", action="store_true", help="Run system checks only (no tests)")

    parser.add_argument("--lint", action="store_true", help="Run code linting only")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    parser.add_argument(
        "--parallel", "-p", type=int, help="Run tests in parallel (number of processes)"
    )

    args = parser.parse_args()

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    print("🎬 Moodie Test Runner")
    print("=" * 60)

    success = True

    # Handle specific test path
    if args.test_path:
        if args.pytest:
            success &= run_pytest_tests(args.test_path, args.verbose, args.coverage)
        else:
            success &= run_django_tests(
                args.test_path, 2 if args.verbose else 1, args.parallel, args.coverage
            )
        return 0 if success else 1

    # Handle specific test types
    if args.unit:
        success &= run_django_tests(
            "tests.unit", 2 if args.verbose else 1, args.parallel, args.coverage
        )
        return 0 if success else 1

    if args.integration:
        success &= run_django_tests(
            "tests.integration", 2 if args.verbose else 1, args.parallel, args.coverage
        )
        return 0 if success else 1

    if args.e2e:
        success &= run_django_tests(
            "tests.e2e", 2 if args.verbose else 1, args.parallel, args.coverage
        )
        return 0 if success else 1

    # Handle specific runners
    if args.django:
        success &= run_django_tests(None, 2 if args.verbose else 1, args.parallel, args.coverage)
        return 0 if success else 1

    if args.pytest:
        success &= run_pytest_tests(None, args.verbose, args.coverage)
        return 0 if success else 1

    if args.check:
        success &= run_system_check()
        success &= run_migrations_check()
        return 0 if success else 1

    if args.lint:
        success &= run_linting()
        return 0 if success else 1

    # Default: run comprehensive test suite
    print("\n🚀 Running comprehensive test suite...")

    # System checks
    success &= run_system_check()
    success &= run_migrations_check()

    # Linting
    success &= run_linting()

    # Tests
    if args.coverage:
        success &= run_pytest_tests(None, args.verbose, True)
    else:
        success &= run_django_tests(None, 2 if args.verbose else 1, args.parallel, False)

    # Final result
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests and checks passed!")
        return 0
    else:
        print("❌ Some tests or checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
