from django.urls import path
from . import views
import secrets

random = secrets.token_urlsafe()
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path('account/login/', views.login_page, name='login'),
    path(f'account/logout/', views.log_out, name='log_out'),
    path('account/profile/<int:pk>/', views.update_acct, name='profile'),
    path('people/', views.my_followers, name='follow'),
    path('follow/', views.follow_user, name='create_follow'),
    path('create_profile/', views.create_profile, name='c_follow'),
    path(f'profile/<int:pk>/', views.user_profile, name='u_profile'),
    # Subscription
    path('subscription/', views.sub_grouping, name='sub'),
    path('category/', views.sub_category, name='sub_cat'),
    path('paid/', views.publisher_cat, name='paid'),
    # Dashboard
    path('my_stats/', views.stats, name='stats'),
    path('blog_csv/', views.blog_csv, name='blog_csv'),
]

# def like_post(request):
#     user = request.user
#     blog_id1 = request.POST.get('post_id')
#     if request.method == "POST":
#         blog_id = request.POST.get('post_id')
#         blog_obj = BlogData.objects.get(id=blog_id)
#
#         if user in blog_obj.liked.all():
#             blog_obj.liked.remove(user)
#         else:
#             blog_obj.liked.add(user)
#
#         like, created = Like.objects.get_or_create(user=user, post_id=blog_id)
#         if not created:
#             if like.value == 'Like':
#                 like.value = 'Unlike'
#             else:
#                 like.value = 'Like'
#         like.save()
#     return HttpResponseRedirect(reverse('blog_detail', args=[str(blog_id1)]))
