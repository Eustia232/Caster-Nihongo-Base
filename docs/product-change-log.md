# Product Change Log

## 2026-04-17
- fix: 调整 CLI 单元测试，统一 mock `check_git_env/sync_pull/sync_push`，避免测试环境被 Git 同步前置校验阻断。
- feat: 实现基于 Git 的数据同步机制，将 `data_store/` 目录的复习进度与词库推送到远程仓库。
- feat: 新增 `sync` 手动同步命令，并在 `import`, `review`, `delete` 等操作前后自动注入云端同步埋点。
- feat: 添加对无网络或合并冲突的异常防御 (`SyncError`)，并在触发失败时立刻中断或给与提示。
