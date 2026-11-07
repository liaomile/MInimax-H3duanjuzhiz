# -*- coding: utf-8 -*-
from __future__ import annotations
import re

_LINE_RE = re.compile(
    "(?:\u8bf4|\u8bf4\u9053|\u4f4e\u58f0\u8bf4|\u51b7\u58f0\u8bf4|\u8f7b\u58f0\u8bf4|\u6025\u58f0\u8bf4|\u538b\u58f0\u8bf4)[\uff1a:\\s\u300c]*[\u300c\u300e\"]([^\u300d\u300f\"\n]{1,40})[\u300d\u300f\"]"
)
_LINE_RE2 = re.compile("[\u300c\u300e]([^\u300d\u300f\n]{1,40})[\u300d\u300f].{0,12}\u53e3\u578b\u5bf9\u9f50")
_NO_DIALOGUE = re.compile(
    "(\u672c\u955c\u65e0\u5bf9\u767d|\u65e0\u53ef\u8bfb\u6587\u5b57|\u65e0\u5bf9\u767d|\u4e0d\u8981\u5b57\u5e55|\u7981\u6b62\u5b57\u5e55|\u7eaf\u5a01\u80c1|\u7eaf\u52a8\u4f5c|\u65e0\u4eba\u8bf4\u8bdd)",
    re.I,
)
SUB_BLOCK = (
    "\u3010\u786c\u5b57\u5e55\u4e0e\u5bf9\u767d\u6e05\u6670\uff5c\u5f3a\u5236\u3011\n"
    "\u6709\u5bf9\u767d\u65f6\u5fc5\u987b\u540c\u65f6\u6ee1\u8db3\uff1a\n"
    "1) \u5bf9\u767d\u5410\u5b57\u6e05\u6670\u3001\u8bed\u901f\u9002\u4e2d\u3001\u97f3\u91cf\u660e\u663e\u538b\u8fc7\u73af\u5883\u58f0\u4e0e\u96e8\u58f0\uff1b\u7981\u6b62\u542b\u7cca\u3001\u541e\u5b57\u3001\u6c14\u58f0\u542c\u4e0d\u6e05\u3002\n"
    "2) \u5f00\u53e3\u4eba\u9501\u8138\u53e3\u578b\u5fc5\u987b\u4e0e\u53f0\u8bcd\u9010\u5b57\u5bf9\u9f50\u3002\n"
    "3) \u753b\u9762\u5e95\u90e8\u786c\u5b57\u5e55\uff08\u76f4\u63a5\u70e7\u8fdb\u6210\u7247\uff09\uff1a\u767d\u8272\u4e2d\u6587\u5b57\u3001\u7ec6\u9ed1\u63cf\u8fb9\u3001\u5c45\u4e2d\u3001\u5355\u884c\u4f18\u5148\uff1b\u5b57\u5e55\u539f\u6587\u5fc5\u987b\u4e0e\u53e3\u4e2d\u53f0\u8bcd\u5b8c\u5168\u4e00\u81f4\uff0c\u540c\u6b65\u51fa\u73b0\u540c\u6b65\u6d88\u5931\u3002\n"
    "4) \u786c\u5b57\u5e55\u53ea\u663e\u793a\u672c\u955c\u771f\u5b9e\u5bf9\u767d\u539f\u6587\uff0c\u7981\u6b62\u9519\u5b57\u3001\u4e71\u7801\u3001\u82f1\u6587\u6c34\u5370\u3001Logo\u3001\u989d\u5916\u65c1\u767d\u5b57\u3002\n"
    "\u65e0\u5bf9\u767d\u7684\u955c\u5934\uff1a\u4e0d\u51fa\u73b0\u4efb\u4f55\u5b57\u5e55\u4e0e\u53ef\u8bfb\u6587\u5b57\u3002\n"
)

def extract_lines(prompt: str):
    seen = []
    for rx in (_LINE_RE, _LINE_RE2):
        for m in rx.finditer(prompt):
            t = (m.group(1) or "").strip(" \u3002\uff0c\u3001\uff1b\uff1a")
            if t and t not in seen and len(t) <= 40:
                seen.append(t)
    return seen

def patch_prompt(prompt: str) -> str:
    text = prompt.strip()
    text = text.replace("\u5e95\u90e815%\u7559\u5b57\u5e55", "\u5e95\u90e8\u786c\u5b57\u5e55\u533a\u663e\u793a\u5bf9\u767d\u539f\u6587")
    text = text.replace("\u5e95\u90e815%\u7559\u7a7a", "\u5e95\u90e8\u786c\u5b57\u5e55\u533a\u663e\u793a\u5bf9\u767d\u539f\u6587\uff08\u65e0\u5bf9\u767d\u5219\u7559\u7a7a\uff09")
    lines = extract_lines(text)
    marker = "\u3010\u786c\u5b57\u5e55\u4e0e\u5bf9\u767d\u6e05\u6670\uff5c\u5f3a\u5236\u3011"
    if marker not in text:
        insert = SUB_BLOCK
        if lines:
            joined = " / ".join("\u300c%s\u300d" % x for x in lines)
            insert += "\u672c\u955c\u786c\u5b57\u5e55\u539f\u6587\uff08\u5fc5\u987b\u9010\u5b57\u4e00\u81f4\uff09\uff1a" + joined + "\n"
        if re.search(r"^overall_soundscape:", text, re.M):
            text = re.sub(r"(?m)^overall_soundscape:", insert + "\noverall_soundscape:", text, count=1)
        else:
            text = text.rstrip() + "\n\n" + insert
    def _sound(m):
        body = m.group(1)
        if "\u5bf9\u767d\u6e05\u6670" not in body and "\u5410\u5b57\u6e05\u6670" not in body:
            body = body.rstrip("\uff1b\u3002 ") + "\uff1b\u5bf9\u767d\u5410\u5b57\u6e05\u6670\u3001\u97f3\u91cf\u538b\u8fc7\u73af\u5883\u58f0\u3002"
        else:
            body = re.sub("\u5bf9\u767d\u6e05\u6670", "\u5bf9\u767d\u5410\u5b57\u6e05\u6670\u3001\u97f3\u91cf\u538b\u8fc7\u73af\u5883\u58f0", body)
        return "overall_soundscape: " + body
    text = re.sub(r"(?m)^overall_soundscape:\s*(.+)$", _sound, text, count=1)
    return text.strip() + "\n"
