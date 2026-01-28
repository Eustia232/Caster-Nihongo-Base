from datetime import datetime
from src.data.models import Word
from src.core.exporter import generate_markdown, export_words_to_file, default_out_path
import os


def make_word(id: int, kanji: str, kana: str, meaning: str, pos: str, category=None):
    return Word(
        id=id, kanji=kanji, kana=kana, meaning=meaning, pos=pos, category=category
    )


def test_grouping_and_id_sort():
    w1 = make_word(2, "食べる", "たべる", "吃", "动词", "JLPT5")
    w2 = make_word(1, "勉強する", "べんきょうする", "学习", "动词", "JLPT5")
    w3 = make_word(3, "学校", "がっこう", "学校", "名词", "日常")

    md = generate_markdown([w1, w2, w3])
    # 分类行应该先出现 动词 / JLPT5，然后是 id 升序的两个单词（id 1 然后 2）
    assert "**动词 / JLPT5**" in md
    # 勉強する (id=1) 在 食べる (id=2) 之前
    assert md.index("勉強する") < md.index("食べる")
    # 名词组存在
    assert "**名词 / 日常**" in md


def test_escape_and_linebreak():
    w = make_word(1, "本", "ほん", "书籍|参考\n更多", "名词", "日常")
    md = generate_markdown([w])
    # 竖线被转义
    assert "\|" in md
    # 换行被替换为 <br>
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
