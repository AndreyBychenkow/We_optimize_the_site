from django.core.cache import cache
from django.shortcuts import render, get_object_or_404

from .models import Post, Tag


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_with_tag,
    }


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments.count(),
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.first().title if post.tags.exists() else None,
    }


def index(request):
    most_popular_posts = cache.get('most_popular_posts')
    if most_popular_posts is None:
        posts_query = Post.objects.popular_with_comments_and_tags()
        most_popular_posts = list(posts_query[:5])
        cache.set('most_popular_posts', most_popular_posts, 60 * 15)

    fresh_posts = (
        Post.objects.popular_with_comments_and_tags()
        .order_by('-published_at')[:5]
    )

    most_popular_tags = Tag.objects.cached_with_post_count()[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.popular_with_comments_and_tags(),
        slug=slug
    )

    serialized_comments = [{
        'text': comment.text,
        'published_at': comment.published_at,
        'author': comment.author.username,
    } for comment in post.comments.select_related('author')]

    most_popular_tags = Tag.objects.cached_with_post_count().order_by('-posts_with_tag')[:5]
    most_popular_posts = cache.get('most_popular_posts')

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'comments_count': post.comments.count(),
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag.objects.cached_with_post_count(), title=tag_title)

    related_posts = tag.posts.popular_with_comments_and_tags().order_by('-published_at')[:20]

    most_popular_posts = cache.get('most_popular_posts')
    most_popular_tags = Tag.objects.cached_with_post_count().order_by('-posts_with_tag')[:5]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
