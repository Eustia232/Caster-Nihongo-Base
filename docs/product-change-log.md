# Product Change Log

## 2026-08-18
- fix: 修复复习时带词性标注的假名（如 `だいじ(名)1,3,(形動)0,3`）无法匹配用户输入的问题。将 `normalize` 和 `extract_readings` 提取为模块级函数 `normalize_kana` / `extract_readings`，增加去除圆括号词性标注的逻辑，支持半角/全角括号及复合词性标注。新增 23 个单元测试覆盖各种匹配场景。

## 2026-04-17
- fix: 调整 CLI 单元测试，统一 mock `check_git_env/sync_pull/sync_push`，避免测试环境被 Git 同步前置校验阻断。
- feat: 实现基于 Git 的数据同步机制，将 `data_store/` 目录的复习进度与词库推送到远程仓库。
- feat: 新增 `sync` 手动同步命令，并在 `import`, `review`, `delete` 等操作前后自动注入云端同步埋点。
- feat: 添加对无网络或合并冲突的异常防御 (`SyncError`)，并在触发失败时立刻中断或给与提示。
