from urllib.parse import quote_plus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from Readfiles.decorators import allowed_user
from Readfiles.models import PaidUser
from .models import *
from .forms import *


def index(request):
    tags = BlogTag.objects.all()
    data = request.GET.get('tag')
    if data:
        return redirect(f'/blog/?search={data}')

    items = BlogData.objects.select_related('author').prefetch_related('liked', 'comments')
    paginator = Paginator(items, 3)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {'tags': tags, 'items': items}
    return render(request, 'index/index.html', context)


def nav(request):
    tags = BlogTag.objects.all()
    return render(request, 'navs/nav.html', {'tags': tags})


@login_required
@csrf_protect
def blog_view(request):
    tags = BlogTag.objects.all()
    data = request.GET.get('tag')
    if data:
        return redirect(f'/blog/?search={data}')

    blog_dt = BlogData.objects.select_related('author').prefetch_related('liked', 'comments')

    paginator = Paginator(blog_dt, 6)
    page = request.GET.get('page')
    try:
        blog_dt = paginator.page(page)
    except PageNotAnInteger:
        blog_dt = paginator.page(1)
    except EmptyPage:
        blog_dt = paginator.page(paginator.num_pages)

    context = {'blog_dt': blog_dt, 'tags': tags}
    return render(request, 'blog1/blog_lists.html', context)


def search_res(request):
    if request.is_ajax():
        blog = request.POST.get('blog', '').strip()
        if not blog:
            return JsonResponse({'data': 'No results found!'})

        # select_related prevents N+1 on author access; limit to 10 results
        qs = BlogData.objects.filter(
            Q(title__icontains=blog) | Q(author__username__icontains=blog)
        ).select_related('author').distinct()[:10]

        if qs:
            data = [
                {'pk': pos.pk, 'title': pos.title, 'author': pos.author.username, 'image': pos.image.url}
                for pos in qs
            ]
            return JsonResponse({'data': data})
        return JsonResponse({'data': 'No results found!'})
    return JsonResponse({})


@csrf_protect
def blog_detail(request, pk):
    user = request.user

    # Single query — joins author, prefetches all M2M in 3 extra queries (not N+1)
    view = BlogData.objects.select_related('author').prefetch_related(
        'liked', 'viewed', 'blog_tag'
    ).get(id=pk)

    # Fetch only the fields the template needs for related posts
    other = BlogData.objects.filter(
        author_id=view.author_id
    ).exclude(id=pk).only('id', 'title', 'created')

    tags = BlogTag.objects.all()
    taggs = view.blog_tag.all()  # uses prefetch cache — no extra query
    comments = Comment.objects.filter(blog_id=pk).select_related('name')

    # M2M .add() is idempotent — the DB prevents duplicate entries
    if user.is_authenticated:
        view.viewed.add(user)

    data = request.GET.get('tag')
    if data:
        return redirect(f'/blog/?search={data}')

    form = CommentForm
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.blog = view
            if user.is_authenticated:
                instance.name = user
            else:
                instance.anon_user = request.POST.get('anon-user', '')
            instance.save()
            return HttpResponseRedirect(reverse('blog_detail', args=[str(pk)]))

    context = {
        'comments': comments,
        'form': form,
        'taggs': taggs,
        'tags': tags,
        'view': view,
        'counter': comments.count(),
        'other': other,
        'user': user,
        'encoded_path': quote_plus(request.path),
    }
    return render(request, 'blog1/blog-post.html', context)


@allowed_user(allowed_roles=['Publisher'])
@login_required
@csrf_protect
def blog_upload(request):
    status = PaidUser.objects.filter(user=request.user, category='Paid')
    form = BlogDataForm
    if request.method == 'POST':
        form = BlogDataForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            form.save_m2m()
            return redirect('blog_view')
    context = {'form': form, 'status': status}
    return render(request, 'blog1/upload.html', context)


@allowed_user(allowed_roles=['Publisher'])
@login_required
@csrf_protect
def blog_update(request, pk):
    status = PaidUser.objects.filter(user=request.user, category='Paid')
    data = BlogData.objects.get(id=pk)
    form = BlogDataForm(instance=data)
    if request.method == 'POST':
        form = BlogDataForm(request.POST, request.FILES, instance=data)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            form.save_m2m()
            return redirect(f'/blog/{data.pk}')
    context = {'form': form, 'status': status}
    return render(request, 'blog1/update.html', context)


@allowed_user(allowed_roles=['Publisher'])
@login_required
@csrf_protect
def blog_delete(request, pk):
    data = BlogData.objects.get(id=pk)
    if request.method == 'POST':
        data.delete()
        return redirect('blog_view')
    return render(request, 'blog1/delete.html', {'data': data})


def get_object(Id):
    try:
        return BlogData.objects.get(id__exact=Id)
    except BlogData.DoesNotExist:
        return False


@login_required
def like_post(request):
    user = request.user
    get_blog_id = request.GET.get('blog_id')
    if request.method == 'POST':
        blog_id = request.POST.get('blog_id')
        blog_obj = BlogData.objects.get(id=blog_id)

        # .filter().exists() avoids loading the entire M2M set into memory
        already_liked = blog_obj.liked.filter(pk=user.pk).exists()
        if already_liked:
            blog_obj.liked.remove(user)
            like_value = 'Dislike'
        else:
            blog_obj.liked.add(user)
            like_value = 'Like'

        # Only (user, post) as lookup keys — prevents duplicate rows on IP change
        like, created = Like.objects.get_or_create(
            user=user,
            post_id=blog_id,
            defaults={'value': like_value, 'anon': request.META.get('REMOTE_ADDR', '')}
        )
        if not created:
            like.value = like_value
            like.save(update_fields=['value'])

        data = {
            'value': like.value,
            'likes': blog_obj.liked.count()
        }
        return JsonResponse(data, safe=False)
    return redirect(f'/blog/{get_blog_id}')


def create_episode(request, title, pk):
    episode_form = EpisodeForm
    if request.method == 'POST':
        episode_form = EpisodeForm(request.POST)
        if episode_form.is_valid():
            instance = episode_form.save(commit=False)
            instance.linked_to_id = int(pk)
            instance.save()
    return render(request, 'blog1/create_episode.html', {'form': episode_form, 'title': title})


def episode_data(request):
    if request.method != 'GET':
        return JsonResponse({})

    episode_id = request.GET.get('episode_id')
    if not episode_id:
        return JsonResponse({'episode': [], 'comments': []})

    try:
        episode = Episode.objects.get(id=episode_id)
    except Episode.DoesNotExist:
        return JsonResponse({'episode': [], 'comments': []})

    episode_payload = [{'title': episode.title, 'body': episode.article}]

    comments_payload = [
        {
            'body': comment.body,
            'comment_user': str(comment.name) if comment.name else comment.anon_user,
        }
        for comment in episode.get_episode_comments
    ]

    return JsonResponse({'episode': episode_payload, 'comments': comments_payload}, safe=False)
