# Caster-Nihongo-Base 项目设计规范 (Part 1)

## 1. 核心架构设计 (Architecture)
本项目采用分层架构，确保逻辑层（Service）与表现层（Interface）解耦，为未来从 CLI 迁移至 Web 后端（FastAPI + Vue）打下基础。

### 1.1 分层说明
- **数据层 (Data Layer)**: 负责 YAML/JSON 文件的持久化读写。
- **服务层 (Service Layer)**: 包含 FSRS 算法逻辑、单词导入去重逻辑、复习筛选逻辑。该层不包含任何 `print` 或 `input`，只处理数据模型。
- **接口层 (Interface Layer)**: 当前为 CLI 实现，使用 `Typer` 处理命令行交互，使用 `Rich` 渲染终端界面。

## 2. 数据模型 (Data Models)

### 2.1 words.yaml (静态词库)
```yaml
- id: 1000
  kanji: "食べる"
  kana: "たべる2"
  meaning: "吃"
  pos: "动词"
```
- **去重规则**: 基于 `(kanji, kana)` 组合进行严格去重。

### 2.2 progress.json (FSRS 进度)
```json
{
  "1000": {
    "stability": 0.0,
    "difficulty": 0.0,
    "elapsed_days": 0,
    "scheduled_days": 0,
    "last_review": "2023-10-27T10:00:00",
    "state": 0
  }
}
```
- **关联方式**: 使用 `word_id` 作为键值，与 `words.yaml` 关联。

## 4. 复习模式与交互逻辑 (Review & Interaction)

### 4.1 随机混合模式 (Random Mix)
系统采用共享 FSRS 进度 (1 Word = 1 Card) 的策略。每次复习时，系统会从以下三种题型中随机抽取一种。

### 4.2 题型定义
1.  **模式 1 (中 -> 汉)**:
    - **出题**: 显示 `meaning` 字段。
    - **回答**: 用户输入 `kanji`。
    - **判定**: 字符串完全匹配即为正确 (Rating.Good)，否则为错误 (Rating.Again)。
2.  **模式 2 (中 -> 假)**:
    - **出题**: 显示 `meaning` 字段。
    - **回答**: 用户输入 `kana`。
    - **判定**: 字符串完全匹配（需包含音调数字，如 `たべる2`）即为正确 (Rating.Good)，否则为错误 (Rating.Again)。
3.  **模式 3 (汉 -> 中)**:
    - **出题**: 显示 `kanji` 字段。
    - **流程**: 用户按任意键显示 `meaning` 和 `kana` 后，自行判断是否正确。
    - **回答**: 用户输入 `T` (认识) 或 `F` (不认识)。
    - **判定**: `T` 对应 Rating.Good，`F` 对应 Rating.Again。

### 4.3 辅助信息展示 (POS)
- 在所有模式中，**词性 (pos)** 仅在答案揭晓阶段作为辅助参考信息展示，不在出题阶段提供提示。

### 5. 项目目录结构设计 (Directory Structure)

```text
Caster-Nihongo-Base/
├── main.py                # 顶层启动脚本 (入口)
├── src/
│   ├── core/              # 【服务层】核心业务逻辑
│   │   ├── fsrs_engine.py # FSRS 算法封装
│   │   └── logic.py       # 导入去重、复习筛选逻辑
│   ├── data/              # 【数据层】模型与持久化
│   │   ├── models.py      # Pydantic 数据模型 (Word, Card)
│   │   └── repository.py  # YAML/JSON 的读写实现
│   └── cli/               # 【表现层】CLI 交互
│       ├── main.py        # Typer 命令行定义
│       └── ui_utils.py    # Rich 界面美化工具
├── data_store/            # 【持久化存储】
│   ├── words.yaml         # 静态词库 (自动生成/维护)
│   └── progress.json      # SRS 进度 (自动生成/维护)
├── new.txt                # 录入缓冲文件 (用户手动填写)
└── pyproject.toml         # 依赖配置
```

## 6. 技术栈依赖建议

### 核心依赖
- **fsrs**: 实现 Spaced Repetition 算法的核心。
- **pydantic**: 用于定义严谨的数据模型。
- **pyyaml**: 处理 `words.yaml` 的读写。
- **typer**: 构建功能强大的命令行接口。
- **rich**: 提升终端的交互视觉体验。

### 开发依赖
- **ruff**: 代码格式化与 Lint。
- **pytest**: 单元测试，确保 FSRS 逻辑正确。
