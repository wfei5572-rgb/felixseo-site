#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_cover_b.py — felixseo.com 封面生成器（新版版式：左上品牌行 + 无衬线大标题）

版式取自近期文章（No.105–No.108 用的 B 版）：
  左上   FELIXSEO · FIELD NOTES      (HelveticaNeue 22, 浅青)
  中部   大标题                       (Hiragino Sans GB W6, 58)
  标题下 副标题                       (28)
  下部   短强调条 + 左下分类           (强调条 160x5, 分类 26)

用法:
  python3 tools/make_cover_b.py --slug xxx --title "标题" --sub "副标题" \
      --cat "GEO优化" --out assets/covers/xxx.jpg
"""
import argparse, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, "tools", "_bg_b.jpg")
W, H = 1200, 630
SANS_T = "/System/Library/Fonts/Hiragino Sans GB.ttc"   # index 2 = W6
SANS_R = "/System/Library/Fonts/HelveticaNeue.ttc"
C_BRAND = (159, 224, 220)
C_TITLE = (240, 255, 255)
C_SUB = (170, 215, 212)
C_ACCENT = (120, 197, 189)
C_CAT = (140, 208, 207)
LEFT = 82


def build(title, sub, cat):
    bg = Image.open(BG).convert("RGB")
    d = ImageDraw.Draw(bg)

    f_brand = ImageFont.truetype(SANS_R, 22)
    d.text((LEFT, 225), "FELIXSEO · FIELD NOTES", font=f_brand, fill=C_BRAND)

    MAXW = 1200 - LEFT - 58
    size = 58
    f_t = ImageFont.truetype(SANS_T, size, index=2)
    while size > 36 and d.textlength(title, font=f_t) > MAXW:
        size -= 2
        f_t = ImageFont.truetype(SANS_T, size, index=2)
    # 仍放不下则换行（最多两行），并下移副标题
    lines, shift = [title], 0
    if d.textlength(title, font=f_t) > MAXW:
        lines, rest = [], title
        while rest:
            cut = len(rest)
            while cut > 1 and d.textlength(rest[:cut], font=f_t) > MAXW:
                cut -= 1
            lines.append(rest[:cut]); rest = rest[cut:]
        shift = int(size * 1.18)
    y = 278
    for ln in lines:
        d.text((LEFT, y), ln, font=f_t, fill=C_TITLE)
        y += int(size * 1.18)

    f_s = ImageFont.truetype(SANS_T, 28, index=0)
    d.text((LEFT, 370 + shift), sub, font=f_s, fill=C_SUB)

    d.rectangle([80, 468, 240, 472], fill=C_ACCENT)

    f_c = ImageFont.truetype(SANS_T, 26, index=0)
    d.text((LEFT, 502), cat, font=f_c, fill=C_CAT)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--sub", default="")
    ap.add_argument("--cat", default="")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if not os.path.exists(BG):
        raise SystemExit(f"缺少背景层 {BG}，先运行 tools/build_bg_b.py")
    img = build(a.title, a.sub, a.cat)
    out = a.out or os.path.join(ROOT, "assets", "covers", f"{a.slug}.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, quality=92)
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
