from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def page_look(posts, request):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.order_by('-pub_date')
    page_obj = page_look(posts, request)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = page_look(posts, request)
    title = f'Записи сообщества {group.title}'
    context = {
        'title': title,
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    posts_count = author.posts.count()
    page_obj = page_look(author_posts, request)
    context = {
        'author': author,
        'author_posts': author_posts,
        'posts_count': posts_count,
        'page_obj': page_obj

    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    comments = post.comments.all() 
    form = CommentForm() 
    title = post.text[0:30]
    context = {
        'posts': post,
        'posts_count': posts_count,
        'comments': comments,
        'title': title,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
@csrf_exempt
def post_create(request):
    if request.method == 'POST':
        form = PostForm( 
        request.POST or None, 
        files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
@csrf_exempt
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'is_edit': True,
        'form': form,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts_list = Post.objects.filter(author__following__user=request.user)
    page = paginator_group(request, posts_list)
    context = {"page_obj": page}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.filter(user=user, author__username=username).delete()
    return redirect("posts:profile", username=username)
