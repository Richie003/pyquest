from django.contrib import admin

# Register your models here.
from .models import BlogData, BlogTag, Comment, Like, Settings, Theme, NewBlog


class BlogDataAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'description',
        'created', 'title')
    list_filter = (
        'author',
        'description',
        'created', 'title', 'blog_tag')


admin.site.register(BlogData, BlogDataAdmin)
admin.site.register(BlogTag)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Settings)
admin.site.register(Theme)
admin.site.register(NewBlog)
