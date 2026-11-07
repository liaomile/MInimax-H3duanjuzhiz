# -*- coding: utf-8 -*-
"""《青锋不问名》资产闸门：提示词引用的每个 @图片 路径必须真实存在、规格正确、且登记在资产卡上。

用法：python _tools/check_qingfeng_assets.py
退出码 0 = 可开跑；非 0 = 有缺口，先补再跑。
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"D:\MInimax H3剧本创作")
DRAMA = ROOT / "样例剧本" / "01_青锋不问名"
ASSETS = ROOT / "assets" / "01_青锋不问名"
CARD = ASSETS / "00_上传顺序与音色卡.md"
SPEC = {"角色": (720, 1280), "场景": (720, 1280), "道具": (1280, 720)}

PATH_RX = re.compile(r"assets/01_青锋不问名/[^ \t\r\n、，）)」』]*\.(?:jpg|jpeg|png|wav)")
SLOT_RX = re.compile(r"^@图片(\d+)\s*=\s*(\S+)")


def refs():
    """提示词里引用的资产 -> 引用它的镜清单"""
    out = defaultdict(list)
    for p in sorted(DRAMA.glob("第*集/**/*.txt")):
        for line in p.read_text(encoding="utf-8").splitlines():
            for m in PATH_RX.finditer(line):
                out[m.group(0)].append(p)
    return out


def main() -> int:
    problems = []
    warnings = []
    card = CARD.read_text(encoding="utf-8") if CARD.exists() else ""

    for rel, users in sorted(refs().items()):
        f = ROOT / rel
        if not f.exists():
            ep = sorted({p.parts[-3] for p in users})
            msg = f"{rel} ← 被 {len(users)} 镜引用（{', '.join(ep[:4])}）"
            (warnings if rel.endswith(".wav") else problems).append(
                ("音色未就位，对白镜先出画面后期对口型 " if rel.endswith(".wav") else "缺文件 ") + msg)

    for f in sorted(ASSETS.glob("*/*.jpg")):
        kind = f.parent.name
        want = SPEC.get(kind)
        got = Image.open(f).size
        if want and got != want:
            problems.append(f"规格错 {f.relative_to(ASSETS)} 实际{got} 应为{want}")
        if f.name not in card:
            problems.append(f"未登记 {f.relative_to(ASSETS)} —— 资产卡里查不到")

    slots = 0
    for p in sorted(DRAMA.glob("第*集/V2_导演精改版/镜*.txt")):
        lines = p.read_text(encoding="utf-8").splitlines()
        found = {}
        for ln in lines:
            m = SLOT_RX.match(ln)
            if m:
                found[int(m.group(1))] = m.group(2)
        n = len(found)
        slots += n
        if n:
            expect = set(range(1, n + 1))
            if set(found) != expect:
                problems.append(f"槽位断号 {p.relative_to(DRAMA)} 用了{sorted(found)}")
            doc = " ".join(ln for ln in lines if ln.startswith("@图片") and not SLOT_RX.match(ln))
            for i in sorted(found):
                if f"@图片{i} " not in doc and f"@图片{i}（" not in doc:
                    problems.append(f"未说明 {p.relative_to(DRAMA)} @图片{i}({Path(found[i]).name}) 上传了但【参考素材说明】没写它锁什么")

    print(f"扫描：引用资产 {len(refs())} 条 · 在场文件 {len(list(ASSETS.glob('*/*.jpg')))} 张 · V2 上传槽 {slots} 个")
    if warnings:
        print(f"\n提醒 {len(warnings)} 条（不阻塞出片）：")
        for x in warnings:
            print("  [!]", x)
    if problems:
        print(f"\n发现 {len(problems)} 个阻塞问题：")
        for x in problems:
            print("  [X]", x)
        return 1
    print("全部通过：提示词引用的图像资产都在场、规格对、已登记、槽位连续且有锁定说明。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
