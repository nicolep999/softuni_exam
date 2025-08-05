from django.contrib import admin
from .models import Review, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("user", "content", "created_at")


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "movie_title",
        "user",
        "rating",
        "created_at",
        "updated_at",
        "comment_count",
    )
    list_filter = ("rating", "created_at", "movie")
    search_fields = ("title", "content", "user__username", "movie__title")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = [CommentInline]
    list_per_page = 20

    def movie_title(self, obj):
        return obj.movie.title

    movie_title.short_description = "Movie"
    movie_title.admin_order_field = "movie__title"

    def comment_count(self, obj):
        return obj.comments.count()

    comment_count.short_description = "Comments"


class RatingFilter(admin.SimpleListFilter):
    title = "Rating"
    parameter_name = "rating"

    def lookups(self, request, model_admin):
        return (
            ("low", "Low (1-3)"),
            ("medium", "Medium (4-7)"),
            ("high", "High (8-10)"),
        )

    def queryset(self, request, queryset):
        if self.value() == "low":
            return queryset.filter(rating__lte=3)
        if self.value() == "medium":
            return queryset.filter(rating__gt=3, rating__lt=8)
        if self.value() == "high":
            return queryset.filter(rating__gte=8)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("truncated_content", "user", "review_title", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "user__username", "review__title")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    def truncated_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    truncated_content.short_description = "Content"

    def review_title(self, obj):
        return obj.review.title

    review_title.short_description = "Review"
    review_title.admin_order_field = "review__title"


# Register models
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
