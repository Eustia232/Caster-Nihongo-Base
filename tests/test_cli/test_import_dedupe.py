import io
import pytest

from src.cli import main as cli_main
from src.data.models import Word


def make_word(word_id: int, kanji: str, kana: str):
    return Word(id=word_id, kanji=kanji, kana=kana, meaning="m", pos="n", category=None)


def test_import_skips_duplicates(monkeypatch, tmp_path, capsys):
    # existing words contain one entry
    existing = [make_word(1, "勉強する", "べんきょうする0")]

    class DummyRepo:
        def __init__(self, path):
            self.path = path

        def load_all(self):
            return existing

        def save_all(self, words):
            # assert that only the non-duplicate word is added
            assert len(words) == 2
            assert words[0].kanji == "勉強する"

    monkeypatch.setattr(cli_main, "WordRepository", DummyRepo)

    # Prepare file content containing a duplicate and a new word
    content = "勉強する|べんきょうする0|学习|动词\n新しい|あたらしい0|新|形容词\n"

    # Monkeypatch importer to return parsed words
    class DummyImporter:
        def process_file(self, c, start_id):
            assert c == content
            return [
                make_word(2, "勉強する", "べんきょうする0"),
                make_word(3, "新しい", "あたらしい0"),
            ]

    monkeypatch.setattr(cli_main, "WordImporter", lambda: DummyImporter())

    # Run import_cmd
    # create a temp file
    p = tmp_path / "new.txt"
    p.write_text(content, encoding="utf-8")

    monkeypatch.setattr(cli_main.typer, "confirm", lambda msg: True)

    cli_main.import_cmd(str(p))

    out = capsys.readouterr().out
    assert "准备导入 1 个单词" in out or "准备导入 1 个单词" in out
