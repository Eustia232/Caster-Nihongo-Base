# Product Change Log

## 2026-11-11
- docs: `NEW_TXT_SPEC.md` 新增自包含声明：参考该规范编写、校验或导入 `new.txt` 时无需阅读仓库源代码。
- data: `new.txt` 按 `NEW_TXT_SPEC.md` 整文件更新 13 词：掛ける、消える、寝る、晴れる、見せる、締める、並べる、開ける、もちろん、少し、大勢、少しも、だんだん。其中 開ける 已在词库（id 259），导入时将自动跳过，实际新增 12 词；导入由用户手动执行 `import.bat`。

## 2026-11-05
- docs: 新增日语近义词语辨析手册 `docs/vocab-synonyms.md`，覆盖 `words.yaml` 全部 466 词：按语义场分为动词 56 组、名词 40 组、形容词/形容动词 15 组、副词 6 组、同音异义词 15 组、自他动词对照表、N5 词库外对比 35 组，每组含核心区别要点与双语例句；文末附全词索引（按五十音顺，标注所在小节）与 13 个无近义对照词的附录。

## 2026-08-18
- data: 将词汇例句集审核结果同步回 `data_store/words.yaml`，更新 204 条单词的 meaning 字段（补充常见义项、修正不准确释义），kanji/kana/pos/category 及新增词条均未改动。
- docs: 生成日语词汇例句集 `docs/vocab-examples.md`，覆盖全部 332 词，每个常见释义配双语对照例句（N5-N4 级别），同时审核修正释义 173 处。
- fix: 修复复习时带词性标注的假名（如 `だいじ(名)1,3,(形動)0,3`）无法匹配用户输入的问题。将 `normalize` 和 `extract_readings` 提取为模块级函数 `normalize_kana` / `extract_readings`，增加去除圆括号词性标注的逻辑，支持半角/全角括号及复合词性标注。新增 23 个单元测试覆盖各种匹配场景。

## 2026-04-17
- fix: 调整 CLI 单元测试，统一 mock `check_git_env/sync_pull/sync_push`，避免测试环境被 Git 同步前置校验阻断。
- feat: 实现基于 Git 的数据同步机制，将 `data_store/` 目录的复习进度与词库推送到远程仓库。
- feat: 新增 `sync` 手动同步命令，并在 `import`, `review`, `delete` 等操作前后自动注入云端同步埋点。
- feat: 添加对无网络或合并冲突的异常防御 (`SyncError`)，并在触发失败时立刻中断或给与提示。
