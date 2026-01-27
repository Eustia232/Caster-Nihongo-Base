import pytest
import os
from src.data.repository import WordRepository, ProgressRepository
from src.data.models import Word, SRSProgress
from datetime import datetime


def test_word_repository_load(tmp_path):
    # ... 原有测试 ...
    yaml_content = """
- id: 1
  kanji: 食べる
  kana: たべる2
  meaning: 吃
  pos: 动词
"""
    data_file = tmp_path / "words.yaml"
    data_file.write_text(yaml_content, encoding="utf-8")

    repo = WordRepository(str(data_file))
    words = repo.load_all()

    assert len(words) == 1
    assert words[0].kanji == "食べる"
    assert words[0].id == 1


def test_progress_repository_save_load(tmp_path):
    data_file = tmp_path / "progress.json"
    repo = ProgressRepository(str(data_file))

    progress = SRSProgress(
        stability=0.5,
        difficulty=3.0,
        elapsed_days=1,
        scheduled_days=2,
        last_review=datetime(2026, 1, 27, 12, 0, 0),
        state=0,
    )

    repo.save(1, progress)
    loaded = repo.load(1)

    assert loaded is not None
    assert loaded.stability == 0.5
    assert loaded.last_review == progress.last_review
