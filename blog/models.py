from django.conf import settings
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.timezone import now


# Create your models here.
class BlogTag(models.Model):
    lists = (
        ('AI', 'AI'),
        ('KITCHEN', 'KITCHEN')
    )
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.name)


class BlogData(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    title = models.CharField(default='', max_length=100, null=True, blank=True)
    description = models.CharField(default='', max_length=200, blank=True, null=True)
    # article = models.TextField(default='', max_length=7000, null=False, blank=False, )
    article = RichTextField(blank=True, null=True)
    image = models.ImageField(default='profile1.jpg', blank=True, null=True,
                                upload_to='blog_img/')
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes', default='', blank=True)
    anon_like = models.CharField(default="", max_length=255, blank=True, null=False)
    viewed = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='viewed', default='', blank=True)
    created = models.DateTimeField(auto_created=True, auto_now_add=True, editable=True)
    updated = models.DateTimeField(auto_now=True)
    blog_tag = models.ManyToManyField(BlogTag)

    def __str__(self):
        return str(self.title)

    def __unicode__(self):
        return str(self.title)

    @property
    def num_likes(self):
        return self.liked.all().count()
    
    @property
    def get_comments(self):
        return Comment.objects.filter(id=self.id)
    
    @property
    def get_episodes(self):
        query_episodes = Episode.objects.filter(linked_to_id=self.id)
        return query_episodes
        

    class Meta:
        ordering = ['-created', '-updated']

class Comment(models.Model):
    blog = models.ForeignKey(BlogData, null=True, related_name="comments", on_delete=models.SET_NULL)
    name = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    anon_user = models.CharField(default='', max_length=255, blank=True)
    body = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return "%s - %s" % (self.blog, self.name)
        elif self.anon_user:
            return "%s - %s" % (self.blog, self.anon_user)
        else:
            return str(self.blog)

    class Meta:
        ordering = ['-date_added']


class Episode(models.Model):
    linked_to = models.ForeignKey(BlogData, null=True, default=1, on_delete=models.SET_NULL, blank=True)
    title = models.CharField(default='', max_length=100, null=True, blank=True)
    article = RichTextField(blank=True, null=True)
    created = models.DateTimeField(auto_created=True, auto_now_add=True, editable=True)
    updated = models.DateTimeField(default=now)
    
    def __str__(self):
        return str(self.linked_to)
    
    @property
    def get_episode_comments(self):
        query_episode_comment = EpisodeComment.objects.filter(episode_name=self.id)
        return query_episode_comment
    
    class Meta:
        ordering = ['-created']

class EpisodeComment(models.Model):
    episode_name = models.ForeignKey(Episode, null=True, related_name="comments", on_delete=models.SET_NULL)
    name = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    anon_user = models.CharField(default='', max_length=255, blank=True)
    body = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return "%s - %s" % (self.blog, self.name)
        elif self.anon_user:
            return "%s - %s" % (self.blog, self.anon_user)
        else:
            return str(self.episode_name)

    class Meta:
        ordering = ['-date_added']
class Like(models.Model):
    LIKE_CHOICES = (
        ('Like', 'Like'),
        ('Dislike', 'Dislike'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, default=1, on_delete=models.CASCADE, blank=True)
    post = models.ForeignKey(BlogData, null=True, default=1, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, default="", max_length=20)
    anon = models.CharField(default="", max_length=255, blank=True, null=False)

    def __str__(self):
        return str(self.post)


class Settings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class Theme(models.Model):
    name = models.CharField(max_length=30, default='')
    theme = models.CharField(max_length=30, default='')

    def __str__(self):
        return str(self.theme)


class NewBlog(models.Model):
    number = models.CharField(max_length=500, default='')

    def __str__(self):
        return self.number
