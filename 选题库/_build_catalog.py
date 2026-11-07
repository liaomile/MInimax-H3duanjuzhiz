# -*- coding: utf-8 -*-
"""把 497 条选题写成总表、纯剧名、分赛道目录。"""
import collections
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_entries.tsv")
OUT_MD = os.path.join(HERE, "爆款选题库_497部.md")
OUT_TXT = os.path.join(HERE, "授权清单_纯剧名_497.txt")
OUT_EASY = os.path.join(HERE, "优先开拍_低难度清单.txt")


def main():
    rows = []
    with open(SRC, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 4:
                raise SystemExit("列数不对: %s" % line[:40])
            rows.append(parts)
    if len(rows) != 497:
        raise SystemExit("需要 497 条，实际 %d" % len(rows))
    titles = [r[0] for r in rows]
    dup = [t for t, c in collections.Counter(titles).items() if c > 1]
    if dup:
        raise SystemExit("剧名重复: " + "、".join(dup))
    banned = {"双届倒爷", "末班电梯", "修图师", "青锋不问名"}
    hit = banned & set(titles)
    if hit:
        raise SystemExit("与已有作品重名: " + "、".join(hit))

    lines = []
    lines.append("# 爆款选题库 · 497 部（剧名 + 大纲）")
    lines.append("")
    lines.append("> 配合授权页「授权短剧名称」。表上已有《双届倒爷》，本库是另外 497 个名字，合计可凑满 500 部里的大头。")
    lines.append("> 这是**原创选题库**，按红果/抖音已验证结构来写：3 秒冲突、中段打脸、终局留选择。")
    lines.append("> 难度「低」= 1～2 个场景、3 人以内，适合你现在本地 H3 先拍；「中/高」人多戏多，等流程跑顺再动。")
    lines.append("> 签约栏只填你确认要做、版权在你手里的名字。497 部不要一起开拍，先从文末「优先开拍」里测 1 部。")
    lines.append("")
    lines.append("纯剧名另见：`授权清单_纯剧名_497.txt`（一行一部，方便粘贴）。")
    lines.append("")
    by = collections.Counter(r[1] for r in rows)
    lines.append("## 赛道分布")
    lines.append("")
    lines.append("| 赛道 | 部数 |")
    lines.append("| --- | ---: |")
    for k, v in by.most_common():
        lines.append("| %s | %d |" % (k, v))
    lines.append("")
    easy = []
    for i, (title, track, level, outline) in enumerate(rows, 1):
        lines.append("### %03d %s" % (i, title))
        lines.append("")
        lines.append("- 赛道：%s" % track)
        lines.append("- 拍摄难度：%s" % level)
        lines.append("- 大纲：%s" % outline)
        lines.append("")
        if level == "低":
            easy.append((i, title, track))
    lines.append("## 优先开拍（难度：低）")
    lines.append("")
    lines.append("一人本地，先拍这些。每部只做第 1 集 + 中段打脸集，测完播再铺。")
    lines.append("")
    for i, title, track in easy:
        lines.append("- %03d 《%s》（%s）" % (i, title, track))
    lines.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(titles) + "\n")
    with open(OUT_EASY, "w", encoding="utf-8") as f:
        f.write("\n".join("%03d\t%s\t%s" % x for x in easy) + "\n")
    print("OK", len(rows), "低难度", len(easy))


if __name__ == "__main__":
    main()
