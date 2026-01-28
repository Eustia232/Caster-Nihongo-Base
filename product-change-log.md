# Product Change Log

## [2026-01-28]
### Added
- 在 `words.yaml` 中新增了 10 个常用日语单词。
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
- 创建 `AGENT.md` 作为项目规格说明书。
- 完成 `README.md` 的撰写，面向公开开源标准。
- 在 `AGENT.md` 中增加项目 TODO List。
### Changed
- 将开发守则 (Development Rules) 移动至 `AGENT.md` 的最顶端（第 0 节）。
