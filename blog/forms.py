from django import forms
from django.forms import CheckboxSelectMultiple

from .models import Comment, BlogData, Settings, BlogTag, Episode
from django.dispatch import receiver


class BlogDataForm(forms.ModelForm):
    class Meta:
        model = BlogData
        fields = (
            'title',
            'description',
            'article',
            'image',
            'blog_tag'
        )

    # def __init__(self, *args, **kwargs):
    #     super(BlogDataForm, self).__init__(*args, **kwargs)

    #     self.fields["blog_tag"].widget = CheckboxSelectMultiple()
    #     self.fields["blog_tag"].queryset = BlogTag.objects.all()

    # def save(self, commit=True):
    #     # Save the provided password in hashed format
    #     blog = super(BlogDataForm, self).save(commit=False)
    #     blog.blog_tag(self.cleaned_data["blog_tag"])
    #     if commit:
    #         blog.save()
    #     return blog


class EpisodeForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = (
            'title',
            'article',
        )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            "body",
        )


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = (
            '__all__'
        )
