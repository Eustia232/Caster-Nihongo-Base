"""Tests for normalize_kana and extract_readings used in review matching."""

from src.cli.main import normalize_kana, extract_readings


# ── normalize_kana tests ──────────────────────────────────────────────


class TestNormalizeKana:
    def test_simple_kana_with_pitch(self):
        assert normalize_kana("たべる2") == "たべる"

    def test_simple_kana_without_pitch(self):
        assert normalize_kana("たべる") == "たべる"

    def test_multi_pitch_single_reading(self):
        assert normalize_kana("きっさてん3,0") == "きっさてん"

    def test_pos_annotated_multi_reading(self):
        """だいじ(名)1,3,(形動)0,3 should normalize to だいじ"""
        assert normalize_kana("だいじ(名)1,3,(形動)0,3") == "だいじ"

    def test_fullwidth_parentheses(self):
        """Full-width parentheses （名） should also be stripped."""
        assert normalize_kana("だいじ（名）1,3") == "だいじ"

    def test_bracketed_numbers(self):
        assert normalize_kana("がっこう[1]2") == "がっこう"

    def test_fullwidth_digits_and_comma(self):
        assert normalize_kana("たべ３，２") == "たべ"

    def test_trailing_digits_stripped(self):
        assert normalize_kana("ほん1") == "ほん"

    def test_empty_string(self):
        assert normalize_kana("") == ""

    def test_only_pitch_numbers(self):
        """If only digits remain after stripping, result should be empty."""
        assert normalize_kana("3,0") == ""

    def test_complex_pos_annotation(self):
        """(副;名) style annotation should be fully removed."""
        assert normalize_kana("ぽんぽん(副;名)1,(形動)0") == "ぽんぽん"

    def test_whitespace_stripped(self):
        # Leading/trailing whitespace is stripped first, then pitch removed
        assert normalize_kana("  たべる2  ") == "たべる"


# ── extract_readings tests ────────────────────────────────────────────


class TestExtractReadings:
    def test_simple_kana(self):
        assert extract_readings("たべる2") == ["たべる"]

    def test_multi_pitch_single_reading(self):
        assert extract_readings("きっさてん3,0") == ["きっさてん"]

    def test_pos_annotated_same_kana(self):
        """Both POS share the same kana -> single entry."""
        assert extract_readings("だいじ(名)1,3,(形動)0,3") == ["だいじ"]

    def test_no_annotation(self):
        assert extract_readings("がっこう") == ["がっこう"]

    def test_empty_string(self):
        assert extract_readings("") == []

    def test_fullwidth_parentheses(self):
        assert extract_readings("だいじ（名）1,3,（形動）0,3") == ["だいじ"]


# ── Integration: user answer matching ─────────────────────────────────


class TestReviewMatching:
    """Simulate the actual comparison logic used in review()."""

    def _matches(self, user_answer: str, word_kana: str) -> bool:
        return normalize_kana(user_answer) in [
            normalize_kana(r) for r in extract_readings(word_kana)
        ]

    def test_plain_answer_matches_annotated_kana(self):
        assert self._matches("だいじ", "だいじ(名)1,3,(形動)0,3")

    def test_answer_with_pitch_matches(self):
        assert self._matches("だいじ1", "だいじ(名)1,3,(形動)0,3")

    def test_simple_word_still_works(self):
        assert self._matches("たべる", "たべる2")

    def test_wrong_answer_does_not_match(self):
        assert not self._matches("ちがう", "だいじ(名)1,3,(形動)0,3")

    def test_multi_pitch_word(self):
        assert self._matches("きっさてん", "きっさてん3,0")
