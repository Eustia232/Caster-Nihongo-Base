import pytest
from src.core.importer import WordImporter
from src.core.exceptions import ImporterError
from src.data.models import Word


def test_word_importer_parse_line():
    importer = WordImporter()
    line = "勉強する|べんきょうする0|学习|动词1"
    word = importer.parse_line(line, word_id=100)

    assert word.id == 100
    assert word.kanji == "勉強する"
    assert word.kana == "べんきょうする0"
    assert word.meaning == "学习"
    assert word.pos == ["动词1"]


def test_word_importer_parse_multi_pos():
    importer = WordImporter()
    line = "綺麗|きれい|漂亮|形容动词,名词"
    word = importer.parse_line(line, word_id=200)

    assert word.pos == ["形容动词", "名词"]


def test_word_importer_parse_multi_pos_chinese_comma():
    importer = WordImporter()
    line = "綺麗|きれい|漂亮|形容动词，名词"
    word = importer.parse_line(line, word_id=201)

    assert word.pos == ["形容动词", "名词"]


def test_word_importer_invalid_line():
    importer = WordImporter()
    with pytest.raises(ValueError):
        importer.parse_line("invalid|line", word_id=101)


def test_parse_line_with_category():
    importer = WordImporter()
    line = "勉強する|べんきょうする0|学习|动词1|JLPT5"
    word = importer.parse_line(line, word_id=102)
    assert word.pos == ["动词1"]
    assert word.category == "JLPT5"


def test_process_file_blocks_missing_readings(tmp_path):
    importer = WordImporter()
    content = "漢字| |意义|名词\n"
    words = importer.process_file(content, start_id=1)
    assert hasattr(importer, "last_problems")
    assert importer.last_problems
    for w in words:
        assert getattr(w, "kana", "")
