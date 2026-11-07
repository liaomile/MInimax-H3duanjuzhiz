# -*- coding: utf-8 -*-
"""MiniMax H3 对白转码：人读台词 → 模型听得懂的 <d>[Chinese]…</d> 块。

任何短剧上云前，对白镜必须经过本模块（或等价手写同一语法）。
禁止只靠「角色：『台词』」中文叙述指望模型听懂。

用法：
    from h3_dialogue_codec import sanitize_line, speak_line, lips_closed, soundscape_ambient, cjk_ok

参考：
  - ComfyUI MiniMax H3 Prompt Guide（Speaker IDs + dialogue tags）
  - 本仓库《七星》/ Muse：NAME (S1) says: <d>[Chinese] …</d>
"""
from __future__ import annotations

import re
from typing import Iterable

# 口型预算（CJK 字数，不含标点）。超时必须拆镜，禁止塞进同一个 <d>。
MAX_CJK = {
    4: 8,
    5: 10,
    6: 12,
    7: 14,
    8: 16,
    9: 18,
    10: 20,
    12: 24,
}

# 剧本表演标点 → 进模型前清洗（官方：省略号/装饰符伤可懂度）
_SANITIZE_RE = re.compile(r"[～~…〜]+")
_KEEP_PUNCT = set("，。？！、；：—-,.?!;:")


def cjk_count(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def sanitize_line(text: str) -> str:
    """人读台词 → <d> 内逐字稿。保留逗号句号问叹；去掉波浪/省略装饰。"""
    s = (text or "").strip()
    s = s.replace("「", "").replace("」", "").replace("“", "").replace("”", "")
    s = s.replace('"', "").replace("'", "")
    # 表演波浪/省略：问叹前直接删；其余改成逗号停顿
    s = re.sub(r"[～~…〜]+(?=[？?！!])", "", s)
    s = _SANITIZE_RE.sub("，", s)
    s = re.sub(r"[，,]{2,}", "，", s)
    s = re.sub(r"\s+", "", s)
    if s and s[-1] not in _KEEP_PUNCT:
        # 无收尾标点时默认句号，避免模型拖腔乱续
        if s.endswith(("吗", "么", "呢", "吧")):
            s += "？"
        else:
            s += "。"
    return s


def cjk_ok(line: str, duration_sec: int) -> tuple[bool, int, int]:
    n = cjk_count(sanitize_line(line))
    # 就近档
    limit = MAX_CJK.get(duration_sec)
    if limit is None:
        keys = sorted(MAX_CJK)
        limit = MAX_CJK[min(keys, key=lambda k: abs(k - duration_sec))]
    return n <= limit, n, limit


def speak_line(
    en_name: str,
    chinese_line: str,
    *,
    delivery: str = "",
    verb: str = "says",
    speaker_id: str = "S1",
) -> str:
    """生成 H3 锁定对白行。delivery/verb 在标签外；标签内只有语言标 + 原文。"""
    line = sanitize_line(chinese_line)
    if not line:
        raise ValueError("empty spoken line")
    name = en_name.strip().upper().replace("_", " ")
    deliv = f", {delivery.strip()}" if delivery.strip() else ""
    return f"{name} ({speaker_id}) {verb}{deliv}: <d>[Chinese] {line}</d>"


def lips_closed(en_names: Iterable[str]) -> str:
    names = [n.strip().upper().replace("_", " ") for n in en_names if n and n.strip()]
    if not names:
        return "No other speaker IDs. Everyone else keeps lips closed."
    if len(names) == 1:
        return f"{names[0]} does not speak; lips closed. No other speaker IDs."
    joined = ", ".join(names)
    return f"{joined} do not speak; lips closed. No other speaker IDs."


def soundscape_ambient(parts: Iterable[str]) -> str:
    """overall_soundscape：只写环境/动作/气息，禁止写「对白如上」或 human speech 词。"""
    banned = (
        "对白",
        "台词",
        "说话",
        "voice",
        "speech",
        "dialogue",
        "talk",
        "whisper",
        "murmur",
        "conversation",
        "words",
    )
    cleaned = []
    for p in parts:
        s = (p or "").strip().rstrip("；;。.")
        if not s:
            continue
        low = s.lower()
        if any(b in s or b in low for b in banned):
            continue
        cleaned.append(s)
    if not cleaned:
        return "outdoor air, soft cloth rustle, quiet room tone."
    return "; ".join(cleaned) + "."


def format_dialogue_lock(
    *,
    speaker_en: str,
    line_zh: str,
    duration_sec: int,
    delivery: str = "",
    verb: str = "says",
    silent_en: Iterable[str] = (),
    ambient: Iterable[str] = (),
) -> tuple[str, str]:
    """返回 (对白锁正文, overall_soundscape 字符串)。超预算抛错。"""
    ok, n, limit = cjk_ok(line_zh, duration_sec)
    if not ok:
        raise ValueError(
            f"台词 {n} 字超出 {duration_sec}s 口型预算（上限 {limit}）：{line_zh!r}"
        )
    body = "\n".join(
        [
            speak_line(speaker_en, line_zh, delivery=delivery, verb=verb),
            lips_closed(silent_en),
            "Exactly one <d> block in this shot. Do not invent extra spoken words.",
        ]
    )
    return body, soundscape_ambient(ambient)


# 《三魂逆命》等常用中文名 → 英文声线 ID（可按剧扩展）
DEFAULT_NAME_MAP = {
    "陆野": "LU YE",
    "赵莽": "ZHAO MANG",
    "赵彪": "ZHAO BIAO",
    "钱四": "QIAN SI",
    "周顺": "ZHOU SHUN",
    "石墩": "SHI DUN",
    "青蘅": "QING HENG",
    "顾承": "GU CHENG",
    "夏疤": "XIA BA",
    "老帚": "LAO ZHOU",
    "武浩": "LU YE",
    "史彪": "ZHAO MANG",
    "史虎": "ZHAO BIAO",
    "李四海": "QIAN SI",
    "张三顺": "ZHOU SHUN",
    "马大傻子": "SHI DUN",
}


def resolve_en(name_zh: str, name_map: dict[str, str] | None = None) -> str:
    m = name_map or DEFAULT_NAME_MAP
    if name_zh in m:
        return m[name_zh]
    # 已是英文
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9 _\-]*", name_zh or ""):
        return name_zh.upper()
    raise KeyError(f"unknown speaker name: {name_zh!r} — add to name_map")
