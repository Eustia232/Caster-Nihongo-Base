from datetime import datetime, timezone, timedelta
import random

import pytest

from src.cli import main as cli_main
from src.data.models import Word, SRSProgress


def make_word(
    word_id: int,
    kanji: str = "漢字",
    kana: str = "かな",
    meaning: str = "释义",
    pos: str = "n",
):
    return Word(
        id=word_id, kanji=kanji, kana=kana, meaning=meaning, pos=pos, category=None
    )


def make_progress(due: datetime = None, archived: bool = False):
    if due is None:
        due = datetime.now(timezone.utc)
    return SRSProgress(
        stability=1.0,
        difficulty=1.0,
        due=due,
        last_review=None,
        state=0,
        consecutive_successes=0,
        archived=archived,
    )


def test_batching_limits(monkeypatch, tmp_path, capsys):
    # Prepare 25 words: all due now
    words = [make_word(i) for i in range(1, 26)]

    # Replace WordRepository.load_all to return our words
    class DummyWordRepo:
        def __init__(self, *_):
            pass

        def load_all(self):
            return words

    # Progress repo: return None for new words to simulate new cards (due immediately)
    class DummyProgressRepo:
        def __init__(self, *_):
            self.store = {}

        def load(self, word_id):
            return None

        def save(self, word_id, progress):
            # record saves
            self.store[word_id] = progress

    monkeypatch.setattr(cli_main, "WordRepository", DummyWordRepo)
    monkeypatch.setattr(cli_main, "ProgressRepository", DummyProgressRepo)

    # Monkeypatch random.shuffle to keep deterministic order
    monkeypatch.setattr(random, "shuffle", lambda x: None)

    # Simulate user interactions: for each prompt, return correct kana; for confirms, say yes twice then no
    prompts = []

    def fake_prompt(text, default=None, show_default=None):
        prompts.append(text)
        return "かな"

    confirms = iter([True, True, False])

    def fake_confirm(text, default=True):
        return next(confirms)

    monkeypatch.setattr(cli_main.typer, "prompt", fake_prompt)
    monkeypatch.setattr(cli_main.typer, "confirm", fake_confirm)

    # Run review
    cli_main.review()

    # Capture printed output
    captured = capsys.readouterr()
    # Rely on numeric indicators to avoid locale/encoding issues in CI
    assert "25" in captured.out
    # Ensure batching prompts occurred (after 10 and 20 completed)
    assert "10/25" in captured.out
    assert "20/25" in captured.out
