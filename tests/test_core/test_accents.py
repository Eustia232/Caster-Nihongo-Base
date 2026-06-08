import os
from src.core.accents import fill_pitch_for_content, load_accents


def test_load_accents(tmp_path):
    p = tmp_path / "acc.txt"
    p.write_text("辞書\tじしょ\t3,2\n銀行\tぎんこう\t4\n", encoding="utf-8")
    acc = load_accents(str(p))
    assert acc.get(("辞書", "じしょ")) == "3,2"
    assert acc.get(("銀行", "ぎんこう")) == "4"


def test_fill_exact_match(tmp_path):
    accf = tmp_path / "acc.txt"
    accf.write_text("辞書\tじしょ\t3,2\n", encoding="utf-8")

    content = "辞書|じしょ|词典|名词\n"
    out, missing = fill_pitch_for_content(content, str(accf))
    assert "辞書|じしょ3,2|词典|名词" in out
    assert missing == []


def test_fill_with_placeholder_removal(tmp_path):
    accf = tmp_path / "acc.txt"
    accf.write_text("辞書\tじしょ\t3,2\n", encoding="utf-8")

    content = "辞書|じしょ0|词典|名词\n"
    out, missing = fill_pitch_for_content(content, str(accf))
    assert "辞書|じしょ3,2|词典|名词" in out
    assert missing == []


def test_fuzzy_match_by_kanji(tmp_path):
    accf = tmp_path / "acc.txt"
    # only one entry for 銀行 -> used as fuzzy fallback
    accf.write_text("銀行\tぎんこう\t4\n", encoding="utf-8")

    content = "銀行|ぎんこ|银行|名词\n"
    out, missing = fill_pitch_for_content(content, str(accf))
    # normalized reading should be used + fuzzy pitch appended
    assert "銀行|ぎんこ4|银行|名词" in out
    assert missing == []


def test_already_has_pitch_is_preserved(tmp_path):
    accf = tmp_path / "acc.txt"
    accf.write_text("辞書\tじしょ\t3,2\n", encoding="utf-8")

    content = "辞書|じしょ3,2|词典|名词\n"
    out, missing = fill_pitch_for_content(content, str(accf))
    assert "辞書|じしょ3,2|词典|名词" in out
    assert missing == []


def test_no_match_leaves_normalized_reading(tmp_path):
    accf = tmp_path / "acc.txt"
    # empty accents
    accf.write_text("", encoding="utf-8")

    content = "辞書|じしょ0|词典|名词\n"
    out, missing = fill_pitch_for_content(content, str(accf))
    assert "辞書|じしょ|词典|名词" in out
    assert missing == [(1, "辞書|じしょ|词典|名词")]
