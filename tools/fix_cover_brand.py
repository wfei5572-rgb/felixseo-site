#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_cover_brand.py — 替换封面里的旧品牌署名，标题等其余像素完全不动。

步骤：
  1. 用封面自身的上下无文字行做垂直插值，重建被字盖住的背景（渐变/圆环/边框不变）
  2. 用与原图最接近的等宽字体，在原位置右对齐绘制新署名
  3. 校验：署名区不再有旧品牌，且无残留亮像素

用法:
  python3 tools/fix_cover_brand.py --slug b2b-keyword-research --out /tmp/x.jpg
  python3 tools/fix_cover_brand.py --all
"""
import argparse, glob, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERS = os.path.join(ROOT, "assets", "covers")
MONO = "/System/Library/Fonts/Menlo.ttc"
SANS = "/System/Library/Fonts/HelveticaNeue.ttc"
TARGET = "FELIXSEO . FIELD NOTES"
TARGET_B = "FELIXSEO · FIELD NOTES"
TEXT_RGB = (216, 254, 255)
SRC_STR = "HUDOO-TECH . BDM . FELIX"
ADV = 13.6           # 原字体等宽推进
SIZE = 21            # Menlo 字号
TRACK = 1.0          # 字间距补偿


def is_template_a(path):
    a = np.asarray(Image.open(path).convert("L")).astype(int)
    return a[104].mean() > 110 and a[526].mean() > 110


def draw_tracked(draw, x, y, text, font, fill, track=TRACK):
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x


def text_width(draw, text, font, track=TRACK):
    return sum(draw.textlength(c, font=font) for c in text) + track * (len(text) - 1)


def brand_bbox(img):
    """定位右下署名带：返回 (x0,x1,y0,y1)"""
    a = np.asarray(img.convert("L")).astype(int)
    band = a[535:562, 700:1164]
    xs = [x for x in range(band.shape[1]) if (band[:, x] > 140).sum() > 0]
    if not xs:
        return None
    return (700 + min(xs) - 4, 1163, 536, 560)


def fix_one_b(path, out_path=None):
    """模板B：旧品牌在左上角 "HUDOO-TECH · FIELD NOTES" """
    img = Image.open(path).convert("RGB")
    a = np.asarray(img).astype(float)
    g = np.asarray(img.convert("L")).astype(int)
    reg = g[200:275, 40:640]
    ys = [y for y in range(reg.shape[0]) if (reg[y] > 120).sum() > 2]
    xs = [x for x in range(reg.shape[1]) if (reg[:, x] > 120).sum() > 0]
    if not ys:
        return None
    x0, x1 = 40 + min(xs) - 4, 40 + max(xs) + 4
    y0, y1 = 200 + min(ys) - 4, 200 + max(ys) + 4

    lo = a[y0 - 5, x0:x1 + 1]
    hi = a[y1 + 5, x0:x1 + 1]
    for i, y in enumerate(range(y0, y1 + 1)):
        t = (i + 0.5) / (y1 - y0 + 1)
        a[y, x0:x1 + 1] = lo * (1 - t) + hi * t

    base = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(base)
    f = ImageFont.truetype(SANS, 22)
    # 校准纵向位置：让 ink 带对齐原图
    probe = Image.new("L", (700, 60), 0)
    pd = ImageDraw.Draw(probe)
    pd.text((10, 10), TARGET_B, font=f, fill=255)
    pa = np.asarray(probe)
    pys = [y for y in range(60) if pa[y].max() > 100]
    ink_top = min(pys) - 10
    d.text((82, y0 + 4 - ink_top), TARGET_B, font=f, fill=(159, 224, 220))
    out = out_path or path
    base.save(out, quality=92)
    return out


def fix_one(path, out_path=None):
    img = Image.open(path).convert("RGB")
    a = np.asarray(img).astype(float)
    bb = brand_bbox(img)
    if bb is None:
        return None
    x0, x1, y0, y1 = bb

    # 1) 重建背景
    lo = a[y0 - 4, x0:x1 + 1]
    hi = a[y1 + 4, x0:x1 + 1]
    for i, y in enumerate(range(y0, y1 + 1)):
        t = (i + 0.5) / (y1 - y0 + 1)
        a[y, x0:x1 + 1] = lo * (1 - t) + hi * t

    base = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(base)

    # 2) 绘制新署名（右对齐到原文字右缘 1139）
    f = ImageFont.truetype(MONO, SIZE)
    w = text_width(d, TARGET, f)
    x = 1139 - w
    draw_tracked(d, x, 536, TARGET, f, TEXT_RGB)

    out = out_path or path
    base.save(out, quality=92)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    if a.slug:
        p = os.path.join(COVERS, f"{a.slug}.jpg")
        print(fix_one(p, a.out))
        return
    files = sorted(glob.glob(os.path.join(COVERS, "*.jpg")))
    ta = [f for f in files if is_template_a(f)]
    tb = [f for f in files if not is_template_a(f)]
    print(f"模板A {len(ta)} 张 / 模板B {len(tb)} 张")
    if a.limit:
        ta = ta[:a.limit]
    for f in ta:
        fix_one(f)
    print(f"已处理模板A {len(ta)} 张")
    for f in tb:
        fix_one_b(f)
    print(f"已处理模板B {len(tb)} 张")


if __name__ == "__main__":
    main()
