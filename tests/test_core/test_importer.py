import pytest
from src.core.importer import WordImporter
from src.core.exceptions import ImporterError
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


def test_parse_line_with_category():
    importer = WordImporter()
    line = "勉強する|べんきょうする0|学习|动词|JLPT5"
    word = importer.parse_line(line, word_id=102)


def test_process_file_blocks_missing_readings(tmp_path):
    importer = WordImporter()
    # content has a line with empty kana column
    content = "漢字| |意义|名词\n"
    try:
        importer.process_file(content, start_id=1)
        assert False, "Expected ImporterError"
    except ImporterError as e:
        assert e.problems and "missing kana" in e.problems[0]

    assert word.category == "JLPT5"
