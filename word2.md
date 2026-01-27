# Caster-Nihongo-Base 项目规划 (FSRS版)

## 1. 核心架构与逻辑
- **算法**: 使用 **FSRS (Free Spaced Repetition Scheduler)**。
- **反馈模式**: 二进制反馈 (Binary Review)。
  - **正确 (Correct)**: 映射至 FSRS 的 `Rating.Good` (3)。
  - **错误 (Incorrect)**: 映射至 FSRS 的 `Rating.Again` (1)。
- **扩展性**: 逻辑层、数据层、界面层分离，支持未来转为 FastAPI + Vue 架构。

## 2. 数据存储 (Data Storage)
- **words.yaml**: 核心词库（手动录入的持久化结果）。
  ```yaml
  - id: 1001
    kanji: "食べる"
    kana: "たべる2"
    meaning: "吃"
    pos: "动词"
  ```
- **progress.json**: 进度数据库。存储每个 ID 对应的 FSRS 卡片状态。
  - 关键字段: `stability`, `difficulty`, `elapsed_days`, `scheduled_days`, `last_review`, `state`。
- **new.txt**: 批量录入缓冲文件。
  - 格式: `汉字|假名+音调|释义|词性`
  - 示例: `勉強する|べんきょうする0|学习|动词`

## 3. 核心功能模块
### 3.1 `import` 模块
- 解析 `new.txt` 中的 `A` 方案格式。
- 检查重复，生成唯一 ID（1000起）。
- 在 `words.yaml` 追加词条。
- 在 `progress.json` 中调用 `fsrs` 库初始化 `Card` 对象。
- 清空 `new.txt`。

### 3.2 `review` 模块
- 调用 `fsrs` 库计算当前应复习的卡片。
- **交互流程**:
  1. 显示汉字。
  2. 用户按任意键显示假名（含音调）、释义、词性。
  3. 用户选择：`[y] 认识 / [n] 不认识`。
  4. 根据 FSRS 计算 `next_state` 并保存至 `progress.json`。

### 3.3 `export` 模块
- 将 `words.yaml` 导出为 `dictionary.md`。
- 包含列：ID、汉字、假名、释义、词性。

## 4. 技术栈依赖
- `fsrs`: 核心算法库。
- `pydantic`: 数据验证与模型管理。
- `pyyaml`: YAML 读写。
- `rich`: 终端美化与交互。
- `typer`: CLI 命令行构建。

## 5. 项目目录结构建议
```text
caster-nihongo/
├── main.py            # CLI 入口
├── core/
│   ├── srs.py         # FSRS 封装逻辑
│   └── models.py      # Pydantic 数据模型
├── data/
│   ├── storage.py     # YAML/JSON 读写封装
│   ├── words.yaml     # 词库 (自动生成)
│   └── progress.json  # 进度 (自动生成)
├── new.txt            # 录入文件 (手动维护)
├── word2.md           # 本规则文件
└── pyproject.toml     # 依赖管理
```
