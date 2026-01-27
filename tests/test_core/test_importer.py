import pytest
from src.core.importer import WordImporter
from src.data.models import Word


def test_word_importer_parse_line():
    importer = WordImporter()
    line = "勉強する|べんきょうする0|学习|动词"
    word = importer.parse_line(line, word_id=100)

    assert word.id == 100
    assert word.kanji == "勉強する"
    assert word.kana == "べんきょうする0"
    assert word.meaning == "学习"
    assert word.pos == "动词"


def test_word_importer_invalid_line():
    importer = WordImporter()
    with pytest.raises(ValueError):
        importer.parse_line("invalid|line", word_id=101)
