new.txt import format
====================

Purpose
- Short machine-readable specification for `new.txt` files used to import words.

Format
- Each non-empty line is a single word record. Fields are separated by `|` (pipe).
- Exactly four fields per line in this order: `kanji | kana | meaning | pos`.

Field rules
- Trim whitespace around fields.
- Lines with fewer or more than four pipe-separated fields are invalid.
- Do not include extra metadata or extra `|` characters.

Allowed pos values (exact string match)
- 名词
- 动词1
- 动词5
- 形容词
- 形容动词
- 副词

Examples
- 勉強する|べんきょうする0|学习|动词1
- 学校|がっこう0|学校|名词
- 高い|たかい2|高的|形容词

Notes
- This file is intended for other agents or tools to read when generating or validating `new.txt` input. It intentionally omits any mention of category handling; only the four fields above are part of the import format.
