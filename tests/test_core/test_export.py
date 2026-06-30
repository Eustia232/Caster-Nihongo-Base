from datetime import datetime
from src.data.models import Word
from src.core.exporter import generate_markdown, export_words_to_file, default_out_path
import os


def make_word(id: int, kanji: str, kana: str, meaning: str, pos, category=None):
    if isinstance(pos, str):
        pos = [pos]
    return Word(
        id=id, kanji=kanji, kana=kana, meaning=meaning, pos=pos, category=category
    )


def test_grouping_and_id_sort():
    w1 = make_word(2, "食べる", "たべる", "吃", "动词1", "JLPT5")
    w2 = make_word(1, "勉強する", "べんきょうする", "学习", "动词1", "JLPT5")
    w3 = make_word(3, "学校", "がっこう", "学校", "名词", "日常")

    md = generate_markdown([w1, w2, w3])
    assert "**动词1 / JLPT5**" in md
    assert md.index("勉強する") < md.index("食べる")
    assert "**名词 / 日常**" in md


def test_default_sort_order_no_classify():
    w1 = make_word(1, "A名词1", "a", "m1", "名词", None)
    w2 = make_word(2, "B名词2", "b", "m2", "名词", "菜")
    w3 = make_word(3, "C动词", "c", "m3", "动词1", None)

    md = generate_markdown([w1, w2, w3])
    idx1 = md.index("**名词**")
    idx2 = md.index("**名词 / 菜**")
    idx3 = md.index("**动词1**")
    assert idx1 < idx2 < idx3


def test_multi_pos_classification_name():
    w = make_word(1, "綺麗", "きれい", "漂亮", ["形容动词", "名词"], None)
    md = generate_markdown([w])
    assert "**形容动词、名词**" in md


def test_multi_pos_sort_by_first_pos():
    w1 = make_word(1, "Z自动1", "a", "m1", ["形容动词", "名词"], None)
    w2 = make_word(2, "A名1", "b", "m2", ["名词", "形容动词"], None)

    md = generate_markdown([w1, w2])
    idx1 = md.index("**名词、形容动词**")
    idx2 = md.index("**形容动词、名词**")
    assert idx1 < idx2


def test_escape_and_linebreak():
    w = make_word(1, "本", "ほん", "书籍|参考\n更多", "名词", "日常")
    md = generate_markdown([w])
    assert "\|" in md
    assert "<br>" in md


def test_export_writes_file(tmp_path):
    w = make_word(1, "高い", "たかい", "贵", "形容词", "JLPT4")
    out = tmp_path / "words-test.md"
    path = export_words_to_file([w], str(out), classify_config=None)
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "词汇表" in content
    assert "高い" in content
