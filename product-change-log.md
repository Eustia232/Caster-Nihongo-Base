# Product Change Log

## [2026-01-27]
### Added
- 完成 CLI 交互层：实现 `import` 单词导入和 `review` FSRS 复习命令。
- 集成 FSRS 算法并实现 `FSRSEngine` 包装类。
- 实现 `WordImporter` 逻辑，支持按格式解析单词。
- 实现 Repository 模式：`WordRepository` (YAML) 和 `ProgressRepository` (JSON)。
- 定义数据模型：`Word` (单词模型) 和 `SRSProgress` (FSRS 进度模型)。
- 添加核心依赖：`pydantic`, `fsrs`, `typer`, `rich`, `pyyaml`, `pytest`。
- 创建 `AGENT.md` 作为项目规格说明书。
- 完成 `README.md` 的撰写，面向公开开源标准。
- 在 `AGENT.md` 中增加项目 TODO List。
### Changed
- 将开发守则 (Development Rules) 移动至 `AGENT.md` 的最顶端（第 0 节）。
