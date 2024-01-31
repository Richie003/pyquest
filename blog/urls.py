from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views
import secrets

random = secrets.token_urlsafe()

urlpatterns = [
    path('', views.index, name='home'),
    path("blog/", views.blog_view, name="blog_view"),
    path(f"blog/<int:pk>/", views.blog_detail, name="blog_detail"),
    path(f'upload/', views.blog_upload, name='upload_b'),
    path('update/<str:pk>/', views.blog_update, name='update'),
    path('delete/<str:pk>/', views.blog_delete, name='delete'),
    path('like/', views.like_post, name='like_blog'),
    path('search/', views.search_res, name='search'),
    path('create_episode/<str:title>/<int:pk>/', views.create_episode, name="create_episode"),
    path('get_episode_data/', views.episode_data)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# def cocktail_sort(a):
#     n = len(a)
#     swapped = True
#     start = 0
#     end = n - 1
#     while swapped:
#         swapped = False
#         for i in range(start, end):
#             if a[i] > a[i + 1]:
#                 a[i], a[i + 1] = a[i + 1], a[i]
#                 swapped = True
#         if not swapped:
#             break
#         swapped = False
#         end = end - 1
#         for i in range(end - 1, start - 1, -1):
#             if a[i] > a[i + 1]:
#                 a[i], a[i + 1] = a[i + 1], a[i]
#                 swapped = True
#         start = start + 1