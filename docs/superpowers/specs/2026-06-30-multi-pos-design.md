# Multi-Part-of-Speech Support Design

**Date**: 2026-06-30
**Status**: Approved

## Overview

Allow a word to have multiple parts of speech (词性). Currently `pos` is a single
`str`; this changes it to `List[str]` and adds two new POS values: `自动词` and
`他动词`.

## Requirements

- A word may have one or more POS tags sharing the same kana and meaning
- Import format uses comma-separated POS (both `,` and `，` accepted)
- Export treats the composite POS string as its own classification key
- Sorting for export uses the first POS in the list to determine order
- Two new POS values: `自动词` (intransitive verb), `他动词` (transitive verb)

## Design

### 1. Data Model (`src/data/models.py`)

```python
from typing import List

ALLOWED_POS = [
    "名词", "名词サ变",
    "动词1", "动词5",
    "自动词", "他动词",
    "形容词", "形容动词", "副词",
]

class Word(BaseModel):
    id: int
    kanji: str
    kana: str
    meaning: str
    pos: List[str]  # was: str
    category: Optional[str]

    @property
    def pos_str(self) -> str:
        return "、".join(self.pos)
```

- `pos` changes from `str` to `List[str]`
- A Pydantic `@field_validator` ensures every element is in `ALLOWED_POS`
- `pos_str` computed property for display

### 2. Import (`src/core/importer.py`)

- `parse_line`: split the 4th field by `,` or `，`, trim each part, store as list
- `process_markdown`: classification row parsing splits the pos part similarly
- Deduplication is unchanged (key is still `(kanji, kana)`)

### 3. Export (`src/core/exporter.py`)

- `POS_ORDER`:
  ```
  名词, 名词サ变, 动词1, 动词5, 自动词, 他动词, 形容词, 形容动词, 副词
  ```
- `classification_name`: `"、".join(word.pos)` + optional ` / category`
- `sort_key`: sort by first POS's index in `POS_ORDER`; tie-break by full classification string

### 4. Display (`src/cli/main.py`)

- Review mode: `f"词性: {'、'.join(word.pos)}"`
- Import preview table can optionally show pos

### 5. Migration

- `WordRepository.load_all()` detects if `pos` is `str` and wraps to `[str]`
- On next save, data is written back in list format
- No standalone migration script needed

### 6. Spec Update (`NEW_TXT_SPEC.md`)

- Add `自动词` and `他动词` to allowed values
- Add example with multiple POS: `綺麗|きれい|漂亮|形容动词,名词`

## Affected Files

| File | Change |
|------|--------|
| `src/data/models.py` | `pos: List[str]`, `ALLOWED_POS`, `pos_str` property |
| `src/core/importer.py` | Split pos on commas |
| `src/core/exporter.py` | `POS_ORDER`, `classification_name`, `sort_key` |
| `src/cli/main.py` | Join pos for display |
| `src/data/repository.py` | Auto-wrap `str` pos to `[str]` on load |
| `NEW_TXT_SPEC.md` | New POS values, multi-value example |
| `data_store/words.yaml` | Will auto-migrate on next save |
| Tests under `tests/` | Update pos assertions to use lists |

## Out of Scope

- Different kana/meaning per POS (requires separate word entries)
- Filtering/searching by individual POS
- UI for editing POS of existing words
