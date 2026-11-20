#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从全部模板A封面取逐像素中位数，得到无文字的干净背景层。"""
import glob, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "assets", "covers", "*.jpg")


def is_template_a(p):
    im = Image.open(p); a = np.asarray(im.convert("L")).astype(int)
    return (a[104].mean() > 110) and (a[526].mean() > 110)


files = sorted(glob.glob(C))
ta = [f for f in files if is_template_a(f)]
print(f"模板A 封面 {len(ta)} / {len(files)}")
stack = np.stack([np.asarray(Image.open(f).convert("RGB")).astype(np.uint8) for f in ta])
bg = np.median(stack, axis=0).astype(np.uint8)
out = os.path.join(ROOT, "tools", "_bg.jpg")
Image.fromarray(bg).save(out, quality=95)
print("背景层:", out, Image.open(out).size)
