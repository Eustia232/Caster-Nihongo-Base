import pytest
import os
from datetime import datetime, timezone
from src.data.repository import WordRepository, ProgressRepository
from src.data.models import Word, SRSProgress


def test_word_repository_load(tmp_path):
    yaml_content = """
- id: 1
  kanji: 食べる
  kana: たべる2
  meaning: 吃
  pos: 动词
  category: ""
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
        due=datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc),
        last_review=datetime(2026, 1, 27, 12, 0, 0, tzinfo=timezone.utc),
        state=0,
        step=0,
        consecutive_successes=0,
        archived=False,
        archived_at=None,
        archived_reason=None,
    )

    repo.save(1, progress)
    loaded = repo.load(1)

    assert loaded is not None
    assert loaded.stability == 0.5
    # 注意：JSON 序列化后微秒可能会有差异或被忽略，但 isoformat 通常没问题
    assert loaded.due.isoformat() == progress.due.isoformat()


def test_word_repository_delete_many(tmp_path):
    yaml_content = """
- id: 1
  kanji: 食べる
  kana: たべる2
  meaning: 吃
  pos: 动词
- id: 2
  kanji: 飲む
  kana: のむ1
  meaning: 喝
  pos: 动词
- id: 3
  kanji: 行く
  kana: いく0
  meaning: 去
  pos: 动词
"""
    data_file = tmp_path / "words.yaml"
    data_file.write_text(yaml_content, encoding="utf-8")

    repo = WordRepository(str(data_file))
    repo.delete_many([1, 3, 99])  # 99 不存在，应忽略

    words = repo.load_all()
    assert len(words) == 1
    assert words[0].id == 2
    assert words[0].kanji == "飲む"


def test_progress_repository_delete_many(tmp_path):
    data_file = tmp_path / "progress.json"
    repo = ProgressRepository(str(data_file))

    progress = SRSProgress(
        stability=0.5,
        difficulty=3.0,
        due=datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc),
        last_review=datetime(2026, 1, 27, 12, 0, 0, tzinfo=timezone.utc),
        state=0,
        step=0,
        consecutive_successes=0,
        archived=False,
        archived_at=None,
        archived_reason=None,
    )

    repo.save(1, progress)
    repo.save(2, progress)
    repo.save(3, progress)

    repo.delete_many([1, 3, 99])  # 99 不存在，应忽略

    assert repo.load(1) is None
    assert repo.load(2) is not None
    assert repo.load(3) is None
