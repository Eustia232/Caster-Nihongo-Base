Export feature specification
============================

This document records the confirmed export requirements. It is a translation and relocation of the previous `docs/export_requirements.md` into the `docs/plans/` folder. The meaning is preserved; wording has been adapted into English.

1. Summary
- Output format: UTF-8 encoded Markdown table file.
- Default output path and filename: `export/words-YYYYMMDD.md` where `YYYYMMDD` is the UTC date of export (for example `export/words-20260128.md`).
- The first line inside the exported file must be the fixed title `词汇表` (this exact text is required by the specification). No additional export timestamp or summary line is included by default.

2. Table structure and classification presentation (core rules)
- Table columns (exactly three columns):
  - First column header: `汉字` (kanji)
  - Second column header: `假名` (kana)
  - Third column header: `释义` (meaning)
- Classification is not a column. Instead, each category appears as a standalone table row: the classification row places the classification name in the first column and leaves the remaining columns empty.
- Classification naming rule: combine `pos` and `category` into `pos / category`. The project guarantees `pos` is never empty, therefore classification names are always present.

3. Grouping and ordering
- Words are grouped by classification; words that share the same classification appear together.
- Within each classification group, words are ordered by `id` ascending.
- Classification groups are ordered by dictionary order (string ascending) by default.
- The implementation must reserve a customizable place for classification order/rules (for example an external config file). Recommended default config path: `export/classify.txt`. When a custom order is provided, groups listed in the config appear in that order; groups not listed follow default ordering.

4. Table rendering details
- Classification row rendering: the classification name is shown in bold (for example: `| **动词 / JLPT5** |  |  |`).
- There is no blank line after a classification row; word rows follow immediately beneath the classification row.
- Special characters inside cells: a pipe character `|` must be escaped as `\|`. Newlines inside a cell must be replaced with `<br>` so the Markdown table stays intact.

5. Scope and field filtering
- By default export includes all words from the repository (including entries where `category` is empty or an empty string).
- Exported rows include only the three columns above. SRS/progress fields (for example `id`, `pos`, `category`, `consecutive_successes`, `archived`, etc.) are NOT output as table columns. They remain available for grouping and ordering logic.

6. Configurable points (must be extensible)
- Classification mapping and order must be configurable via an external file (recommended `export/classify.txt`) or code constant; implementation should allow future extension to JSON/YAML or other sources.
- Output path is configurable (default `export/words-YYYYMMDD.md`).
- Special-character handling strategy should be configurable (default: `|` -> `\\|`, newline -> `<br>`).

7. Example snippet

词汇表

| 汉字 | 假名 | 释义 |
|---|---|---|
| **动词 / JLPT5** |  |  |
| 勉強する | べんきょうする | 学习 |
| 食べる | たべる | 吃 |

8. Notes and forward-looking suggestions
- If it becomes necessary to include export metadata (export time, author, summary), add an optional metadata block such as a YAML front-matter or a small header before the table.
- If more complex classification mappings are required (for example mapping multiple `pos` values to one label or ordering by JLPT level), provide a mapping file format with matching rules and priorities.

Maintenance hint: this document is the canonical feature specification for the Markdown exporter and lives in `docs/plans/2026-01-28-export-requirements.md`. Implementation should follow this spec; tests should validate grouping, ordering and escaping behavior.
