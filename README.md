# Zaman Technical Services website

Static site hosted on Vercel at https://zaman-psi.vercel.app/

## Adding a blog post

1. Create `blog/posts/<slug>.md` with front matter (`title`, `slug`, `description`, `date`, `category`, `keywords`) and a Markdown body (`##`/`###` headings, paragraphs, `-`/`1.` lists, `**bold**`, `[links](/zaman/...)`).
2. Run `python3 tools/build_blog.py`. It regenerates the post pages, `blog/index.html`, `blog/feed.xml`, `sitemap.xml`, `robots.txt` and the latest-posts block on the home page.
3. Commit and push.

If the site moves to its own domain, update `SITE` and `BASE` in `tools/build_blog.py` and the absolute URLs in the `<head>` of `index.html`.
