import os
import re
from typing import Dict, List, Optional, Tuple


def _is_kana(s: str) -> bool:
    """Return True if string s is (mostly) kana (hiragana/katakana)."""
    if not s:
        return False
    # Hiragana: \u3040-\u309F, Katakana: \u30A0-\u30FF, include prolonged sound mark
    return bool(re.match(r"^[\u3040-\u309F\u30A0-\u30FFー]+$", s))


def load_accents(path: str) -> Dict[Tuple[str, str], str]:
    """Load accents file into a mapping (kanji, normalized_reading) -> pitch string.

    The accents file is tab-separated but historically contains several variants:
    - kanji\treading\tpitch
    - reading\tpitch (kanji omitted)
    - kanji\t\tpitch (empty reading column; reading may be in kanji column)

    This loader is tolerant: it detects which column contains kana (reading)
    and normalizes the reading using _normalize_reading_for_match so lookups
    are consistent whether the input line had kana in the first or second column.
    """
    accents: Dict[Tuple[str, str], str] = {}
    if not os.path.exists(path):
        return accents

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")

            kanji_raw = ""
            reading_raw = ""
            pitch = ""

            if len(parts) >= 3:
                kanji_raw = parts[0].strip()
                reading_raw = parts[1].strip()
                pitch = parts[2].strip()
            elif len(parts) == 2:
                a = parts[0].strip()
                b = parts[1].strip()
                # if first column looks like kana, treat it as reading
                if _is_kana(a):
                    kanji_raw = ""
                    reading_raw = a
                    pitch = b
                else:
                    # otherwise treat as kanji + pitch (no explicit reading)
                    kanji_raw = a
                    reading_raw = ""
                    pitch = b
            else:
                continue

            # if reading column is empty but kanji_raw actually contains kana,
            # treat kanji_raw as the reading and clear kanji
            if not reading_raw and _is_kana(kanji_raw):
                reading_raw = kanji_raw
                kanji_raw = ""

            if not reading_raw:
                # nothing to index by reading; still record fuzzy kanji->pitch
                if kanji_raw and pitch:
                    accents[(kanji_raw, "")] = pitch
                continue

            norm_reading = _normalize_reading_for_match(reading_raw)
            if not norm_reading:
                continue

            accents[(kanji_raw, norm_reading)] = pitch

    return accents


def _normalize_reading_for_match(reading: str) -> str:
    s = reading or ""
    s = s.strip()
    # remove bracketed numbers like [1]
    s = re.sub(r"\[\d+\]", "", s)
    # remove trailing digits (placeholders like 0)
    s = re.sub(r"\d+$", "", s)
    return s


def fill_pitch_for_content(content: str, accents_path: str) -> Tuple[str, List[Tuple[int, str]]]:
    """Given file content (pipe-separated lines), return content with pitch filled.

    Returns:
        Tuple of (processed_content, missing_pitch_lines)
        - processed_content: content with pitch filled where found
        - missing_pitch_lines: list of (line_number, original_line) where pitch was not found

    Behavior:
    - For each line containing '|' split into parts, expect parts[0]=kanji, parts[1]=reading
    - Normalize reading by removing trailing placeholder digits; if reading already
      ends with a pitch-like pattern (digits or digits+comma), assume it's present and skip.
    - Try exact match (kanji, reading) against accents file; if not found, try first
      entry with same kanji as a fuzzy fallback.
    - If pitch found, clean spaces from pitch (keep commas) and append to reading.
    - If no pitch found, use normalized reading (without trailing placeholder digits).
    """
    accents = load_accents(accents_path)

    # build fuzzy mapping: kanji -> first pitch found
    fuzzy: Dict[str, str] = {}
    # build reading index: reading -> first pitch found (useful when kanji is empty)
    reading_index: Dict[str, str] = {}
    for (k, r), p in accents.items():
        # accents keys are (kanji, normalized_reading) from load_accents
        if k and k not in fuzzy:
            fuzzy[k] = p
        if r and r not in reading_index:
            reading_index[r] = p

    out_lines = []
    missing_pitch_lines: List[Tuple[int, str]] = []
    for lineno, raw in enumerate(content.splitlines(), start=1):
        line = raw.rstrip("\n")
        if "|" not in line or not line.strip():
            out_lines.append(line)
            continue

        parts = [p for p in line.split("|")]
        # ensure we have at least two columns
        if len(parts) < 2:
            out_lines.append(line)
            continue

        kanji = parts[0].strip()
        reading = parts[1].strip()

        # normalize reading by removing bracketed numbers and trailing placeholder digits
        norm = _normalize_reading_for_match(reading)

        # detect if reading already contains a pitch at the end (e.g. "じしょ3" or "じしょ3,2").
        # If the suffix is a real pitch (contains a non-zero digit) preserve the original line.
        # If the suffix is only a placeholder like '0', treat it as absent and continue lookup.
        m = re.search(r"([0-9０-９]+(?:[,，][0-９]+)*)$", reading)
        if m:
            suffix = m.group(1)
            # normalize fullwidth digits to ASCII for decision
            suffix_ascii = suffix.translate(
                str.maketrans("０１２３４５６７８９", "0123456789")
            ).replace("，", ",")
            # if suffix is not solely zero(s), consider it a real pitch and preserve
            if any(ch != "0" and ch != "," for ch in suffix_ascii):
                out_lines.append(line)
                continue

        # exact match
        pitch: Optional[str] = None
        if (kanji, norm) in accents:
            pitch = accents[(kanji, norm)]
        else:
            # if kanji is empty, try reading-based lookup (best-effort)
            if not kanji:
                pitch = reading_index.get(norm)
            # fuzzy by kanji (fallback)
            if pitch is None:
                pitch = fuzzy.get(kanji)

        if pitch:
            clean_pitch = pitch.replace(" ", "")
            parts[1] = f"{norm}{clean_pitch}"
            out_lines.append("|".join(parts))
        else:
            # no pitch found: use normalized reading (remove placeholders)
            parts[1] = norm
            processed_line = "|".join(parts)
            missing_pitch_lines.append((lineno, processed_line))
            out_lines.append(processed_line)

    return (
        "\n".join(out_lines) + ("\n" if content.endswith("\n") else ""),
        missing_pitch_lines,
    )
