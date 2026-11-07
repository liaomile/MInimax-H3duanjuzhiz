# -*- coding: utf-8 -*-
import collections

rows = []
with open("_entries.tsv", encoding="utf-8") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        t, tr, lv, _ = line.strip().split("\t")
        rows.append((t, tr, lv))

print("total", len(rows))
print("by_track:")
for k, v in collections.Counter(r[1] for r in rows).most_common():
    print("%s\t%d" % (k, v))
print("by_level", dict(collections.Counter(r[2] for r in rows)))
print("---321起(补足段样例)---")
for t, tr, lv in rows[320:335]:
    print("%s | %s | %s" % (tr, lv, t))
