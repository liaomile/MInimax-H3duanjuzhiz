# -*- coding: utf-8 -*-
"""为缺「五镜节奏公式」声明的集补上公式行。

公式取值必须与该集实际的五镜景别一致（规范：五镜节奏公式「一集只用一种，集与集轮换」）。
四型：
  A 对话集：建立 → 插入(手/道具) → 近景(一人一句) → 反应(不给台词) → 钩子(定格/空镜)
  B 发现集：插入 → 中景(人+空间) → 特写(异常) → 反应 → 空镜/背影
  C 压迫集：主观(POV) → 中景 → 过肩 → 特写(手/门缝) → 定格
  自由：按该集实际景别序列描述
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"D:\MInimax H3剧本创作\穿越改编_阴差")

# 规范给出的三型；其余按实际景别走自由描述
TYPE_BY_SHOTS = {
    ("中景", "插入镜", "特写", "过肩", "定格"): ("C 压迫集", "主观（POV）→ 插入 → 过肩 → 特写 → 定格"),
    ("插入镜", "中景", "特写", "近景", "空镜 → 背影"): ("B 发现集", "插入 → 中景 → 特写 → 反应 → 空镜/背影"),
    ("中景", "插入镜", "近景", "近景", "特写 → 近景"): ("A 对话集", "建立 → 插入（手/道具）→ 近景 → 近景 → 钩子（定格）"),
}

FRAMING_ALIAS = {
    "特写 → 近景": "特写",
    "近景 → 特写": "近景",
    "空镜 → 背影": "空镜",
    "中景 → 背影": "中景",
    "近景 → 空镜": "近景",
    "特写 → 空镜": "特写",
    "中景 → 特写": "中景",
}


def main() -> None:
    fixed = []
    for d in sorted(ROOT.glob("第*集"), key=lambda p: int(p.name[1:3])):
        f = d / "单集剧本_V4.md"
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8").replace("\r\n", "\n")
        if "五镜节奏公式" in t:
            continue

        blocks = re.split(r"^### 镜", t, flags=re.M)[1:]
        shots = []
        for b in blocks:
            head = b.split("\n")[0]
            parts = [x.strip() for x in head.split("·")]
            raw = parts[2] if len(parts) > 2 else ""
            shots.append(FRAMING_ALIAS.get(raw, raw))

        key = tuple(shots)
        if key in TYPE_BY_SHOTS:
            tname, seq = TYPE_BY_SHOTS[key]
        else:
            tname = "自由型"
            seq = " → ".join(shots)

        line = f"> 五镜节奏公式：**{tname}**（{seq}）\n"
        marker = "## 分镜（5 × 8 秒）\n\n"
        if marker in t:
            t = t.replace(marker, marker + line, 1)
        else:
            m = re.search(r"^## 分镜.*$", t, flags=re.M)
            if not m:
                continue
            t = t[: m.end()] + "\n\n" + line.rstrip("\n") + t[m.end():]

        f.write_text(t, encoding="utf-8", newline="\n")
        fixed.append((d.name, tname, seq))

    for name, tname, seq in fixed:
        print(f"{name}: {tname}（{seq}）")
    print(f"\n共补 {len(fixed)} 集")


if __name__ == "__main__":
    main()
