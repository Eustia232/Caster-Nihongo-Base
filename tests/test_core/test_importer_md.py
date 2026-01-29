from src.core.importer import WordImporter


SAMPLE_MD = """词汇表

| 汉字 | 假名 | 释义 |
|---|---|---|
| **动词 / daily** |  |  |
| 勉強する | べんきょうする0 | 学习 |
| 食べる | たべる2 | 吃 |
| **名词** |  |  |
| 本 | ほん1 | 书 |
"""


def test_process_markdown_basic():
    importer = WordImporter()
    words = importer.process_markdown(SAMPLE_MD, start_id=1)
    assert len(words) == 3
    assert words[0].id == 1
    assert words[0].kanji == "勉強する"
    assert words[0].kana == "べんきょうする0"
    assert words[0].pos == "动词"
    assert words[0].category == "daily"

    assert words[2].kanji == "本"
    assert words[2].pos == "名词"
