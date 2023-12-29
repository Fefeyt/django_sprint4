from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.utils import timezone
from .models import Post, Category, Comments
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileEditForm, CreatePostForm, CommentsForm
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (UpdateView, DeleteView,
                                  ListView, CreateView,
                                  DetailView, )
from django.db.models import Count


def filter_queryset(queryset):
    return queryset.filter(pub_date__lte=timezone.now(),
                           is_published=True,
                           category__is_published=True)


@login_required
def add_comment(request, comment_id):
    post = get_object_or_404(Post, pk=comment_id)
    form = CommentsForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('..')


class IndexView(ListView):
    model = Post
    queryset = filter_queryset(
        Post.objects.annotate(comment_count=Count('comments')))
    paginate_by = 10
    template_name = 'blog/index.html'
    ordering = '-pub_date'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['post_id'])
        if not post.is_published and post.author != request.user:
            raise Http404
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        comments = self.object.comments.select_related('author')
        context['comments'] = comments
        context['comment_count'] = comments.count()
        return context


class CategoryPostsView(ListView):
    model = Category
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category.objects.filter(
            is_published=True), slug=self.kwargs['category_slug'])
        context["category"] = category
        posts = category.post.filter(
            pub_date__lte=timezone.now(), is_published=True).annotate(
            comment_count=Count('comments')).order_by('-pub_date')
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context


class ProfileView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/profile.html'

    def get_queryset(self):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404("Пользователь не найден")
        return Post.objects.filter(author=user).annotate(
            comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.filter(username=self.kwargs['username']).first()
        context['profile'] = user
        return context


@login_required
def edit_profile(request, username):
    instance = get_object_or_404(User, username=username)
    form = ProfileEditForm(request.POST or None, instance=instance)
    context = {'form': form, }
    if form.is_valid():
        form.save()
        return redirect('..')
    return render(request, 'blog/user.html', context)


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostMixin(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class EditPostView(PostMixin, UpdateView):
    form_class = CreatePostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        post_id = self.object.id
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


class DeletePostView(PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_object()
        context['form'] = CreatePostForm(instance=instance)
        return context

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentsMixin(LoginRequiredMixin):
    model = Comments
    form_class = CommentsForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comments, id=kwargs['comment_id'])
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={'post_id': self.kwargs['post_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = get_object_or_404(
            Comments, id=self.kwargs['comment_id'])
        return context


class CommentsUpdateView(CommentsMixin, UpdateView):
    pass


class CommentsDeleteView(CommentsMixin, DeleteView):
    pass
