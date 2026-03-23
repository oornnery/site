import logging
import math
import re
from collections import Counter
from datetime import datetime, time, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

from app.core.config import settings
from app.core.i18n import get_translations
from app.models.blog import BlogPost, BlogTag
from app.services.seo import _resolve_site_name
from app.infrastructure.markdown import (
    get_blog_post_by_slug,
    load_all_blog_posts,
)
from app.services.seo import seo_for_page
from app.models.contexts import (
    BlogHomePageContext,
    BlogPostDetailPageContext,
    BlogPostsPageContext,
    BlogTagsPageContext,
    PageRenderData,
)

logger = logging.getLogger(__name__)

_FEATURED_LIMIT = 3
_RECENT_LIMIT = 3
_TAG_DISPLAY_LIMIT = 10


class BlogPageService:
    @staticmethod
    def _post_url(slug: str) -> str:
        return f"/blog/posts/{slug}"

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        return tag.strip().lower()

    @staticmethod
    def _build_tag_stats(posts: tuple[BlogPost, ...]) -> tuple[BlogTag, ...]:
        counter: Counter[str] = Counter()
        for post in posts:
            for tag in post.tags:
                normalized = tag.strip().lower()
                if normalized:
                    counter[normalized] += 1

        tags = tuple(
            BlogTag(name=name, count=count)
            for name, count in sorted(
                counter.items(), key=lambda item: (-item[1], item[0])
            )
        )
        return tags

    @staticmethod
    def _estimate_read_time_minutes(content_html: str) -> int:
        plain_text = re.sub(r"<[^>]+>", " ", content_html)
        words = [word for word in plain_text.split() if word.strip()]
        return max(1, math.ceil(len(words) / 220))

    def _adjacent_posts(
        self, post: BlogPost, lang: str | None = None
    ) -> tuple[BlogPost | None, BlogPost | None]:
        posts = load_all_blog_posts(lang)
        for index, candidate in enumerate(posts):
            if candidate.slug != post.slug:
                continue
            previous_post = posts[index - 1] if index > 0 else None
            next_post = posts[index + 1] if index + 1 < len(posts) else None
            return previous_post, next_post
        return None, None

    def build_home_page(self, lang: str | None = None) -> PageRenderData:
        t = get_translations(lang)
        posts = load_all_blog_posts(lang)
        featured_candidates = [post for post in posts if post.featured]
        non_featured_candidates = [post for post in posts if not post.featured]
        featured_posts = tuple(
            (featured_candidates + non_featured_candidates)[:_FEATURED_LIMIT]
        )
        recent_posts = posts[:_RECENT_LIMIT]
        tags = self._build_tag_stats(posts)[:_TAG_DISPLAY_LIMIT]

        seo = seo_for_page(
            title=t.pages.blog.seo_title,
            description=t.pages.blog.seo_description,
            path="/blog",
            lang=lang or "",
        )
        logger.debug(
            "Blog home use-case built with post_count=%s featured_count=%s.",
            len(posts),
            len(featured_posts),
        )
        return PageRenderData(
            template="pages/blog/home.jinja",
            context=BlogHomePageContext(
                seo=seo,
                featured_posts=featured_posts,
                recent_posts=recent_posts,
                tags=tags,
            ),
        )

    def build_posts_page(
        self, q: str = "", page: int = 1, page_size: int = 10, lang: str | None = None
    ) -> PageRenderData:
        t = get_translations(lang)
        all_posts = load_all_blog_posts(lang)

        query = q.strip()[:200]
        if query:
            query_lower = query.lower()
            all_posts = tuple(
                post
                for post in all_posts
                if query_lower in post.title.lower()
                or query_lower in (post.description or "").lower()
                or any(query_lower in tag.lower() for tag in post.tags)
            )

        total = len(all_posts)
        total_pages = max(1, math.ceil(total / page_size))
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        posts = all_posts[start : start + page_size]

        seo = seo_for_page(
            title=t.pages.blog.posts_seo_title,
            description=t.pages.blog.posts_seo_description,
            path="/blog/posts",
            lang=lang or "",
        )
        return PageRenderData(
            template="pages/blog/posts.jinja",
            context=BlogPostsPageContext(
                seo=seo,
                posts=posts,
                q=query,
                page=page,
                total_pages=total_pages,
            ),
        )

    def get_post(self, slug: str, lang: str | None = None) -> BlogPost | None:
        return get_blog_post_by_slug(slug, lang)

    def build_post_page(
        self, post: BlogPost, lang: str | None = None
    ) -> PageRenderData:
        seo = seo_for_page(
            title=post.title,
            description=post.description,
            path=self._post_url(post.slug),
            og_type="article",
            keywords=post.tags,
            lang=lang or "",
        )
        previous_post, next_post = self._adjacent_posts(post, lang)
        read_time_minutes = self._estimate_read_time_minutes(post.content_html)
        return PageRenderData(
            template="pages/blog/detail.jinja",
            context=BlogPostDetailPageContext(
                seo=seo,
                post=post,
                previous_post=previous_post,
                next_post=next_post,
                read_time_minutes=read_time_minutes,
            ),
        )

    def build_tags_page(
        self,
        tag: str | None = None,
        page: int = 1,
        page_size: int = 10,
        lang: str | None = None,
    ) -> PageRenderData:
        t = get_translations(lang)
        posts = load_all_blog_posts(lang)
        tags = self._build_tag_stats(posts)
        selected_tag = tag.strip() if tag else ""
        selected_tag_normalized = self._normalize_tag(selected_tag)

        if selected_tag_normalized:
            filtered_posts = tuple(
                post
                for post in posts
                if selected_tag_normalized
                in {self._normalize_tag(post_tag) for post_tag in post.tags}
            )
            title = t.pages.blog.tag_title_template.format(tag=selected_tag)
            description = t.pages.blog.tag_description_template.format(tag=selected_tag)
            path = f"/blog/tags/{selected_tag}"
        else:
            filtered_posts = posts
            title = t.pages.blog.tags_title
            description = t.pages.blog.tags_description
            path = "/blog/tags"

        total = len(filtered_posts)
        total_pages = max(1, math.ceil(total / page_size))
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        paginated_posts = filtered_posts[start : start + page_size]

        seo = seo_for_page(
            title=title,
            description=description,
            path=path,
            lang=lang or "",
        )
        return PageRenderData(
            template="pages/blog/tags.jinja",
            context=BlogTagsPageContext(
                seo=seo,
                tags=tags,
                posts=paginated_posts,
                selected_tag=selected_tag,
                page=page,
                total_pages=total_pages,
            ),
        )

    def build_rss_feed(self, lang: str | None = None) -> str:
        t = get_translations(lang)
        posts = load_all_blog_posts(lang)
        site_name = _resolve_site_name(lang=lang or "")
        base_url = str(settings.base_url).rstrip("/")
        blog_url = f"{base_url}/blog"
        feed_url = f"{base_url}/blog/feed.xml"

        items: list[str] = []
        for post in posts[:50]:
            post_url = f"{base_url}{self._post_url(post.slug)}"
            description = escape(post.description or "")
            if post.date is not None:
                published_dt = datetime.combine(
                    post.date, time.min, tzinfo=timezone.utc
                )
                pub_date = format_datetime(published_dt, usegmt=True)
                pub_date_tag = f"<pubDate>{pub_date}</pubDate>"
            else:
                pub_date_tag = ""

            categories = "".join(
                f"<category>{escape(tag)}</category>"
                for tag in post.tags
                if tag.strip()
            )
            items.append(
                "<item>"
                f"<title>{escape(post.title)}</title>"
                f"<link>{escape(post_url)}</link>"
                f'<guid isPermaLink="true">{escape(post_url)}</guid>'
                f"<description>{description}</description>"
                f"{pub_date_tag}"
                f"{categories}"
                "</item>"
            )

        rss_lang = "pt-br" if lang and lang.startswith("pt") else "en-us"
        feed = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">'
            "<channel>"
            f"<title>{escape(site_name)} Blog</title>"
            f"<link>{escape(blog_url)}</link>"
            f"<description>{escape(t.pages.blog.rss_description)}</description>"
            f"<language>{rss_lang}</language>"
            f'<atom:link href="{escape(feed_url)}" rel="self" type="application/rss+xml"/>'
            f"{''.join(items)}"
            "</channel>"
            "</rss>"
        )
        return feed
