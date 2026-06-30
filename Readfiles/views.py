import csv
import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from django.db.models import Count

from blog.models import BlogTag, BlogData
from .decorators import unauthenticated_user, allowed_user
from .forms import UserAdminCreationForm, BioForms, CategoryForm, SubscriptionForm

# Create your views here.
from .models import User, Bio, Follow, Category, Subscription, PaidUser

def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@unauthenticated_user
@ensure_csrf_cookie
@csrf_protect
def register_view(request):
    """
    The `register_view` function handles the registration process for users, including form validation,
    saving user information, authentication, and session management.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    user. It contains information about the request, such as the method used (GET or POST), the user's
    IP address, and any data submitted with the request
    :return: a redirect to the 'sub_cat' URL if the form is valid and the user is authenticated.
    Otherwise, it is rendering the 'accounts/register.html' template with the form as context.
    """
    form = UserAdminCreationForm
    if request.method == 'POST':
        form = UserAdminCreationForm(request.POST or None, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.ip = request.META['REMOTE_ADDR']
            instance.save()
            username = request.POST.get('username')
            password = request.POST.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                get_user = Bio.objects.filter(user_id=request.user.pk)
                get_user.update(
                    active_user=True
                )
                request.session['member_id'] = username + '45'

            return redirect('sub_cat')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


# @unauthenticated_user
@unauthenticated_user  # @cache_page(60 * 9)
# @ensure_csrf_cookie
@csrf_protect
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            get_user = Bio.objects.filter(user_id=request.user.pk)
            get_user.update(
                active_user=True
            )
            request.session['member_id'] = username + '45'
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            else:
                messages.info(request, f"{username} logged in successfully, you're now a verified customer :) ✔")
                return redirect('home')
        else:
            messages.info(request, 'registration number OR password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)


def log_out(request):
    user = request.user.pk
    get_user = Bio.objects.filter(user_id=user)
    get_user.update(
        active_user=False
    )
    logout(request)
    # del request.session['member_id']
    return redirect('login')


@allowed_user(allowed_roles=['Publisher', 'None'])
def sub_grouping(request):
    subscribe_all = Subscription.objects.all()
    if request.method == "POST":
        choice = request.POST.get('choice')
        category = Category.objects.get_or_create()
    return render(request, 'accounts/others/pricing.html')


@login_required(login_url='login')
@csrf_protect
def update_acct(request, pk):
    user = Bio.objects.get(id=pk)
    form = BioForms(instance=user)
    if request.method == 'POST':
        form = BioForms(request.POST or None, request.FILES, instance=user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'accounts/profile.html', context)


def my_followers(request):
    user = request.user
    views = Bio.objects.select_related('user').exclude(user=user)
    context = {"views": views, "user": user}
    return render(request, 'accounts/others/followers.html', context)


def follow_user(request):
    follow_id = request.POST.get('follow_id')
    if request.method == 'POST':
        user = request.user
        bio = Bio.objects.get(id=user.pk)
        users = User.objects.get(id=follow_id)
        if users in bio.friend.all():
            bio.friend.remove(follow_id)
        else:
            bio.friend.add(follow_id)

        follows, created = Follow.objects.get_or_create(follower=user, following_id=follow_id)
        if not created:
            follows.value = 'Unfollow' if follows.value == 'Follow' else 'Follow'
            follows.save(update_fields=['value'])
    return HttpResponseRedirect(reverse('u_profile', args=[str(follow_id)]))


def create_profile(request):
    form = BioForms
    if request.method == 'POST':
        form = BioForms(request.POST or None, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
    context = {
        "form": form
    }
    return render(request, 'accounts/profile.html', context)


def user_profile(request, pk):
    user = request.user
    # Single query — removed duplicate Bio.objects.get(pk=pk)
    bios = Bio.objects.select_related('user').prefetch_related('following').get(pk=pk)
    blog = BlogData.objects.filter(author=bios.user).only('id', 'title', 'image', 'created')
    active = bios.active_user
    follow = bios.user in bios.following.all()  # uses prefetch cache

    if request.method == 'POST':
        if bios.user in bios.following.all():
            bios.following.remove(bios.user)
        else:
            bios.following.add(bios.user)
        return JsonResponse({'following': bios.following.count()}, safe=False)

    paginator = Paginator(blog, 5)
    page = request.GET.get('page')
    try:
        blog = paginator.page(page)
    except PageNotAnInteger:
        blog = paginator.page(1)
    except EmptyPage:
        blog = paginator.page(paginator.num_pages)

    context = {'bios': bios, 'blog': blog, 'active': active, 'follow': follow}
    return render(request, 'accounts/others/profile_card.html', context)


@allowed_user(allowed_roles=['None'])
def sub_category(request):
    form = SubscriptionForm
    user = User.objects.all().filter(username=request.user)
    if request.method == "POST":
        form = SubscriptionForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            if request.POST.get('plan') == 'Publisher':
                user.update(
                    category='Publisher'
                )
                return redirect('sub')
            else:
                user.update(
                    category='Reader'
                )
                return redirect('home')

    context = {
        'form': form
    }
    return render(request, 'accounts/category.html', context)


def publisher_cat(request):
    user = request.user
    user_pay = PaidUser.objects.all().filter(user=user)
    # pay = PaidUser.objects.get(id=user.pk)
    if request.method == 'POST':
        category = request.POST.get('category')
        if not user_pay:
            data = PaidUser.objects.create(
                id=user.id,
                user=user,
                category=category,
                due_date=timezone.now() + datetime.timedelta(days=365)
            )
            data.save()
        else:
            # calc = '2022-06-30 00:00:00'
            user_pay.update(
                user=user,
                category=category,
                due_date=timezone.now() + datetime.timedelta(days=365)
            )

    return redirect('home')


@allowed_user(allowed_roles=['Publisher'])
@login_required(login_url='login')
def stats(request):
    if request.method == 'POST':
        blog_ID = request.POST.get('blog_ID')
        BlogData.objects.filter(id=blog_ID).delete()
        return redirect('stats')

    data = BlogData.objects.filter(author=request.user).prefetch_related('liked', 'comments', 'viewed')
    # Compute real aggregates from the prefetch cache — no extra DB queries
    data_list = list(data)
    total_posts = len(data_list)
    total_likes = sum(p.liked.count() for p in data_list)
    total_comments = sum(p.comments.count() for p in data_list)
    total_views = sum(p.viewed.count() for p in data_list)
    context = {
        'data': data,
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_views': total_views,
    }
    return render(request, 'admin/user_stats.html', context)


def blog_csv(request):
    # annotate like_count to avoid N+1 (blog.liked.all().count() per row)
    blogs = BlogData.objects.select_related('author').annotate(like_count=Count('liked'))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={request.user}-bloggarian.csv'

    writer = csv.writer(response)
    writer.writerow(['AUTHOR', 'TITLE', 'IMAGE', 'LIKES', 'CREATED'])
    for blog in blogs:
        writer.writerow([blog.author, blog.title, blog.image, blog.like_count, blog.created.date()])

    return response

# TODO:
