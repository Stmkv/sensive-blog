from django.contrib import admin

from blog.models import Comment, Post, Tag


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ["author"]
    list_per_page = 10


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ["author"]
    list_per_page = 10
    exclude = ["likes"]


admin.site.register(Tag)
