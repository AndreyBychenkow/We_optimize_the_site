from django.core.cache import cache
from django.db.models import Count, Prefetch
from django.shortcuts import render, get_object_or_404

from .models import Post, Tag


def get_tags_with_post_count():
    tags = cache.get('tags_with_post_count')
    if tags is None:
        tags = Tag.objects.annotate(posts_with_tag=Count('posts')).select_related()
        cache.set('tags_with_post_count', tags, 60 * 15)
    return tags


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
        'comments_amount': getattr(post, 'comments_count', 0),
        'likes_amount': post.likes.count(),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title if post.tags.exists() else None,
    }


def index(request):
    most_popular_posts = cache.get('most_popular_posts')
    if most_popular_posts is None:
        most_popular_posts = Post.objects.annotate(likes_count=Count('likes')).select_related(
            'author').prefetch_related(
            Prefetch('tags', queryset=get_tags_with_post_count())
        ).order_by('-likes_count')[:5]
        cache.set('most_popular_posts', most_popular_posts, 60 * 15)

    fresh_posts = Post.objects.fetch_with_comments_count().select_related('author').prefetch_related(
        Prefetch('tags', queryset=get_tags_with_post_count())
    ).order_by('-published_at')[:5]

    most_popular_tags = get_tags_with_post_count().order_by('-posts_with_tag')[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.only('id', 'title', 'text', 'slug', 'image', 'published_at', 'author_id')
        .select_related('author')
        .prefetch_related('comments', Prefetch('tags', queryset=get_tags_with_post_count()))
        .annotate(
            comments_count=Count('comments'),
            likes_count=Count('likes')
        ),
        slug=slug
    )

    serialized_comments = [{
        'text': comment.text,
        'published_at': comment.published_at,
        'author': comment.author.username,
    } for comment in post.comments.select_related('author').all()]

    most_popular_tags = get_tags_with_post_count().order_by('-posts_with_tag')[:5]
    most_popular_posts = cache.get('most_popular_posts')

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
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
    tag = get_object_or_404(get_tags_with_post_count(), title=tag_title)

    related_posts = tag.posts.annotate(comments_count=Count('comments')).select_related('author').prefetch_related(
        Prefetch('tags', queryset=get_tags_with_post_count())).order_by('-published_at')[:20]

    most_popular_posts = cache.get('most_popular_posts')
    most_popular_tags = get_tags_with_post_count().order_by('-posts_with_tag')[:5]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
