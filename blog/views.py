import json
from urllib.parse import quote_plus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import JsonResponse, Http404, HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from Readfiles.decorators import authorized_user, allowed_user
from Readfiles.models import User, PaidUser
from .models import *
from .forms import *


# Create your views here.
def index(request):
    print(request.session.keys())
    upd = NewBlog.objects.all()
    tags = BlogTag.objects.all()
    items = BlogData.objects.all()
    data = request.GET.get('tag')
    if data:
        url = f'/blog/?search={data}'
        return redirect(url)
    # limit blog output to 3 with paginator
    paginator = Paginator(items, 3)
    page = request.GET.get('page')
    # page = paginator.get_page(page)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    context = {
        'tags': tags,
        'upd': upd,
        'items': items
    }
    return render(request, 'index/index.html', context)


def nav(request):
    tags = BlogTag.objects.all()
    context = {'tags': tags}
    return render(request, 'navs/nav.html', context)


@login_required
@csrf_protect
def blog_view(request):
    blog_dt = BlogData.objects.all()
    blog_count = blog_dt.count()
    tags = BlogTag.objects.all()
    # posts = BlogData.objects.get(blog_tag='blog_tag')
    data = request.GET.get('tag')
    if data:
        url = f'/blog/?search={data}'
        return redirect(url)
    paginator = Paginator(blog_dt, 6)
    page = request.GET.get('page')
    # page = paginator.get_page(page)
    try:
        blog_dt = paginator.page(page)
    except PageNotAnInteger:
        blog_dt = paginator.page(1)
    except EmptyPage:
        blog_dt = paginator.page(paginator.num_pages)
    context = {
        "blog_dt": blog_dt,
        'tags': tags,
        "blog_count": blog_count
    }
    return render(request, "blog1/blog_lists.html", context)

def search_res(request):
    if request.is_ajax():
        res= None
        blog = request.POST.get('blog')
        qs= BlogData.objects.filter(
            Q(title__icontains=blog) |
            Q(author__username__icontains=blog)
            ).distinct()
        # print(qs)
        if len(qs)>0 and len(blog)>0:
            data = []
            for pos in qs:
                item = {
                    'pk': pos.pk,
                    'title': pos.title,
                    'author': pos.author.username,
                    'image': pos.image.url
                }
                data.append(item)
            res= data
        else:
            res = 'No results found!'
        return JsonResponse({'data': res})
    return JsonResponse({})

@csrf_protect
def blog_detail(request, pk):
    user = request.user
    # ip_add = request.META['REMOTE_ADDR']
    view = BlogData.objects.get(id=pk)
    like_count = Like.objects.filter(post=view)
    stringed = quote_plus(view.title)
    encoded_path = quote_plus(request.path)
    other = BlogData.objects.filter(author=view.author).exclude(id=pk)
    blog_tag = BlogTag.objects.all()
    tags = BlogTag.objects.all()
    comments = Comment.objects.all().filter(blog_id=view)
    taggs = view.blog_tag.all()
    theme = Theme.objects.all()
    data = request.GET.get('tag')
    if user.is_authenticated:
        request.session['view'] = user.username
        if request.session['view'] not in view.viewed.all():
            view.viewed.add(user)
    else:
        pass
    if data:
        url = f'/blog/?search={data}'
        return redirect(url)
    form = CommentForm
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid():
            if request.user.is_authenticated:
                form = form.save()
                form.name = request.user
                form.blog = view
                form.save()
                url = f'/blog/{view.pk}'
                return HttpResponseRedirect(reverse('blog_detail', args=[str(pk)]))
            else:
                instance =form.save(commit=False)
                instance.anon_user = request.POST.get('anon-user')
                instance.blog = view
                instance.save()
                url = f'/blog/{view.pk}'
                return HttpResponseRedirect(reverse('blog_detail', args=[str(pk)]))
    # related = BlogData.objects.all().filter(blog_tag=view.blog_tag)

    context = {
        "blog_tag": blog_tag,
        "comments": comments,
        'form': form,
        'taggs': taggs,
        'i': view.viewed.all(),
        "tags": tags,
        'view': view,
        'counter': comments.count(),
        'theme': theme,
        'other': other,
        "user": user,
        "stringed": stringed,
        "like_count": like_count,
        'encoded_path': encoded_path
    }
    return render(request, "blog1/blog-post.html", context)


@allowed_user(allowed_roles=['Publisher'])
@login_required
@csrf_protect
def blog_upload(request):
    status = PaidUser.objects.all().filter(user=request.user, category='Paid')
    form = BlogDataForm
    # user = None
    if request.method == 'POST':
        form = BlogDataForm(request.POST or None, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()

            tag = request.POST.getlist('hidden-values')
            proper_tag_list = [int(num) for num in tag[0].split(',')]
            print(proper_tag_list)
            for i in proper_tag_list:
                instance.blog_tag.add(int(i))
            # add_tag.save()
            return redirect('blog_view')
    context = {
        'form': form,
        'status': status
    }
    return render(request, 'blog1/upload.html', context)


@allowed_user(allowed_roles=['Publisher'])
@login_required
@csrf_protect
def blog_update(request, pk):
    status = PaidUser.objects.all().filter(user=request.user, category='Paid')
    data = BlogData.objects.get(id=pk)
    form = BlogDataForm(instance=data)
    if request.method == 'POST':
        form = BlogDataForm(request.POST or None, request.FILES, instance=data)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            tag = request.POST.getlist('hidden-values')
            print(tag)
            obj = instance.blog_tag.all()
            if tag != ['']:
                proper_tag_list = [int(num) for num in tag[0].split(',')]
                for i in proper_tag_list:
                    if i not in obj:
                        instance.blog_tag.set(proper_tag_list)

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
    context = {'data': data}
    return render(request, 'blog1/delete.html', context)


def get_object(Id):
    try:
        return BlogData.objects.get(id__exact=Id)
    except:
        return False

@login_required
def like_post(request):
    user = request.user
    get_blog_id = request.GET.get('blog_id')
    if request.method == "POST":
        blog_id = request.POST.get('blog_id')
        blog_obj = BlogData.objects.get(id=blog_id)
        if not user.is_anonymous:
            if user in blog_obj.liked.all():
                blog_obj.liked.remove(user)
            else:
                blog_obj.liked.add(user)
        else:
            blog_obj.objects.update(id=blog_id, anon_like=request.META['REMOTE_ADDR'])
        if not user.is_anonymous:
            like, created = Like.objects.get_or_create(user=user, post_id=blog_id, anon=request.META['REMOTE_ADDR'])
        else:
            like, created = Like.objects.get_or_create(post_id=blog_id, anon=request.META['REMOTE_ADDR'])
        if not created:
            if like.value == 'Like':
                like.value = 'Dislike'
            else:
                like.value = 'Like'
        else:
            like.value = 'Like'

        blog_obj.save()
        like.save()

        data = {
            'value': like.value,
            'likes': blog_obj.liked.all().count()
        }
        return JsonResponse(data, safe=False)
    return redirect(f'/blog/{get_blog_id}')


def create_episode(request, title, pk):
    episode_form = EpisodeForm
    if request.method == "POST":
        episode_form = EpisodeForm(request.POST or None)
        if episode_form.is_valid():
            instance = episode_form.save(commit=False)
            instance.linked_to_id = int(pk)
            instance.save()
    context = {
        'form':episode_form,
        'title':title
    }
    return render(request, 'blog1/create_episode.html', context)

# use cache per page to render the episodes to users
def episode_data(request):
    """
    The function `episode_data` retrieves episode data and comments based on the provided episode ID.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the request method (GET, POST, etc.), request headers,
    request body, and query parameters
    :return: a JSON response that includes the episode data and comments.
    """
    REQ=request.GET
    episode_data = []
    episode_comments = []
    if request.method == "GET":
        episode_id = REQ["episode_id"]
        query_episode_model = Episode.objects.get(id=episode_id)
        get_comments = query_episode_model.get_episode_comments
        meta_data = {
            'title':query_episode_model.title,
            'body':query_episode_model.article
        }
        episode_data.append(meta_data)
        print(episode_data)
        # 
        for comment in get_comments:
            comment_data = {
                'body':comment.body,
                'comment_user':(comment.user if comment.user else comment.anon_user)
            }
            episode_comments.append(comment_data)
    return JsonResponse({
        "episode":episode_data,
        "comments":episode_comments
    }, safe=False)
        