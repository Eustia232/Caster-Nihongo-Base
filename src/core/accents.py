import os
import re
from typing import Dict, Tuple, Optional


def load_accents(path: str) -> Dict[Tuple[str, str], str]:
    """Load accents file into a mapping (kanji, reading) -> pitch string.

    Expects a tab-separated file with at least three columns: kanji\treading\tpitch
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
            if len(parts) < 3:
                continue
            kanji = parts[0].strip()
            reading = parts[1].strip()
            pitch = parts[2].strip()
            if kanji and reading:
                accents[(kanji, reading)] = pitch

    return accents


def _normalize_reading_for_match(reading: str) -> str:
    s = reading or ""
    s = s.strip()
    # remove bracketed numbers like [1]
    s = re.sub(r"\[\d+\]", "", s)
    # remove trailing digits (placeholders like 0)
    s = re.sub(r"\d+$", "", s)
    return s


def fill_pitch_for_content(content: str, accents_path: str) -> str:
    """Given file content (pipe-separated lines), return content with pitch filled.

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
    for (k, r), p in accents.items():
        if k not in fuzzy:
            fuzzy[k] = p

    out_lines = []
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

        # detect if reading already contains a pitch at the end (e.g. "じしょ3" or "じしょ3,2")
        if re.search(r"\d+(,\d+)*$", reading):
            # already has pitch-ish suffix; keep as-is
            out_lines.append(line)
            continue

        norm = _normalize_reading_for_match(reading)

        # exact match
        pitch: Optional[str] = None
        if (kanji, norm) in accents:
            pitch = accents[(kanji, norm)]
        else:
            # fuzzy by kanji
            pitch = fuzzy.get(kanji)

        if pitch:
            clean_pitch = pitch.replace(" ", "")
            parts[1] = f"{norm}{clean_pitch}"
        else:
            # no pitch found: use normalized reading (remove placeholders)
            parts[1] = norm

        out_lines.append("|".join(parts))

    return "\n".join(out_lines) + ("\n" if content.endswith("\n") else "")
