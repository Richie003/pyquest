from django.db.models.signals import post_save
from .models import BlogData, NewBlog


def blog_alert(sender, instance, created, **kwargs):
    if created:
        NewBlog.objects.update(
            number=1
        )
        print('New Blog created!!')


post_save.connect(blog_alert, sender=BlogData)
