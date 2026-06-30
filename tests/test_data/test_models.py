import pytest
from datetime import datetime, timezone
from src.data.models import Word, SRSProgress, ALLOWED_POS


def test_word_model_validation():
    data = {
        "id": 1000,
        "kanji": "食べる",
        "kana": "たべる2",
        "meaning": "吃",
        "pos": ["动词1"],
        "category": None,
    }
    word = Word(**data)
    assert word.id == 1000
    assert word.kanji == "食べる"
    assert word.pos == ["动词1"]
    assert word.pos_str == "动词1"


def test_word_multi_pos():
    data = {
        "id": 2000,
        "kanji": "綺麗",
        "kana": "きれい",
        "meaning": "漂亮",
        "pos": ["形容动词", "名词"],
        "category": None,
    }
    word = Word(**data)
    assert word.pos == ["形容动词", "名词"]
    assert word.pos_str == "形容动词、名词"


def test_word_pos_validator_rejects_invalid():
    with pytest.raises(ValueError, match="非法词性"):
        Word(
            id=3000,
            kanji="x",
            kana="x",
            meaning="x",
            pos=["不存在"],
            category=None,
        )


def test_ensure_list_coerces_string():
    word = Word(
        id=4000,
        kanji="x",
        kana="x",
        meaning="x",
        pos="名词",
        category=None,
    )
    assert word.pos == ["名词"]


def test_pos_str_single():
    word = Word(
        id=5000,
        kanji="x",
        kana="x",
        meaning="x",
        pos=["自动词"],
        category=None,
    )
    assert word.pos_str == "自动词"


def test_srs_progress_model():
    data = {
        "stability": 0.5,
        "difficulty": 3.0,
        "due": datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc),
        "last_review": datetime(2026, 1, 27, 12, 0, 0, tzinfo=timezone.utc),
        "state": 0,
    }
    progress = SRSProgress(**data)
    assert progress.stability == 0.5
    assert progress.due.day == 28
