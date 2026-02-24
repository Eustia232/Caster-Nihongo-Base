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
  - Kana/读音 规则：填写假名读音时只需要填写纯假名（例如 `じしょ`），不需要在 `new.txt` 中加入音调数字或其他音调标记。导入时程序会自动根据仓库根目录的 `accents.txt` 为假名补全音调；如果 `accents.txt` 中存在对应条目，会以其为准。
  - 更新行为：每次你准备更新单词列表时，请用新的内容替换（清空并覆盖）工作目录下的 `new.txt`，不要在原文件末尾追加新行。导入工具会按整个文件的当前内容执行导入。
  - 空汉字处理：如果某条目没有汉字（例如外来语或仅假名），请把汉字字段留空但保留分隔符。例如：`|スイッチ|开关|名词` 表示汉字为空、假名为 `スイッチ`。

Allowed pos values (exact string match)
- 名词
- 名词サ变
- 动词1
- 动词5
- 形容词
- 形容动词
- 副词

Examples
 - 勉強する|べんきょうする|学习|动词1
 - 学校|がっこう|学校|名词
 - 高い|たかい|高的|形容词

Notes
- This file is intended for other agents or tools to read when generating or validating `new.txt` input. It intentionally omits any mention of category handling; only the four fields above are part of the import format.

Workflow / 使用说明
- 当你只需要更新导入内容时（修改 `new.txt`），只需编辑此文件并保存即可：不需要提交 git、也不需要运行单元测试或其他验证步骤。CLI 的 `import` 命令会直接读取工作目录下的 `new.txt`（或你指定的文件名），例如：
  - `uv run main.py import new.txt`
- 注意事项：确保文件为 UTF-8 编码且遵循本规范中列出的字段与格式规则。如果你希望将修改记录到版本控制，请自行 `git add` / `git commit`（该操作不是必须的导入前提）。
