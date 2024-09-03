from django.db.models import Count, F, Prefetch
from django.shortcuts import render

from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {"title": tag.title, "posts_with_tag": tag.posts_with_tag_count}


def index(request):
    most_popular_posts = (
        Post.objects.popular()
        .annotate(tags_count=Count("tags"))
        .prefetch_related(
            Prefetch("author"),
            Prefetch(
                "tags",
                queryset=Tag.objects.order_by("title").annotate(
                    posts_with_tag_count=Count("posts")
                ),
            ),
        )
        .fetch_with_comments_count()[:5]
    )

    most_fresh_posts = (
        Post.objects.fresh()
        .annotate(tags_count=Count("tags"))
        .prefetch_related(
            Prefetch("author"),
            Prefetch(
                "tags",
                queryset=Tag.objects.order_by("title").annotate(
                    posts_with_tag_count=Count("posts")
                ),
            ),
        )
        .fetch_with_comments_count()[:5]
    )

    most_popular_tags = Tag.objects.popular().annotate(posts_with_tag_count=Count("posts"))[:5]

    context = {
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
        "page_posts": [serialize_post(post) for post in most_fresh_posts],
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = (
        Post.objects.annotate(likes_count=Count("likes"))
        .prefetch_related("tags", "author")
        .get(slug=slug)
    )

    comments = (
        Comment.objects.filter(post=post)
        .annotate(author_username=F("author__username"))
        .values("text", "published_at", "author_username")
    )

    related_tags = Tag.objects.filter(posts=post).annotate(posts_with_tag_count=Count("posts"))

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": comments,
        "likes_amount": post.likes_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular().annotate(posts_with_tag_count=Count("posts"))[:5]

    most_popular_posts = (
        Post.objects.popular()
        .annotate(tags_count=Count("tags"))
        .prefetch_related(
            Prefetch("author"),
            Prefetch(
                "tags",
                queryset=Tag.objects.order_by("title").annotate(
                    posts_with_tag_count=Count("posts")
                ),
            ),
        )
        .fetch_with_comments_count()[:5]
    )

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    tag = Tag.objects.annotate(posts_with_tag_count=Count("posts")).get(title=tag_title)

    most_popular_tags = Tag.objects.popular().annotate(posts_with_tag_count=Count("posts"))[:5]

    most_popular_posts = (
        Post.objects.popular()
        .annotate(tags_count=Count("tags"))
        .prefetch_related(
            Prefetch("author"),
            Prefetch(
                "tags",
                queryset=Tag.objects.order_by("title").annotate(
                    posts_with_tag_count=Count("posts")
                ),
            ),
        )
        .fetch_with_comments_count()[:5]
    )

    related_posts = (
        Post.objects.filter(tags=tag)
        .annotate(comments_count=Count("comments"))
        .prefetch_related(
            Prefetch("author"),
            Prefetch(
                "tags",
                queryset=Tag.objects.order_by("title").annotate(
                    posts_with_tag_count=Count("posts")
                ),
            ),
        )
        .all()[:20]
    )

    context = {
        "tag": tag.title,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, "contacts.html", {})
