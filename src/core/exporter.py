import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict

from src.data.models import Word


def _escape_cell(s: str) -> str:
    if s is None:
        return ""
    # 转义竖线，换行替换为 <br>
    return s.replace("|", "\\|").replace("\n", "<br>")


def classification_name(word: Word) -> str:
    # 按规则：若 category 非空则为 "pos / category"，否则仅为 pos
    if word.category is None:
        return word.pos
    if str(word.category).strip() == "":
        return word.pos
    return f"{word.pos} / {word.category}"


def load_classify_order(path: str) -> Optional[List[str]]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return lines
    except Exception:
        return None


def generate_markdown(
    words: List[Word], classify_order: Optional[List[str]] = None
) -> str:
    # 分组
    groups: Dict[str, List[Word]] = {}
    for w in words:
        key = classification_name(w)
        groups.setdefault(key, []).append(w)

    # 分类顺序
    keys = list(groups.keys())

    # default pos ordering and helpers (used for both classify_order present/absent)
    # 新增名词サ变（表示可する的名词，suru-noun）并把它放在名词之后
    POS_ORDER = ["名词", "名词サ变", "动词1", "动词5", "形容词", "形容动词", "副词"]

    import re as _re

    def parse_key(k: str):
        parts = _re.split(r"\s*/\s*", k, maxsplit=1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return k.strip(), None

    def sort_key(k: str):
        pos, cat = parse_key(k)
        try:
            pos_idx = POS_ORDER.index(pos)
        except ValueError:
            pos_idx = len(POS_ORDER)
        has_cat = 0 if not cat else 1
        cat_key = cat or ""
        return (pos_idx, has_cat, cat_key, k)

    if classify_order:
        # When a classify_order is provided, treat entries as desired pos order.
        # For each pos entry, include all groups whose pos matches it. Within a
        # pos, list the no-category group first, then categorized groups by
        # category name. Remaining groups (not matched by classify_order) are
        # appended using the default sort_key.
        ordered: List[str] = []
        remaining = set(keys)
        for entry in classify_order:
            # collect groups whose pos equals this entry
            matched = [k for k in keys if k in remaining and parse_key(k)[0] == entry]
            if matched:
                # sort matched: no-category first, then by category
                matched_sorted = sorted(
                    matched,
                    key=lambda kk: (
                        0 if parse_key(kk)[1] is None else 1,
                        parse_key(kk)[1] or "",
                    ),
                )
                for mk in matched_sorted:
                    ordered.append(mk)
                    remaining.discard(mk)
            else:
                # if user provided a full key that exactly matches, accept it
                if entry in remaining:
                    ordered.append(entry)
                    remaining.discard(entry)

        rest = sorted(list(remaining), key=sort_key)
        ordered.extend(rest)
        keys = ordered
    else:
        keys = sorted(keys, key=sort_key)

    # 生成 Markdown
    lines: List[str] = []
    lines.append("词汇表")
    lines.append("")
    lines.append("| 汉字 | 假名 | 释义 |")
    lines.append("|---|---|---|")

    for key in keys:
        lines.append(f"| **{_escape_cell(key)}** |  |  |")
        # 同一分类内按 id 升序
        for w in sorted(groups[key], key=lambda x: x.id):
            k = _escape_cell(w.kanji)
            ka = _escape_cell(w.kana)
            m = _escape_cell(w.meaning)
            lines.append(f"| {k} | {ka} | {m} |")

    return "\n".join(lines) + "\n"


def export_words_to_file(
    words: List[Word], out_path: str, classify_config: Optional[str] = None
) -> str:
    # 读取用户自定义分类顺序（可选）
    classify_order = None
    if classify_config:
        classify_order = load_classify_order(classify_config)

    content = generate_markdown(words, classify_order=classify_order)

    # 确保目录存在
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    return out_path


def default_out_path() -> str:
    # Use Asia/Shanghai time (UTC+8) for filename timestamps without requiring tzdata
    sh = datetime.now(timezone.utc) + timedelta(hours=8)
    return os.path.join("export", f"words-{sh.strftime('%Y%m%d%H%M')}.md")
