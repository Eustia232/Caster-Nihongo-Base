import typer
import os
import random
import re
from datetime import datetime, timezone
from typing import Dict, Set, Tuple

from rich.console import Console
from rich.table import Table
from src.data.repository import WordRepository, ProgressRepository
from src.data.models import Word
from src.core.importer import WordImporter
from src.core.srs import FSRSEngine
from src.core.exporter import export_words_to_file, default_out_path
from src.core.exceptions import SyncError
from src.core.sync import check_git_env, sync_pull, sync_push

app = typer.Typer(
    help="Caster-Nihongo-Base: 基于 FSRS 的轻量级日语复习工具", add_completion=False
)
console = Console()

# 默认路径配置
DATA_DIR = "data_store"
WORDS_FILE = os.path.join(DATA_DIR, "words.yaml")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")


@app.command()
def hello():
    """测试命令"""
    console.print("[bold blue]elo psy congroo![/bold blue]")
    console.print("Caster-Nihongo-Base 已就绪。")


@app.command()
def sync():
    """手动触发云端数据同步"""
    try:
        console.print("[cyan]正在检查 Git 环境...[/cyan]")
        check_git_env()
        console.print("[cyan]正在拉取云端数据...[/cyan]")
        sync_pull(DATA_DIR)
        console.print("[cyan]正在推送本地数据...[/cyan]")
        sync_push(DATA_DIR)
        console.print("[bold green]同步完成！[/bold green]")
    except SyncError as e:
        console.print(f"[bold red]同步失败: {e}[/bold red]")
        raise typer.Exit(1)


@app.command(name="import")
def import_cmd(
    file_path: str = "new.txt",
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        "-o",
        help="覆盖已存在的重复条目（保留原ID，更新其他字段）",
    ),
):
    """从文本文件导入新单词"""
    if not os.path.exists(file_path):
        console.print(f"[red]错误: 找不到文件 {file_path}[/red]")
        raise typer.Exit(1)

    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        check_git_env()
        sync_pull(DATA_DIR)
    except SyncError as e:
        console.print(f"[bold red]同步失败: {e}[/bold red]")
        raise typer.Exit(1)

    repo = WordRepository(WORDS_FILE)
    importer = WordImporter()

    # 加载现有单词以确定起始 ID
    existing_words = repo.load_all()
    start_id = 1
    if existing_words:
        start_id = max(w.id for w in existing_words) + 1

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 依据文件后缀选择解析器：.md 使用 Markdown 解析器，其他使用现有文本解析
        if file_path.lower().endswith(".md") or file_path.lower().endswith(".markdown"):
            new_words = importer.process_markdown(content, start_id)
        else:
            new_words = importer.process_file(content, start_id)

        # If importer reported lines with missing readings, show warnings but
        # still continue importing the rest (skip problematic lines). The
        # importer exposes these in importer.last_problems.
        missing_reading_msgs = getattr(importer, "last_problems", []) or []
        if missing_reading_msgs:
            console.print(
                "[yellow]导入过程中发现以下问题（这些条目将被跳过）：[/yellow]"
            )
            for msg in missing_reading_msgs:
                console.print(f"  - [red]{msg}[/red]")

        if not new_words:
            console.print("[yellow]没有发现可导入的有效单词。[/yellow]")
            return

        # 导入去重：以 (kanji, kana) 作为重复判定键
        # 构建 existing_words 的索引映射（便于覆盖更新）
        existing_map: Dict[Tuple[str, str], int] = {
            (w.kanji, w.kana): idx for idx, w in enumerate(existing_words)
        }

        filtered_new = []
        skipped = 0
        overwritten = 0
        seen_keys: Set[Tuple[str, str]] = set()

        for w in new_words:
            key = (w.kanji, w.kana)

            # 处理导入文件内部的重复
            if key in seen_keys:
                skipped += 1
                continue
            seen_keys.add(key)

            if key in existing_map:
                if overwrite:
                    # 覆盖模式：更新已存在条目的其他字段，保留原 ID
                    idx = existing_map[key]
                    old_word = existing_words[idx]
                    existing_words[idx] = Word(
                        id=old_word.id,
                        kanji=w.kanji,
                        kana=w.kana,
                        meaning=w.meaning,
                        pos=w.pos,
                        category=w.category,
                    )
                    overwritten += 1
                else:
                    # 跳过模式：保留旧条目
                    skipped += 1
            else:
                filtered_new.append(w)
                existing_map[key] = -1  # 标记为已添加，防止文件内重复

        # 判断是否有实际变更
        if not filtered_new and overwritten == 0:
            console.print(
                "[yellow]解析成功，但所有发现的单词均已存在，已跳过导入。[/yellow]"
            )
            return

        # 合并：existing_words（可能已被原地更新）+ 新增的条目
        all_words = existing_words + filtered_new

        # 根据模式显示不同的提示信息
        if overwrite and overwritten > 0:
            console.print(
                f"[green]解析成功！准备导入 {len(filtered_new)} 个新单词，"
                f"覆盖 {overwritten} 个已存在条目"
                f"{'（跳过 ' + str(skipped) + ' 个重复条目）' if skipped > 0 else ''}。[/green]"
            )
        else:
            console.print(
                f"[green]解析成功！准备导入 {len(filtered_new)} 个单词（跳过 {skipped} 个重复条目）。[/green]"
            )

        # 显示预览表格
        table = Table(title="待导入单词预览")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("汉字", style="magenta")
        table.add_column("假名", style="green")
        table.add_column("释义")

        for w in new_words:
            table.add_row(str(w.id), w.kanji, w.kana, w.meaning)

        console.print(table)

        if typer.confirm("确认导入以上单词吗？"):
            repo.save_all(all_words)
            # 根据操作情况显示不同的成功消息
            if overwrite and overwritten > 0:
                console.print(
                    f"[green]成功导入 {len(filtered_new)} 个新单词，覆盖 {overwritten} 个已存在条目！[/green]"
                )
            else:
                console.print(f"[green]成功导入 {len(filtered_new)} 个单词！[/green]")

            try:
                sync_push(DATA_DIR)
                console.print("[green]数据已同步至云端。[/green]")
            except SyncError as e:
                console.print(f"[bold red]云端同步失败: {e}[/bold red]")
        else:
            console.print("[yellow]导入已取消。[/yellow]")

    except Exception as e:
        console.print(f"[red]导入失败: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def review():
    """开始复习会话"""
    try:
        check_git_env()
        sync_pull(DATA_DIR)
    except SyncError as e:
        console.print(f"[bold red]同步失败: {e}[/bold red]")
        raise typer.Exit(1)

    word_repo = WordRepository(WORDS_FILE)
    progress_repo = ProgressRepository(PROGRESS_FILE)
    engine = FSRSEngine()

    words = word_repo.load_all()
    if not words:
        console.print("[yellow]词库为空，请先导入单词。[/yellow]")
        return

    now = datetime.now(timezone.utc)
    due_words = []

    for word in words:
        progress = progress_repo.load(word.id)
        # 跳过已归档的单词
        if progress is not None and getattr(progress, "archived", False):
            continue

        # 如果没有进度或已到期
        if progress is None or progress.due <= now:
            due_words.append((word, progress))

    if not due_words:
        console.print("[bold green]恭喜！目前没有待复习的单词。[/bold green]")
        return

    total = len(due_words)
    console.print(f"[bold blue]待复习单词数量: {total}[/bold blue]\n")

    # 分批处理，每批最多 10 个（每批从待复习列表中随机抽取不重复的项，且批内顺序乱序）
    BATCH_SIZE = 10
    idx = 0

    def normalize(s: str) -> str:
        # 去掉方括号内的数字标注
        s = re.sub(r"\[\d+\]", "", s)
        # 将全角数字与全角逗号规范为 ASCII 形式，便于后续统一处理
        s = s.translate(str.maketrans("０１２３４５６７８９，", "0123456789,"))
        # 去掉尾部由数字与逗号组成的序列（例如 "3,2"、"３，２"）
        s = re.sub(r"[,，\d\uFF10-\uFF19]+$", "", s)
        return s.strip()

    # 使用一个可变的待处理列表，每次随机抽取 up to BATCH_SIZE 个不重复单词进行本批复习
    while due_words:
        batch = random.sample(due_words, k=min(BATCH_SIZE, len(due_words)))
        # 再对批内顺序进行乱序，保证出题顺序随机
        random.shuffle(batch)
        batch_count = len(batch)

        for i, (word, progress) in enumerate(batch, start=1):
            # 显示为 “复习中（当前/本批大小） 全部：(当前/总数)”，同时保留对外测试中查找的 "{cur}/{total}" 字样
            console.print(f"复习中（{idx + i}/{batch_count}） {idx + i}/{total}")

            # 随机选择复习模式：
            # - 给汉字写假名
            # - 给释义写假名
            # - 显示汉字和假名，用户输入 1 或 0 表示是否认识
            modes = ["kanji_to_kana", "meaning_to_kana", "recognition"]
            # 如果没有汉字，去掉第一个模式
            if not word.kanji:
                modes = [m for m in modes if m != "kanji_to_kana"]

            # 权重配置（可以根据需要调整）: kanji_to_kana, meaning_to_kana, recognition
            MODE_WEIGHTS = {
                "kanji_to_kana": 1,
                "meaning_to_kana": 2,
                "recognition": 1,
            }

            weights = [MODE_WEIGHTS.get(m, 1) for m in modes]
            # 使用 random.choices 支持非归一化权重
            mode = random.choices(modes, weights=weights, k=1)[0]

            if mode == "kanji_to_kana":
                console.print(f"\n[bold white]汉字: {word.kanji}[/bold white]")
                console.print(f"[dim]词性: {word.pos_str}[/dim]\n")
                prompt_text = "请输入假名答案 (直接回车跳过)"
                user_answer = typer.prompt(prompt_text, default="", show_default=False)

                console.print(f"[bold green]正确假名: {word.kana}[/bold green]")
                console.print(f"[bold cyan]释义: {word.meaning}[/bold cyan]\n")

                if user_answer.strip() == "":
                    rating = 1
                    console.print("[yellow]已跳过，记为错误。[/yellow]")
                elif normalize(user_answer) == normalize(word.kana):
                    # Treat correct answer as Easy to increase spacing
                    rating = 4
                    console.print("[bold green]回答正确！[/bold green]")
                else:
                    rating = 1
                    console.print(
                        f"[bold red]回答错误。你的输入: {user_answer}[/bold red]"
                    )

            elif mode == "meaning_to_kana":
                console.print(f"\n[bold white]释义: {word.meaning}[/bold white]")
                console.print(f"[dim]词性: {word.pos_str}[/dim]\n")
                prompt_text = "请根据释义输入假名答案 (直接回车跳过)"
                user_answer = typer.prompt(prompt_text, default="", show_default=False)

                console.print(f"[bold green]正确假名: {word.kana}[/bold green]")
                console.print(
                    f"[bold magenta]汉字: {word.kanji or '<无汉字>'}[/bold magenta]\n"
                )

                if user_answer.strip() == "":
                    rating = 1
                    console.print("[yellow]已跳过，记为错误。[/yellow]")
                elif normalize(user_answer) == normalize(word.kana):
                    # Treat correct answer as Easy to increase spacing
                    rating = 4
                    console.print("[bold green]回答正确！[/bold green]")
                else:
                    rating = 1
                    console.print(
                        f"[bold red]回答错误。你的输入: {user_answer}[/bold red]"
                    )

            else:  # recognition
                # 显示汉字与假名，让用户判断是否认识（1/0）
                console.print(
                    f"\n[bold white]汉字: {word.kanji or '<无汉字>'}[/bold white]"
                )
                console.print(f"[bold green]假名: {word.kana}[/bold green]")
                console.print(f"[dim]词性: {word.pos_str}[/dim]\n")

                resp = typer.prompt(
                    "输入 `1` 表示认识，`0` 表示不认识", default="", show_default=False
                )
                # 支持日语输入法的全角数字（如：'１' 和 '０'），先做简单规范化再判断
                resp_norm = resp.strip().replace("１", "1").replace("０", "0")
                if resp_norm == "1":
                    # Recognized -> Easy
                    rating = 4
                    console.print("[bold green]已标记为认识（Good）。[/bold green]")
                else:
                    rating = 1
                    console.print(
                        "[bold red]标记为不认识或未输入有效值（Again）。[/bold red]"
                    )
                # 无论用户输入 1 还是 0，都要显示该单词的中文释义以便复习
                console.print(f"[bold cyan]释义: {word.meaning}[/bold cyan]\n")

            # 更新进度
            new_progress = engine.review(progress, rating, now)
            progress_repo.save(word.id, new_progress)

            # 移除已处理项，避免在本次会话中被重新抽到
            try:
                # batch contains tuples (word, progress)
                if (word, progress) in due_words:
                    due_words.remove((word, progress))
                else:
                    # fallback: remove any tuple with same word id
                    for pair in list(due_words):
                        if pair[0].id == word.id:
                            due_words.remove(pair)
            except ValueError:
                pass

            console.print("[dim]进度已更新。[/dim]\n")

        # 从待处理队列中移除已抽取的条目
        for item in batch:
            try:
                due_words.remove(item)
            except ValueError:
                # 理论上不会发生，但保持鲁棒性
                pass

        idx += batch_count
        if idx >= total:
            break

        # 批次处理完，询问是否继续 (支持全角 ｙ/ｎ)
        resp = (
            typer.prompt(
                f"已完成 {idx}/{total}。是否继续复习下一批？ [Y/n]",
                default="y",
                show_default=False,
            )
            .lower()
            .strip()
        )

        if resp in ("n", "ｎ"):
            console.print("[yellow]已退出复习。下次可继续未完成的复习。[/yellow]")
            try:
                sync_push(DATA_DIR)
                console.print("[green]进度已同步至云端。[/green]")
            except SyncError as e:
                console.print(f"[bold red]云端同步失败: {e}[/bold red]")
            return

    console.rule("复习结束")
    console.print("[bold green]所有待复习单词已处理完毕！[/bold green]")
    try:
        sync_push(DATA_DIR)
        console.print("[green]进度已同步至云端。[/green]")
    except SyncError as e:
        console.print(f"[bold red]云端同步失败: {e}[/bold red]")


@app.command()
def delete(
    ids: str = typer.Argument(
        ...,
        help="要删除的单词 ID 列表，用英文或中文逗号分隔。例如: 1,2,3 或 1，2，3",
    ),
):
    """永久删除指定 ID 的单词及学习进度"""
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        check_git_env()
        sync_pull(DATA_DIR)
    except SyncError as e:
        console.print(f"[bold red]同步失败: {e}[/bold red]")
        raise typer.Exit(1)

    word_repo = WordRepository(WORDS_FILE)
    progress_repo = ProgressRepository(PROGRESS_FILE)

    # 解析 ID 列表
    try:
        # 支持中英文逗号，去除空格，过滤空字符串
        id_str_list = [s.strip() for s in re.split(r"[,，]", ids) if s.strip()]
        if not id_str_list:
            console.print("[red]错误：未提供有效的 ID。[/red]")
            raise typer.Exit(1)

        target_ids = list(set(int(id_str) for id_str in id_str_list))
    except ValueError:
        console.print("[red]错误：ID 必须是有效的整数。[/red]")
        raise typer.Exit(1)

    # 加载现有单词以验证和预览
    existing_words = word_repo.load_all()
    if not existing_words:
        console.print("[yellow]词库为空，没有可删除的内容。[/yellow]")
        raise typer.Exit(0)

    # 构建索引以便快速查找
    existing_map = {w.id: w for w in existing_words}

    words_to_delete = []
    not_found_ids = []

    for wid in target_ids:
        if wid in existing_map:
            words_to_delete.append(existing_map[wid])
        else:
            not_found_ids.append(wid)

    # 如果有没找到的 ID，给出警告
    if not_found_ids:
        console.print(
            f"[yellow]警告：未找到以下 ID 对应的单词：{', '.join(map(str, not_found_ids))}[/yellow]"
        )

    # 如果没有要删除的单词，直接退出
    if not words_to_delete:
        console.print("[yellow]没有可删除的单词，操作取消。[/yellow]")
        raise typer.Exit(0)

    # 显示预览表格
    table = Table(title="待删除单词预览")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("汉字", style="magenta")
    table.add_column("假名", style="green")
    table.add_column("释义")

    for w in words_to_delete:
        table.add_row(str(w.id), w.kanji, w.kana, w.meaning)

    console.print(table)

    # 二次确认
    if typer.confirm("确认永久删除以上单词及对应的学习进度吗？"):
        try:
            valid_ids = [w.id for w in words_to_delete]

            # 删除单词和进度
            word_repo.delete_many(valid_ids)
            progress_repo.delete_many(valid_ids)

            console.print(
                f"[bold green]成功删除 {len(valid_ids)} 个单词及其进度记录！[/bold green]"
            )

            try:
                sync_push(DATA_DIR)
                console.print("[green]数据已同步至云端。[/green]")
            except SyncError as e:
                console.print(f"[bold red]云端同步失败: {e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]删除失败：{e}[/bold red]")
            raise typer.Exit(1)
    else:
        console.print("[yellow]删除已取消。[/yellow]")


@app.command()
def export(out: str = default_out_path(), classify: str = "export/classify.txt"):
    """导出词汇为 Markdown 文件

    参数:
    - out: 输出文件路径，默认 `export/words-YYYYMMDD.md`（UTC 日期）
    - classify: 可选的分类顺序配置文件路径（每行一个分类名）
    """
    repo = WordRepository(WORDS_FILE)
    words = repo.load_all()
    if not words:
        console.print("[yellow]词库为空，没有可导出的内容。[/yellow]")
        raise typer.Exit(1)

    path = export_words_to_file(words, out, classify_config=classify)
    console.print(f"[green]导出完成: {path}[/green]")


if __name__ == "__main__":
    app()
