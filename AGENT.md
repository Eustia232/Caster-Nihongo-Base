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

## 6. 项目 TODO List (Roadmap)

### 第一阶段：基础设施 (Phase 1: Infrastructure) - [ ]
- [ ] 1.1 定义 Pydantic 数据模型 (`src/data/models.py`)
- [ ] 1.2 实现 YAML/JSON 仓储访问层 (`src/data/repository.py`)
- [ ] 1.3 编写仓储层单元测试 (`tests/test_data/`)

### 第二阶段：核心逻辑 (Phase 2: Core Logic) - [ ]
- [ ] 2.1 封装 FSRS 算法引擎 (`src/core/fsrs_engine.py`)
- [ ] 2.2 实现单词导入服务，含去重逻辑 (`src/core/logic.py`)
- [ ] 2.3 实现复习筛选与三种随机题型逻辑 (`src/core/logic.py`)

### 第三阶段：表现层开发 (Phase 3: Interface) - [ ]
- [ ] 3.1 搭建 Typer CLI 基础框架 (`src/cli/main.py`)
- [ ] 3.2 实现 `import` 命令交互
- [ ] 3.3 实现 `review` 命令交互（含 Rich 渲染）
- [ ] 3.4 实现 `export` 命令导出 Markdown

### 第四阶段：集成与交付 (Phase 4: Integration) - [ ]
- [ ] 4.1 编写顶层入口 `main.py`
- [ ] 4.2 进行全流程冒烟测试
- [ ] 4.3 完善文档与使用说明
