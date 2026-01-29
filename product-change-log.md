# Product Change Log

## [2026-01-28]
### Added
- Added English export requirements plan at `docs/plans/2026-01-28-export-requirements.md`.
 - Importer now supports optional category field when parsing lines (5th pipe-separated field). See `src/core/importer.py`.
### Added
- 新增 Markdown 导出器（`src/core/exporter.py`），实现按 `pos / category` 分组并生成 `export/words-YYYYMMDD.md`。
- 在 CLI 中新增 `export` 命令（`src/cli/main.py`），支持 `--out` 与 `--classify` 参数以导出词汇为 Markdown。
- 新增导出相关测试 `tests/test_core/test_export.py`，覆盖分组、排序与转义逻辑。
- 新增导出需求文档 `docs/export_requirements.md` 与演示文件 `demo.md`。
 - 自动归档（auto-archive）功能：当单词连续答对 6 次后，系统自动将其标记为归档（`archived=True`），并在复习选择中跳过。
   - 变更位置：`src/data/models.py`（新增字段 `consecutive_successes`, `archived`, `archived_at`, `archived_reason`），`src/core/srs.py`（更新归档判定逻辑），`src/cli/main.py`（跳过归档条目），新增测试 `tests/test_core/test_auto_archive.py`。
### Added
- 在 `words.yaml` 中新增了 10 个常用日语单词。
### Changed
- 新增 `category` 可选字段到 `Word` 数据模型；更新 `src/data/models.py`, `src/data/repository.py`, `src/core/importer.py`，以及相关测试与 `data_store/words.yaml`（现有词条的 `category` 设为空字符串），以保持向后兼容。
### Changed
- 优化 `review` 命令流程：现在复习时会提示用户输入假名答案，并根据输入正确性自动判定 FSRS 等级（正确为 Good，错误/跳过为 Again），不再需要手动选择 1-4 评分。
- 增强假名答案归一化逻辑：对比时现在可以自动忽略 `[n]` 格式以及末尾数字格式（如 `たべる2`）的音调标记。

## [2026-01-29]
### Changed
- 将 `review` 命令分批处理：每批最多 10 个单词，处理完一批后提示用户继续或退出；如果可复习单词少于 10 个则按实际数量处理。
  - 变更位置：`src/cli/main.py`
  - 新增单元测试：`tests/test_cli/test_review_batching.py`

### Administrative
- 修正：遵循 `.gitignore` 指南，不应将本仓库中被忽略的 `AGENTS.md` 文件加入版本控制。已将 `AGENTS.md` 从暂存区移除并恢复为未跟踪（保留本地副本），以遵循仓库忽略规则。

### Added
- 新增自动音调补全模块 `src/core/accents.py`，在导入时会使用仓库根目录的 `accents.txt` 为假名字段补上音调，并在导入到 `data_store/words.yaml` 前完成预处理。

### Changed
- 在 `src/core/importer.py` 的 `process_file` 中集成了音调自动补全调用，导入前会把 `new.txt` 的假名字段规范化并尝试从 `accents.txt` 查找音调，匹配优先使用 `(kanji, reading)` 精确匹配，未命中时按 `kanji` 模糊退路。
  - 当 `kanji` 为空时，增加了基于 `reading` 的回退查找：会使用 `accents.txt` 中首个出现的相同假名的音调（实现路径：`src/core/accents.py`，添加了 `reading_index`），以支持无汉字的行也能补全音调。

## [2026-01-27]
### Added
- 完成 CLI 交互层：实现 `import` 单词导入和 `review` FSRS 复习命令。
- 集成 FSRS 算法并实现 `FSRSEngine` 包装类。
- 实现 `WordImporter` 逻辑，支持按格式解析单词。
- 实现 Repository 模式：`WordRepository` (YAML) 和 `ProgressRepository` (JSON)。
- 定义数据模型：`Word` (单词模型) 和 `SRSProgress` (FSRS 进度模型)。
- 添加核心依赖：`pydantic`, `fsrs`, `typer`, `rich`, `pyyaml`, `pytest`。
 - 创建 `AGENTS.md` 作为项目规格说明书。
 - 完成 `README.md` 的撰写，面向公开开源标准。
 - 在 `AGENTS.md` 中增加项目 TODO List。
### Changed
- 将开发守则 (Development Rules) 移动至 `AGENTS.md` 的最顶端（第 0 节）。
