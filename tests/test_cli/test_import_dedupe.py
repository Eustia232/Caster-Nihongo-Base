import io
import pytest
from typing import Optional

from src.cli import main as cli_main
from src.data.models import Word


def _disable_sync_hooks(monkeypatch):
    monkeypatch.setattr(cli_main, "check_git_env", lambda: None)
    monkeypatch.setattr(cli_main, "sync_pull", lambda _path: None)
    monkeypatch.setattr(cli_main, "sync_push", lambda _path: None)


def make_word(
    word_id: int,
    kanji: str,
    kana: str,
    meaning: str = "m",
    pos: str = "名词",
    category: Optional[str] = None,
):
    return Word(
        id=word_id, kanji=kanji, kana=kana, meaning=meaning, pos=[pos], category=category
    )


def test_import_skips_duplicates(monkeypatch, tmp_path, capsys):
    _disable_sync_hooks(monkeypatch)

    existing = [make_word(1, "勉強する", "べんきょうする0")]

    class DummyRepo:
        def __init__(self, path):
            self.path = path

        def load_all(self):
            return existing

        def save_all(self, words):
            assert len(words) == 2
            assert words[0].kanji == "勉強する"

    monkeypatch.setattr(cli_main, "WordRepository", DummyRepo)

    content = "勉強する|べんきょうする0|学习|动词1\n新しい|あたらしい0|新|形容词\n"

    class DummyImporter:
        def process_file(self, c, start_id):
            assert c == content
            return [
                make_word(2, "勉強する", "べんきょうする0"),
                make_word(3, "新しい", "あたらしい0"),
            ]

    monkeypatch.setattr(cli_main, "WordImporter", lambda: DummyImporter())

    p = tmp_path / "new.txt"
    p.write_text(content, encoding="utf-8")

    monkeypatch.setattr(cli_main.typer, "confirm", lambda msg: True)

    cli_main.import_cmd(str(p))

    out = capsys.readouterr().out
    assert "1" in out


def test_import_overwrites_duplicates_when_flag_set(monkeypatch, tmp_path, capsys):
    """测试 --overwrite 模式：重复条目应被覆盖，保留原 ID"""
    _disable_sync_hooks(monkeypatch)

    existing = [
        make_word(1, "勉強する", "べんきょうする0", meaning="旧释义", pos="动词1")
    ]
    saved_words = []

    class DummyRepo:
        def __init__(self, path):
            self.path = path

        def load_all(self):
            return existing

        def save_all(self, words):
            saved_words.extend(words)

    monkeypatch.setattr(cli_main, "WordRepository", DummyRepo)

    content = "勉強する|べんきょうする0|新释义|名词\n新しい|あたらしい0|新|形容词\n"

    class DummyImporter:
        def process_file(self, c, start_id):
            return [
                make_word(
                    2, "勉強する", "べんきょうする0", meaning="新释义", pos="名词"
                ),
                make_word(3, "新しい", "あたらしい0", meaning="新", pos="形容词"),
            ]

    monkeypatch.setattr(cli_main, "WordImporter", lambda: DummyImporter())

    p = tmp_path / "new.txt"
    p.write_text(content, encoding="utf-8")

    monkeypatch.setattr(cli_main.typer, "confirm", lambda msg: True)

    cli_main.import_cmd(str(p), overwrite=True)

    out = capsys.readouterr().out

    assert "覆盖 1 个已存在条目" in out

    assert len(saved_words) == 2

    overwritten_word = next(w for w in saved_words if w.kanji == "勉強する")
    assert overwritten_word.id == 1
    assert overwritten_word.meaning == "新释义"
    assert overwritten_word.pos == ["名词"]

    new_word = next(w for w in saved_words if w.kanji == "新しい")
    assert new_word.meaning == "新"


def test_import_overwrite_only_affects_existing(monkeypatch, tmp_path, capsys):
    """测试 --overwrite 模式：仅覆盖已存在的条目，新条目正常添加"""
    _disable_sync_hooks(monkeypatch)

    existing = []
    saved_words = []

    class DummyRepo:
        def __init__(self, path):
            self.path = path

        def load_all(self):
            return existing

        def save_all(self, words):
            saved_words.extend(words)

    monkeypatch.setattr(cli_main, "WordRepository", DummyRepo)

    content = "新しい|あたらしい0|新|形容词\n"

    class DummyImporter:
        def process_file(self, c, start_id):
            return [
                make_word(1, "新しい", "あたらしい0", meaning="新", pos="形容词"),
            ]

    monkeypatch.setattr(cli_main, "WordImporter", lambda: DummyImporter())

    p = tmp_path / "new.txt"
    p.write_text(content, encoding="utf-8")

    monkeypatch.setattr(cli_main.typer, "confirm", lambda msg: True)

    cli_main.import_cmd(str(p), overwrite=True)

    out = capsys.readouterr().out

    assert "覆盖" not in out
    assert "准备导入 1 个单词" in out

    assert len(saved_words) == 1
    assert saved_words[0].kanji == "新しい"


def test_import_skips_internal_duplicates_in_overwrite_mode(
    monkeypatch, tmp_path, capsys
):
    """测试 --overwrite 模式：导入文件内部的重复条目应被跳过"""
    _disable_sync_hooks(monkeypatch)

    existing = []
    saved_words = []

    class DummyRepo:
        def __init__(self, path):
            self.path = path

        def load_all(self):
            return existing

        def save_all(self, words):
            saved_words.extend(words)

    monkeypatch.setattr(cli_main, "WordRepository", DummyRepo)

    content = "新しい|あたらしい0|新1|形容词\n新しい|あたらしい0|新2|形容词\n"

    class DummyImporter:
        def process_file(self, c, start_id):
            return [
                make_word(1, "新しい", "あたらしい0", meaning="新1", pos="形容词"),
                make_word(2, "新しい", "あたらしい0", meaning="新2", pos="形容词"),
            ]

    monkeypatch.setattr(cli_main, "WordImporter", lambda: DummyImporter())

    p = tmp_path / "new.txt"
    p.write_text(content, encoding="utf-8")

    monkeypatch.setattr(cli_main.typer, "confirm", lambda msg: True)

    cli_main.import_cmd(str(p), overwrite=True)

    assert len(saved_words) == 1
    assert saved_words[0].meaning == "新1"
