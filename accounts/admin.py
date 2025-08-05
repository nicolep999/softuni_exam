from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group, Permission
from .models import Profile

admin.site.unregister(User)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    filter_horizontal = ("favorite_genres",)


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
        "display_avatar",
        "review_count",
        "watchlist_count",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "date_joined")
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "profile__bio",
        "profile__location",
    )
    date_hierarchy = "date_joined"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def display_avatar(self, obj):
        if hasattr(obj, "profile") and obj.profile.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile.avatar.url,
            )
        return "No Avatar"

    display_avatar.short_description = "Avatar"

    def review_count(self, obj):
        return obj.reviews.count()

    review_count.short_description = "Reviews"

    def watchlist_count(self, obj):
        return obj.watchlist.count()

    watchlist_count.short_description = "Watchlist"


def create_admin_groups():
    try:
        content_managers, created = Group.objects.get_or_create(name="Content Managers")
        if created:
            movie_permissions = Permission.objects.filter(
                content_type__app_label="movies",
                content_type__model__in=["movie", "genre", "director", "actor"],
            )
            content_managers.permissions.add(*movie_permissions)

        review_managers, created = Group.objects.get_or_create(name="Review Managers")
        if created:
            review_permissions = Permission.objects.filter(
                content_type__app_label="reviews", content_type__model__in=["review", "comment"]
            )
            review_managers.permissions.add(*review_permissions)
    except Exception:
        print(f"Error creating admin groups: {e}")


admin.site.register(User, CustomUserAdmin)

try:
    create_admin_groups()
except Exception:
    print(f"Error in admin groups creation: {e}")
