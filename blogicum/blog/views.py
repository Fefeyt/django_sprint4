from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
from .models import Post, Category, Comments
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileEditForm, CreatePostForm, CommentsForm
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (UpdateView)

@login_required
def add_comment(request, comment_id):
    post = get_object_or_404(Post, pk=comment_id)
    form = CommentsForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:index')

def index(request):
    template = 'blog/index.html'
    posts = (
        Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()
        ).order_by('-pub_date')
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now(),
            pk=id
        )
    )
    form = CommentsForm()
    comments = Comments.objects.filter(
        post_id=id
    ).order_by('-created_at')
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = (
        Post.objects.filter(
            category=category,
            is_published=True,
            pub_date__lte=datetime.now()
        )
    ).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category,
               'page_obj': page_obj, }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = (
        Post.objects.filter(
            is_published=True,
            category__is_published=True,
            author=user
        )
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile' : user,
        'page_obj' : page_obj
    }
    return render(request, 'blog/profile.html', context)

@login_required
def edit_profile(request, username):
    instance = get_object_or_404(User, username=username)
    form = ProfileEditForm(request.POST or None, instance=instance)
    context = {'form' : form,}  
    if form.is_valid():
        form.save()
        return redirect('..')
    return render(request, 'blog/user.html', context)

@login_required
def create_post(request, id=None):
    if id is not None:
        instance = get_object_or_404(Post, pk=id)
        form = CreatePostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=instance
            )
    else:
        instance = None
        form = CreatePostForm(request.POST or None, files=request.FILES or None,)
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        form.save()
        if id is not None:
            posts_url = reverse('blog:post_detail', kwargs={'id' : id})
            return redirect(posts_url)
        else:
            profile_url = reverse('blog:profile', kwargs={'username': request.user})
            return redirect(profile_url)
    return render(request, 'blog/create.html', context) 

def delete_post(request, id):
    instance = get_object_or_404(Post, pk=id)
    form = CreatePostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        profile_url = reverse('blog:profile', kwargs={'username': request.user})
        return redirect(profile_url)
    return render(request, 'blog/create.html', context)

class CommentsUpdateView(LoginRequiredMixin, UpdateView):
    model = Comments
    form_class = CommentsForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comments, pk=self.kwargs['comment_id'], author=self.request.user)

    def dispatch(self, request, *args, **kwargs): 
        get_object_or_404(Comments, pk=kwargs['comment_id'], author=self.request.user)
        return super().dispatch(request, *args, **kwargs)