import pytest
import os
from src.data.repository import WordRepository
from src.data.models import Word


def test_word_repository_load(tmp_path):
    # 设置模拟的 yaml 内容
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
