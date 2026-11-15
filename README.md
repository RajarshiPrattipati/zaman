# Zaman Technical Services website

Static site hosted on Vercel at https://zaman-psi.vercel.app/

## Adding a blog post

1. Create `blog/posts/<slug>.md` with front matter (`title`, `slug`, `description`, `date`, `category`, `keywords`) and a Markdown body (`##`/`###` headings, paragraphs, `-`/`1.` lists, `**bold**`, `[links](/zaman/...)`).
2. Run `python3 tools/build_blog.py`. It regenerates the post pages, `blog/index.html`, `blog/feed.xml`, `sitemap.xml`, `robots.txt` and the latest-posts block on the home page.
3. Commit and push.

If the site moves to its own domain, update `SITE` and `BASE` in `tools/build_blog.py` and the absolute URLs in the `<head>` of `index.html`.

## Photos

`img/` holds illustrative stock photos from Unsplash (free licence, commercial use allowed). Sources and photographers are in `img/credits.json`. Replace them with photos of real Zaman jobs when available: keep the same file names and sizes (hero 1000×1200, service cards 900×600, gallery 800×600, WebP) and no HTML changes are needed.

Blog header photos live in `blog/img/<slug>.webp` plus a `.jpg` copy for social previews, both 1200×630. Alt text is the `image_alt` field in each post's front matter. Posts without an image fall back to the site share image.
