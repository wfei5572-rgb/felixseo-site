#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish.py — 博客发文时更新索引类文件的确定性部分

自动更新 5 个文件（正文由作者单独写）：
  sitemap.xml            插入 <url>
  feed.xml               插入 <item>
  archive/index.html     对应分类的 <ul> 里插入 <li>
  category/{cat}/index.html  对应分类的 card-grid 里插入卡片
  index.html             首页「精选文章」card-grid 里插入卡片
并同步更新各处「N ARTICLES」计数。

用法:
  python3 tools/publish.py --slug xxx --no 109 --cat geo \
      --title "标题" --desc "摘要" --date 2026.11.24 --read 8
"""
import argparse, email.utils, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://felixseo.com"

# 分类代码 → (archive 段落名, category 目录, pill 显示名)
CAT = {
    "seo":     ("SEO",        "seo",     "谷歌SEO"),
    "geo":     ("GEO",        "geo",     "GEO优化"),
    "website": ("独立站",      "website", "独立站"),
    "ads":     ("广告投放",    "ads",     "广告投放"),
    "social":  ("社媒运营",    "social",  "社媒运营"),
    "cases":   ("案例复盘",    "cases",   "案例复盘"),
    "ai":      ("AI 营销",     "ai",      "AI营销"),
}


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    open(p, "w", encoding="utf-8").write(s)


def once(hay, needle, what):
    if hay.count(needle) != 1:
        raise SystemExit(f"✗ 定位失败（命中 {hay.count(needle)} 次）：{what}")


def upd_sitemap(slug, date):
    p = os.path.join(ROOT, "sitemap.xml")
    h = read(p)
    entry = f"<url><loc>{SITE}/article/{slug}/</loc><lastmod>{date}</lastmod></url>"
    if f"/article/{slug}/" in h:
        return "sitemap 已存在"
    anchor = f"<url><loc>{SITE}/</loc>"
    i = h.index(anchor)
    j = h.index("</url>", i) + len("</url>")
    write(p, h[:j] + entry + h[j:])
    return "sitemap ✓"


def upd_feed(slug, title, desc, date):
    p = os.path.join(ROOT, "feed.xml")
    h = read(p)
    if f"/article/{slug}/" in h:
        return "feed 已存在"
    d = datetime.datetime.strptime(date, "%Y-%m-%d").replace(hour=10, minute=0)
    pub = email.utils.format_datetime(d)
    item = (f"<item><title>{title}</title><link>{SITE}/article/{slug}/</link>"
            f"<guid isPermaLink=\"true\">{SITE}/article/{slug}/</guid>"
            f"<pubDate>{pub}</pubDate><description>{desc}</description></item>")
    m = re.search(r"<channel>", h)
    once(h, "<channel>", "feed <channel>")
    write(p, h[:m.end()] + item + h[m.end():])
    return "feed ✓"


def upd_archive(slug, no, title, cat, date):
    p = os.path.join(ROOT, "archive", "index.html")
    h = read(p)
    if f"/article/{slug}/" in h:
        return "archive 已存在"
    section = CAT[cat][0]
    # 找到该分类段落里的 <ul class="lat-list arc-list">
    idx = 0
    while True:
        i = h.find('<p class="eyebrow">', idx)
        if i < 0:
            raise SystemExit("✗ archive 里找不到分类段落")
        eb = re.search(r'<p class="eyebrow">([^<]+)</p>', h[i:])
        name = eb.group(1)
        u = h.find('<ul class="lat-list arc-list">', i)
        if name == section and u > 0:
            break
        idx = i + 1
    li = (f'<li><a href="/article/{slug}/"><span class="lat-num">No.{no:03d}</span>'
          f'{title}</a><span class="lat-date">{date[:4]}.{date[5:7]}.{date[8:10]}</span></li>')
    write(p, h[:u + len('<ul class="lat-list arc-list">')] + li + h[u + len('<ul class="lat-list arc-list">'):])
    # 计数
    h2 = read(p)
    h2 = re.sub(r"(ARCHIVE · )(\d+)( ARTICLES)", lambda m: f"{m.group(1)}{int(m.group(2))+1}{m.group(3)}", h2, count=1)
    write(p, h2)
    return "archive ✓"


def card_html(slug, title, desc, pill, date, read_min):
    return (f'<div class="card"><a class="card-main" href="/article/{slug}/"><div class="card-body">'
            f'<p class="card-meta"><span class="pill">{pill}</span>'
            f'<span class="card-date">{date[:4]}.{date[5:7]}.{date[8:10]} · {read_min} MIN</span></p>'
            f'<h3 class="card-title">{title}</h3>'
            f'<p class="card-excerpt">{desc}</p></div></a></div>')


def upd_category(slug, title, desc, cat, date, read_min):
    p = os.path.join(ROOT, "category", CAT[cat][1], "index.html")
    h = read(p)
    if f"/article/{slug}/" in h:
        return "category 已存在"
    once(h, '<div class="card-grid">', f"category/{CAT[cat][1]} 的 card-grid")
    card = card_html(slug, title, desc, CAT[cat][2], date, read_min)
    i = h.index('<div class="card-grid">') + len('<div class="card-grid">')
    write(p, h[:i] + card + h[i:])
    h2 = read(p)
    h2 = re.sub(r"(COLUMN · )(\d+)( ARTICLES)", lambda m: f"{m.group(1)}{int(m.group(2))+1}{m.group(3)}", h2, count=1)
    write(p, h2)
    return f"category/{CAT[cat][1]} ✓"


def upd_home(slug, title, desc, cat, date, read_min):
    p = os.path.join(ROOT, "index.html")
    h = read(p)
    if f"/article/{slug}/" in h:
        return "首页已存在"
    m = re.search(r'<p class="eyebrow center">01 / 精选文章</p>', h)
    if not m:
        raise SystemExit("✗ 首页找不到「精选文章」区块")
    g = h.find('<div class="card-grid">', m.start())
    if g < 0:
        raise SystemExit("✗ 首页找不到 card-grid")
    card = card_html(slug, title, desc, CAT[cat][2], date, read_min)
    i = g + len('<div class="card-grid">')
    write(p, h[:i] + card + h[i:])
    return "首页 ✓"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--no", type=int, required=True)
    ap.add_argument("--cat", required=True, choices=list(CAT))
    ap.add_argument("--title", required=True)
    ap.add_argument("--desc", required=True)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--read", type=int, default=8)
    a = ap.parse_args()
    if a.cat not in CAT:
        raise SystemExit("分类不合法")
    art = os.path.join(ROOT, "article", a.slug, "index.html")
    if not os.path.exists(art):
        raise SystemExit(f"✗ 正文不存在：{art}（先写正文再跑 publish.py）")
    steps = [
        upd_sitemap(a.slug, a.date),
        upd_feed(a.slug, a.title, a.desc, a.date),
        upd_archive(a.slug, a.no, a.title, a.cat, a.date),
        upd_category(a.slug, a.title, a.desc, a.cat, a.date, a.read),
        upd_home(a.slug, a.title, a.desc, a.cat, a.date, a.read),
    ]
    print("发布索引更新：" + "，".join(steps))


if __name__ == "__main__":
    main()
