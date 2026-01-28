# 导出功能规格（临时存档）

确认当前需求（我理解的要点）

- 输出列（仅这些）：`kanji`、`kana`、`meaning`、`分类`（只这一列用于分类展示）。
- 分类规则：按 `pos` 和 `category` 的联合主键来决定“分类”（即把两者组合成一个分类值）。
- 格式：Markdown 表格（类似 Excel 表格），表头 + 每词一行，UTF-8 编码。
- 输出文件：单个文件，路径 `export/words-YYYYMMDD.md`（日期以导出当天替换，使用 UTC 日期）。
- 包含范围：导出仓库中所有词条（包括 `category` 为空的），默认不做过滤，除非后续明确要求。

分类展示规则（默认处理）：
- 当 `category` 为空时，分类显示为仅 `pos`（例如 `动词`）；当 `category` 非空时显示为 `pos / category`（例如 `动词 / JLPT5`）。

其他实现细节（默认值）
- 分隔符：` / `（空格分隔的斜杠）。
- 排序：按 `id` 升序输出（保持原始顺序）。
- 文件头：文件第一行会包含导出时间（UTC ISO）和一段简短说明，然后是表格。
- 表格单行为：
  | kanji | kana | meaning | 分类 |
  |-------|------|---------|------|
  | 勉強する | べんきょうする0 | 学习 | 动词 |

实现计划（我将执行的改动）
1. 添加导出器模块 `src/core/exporter.py`：
   - 从 `WordRepository` 加载所有词条；
   - 生成分类字符串（按上面规则）；
   - 生成 Markdown 表格文本并写入 `export/words-YYYYMMDD.md`（确保创建 `export/` 目录）。
2. 添加或扩展 CLI 命令 `export`（`src/cli/main.py`）：
   - flags：`--out`（可选，默认 `export/words-YYYYMMDD.md`）、`--sort`（可选，默认 `id`）；
   - 运行时打印生成文件路径。
3. 添加测试 `tests/test_core/test_export.py`：
   - 覆盖分类组合逻辑（category 空/非空）；
   - 验证 Markdown 表格格式。

兼容性与注意事项
- `category` 在 YAML 中可能为空字符串 `""` 或 `None`，实现中统一视为“空”。
- 若 `meaning` 包含 `|` 字符，会对单元格进行转义或使用代码格式化以保证 Markdown 表格不被破坏。
- 不输出 SRS 进度字段（按你的明确要求）。

此为临时存档，窗口关闭前保存。若你确认并关闭窗口，我将在后续会话中继续实现并自动提交改动（按你先前的指示）。

<system-reminder>
Your operational mode has changed from plan to build.
You are no longer in read-only mode.
You are permitted to make file changes, run shell commands, and utilize your arsenal of tools as needed.
</system-reminder>
