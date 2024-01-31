from django.contrib import admin

# Register your models here.
from .models import *


class BlogDataAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'description',
        'created', 'title')
    list_filter = (
        'author',
        'description',
        'created', 'title', 'blog_tag')

class EpisodesAdmin(admin.ModelAdmin):
    list_display = ('title', 'linked_to', 'created', 'updated')
    search_fields = ('title', 'article')
    list_filter = ('created', 'updated', 'linked_to')
    date_hierarchy = 'created'
    readonly_fields = ('linked_to',)


admin.site.register(BlogData, BlogDataAdmin)
admin.site.register(Episode, EpisodesAdmin)
admin.site.register(BlogTag)
admin.site.register(Comment)
admin.site.register(EpisodeComment)
admin.site.register(Like)
admin.site.register(Settings)
admin.site.register(Theme)
admin.site.register(NewBlog)
