#!/usr/bin/env python3
"""Build the static blog for Zaman Technical Services.

Reads blog/posts/*.md (front matter + a small Markdown subset) and writes:
  blog/index.html, blog/<slug>/index.html, sitemap.xml, robots.txt
and refreshes the "latest posts" block on the home page.

Usage:  python3 tools/build_blog.py
No third-party dependencies.
"""
import html
import json
import math
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "blog" / "posts"
SITE = "https://rajarshiprattipati.github.io"
BASE = "/zaman"            # path the site is served from ("" for a root domain)
URL = SITE + BASE
WA = "971564308235"
TEL = "+971541263162"
BRAND = "Zaman Technical Services"

# ---------------------------------------------------------------- parsing

def parse_post(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    for key in ("title", "slug", "description", "date", "category"):
        if not meta.get(key):
            raise SystemExit(f"{path.name}: missing '{key}'")
    body = m.group(2).strip()
    meta["date_obj"] = date.fromisoformat(meta["date"])
    words = len(re.findall(r"\w+", body))
    meta["words"] = words
    meta["minutes"] = max(1, math.ceil(words / 220))
    meta["html"], meta["toc"] = md_to_html(body)
    meta["url"] = f"{BASE}/blog/{meta['slug']}/"
    return meta


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    def link(m):
        text, href = m.group(1), m.group(2)
        if href.startswith("/zaman"):
            href = BASE + href[len("/zaman"):]
        ext = href.startswith("http") and SITE not in href
        attrs = ' target="_blank" rel="noopener"' if ext else ""
        return f'<a href="{html.escape(href)}"{attrs}>{text}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def md_to_html(src):
    out, toc, para, lst = [], [], [], None

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def close_list():
        nonlocal lst
        if lst:
            out.append(f"</{lst}>")
            lst = None

    for raw in src.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_para(); close_list(); continue
        h = re.match(r"^(#{2,3})\s+(.*)$", line)
        ul = re.match(r"^\s*[-*]\s+(.*)$", line)
        ol = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if h:
            flush_para(); close_list()
            level, text = len(h.group(1)), h.group(2).strip()
            hid = slugify(re.sub(r"[*\[\]]", "", text))
            if level == 2:
                toc.append((hid, re.sub(r"\*\*", "", text)))
            out.append(f'<h{level} id="{hid}">{inline(text)}</h{level}>')
        elif ul or ol:
            flush_para()
            kind = "ul" if ul else "ol"
            if lst != kind:
                close_list(); out.append(f"<{kind}>"); lst = kind
            out.append("<li>" + inline((ul or ol).group(1)) + "</li>")
        else:
            if lst:  # continuation line of a list item
                out[-1] = out[-1][:-5] + " " + inline(line.strip()) + "</li>"
            else:
                para.append(line.strip())
    flush_para(); close_list()
    return "\n".join(out), toc

# ---------------------------------------------------------------- templates

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,400;0,500;0,600;0,700;1,600'
         '&family=Barlow+Condensed:wght@700;800&family=Libre+Baskerville:wght@700&display=swap" rel="stylesheet">')

LOGO = ('<svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true">'
        '<path fill="#FFC629" d="M8 6h46v8L22 50h32v8H8v-8l32-36H8z"/>'
        '<path fill="#FFC629" d="M2 40 30 22l30 18-3 4-27-17L5 44z"/>'
        '<rect x="25" y="34" width="10" height="9" fill="#141414"/>'
        '<path fill="#FFC629" d="M26 35h3.5v3.2H26zM30.5 35H34v3.2h-3.5zM26 39.2h3.5v3H26zM30.5 39.2H34v3h-3.5z"/></svg>')

WA_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2Zm4.52 11.99c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.23.25-.87.85-.87 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.24 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.14-1.18-.06-.1-.22-.16-.47-.28Z"/></svg>')
PHONE_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92Z"/></svg>')


def fmt_date(d):
    return f"{d.day} {d.strftime('%B %Y')}"


def head(title, desc, canonical, og_type="website", extra=""):
    t, d = html.escape(title), html.escape(desc)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="theme-color" content="#141414">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="{BASE}/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{BRAND} blog" href="{BASE}/blog/feed.xml">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{URL}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{URL}/og.png">
{extra}{FONTS}
<link rel="stylesheet" href="{BASE}/blog/blog.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap nav">
    <a href="{BASE}/" class="brand" aria-label="{BRAND} home">{LOGO}<span class="brand-text"><b>Z<span>A</span>M<span>A</span>N</b><small>Technical Services</small></span></a>
    <nav aria-label="Main">
      <a href="{BASE}/#services">Services</a>
      <a href="{BASE}/blog/" class="here">Blog</a>
      <a href="{BASE}/#contact">Contact</a>
    </nav>
    <a class="btn btn-yellow nav-call" href="tel:{TEL}">{PHONE_SVG}<span>054 126 3162</span></a>
  </div>
</header>
"""


def foot():
    year = date.today().year
    return f"""
<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <a href="{BASE}/" class="brand">{LOGO}<span class="brand-text"><b>Z<span>A</span>M<span>A</span>N</b><small>Technical Services</small></span></a>
      <p>Renovation, maintenance and building services across Dubai.</p>
    </div>
    <div>
      <h2>Contact</h2>
      <ul>
        <li><a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp: 056 430 8235</a></li>
        <li><a href="tel:{TEL}">Call: 054 126 3162</a></li>
        <li><a href="mailto:haaqinzmamul@gmail.com">haaqinzmamul@gmail.com</a></li>
        <li>Port Saeed, Deira, Dubai, UAE</li>
      </ul>
    </div>
    <div>
      <h2>Site</h2>
      <ul>
        <li><a href="{BASE}/">Home</a></li>
        <li><a href="{BASE}/#services">Services</a></li>
        <li><a href="{BASE}/blog/">Blog</a></li>
        <li><a href="{BASE}/#contact">Request a quote</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap copy"><span>© {year} {BRAND} Est.</span><span>Dubai DET License No. 1470267</span></div>
</footer>
<div class="fab">
  <a class="f-call" href="tel:{TEL}" aria-label="Call 054 126 3162">{PHONE_SVG}</a>
  <a class="f-wa" href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{WA_SVG}</a>
</div>
</body>
</html>
"""


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"


ORG = {"@type": "HomeAndConstructionBusiness", "name": BRAND + " Est.", "url": URL + "/",
       "logo": URL + "/favicon.svg", "image": URL + "/og.png", "telephone": TEL,
       "email": "haaqinzmamul@gmail.com",
       "address": {"@type": "PostalAddress", "streetAddress": "Office SM1-02-722, Port Saeed",
                   "addressLocality": "Deira, Dubai", "addressCountry": "AE"}}


def card(p, heading="h2"):
    return f"""<article class="card">
  <p class="meta"><span class="cat">{html.escape(p['category'])}</span><time datetime="{p['date']}">{fmt_date(p['date_obj'])}</time></p>
  <{heading}><a href="{p['url']}">{html.escape(p['title'])}</a></{heading}>
  <p>{html.escape(p['description'])}</p>
  <p class="more">{p['minutes']} min read</p>
</article>"""


def cta():
    return f"""<aside class="cta" aria-label="Contact">
  <h2>Need this done in Dubai?</h2>
  <p>Send a few details and photos and we'll reply with a quote.</p>
  <div class="cta-actions">
    <a class="btn btn-wa" href="https://wa.me/{WA}?text={html.escape('Hello Zaman Technical Services, I read your blog and would like a quote.').replace(' ', '%20')}" target="_blank" rel="noopener">{WA_SVG}WhatsApp 056 430 8235</a>
    <a class="btn btn-dark" href="tel:{TEL}">{PHONE_SVG}Call 054 126 3162</a>
  </div>
</aside>"""


def render_post(p, posts):
    canonical = URL + f"/blog/{p['slug']}/"
    others = [o for o in posts if o["slug"] != p["slug"]]
    related = sorted(others, key=lambda o: (o["category"] != p["category"], -o["date_obj"].toordinal()))[:3]
    schema = ld({"@context": "https://schema.org", "@graph": [
        {"@type": "BlogPosting", "headline": p["title"], "description": p["description"],
         "datePublished": p["date"], "dateModified": p["date"], "wordCount": p["words"],
         "articleSection": p["category"], "keywords": p.get("keywords", ""),
         "image": URL + "/og.png", "mainEntityOfPage": canonical, "inLanguage": "en",
         "author": {"@type": "Organization", "name": BRAND, "url": URL + "/"},
         "publisher": ORG},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": URL + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": canonical}]}]})
    extra = (f'<meta property="article:published_time" content="{p["date"]}">\n'
             f'<meta property="article:section" content="{html.escape(p["category"])}">\n' + schema)
    toc = ""
    if len(p["toc"]) >= 3:
        items = "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in p["toc"])
        toc = f'<nav class="toc" aria-label="In this article"><h2>In this article</h2><ol>{items}</ol></nav>'
    rel = "\n".join(card(o, "h3") for o in related)
    return (head(f"{p['title']} | {BRAND}", p["description"], canonical, "article", extra) + f"""
<main id="main">
  <div class="post-hero">
    <div class="wrap narrow">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="{BASE}/">Home</a><span aria-hidden="true">/</span><a href="{BASE}/blog/">Blog</a><span aria-hidden="true">/</span><span aria-current="page">{html.escape(p['category'])}</span></nav>
      <h1>{html.escape(p['title'])}</h1>
      <p class="post-meta"><span class="cat">{html.escape(p['category'])}</span><time datetime="{p['date']}">{fmt_date(p['date_obj'])}</time><span>{p['minutes']} min read</span></p>
    </div>
  </div>
  <article class="wrap narrow prose">
    {toc}
    {p['html']}
    {cta()}
  </article>
  <section class="wrap related" aria-labelledby="rel-h">
    <h2 id="rel-h">Related articles</h2>
    <div class="cards">{rel}</div>
  </section>
</main>
""" + foot())


def render_index(posts):
    canonical = URL + "/blog/"
    desc = ("Practical guides on renovation, gypsum ceilings, painting, AC, plumbing, tiling and electrical "
            "work for homes and offices in Dubai, from Zaman Technical Services.")
    schema = ld({"@context": "https://schema.org", "@type": "Blog", "name": f"{BRAND} Blog",
                 "url": canonical, "description": desc, "publisher": ORG,
                 "blogPost": [{"@type": "BlogPosting", "headline": p["title"],
                               "url": URL + f"/blog/{p['slug']}/", "datePublished": p["date"]} for p in posts]})
    cats = sorted({p["category"] for p in posts})
    chips = '<button class="chip on" data-cat="">All</button>' + "".join(
        f'<button class="chip" data-cat="{html.escape(c)}">{html.escape(c)}</button>' for c in cats)
    cards = "\n".join(card(p).replace('<article class="card">',
                      f'<article class="card" data-cat="{html.escape(p["category"])}">', 1) for p in posts)
    return (head(f"Home Maintenance & Renovation Blog, Dubai | {BRAND}", desc, canonical, "website", schema) + f"""
<main id="main">
  <div class="post-hero">
    <div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="{BASE}/">Home</a><span aria-hidden="true">/</span><span aria-current="page">Blog</span></nav>
      <h1>Renovation &amp; maintenance guides</h1>
      <p class="lede">Practical advice on ceilings, paint, AC, plumbing, tiling and electrical work in Dubai homes and offices.</p>
    </div>
  </div>
  <section class="wrap list">
    <div class="chips" role="group" aria-label="Filter by category">{chips}</div>
    <div class="cards">
{cards}
    </div>
  </section>
</main>
<script>
document.querySelectorAll(".chip").forEach(b => b.addEventListener("click", () => {{
  document.querySelectorAll(".chip").forEach(x => x.classList.toggle("on", x === b));
  const c = b.dataset.cat;
  document.querySelectorAll(".card[data-cat]").forEach(a => a.hidden = c && a.dataset.cat !== c);
}}));
</script>
""" + foot())


def render_feed(posts):
    items = "".join(f"""
  <item><title>{html.escape(p['title'])}</title><link>{URL}/blog/{p['slug']}/</link>
    <guid>{URL}/blog/{p['slug']}/</guid><pubDate>{p['date_obj'].strftime('%a, %d %b %Y')} 08:00:00 +0400</pubDate>
    <category>{html.escape(p['category'])}</category><description>{html.escape(p['description'])}</description></item>"""
                    for p in posts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>{BRAND} Blog</title><link>{URL}/blog/</link>
  <description>Renovation and maintenance guides for Dubai homes and offices.</description>
  <language>en</language>{items}
</channel></rss>
"""


def render_sitemap(posts):
    latest = max(p["date"] for p in posts)
    urls = [(URL + "/", latest, "1.0"), (URL + "/blog/", latest, "0.8")]
    urls += [(URL + f"/blog/{p['slug']}/", p["date"], "0.7") for p in posts]
    body = "".join(f"\n  <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>" for u, d, pr in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}\n</urlset>\n'


def update_home(posts):
    index = ROOT / "index.html"
    src = index.read_text(encoding="utf-8")
    start, end = "<!-- BLOG:START -->", "<!-- BLOG:END -->"
    if start not in src:
        return
    cards = "\n".join(
        f'        <a class="post" href="{p["url"]}"><small>{html.escape(p["category"])} · {fmt_date(p["date_obj"])}</small>'
        f'<b>{html.escape(p["title"])}</b><span>{html.escape(p["description"])}</span></a>' for p in posts[:3])
    new = src[:src.index(start) + len(start)] + "\n" + cards + "\n        " + src[src.index(end):]
    index.write_text(new, encoding="utf-8")


def main():
    posts = sorted((parse_post(f) for f in POSTS_DIR.glob("*.md")),
                   key=lambda p: p["date_obj"], reverse=True)
    slugs = [p["slug"] for p in posts]
    if len(set(slugs)) != len(slugs):
        raise SystemExit("duplicate slugs")
    # warn on broken internal blog links
    for p in posts:
        for s in re.findall(r'/blog/([a-z0-9-]+)/', p["html"]):
            if s not in slugs:
                print(f"warning: {p['slug']} links to missing post '{s}'")
    for p in posts:
        out = ROOT / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_post(p, posts), encoding="utf-8")
    (ROOT / "blog" / "index.html").write_text(render_index(posts), encoding="utf-8")
    (ROOT / "blog" / "feed.xml").write_text(render_feed(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(render_sitemap(posts), encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n", encoding="utf-8")
    update_home(posts)
    print(f"built {len(posts)} posts")


if __name__ == "__main__":
    main()
