# Zaman Technical Services website

Static site hosted on Vercel at https://zaman-psi.vercel.app/

## Adding a blog post

1. Create `blog/posts/<slug>.md` with front matter (`title`, `slug`, `description`, `date`, `category`, `keywords`) and a Markdown body (`##`/`###` headings, paragraphs, `-`/`1.` lists, `**bold**`, `[links](/zaman/...)`).
2. Run `python3 tools/build_blog.py`. It regenerates the post pages, `blog/index.html`, `blog/feed.xml`, `sitemap.xml`, `robots.txt` and the latest-posts block on the home page.
3. Commit and push.

If the site moves to its own domain, update `SITE` and `BASE` in `tools/build_blog.py` and the absolute URLs in the `<head>` of `index.html`.

## Photos

- `img/hero-staircase.webp`, `img/svc-*.webp` and `img/projects/*.webp` are Zaman's own project photos (from the owner's WhatsApp album), cropped to fixed sizes: hero 5:6, service cards 3:2, gallery 4:3, WebP.
- Blog header photos live in `blog/img/<slug>.webp` plus a `.jpg` copy for social previews, 1200×630. Alt text is `image_alt` in each post's front matter. Six use project photos; the rest are free-licence Unsplash photos listed in `img/credits.json`. Swap in project photos as they become available.
- The raw photo folder `IMG2/` is git-ignored.
