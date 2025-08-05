from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = "Create an admin user for the Django application"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="Admin username (default: admin)",
        )
        parser.add_argument(
            "--email",
            type=str,
            default="admin@moodie.com",
            help="Admin email (default: admin@moodie.com)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="admin123",
            help="Admin password (default: admin123)",
        )
        parser.add_argument(
            "--first-name",
            type=str,
            default="Admin",
            help="Admin first name (default: Admin)",
        )
        parser.add_argument(
            "--last-name",
            type=str,
            default="User",
            help="Admin last name (default: User)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        first_name = options["first_name"]
        last_name = options["last_name"]

        # Check if admin user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'⚠️ Admin user "{username}" already exists!'))
            return

        # Create admin user
        try:
            admin_user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password(password),
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Admin user created successfully!"))
            self.stdout.write(f"👤 Username: {admin_user.username}")
            self.stdout.write(f"🔑 Password: {password}")
            self.stdout.write(f"📧 Email: {admin_user.email}")
            self.stdout.write(f"👨‍💼 Full Name: {admin_user.first_name} {admin_user.last_name}")
            self.stdout.write(f"🔗 Admin URL: http://127.0.0.1:8000/admin/")

        except Exception:
            self.stdout.write(self.style.ERROR(f"❌ Error creating admin user: {e}"))
