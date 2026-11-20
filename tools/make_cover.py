#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_cover.py — felixseo.com 文章封面生成器

用法:
  python3 tools/make_cover.py --no 109 --cat GEO --date 2026.11.25 \
      --title "标题" --read "10 MIN READ" [--brand "FELIXSEO . FIELD NOTES"]

输出: assets/covers/{slug}.jpg  (1200x630)
背景层复用 tools/_bg.jpg（由 tools/build_bg.py 从全部封面中位数提取，
保证渐变、圆环、边框与规则线与线上完全一致）。
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, "tools", "_bg.jpg")
OUT = os.path.join(ROOT, "assets", "covers")

W, H = 1200, 630
MARGIN_L, MARGIN_R = 60, 1166
SERIF = "/System/Library/Fonts/Supplemental/Songti.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"

CYAN = (169, 227, 228)      # 顶部/底部辅助文字
WHITE = (255, 255, 255)
DIM = (140, 196, 194)       # 次级文字


def serif(sz):
    return ImageFont.truetype(SERIF, sz, index=0)


def mono(sz):
    return ImageFont.truetype(MONO, sz)


def tracked(draw, xy, text, font, fill, tracking=2.0, anchor_right=False):
    """带字间距的等宽文字绘制。返回绘制总宽度。"""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x, y = xy
    if anchor_right:
        x -= total
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total


def wrap_cjk(draw, text, font, max_w):
    """中文按字符换行（英文单词不拆）。"""
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if draw.textlength(trial, font=font) > max_w and cur:
            # 尽量不在英文单词中间断
            if ch.isascii() and " " in cur.strip() and cur.strip().split()[-1].isascii():
                words = cur.rsplit(" ", 1)
                lines.append(words[0]); cur = words[1] + ch
            else:
                lines.append(cur); cur = ch
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def build(no, cat, date, title, read, brand):
    bg = Image.open(BG).convert("RGB")
    d = ImageDraw.Draw(bg)

    # 顶部栏
    f_bar = mono(20)
    tracked(d, (MARGIN_L, 62), f"FIELD NOTES  .  No.{no:03d}  .  {date[:4]}", f_bar, CYAN, tracking=2.6)
    w = sum(d.textlength(c, font=f_bar) for c in f"FELIX.BLOG") + 2.6 * 8
    tracked(d, (MARGIN_R - w, 62), "FELIX.BLOG", f_bar, CYAN, tracking=2.6)

    # 标题
    f_title = serif(58)
    lines = wrap_cjk(d, title, f_title, MARGIN_R - MARGIN_L - 40)
    y = 236
    for ln in lines:
        d.text((MARGIN_L, y), ln, font=f_title, fill=WHITE)
        y += 80

    # 副标题/阅读时长
    f_sub = serif(26)
    d.text((MARGIN_L, y + 8), f"{cat}  ·  {read}", font=f_sub, fill=DIM)

    # 底部栏
    f_bot = mono(20)
    d.text((MARGIN_L, 538), cat, font=f_bot, fill=CYAN)
    w = sum(d.textlength(c, font=f_bot) for c in brand) + 2.6 * (len(brand) - 1)
    tracked(d, (MARGIN_R - w, 538), brand, f_bot, CYAN, tracking=2.6)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--no", type=int, required=True)
    ap.add_argument("--cat", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--read", default="10 MIN READ")
    ap.add_argument("--brand", default="FELIXSEO . FIELD NOTES")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if not os.path.exists(BG):
        sys.exit(f"缺少背景层 {BG}，先运行 tools/build_bg.py")
    img = build(a.no, a.cat, a.date, a.title, a.read, a.brand)
    out = a.out or os.path.join(OUT, f"{a.slug}.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, quality=92)
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
