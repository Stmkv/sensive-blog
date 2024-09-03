from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Prefetch
from django.urls import reverse


class PostQuerySet(models.QuerySet):
    def popular(self):
        popular_posts = self.annotate(post_count=Count("likes", distinct=True)).order_by(
            "-post_count"
        )
        return popular_posts

    def fresh(self):
        fresh_posts = self.annotate(post_count=Count("likes", distinct=True)).order_by(
            "-published_at"
        )
        return fresh_posts

    def fetch_with_comments_count(self):
        posts_ids = [post.id for post in self]
        posts_with_comments = Post.objects.filter(id__in=posts_ids).annotate(
            comments_count=Count("comments")
        )
        ids_and_comments = posts_with_comments.values_list("id", "comments_count")
        count_for_id = dict(ids_and_comments)
        for post in self:
            post.comments_count = count_for_id[post.id]
        return self

    def count_tags(self):
        tags_count = self.annotate(tags_count=Count("tags"))
        return tags_count

    def create_selection_author_and_tag(self):
        return self.prefetch_related(
            Prefetch("author"),
            Prefetch(
                "tags",
                queryset=Tag.objects.order_by("title").annotate(
                    posts_with_tag_count=Count("posts")
                ),
            ),
        )


class TagQuerySet(models.QuerySet):
    def popular(self):
        most_popular_tags = self.annotate(posts_with_tag_count=Count("posts")).order_by(
            "-posts_with_tag_count"
        )
        return most_popular_tags


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст")
    slug = models.SlugField("Название в виде url", max_length=200)
    image = models.ImageField("Картинка")
    published_at = models.DateTimeField("Дата и время публикации")

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор", limit_choices_to={"is_staff": True}
    )
    likes = models.ManyToManyField(
        User, related_name="liked_posts", verbose_name="Кто лайкнул", blank=True
    )
    tags = models.ManyToManyField("Tag", related_name="posts", verbose_name="Теги")
    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "пост"
        verbose_name_plural = "посты"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", args={"slug": self.slug})


class Tag(models.Model):
    title = models.CharField("Тег", max_length=20, unique=True)
    objects = TagQuerySet.as_manager()

    class Meta:
        ordering = ["title"]
        verbose_name = "тег"
        verbose_name_plural = "теги"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tag_filter", args={"tag_title": self.slug})

    def clean(self):
        self.title = self.title.lower()


class Comment(models.Model):
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост, к которому написан",
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")

    text = models.TextField("Текст комментария")
    published_at = models.DateTimeField("Дата и время публикации")

    class Meta:
        ordering = ["published_at"]
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"

    def __str__(self):
        return f"{self.author.username} under {self.post.title}"
