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
from .models import BlogData, BlogTag, Comment, Settings, Theme, Like, NewBlog
from .forms import CommentForm, BlogDataForm, SettingsForm


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


@login_required(login_url='login')
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
    comments = Comment.objects.all().filter(blog=view)
    counter = comments.count()
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
        'counter': counter,
        'theme': theme,
        'other': other,
        "user": user,
        "stringed": stringed,
        "like_count": like_count,
        # 'ip_add': ip_add,
        'encoded_path': encoded_path
    }
    return render(request, "blog1/blog-post.html", context)


@allowed_user(allowed_roles=['Publisher'])
@login_required(login_url='login')
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

            tag = request.POST.getlist('blog_tag')
            for i in tag:
                instance.blog_tag.add(i)
            # add_tag.save()
            return redirect('blog_view')
    context = {
        'form': form,
        'status': status
    }
    return render(request, 'blog1/upload.html', context)


@allowed_user(allowed_roles=['Publisher'])
@login_required(login_url='login')
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
            tag = request.POST.getlist('blog_tag')
            obj = instance.blog_tag.all()
            for i in tag:
                if i not in obj:
                    instance.blog_tag.set(tag)

            return redirect(f'/blog/{data.pk}')
    context = {'form': form, 'status': status}
    return render(request, 'blog1/update.html', context)


@allowed_user(allowed_roles=['Publisher'])
@login_required(login_url='login')
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

@login_required(login_url='login')
def like_post(request):
    user = request.user
    blog_id1 = request.GET.get('blog_id')
    # print(blog_id1)
    # request.session.flush()
    if request.method == "POST":
        blog_idd = request.POST.get('blog_id')
        blog_obj = BlogData.objects.get(id=blog_idd)
        if not user.is_anonymous:
            if user in blog_obj.liked.all():
                blog_obj.liked.remove(user)
            else:
                blog_obj.liked.add(user)
        else:
            blog_obj.objects.update(id=blog_idd, anon_like=request.META['REMOTE_ADDR'])
        if not user.is_anonymous:
            like, created = Like.objects.get_or_create(user=user, post_id=blog_idd, anon=request.META['REMOTE_ADDR'])
        else:
            like, created = Like.objects.get_or_create(post_id=blog_idd, anon=request.META['REMOTE_ADDR'])
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
    return redirect(f'/blog/{blog_id1}')
