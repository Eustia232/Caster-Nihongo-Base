# Caster-Nihongo-Base

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Caster-Nihongo-Base 是一个专为日语学习者设计的轻量级命令行（CLI）复习工具。它基于先进的 **FSRS (Free Spaced Repetition Scheduler)** 算法，旨在通过高效的科学复习法帮助用户牢固记忆日语单词。

## ✨ 核心特性

- 🧠 **科学复习**: 集成 FSRS 算法，比传统艾宾浩斯遗忘曲线更精准地预测你的记忆状态。
- 🎲 **多维度测试**: 
  - **中 -> 汉**: 根据中文释义拼写日文汉字。
  - **中 -> 假**: 根据中文释义拼写假名（含音调校验）。
  - **汉 -> 中**: 识别日文汉字并自我检测释义。
- 📂 **轻量存储**: 纯文本 YAML/JSON 存储方案，方便备份、版本控制及手动编辑。
- 🚀 **极致简洁**: 专为 Bash/终端爱好者设计，极简交互，单键反馈。
- 🛠️ **可扩展性**: 采用解耦的分层架构，支持未来轻松迁移至 Web 后端（FastAPI + Vue）。

## 🛠️ 安装与运行

本工具推荐使用 [uv](https://github.com/astral-sh/uv) 进行环境管理。

### 1. 克隆仓库
```bash
git clone https://github.com/your-repo/Caster-Nihongo-Base.git
cd Caster-Nihongo-Base
```

### 2. 导入新词
在 `new.txt` 中按以下格式填入单词：
`汉字|假名+音调|释义|词性`
例如：`勉強する|べんきょうする0|学习|动词`

执行导入命令：
```bash
uv run main.py import
```

### 3. 开始复习
```bash
uv run main.py review
```

## 📂 项目结构

- `src/core/`: FSRS 算法核心与业务逻辑。
- `src/data/`: 数据模型与持久化层。
- `src/cli/`: 基于 Typer 和 Rich 的美化终端界面。
- `data_store/`: 你的个人词库与进度存档。

## 📝 路线图

- [ ] 实现基础 CLI 导入与复习功能
- [ ] 支持词库导出为 Markdown 词典
- [ ] 接入 FastAPI 构建 RESTful API
- [ ] 开发 Vue.js 网页版前端

## 📄 开源协议

本项目采用 MIT 协议开源。
