from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import Count, Prefetch
from django.urls import reverse
from django.utils import timezone


class PostQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(likes_count=Count('likes')).order_by('-likes_count')

    def fresh(self):
        return self.order_by('-published_at')

    def with_comments_and_likes(self):
        return self.annotate(
            comments_count=Count('comments'),
            likes_count=Count('likes')
        )

    def popular_with_comments_and_tags(self):
        return self.popular().prefetch_related(
            Prefetch('tags', queryset=Tag.objects.popular()),
            'comments'
        ).select_related('author')

    def fresh_with_comments_and_tags(self):
        return self.fresh().prefetch_related(
            Prefetch('tags', queryset=Tag.objects.popular()),
            'comments'
        ).select_related('author')


class TagQuerySet(models.QuerySet):
    def with_post_count(self):
        return self.annotate(posts_with_tag=Count('posts'))

    def popular(self):
        return self.with_post_count().order_by('-posts_with_tag')

    def cached_with_post_count(self):
        tags = cache.get('tags_with_post_count')
        if tags is None:
            tags = self.with_post_count()
            cache.set('tags_with_post_count', tags, 60 * 15)
        return tags


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка', null=True, blank=True)
    published_at = models.DateTimeField('Дата и время публикации')
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})

    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)

    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args=[self.title])

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации', auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
