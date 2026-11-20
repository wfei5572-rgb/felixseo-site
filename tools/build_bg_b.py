#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从一张已修好品牌的 B 版封面里，重建无文字的干净背景层。"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "covers", "pmax-for-b2b-three-preconditions.jpg")
OUT = os.path.join(ROOT, "tools", "_bg_b.jpg")

# 需要擦除的文字区 (x0,y0,x1,y1)
REGIONS = [
    (76, 224, 346, 252),    # 品牌行
    (76, 276, 1100, 344),   # 标题
    (76, 364, 420, 404),    # 副标题
    (76, 462, 246, 478),    # 强调条
    (76, 496, 240, 534),    # 分类
]

a = np.asarray(Image.open(SRC).convert("RGB")).astype(float)
for x0, y0, x1, y1 in REGIONS:
    lo = a[y0 - 6, x0:x1 + 1]
    hi = a[y1 + 6, x0:x1 + 1]
    for i, y in enumerate(range(y0, y1 + 1)):
        t = (i + 0.5) / (y1 - y0 + 1)
        a[y, x0:x1 + 1] = lo * (1 - t) + hi * t
Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(OUT, quality=95)
print("B 版背景层:", OUT)
