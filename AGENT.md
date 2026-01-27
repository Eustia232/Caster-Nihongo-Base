# Caster-Nihongo-Base 项目规格说明书 (AGENT.md)

## 0. 开发守则 (Development Rules)
1. **身份校验**: 每次回答前必须输出 `elo psy congroo` 以确认上下文未丢失。
2. **变更记录**: 每次代码改动，必须在 `product-change-log.md` 中以追加方式记录内容，禁止覆盖旧内容。
3. **版本控制**: 每次代码改动，必须在 `dev` 分支中进行 git commit。
4. **依赖管理**: 禁止使用 `uv add`，仅允许使用 `uv run`（确保环境纯净，依赖手动维护于 `pyproject.toml`）。

## 1. 核心架构设计 (Architecture)
本项目采用分层架构，确保逻辑层（Service）与表现层（Interface）解耦，支持从 CLI 平滑迁移至 Web 后端（FastAPI + Vue）。

### 1.1 分层说明
- **数据层 (Data Layer)**: 负责 YAML/JSON 文件的持久化读写及 Pydantic 模型定义。
- **服务层 (Service Layer)**: 核心业务逻辑，包括 FSRS 算法封装、导入去重逻辑、复习题型筛选。
- **接口层 (Interface Layer)**: 当前为 CLI 实现（Typer + Rich），未来可扩展为 API 路由。

## 2. 数据模型 (Data Models)

### 2.1 words.yaml (静态词库)
```yaml
- id: 1000
  kanji: "食べる"
  kana: "たべる2"
  meaning: "吃"
  pos: "动词"
```
- **唯一键**: `(kanji, kana)` 组合，用于导入时的严格去重。

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
- **关联**: 使用 `word_id` 作为 Key 关联词库。

## 3. 功能模块 (Workflows)

### 3.1 导入 (Import)
1. 读取 `new.txt` (格式: `汉字|假名+音调|释义|词性`)。
2. 执行严格去重：若 `(kanji, kana)` 已存在则跳过。
3. 自动分配递增唯一 ID（从 1000 开始）。
4. 在 `words.yaml` 追加记录，在 `progress.json` 初始化 FSRS 卡片状态。
5. 操作完成后清空 `new.txt`。

### 3.2 复习 (Review)
- **题型筛选**: 采用共享进度 (1 Word = 1 Card)，每次复习随机抽取以下三种模式之一：
    - **模式 1 (中 -> 汉)**: 显示中文，用户输入汉字。
    - **模式 2 (中 -> 假)**: 显示中文，用户输入假名（含音调数字）。
    - **模式 3 (汉 -> 中)**: 显示汉字，用户自测后输入 `T/F`。
- **判定映射**: 正确或 T 映射为 `Rating.Good`，错误或 F 映射为 `Rating.Again`。
- **辅助显示**: 词性 (pos) 仅在揭晓答案后作为参考展示。

### 3.3 导出 (Export)
- 将 `words.yaml` 导出为 Markdown 表格格式的 `dictionary.md`。

## 4. 目录结构设计 (Directory Structure)
```text
Caster-Nihongo-Base/
├── main.py                # 顶层启动脚本
├── src/
│   ├── core/              # 【服务层】FSRS 封装与核心逻辑
│   ├── data/              # 【数据层】模型定义与持久化接口
│   └── cli/               # 【表现层】Typer 命令与 Rich 交互
├── data_store/            # 【持久化存储】words.yaml, progress.json
├── new.txt                # 录入缓冲文件
└── pyproject.toml         # 依赖配置
```

## 5. 技术栈
- **核心**: Python 3.12+, fsrs, pydantic, pyyaml
- **交互**: typer, rich
- **质量**: ruff, pytest
