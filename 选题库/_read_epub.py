# -*- coding: utf-8 -*-
import zipfile, re
from html.parser import HTMLParser
from collections import Counter

EPUB = r"d:\小说全集保存\东方玄幻\傲剑天穹.epub"
OUT = r"d:\MInimax H3剧本创作\选题库\_aojian_sample.txt"


class T(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = False
        if tag in ("p", "br", "div", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_data(self, d):
        if not self.skip:
            self.parts.append(d)


def html_to_text(raw):
    p = T()
    p.feed(raw)
    text = "".join(p.parts)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


z = zipfile.ZipFile(EPUB)
parts = []
for i in range(1, 11):
    raw = z.read("OEBPS/Text/chapter%d.html" % i).decode("utf-8", "replace")
    text = html_to_text(raw)
    parts.append("==== chapter %d ====\n%s\n" % (i, text[:3500]))

blob = "\n".join(html_to_text(z.read("OEBPS/Text/chapter%d.html" % i).decode("utf-8", "replace")) for i in range(1, 80))
cands = re.findall(r"([\u4e00-\u9fff]{2,3})(?:说道|道：|冷笑|大怒|脸色|微微|怒道)", blob)
parts.append("\n==== top names ====\n" + str(Counter(cands).most_common(50)))
terms = ["祭天", "皇子", "皇帝", "皇宫", "星辰", "星", "摇光", "剑", "修炼", "境界", "灵气", "真元", "丹药", "将军", "皇叔", "林"]
parts.append("\n==== terms ===\n")
for t in terms:
    parts.append("%s %d\n" % (t, blob.count(t)))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("".join(parts))
print("wrote", OUT, "chapters", len([n for n in z.namelist() if "chapter" in n]))
