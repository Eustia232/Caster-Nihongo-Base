# Product Change Log

## [2026-02-02]
### Changed
- 将 FSRS 最小强制下次复习间隔从 1 天改为 17 小时，并改为对所有复习评分均生效（无论答对或答错）。
  - 变更位置：`src/core/srs.py`
  - 说明：原实现仅在 `rating >= 3` 时将 `due` 至少设为 `review_time + 1 day`，导致答错时可能不会触发最小间隔限制。此项修改把最小间隔统一为 17 小时并对所有评分生效，以避免短时间内重复出题。自动归档（连续 6 次正确）逻辑保持不变。


## [2026-01-29]
### Fixed
- 修复：使 `load_accents` 更加鲁棒，支持 accents.txt 中仅包含假名/无汉字的行并对假名进行规范化（去掉尾部占位数字与方括号），以保证在导入时能为无汉字条目正确补上音调。
  - 变更位置：`src/core/accents.py`（改进解析逻辑、增加假名检测与规范化），`src/core/importer.py`（保留调用点，兼容新加载逻辑）。
  - 说明：此前当行没有汉字时，载入的索引未使用与查找时一致的规范化 key，导致 reading-only 查询失败；本次修复统一了规范化流程并容错两列/三列格式。

### Added
- 新增复习模式随机选择功能：在 `review` 命令中每次随机从三种模式中选一项进行出题（给汉字写假名 / 给释义写假名 / 给汉字和假名让用户输入 1/0 表示是否认识），当条目无汉字时会自动移除“给汉字写假名”模式以避免不可用题型。
  - 变更位置：`src/cli/main.py`
  - 说明：简化了交互流程并增加轮换题型，以提高复习多样性；原来的直接以汉字出题仍保留为一种可能模式。

### Fixed
- 修复：在 `review` 命令的“认识判断”题型中，支持日语输入法下的全角数字输入（`１` / `０`），会在内部规范化为 ASCII 数字后再判定用户是否认识。
  - 变更位置：`src/cli/main.py`
  - 说明：之前只有 ASCII 的 `1`/`0` 被识别，使用日语输入法时用户输入全角数字会被误判为无效输入。本次修复将全角数字 `１`/`０` 替换为 `1`/`0`，保持与其它输入一致的体验。

### Changed
- 在 `review` 命令的“认识判断”题型中，改为无论用户输入 `1` 还是 `0` 都显示该单词的中文释义，方便用户在判断认识与否时复核释义。
  - 变更位置：`src/cli/main.py`
  - 说明：提高复习时的上下文信息，特别是在用户仅需判断是否认识时仍能看到释义以加深记忆。

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

## [2026-01-30]
### Added
- 在 `new.txt` 中添加了 9 个常用动词条目：`引く`, `切る`, `入る`, `持つ`, `乗る`, `出す`, `取る`, `歌う`, `思う`（均为四字段格式，UTF-8 编码）。
  - 变更位置：仓库根目录的 `new.txt`
  - 说明：这些条目遵循 `NEW_TXT_SPEC.md` 中的 `kanji | kana | meaning | pos` 格式，便于后续运行 `uv run main.py import` 导入。

  - 更新：对新增词条的释义进行了精简，去除近义重复（例如保留 `歌う` 的“唱歌”，移除重复的“演唱/歌颂”）；保留含义差异较大的多个义项（例如 `引く` 同时保留“拉”与“染上/患病”）。

### Changed
- 小改动：将复习时标题样式从 `----复习中----` 更改为 `复习中-----`，以满足显示偏好。
  - 变更位置：`src/cli/main.py`
  - 说明：现在标题显示为 `复习中（当前/批次大小）`，总数显示为当前处理批次的大小（例如每批最多 10 个则显示 10）。

### Fixed
- 修复：在复习答案比对时，对假名答案的归一化改进，去除尾部的音调数字/逗号序列并规范全角数字为 ASCII（例如将 `スイッチ3,2` 归一为 `スイッチ`），从而避免含多音调后缀时用户只输入假名就被误判为错误。
  - 变更位置：`src/cli/main.py`
  
### Added
- 新增：在 `new.txt` 中添加了 7 个常用词条：`誕生日`, `新幹線`, `飛行機`, `タクシー` (无汉字), `卵`, `野球`, 以及已存在的 `スイッチ` 的无汉字条目保留。
  - 变更位置：仓库根目录的 `new.txt`
  - 说明：这些条目为导入准备，遵循 `new.txt` 规范（四字段，UTF-8）。
### Added
- 新增：在 `new.txt` 中添加了以下词条：`まっすく`（拼写由用户提供，假名形式），`ケーキ`, `サッカー`, `手紙`, `映画`, `パンダ`, `角`, `来年`, `三つ`, `ほか`, `お酒`, `階段`。
  - 变更位置：仓库根目录的 `new.txt`
  - 说明：这些条目已添加为待导入内容，部分为仅假名条目（汉字字段留空），均遵循 `new.txt` 的四字段格式。
### Changed
- 复习抽题逻辑更新：在获取到所有待复习单词后，每次从待复习列表中随机抽取最多 10 个单词作为一批（使用 `random.sample`），并对批内顺序再 `random.shuffle` 一次，保证每次出题的选取与顺序都是随机的。
  - 变更位置：`src/cli/main.py`
  - 说明：原先按列表分片依序出题；现在每批都是随机抽取且批内乱序，避免固定顺序带来的模式化记忆。新增移除已抽取条目的逻辑以确保不重复出题。

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
