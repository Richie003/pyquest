from django.conf import settings
from django.db.models.signals import post_save
from .models import Bio
from .models import User


def user_bio(sender, instance, created, **kwargs):
    if created:
        bio = Bio.objects.create(
            user=instance,
            id=instance.id
        )
        bio.save()


post_save.connect(user_bio, sender=User)
