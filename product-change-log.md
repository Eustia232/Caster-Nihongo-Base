# Product Change Log

## [2026-01-28]
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
