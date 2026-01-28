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
        keys = sorted(keys)

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
