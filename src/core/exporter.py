import os
from datetime import datetime, timezone
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
    if classify_order:
        # 以用户给定顺序为准，未列出的放后按字典序
        ordered = []
        remaining = set(keys)
        for k in classify_order:
            if k in groups:
                ordered.append(k)
                remaining.discard(k)
        rest = sorted(list(remaining))
        ordered.extend(rest)
        keys = ordered
    else:
        # 默认排序：按词性优先级，词性内先无 category（pos）再有 category（pos / category），
        # 有 category 的按 category 字典序
        POS_ORDER = ["名词", "动词1", "动词5", "形容词", "形容动词", "副词"]

        def parse_key(k: str):
            if " / " in k:
                pos, cat = [p.strip() for p in k.split("/", 1)]
                return pos, cat
            return k.strip(), None

        def sort_key(k: str):
            pos, cat = parse_key(k)
            try:
                pos_idx = POS_ORDER.index(pos)
            except ValueError:
                pos_idx = len(POS_ORDER)
            # 无 category 的放在前（0），有 category 的放后（1）
            has_cat = 1 if cat else 0
            cat_key = cat or ""
            return (pos_idx, has_cat, cat_key, k)

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
    utc = datetime.now(timezone.utc)
    return os.path.join("export", f"words-{utc.strftime('%Y%m%d')}.md")
