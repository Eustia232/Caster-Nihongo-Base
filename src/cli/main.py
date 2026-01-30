import typer
import os
import random
import re
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from src.data.repository import WordRepository, ProgressRepository
from src.core.importer import WordImporter
from src.core.srs import FSRSEngine
from src.core.exporter import export_words_to_file, default_out_path

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


@app.command(name="import")
def import_cmd(file_path: str = "new.txt"):
    """从文本文件导入新单词"""
    if not os.path.exists(file_path):
        console.print(f"[red]错误: 找不到文件 {file_path}[/red]")
        raise typer.Exit(1)

    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

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

        if not new_words:
            console.print("[yellow]没有发现可导入的有效单词。[/yellow]")
            return

        # 导入去重：以 (kanji, kana) 作为重复判定键，优先保留已存在的条目
        existing_keys = set((w.kanji, w.kana) for w in existing_words)
        filtered_new = []
        skipped = 0
        for w in new_words:
            key = (w.kanji, w.kana)
            if key in existing_keys:
                skipped += 1
                continue
            filtered_new.append(w)
            existing_keys.add(key)

        if not filtered_new:
            console.print(
                "[yellow]解析成功，但所有发现的单词均已存在，已跳过导入。[/yellow]"
            )
            return

        # 合并并保存（保留 existing_words 的优先权）
        all_words = existing_words + filtered_new

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
            console.print(f"[green]成功导入 {len(new_words)} 个单词！[/green]")
        else:
            console.print("[yellow]导入已取消。[/yellow]")

    except Exception as e:
        console.print(f"[red]导入失败: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def review():
    """开始复习会话"""
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

    random.shuffle(due_words)
    total = len(due_words)
    console.print(f"[bold blue]待复习单词数量: {total}[/bold blue]\n")

    # 分批处理，每批最多 10 个
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

    while idx < total:
        batch = due_words[idx : idx + BATCH_SIZE]
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
                console.print(f"[dim]词性: {word.pos}[/dim]\n")
                prompt_text = "请输入假名答案 (直接回车跳过)"
                user_answer = typer.prompt(prompt_text, default="", show_default=False)

                console.print(f"[bold green]正确假名: {word.kana}[/bold green]")
                console.print(f"[bold cyan]释义: {word.meaning}[/bold cyan]\n")

                if user_answer.strip() == "":
                    rating = 1
                    console.print("[yellow]已跳过，记为错误。[/yellow]")
                elif normalize(user_answer) == normalize(word.kana):
                    rating = 3
                    console.print("[bold green]回答正确！[/bold green]")
                else:
                    rating = 1
                    console.print(
                        f"[bold red]回答错误。你的输入: {user_answer}[/bold red]"
                    )

            elif mode == "meaning_to_kana":
                console.print(f"\n[bold white]释义: {word.meaning}[/bold white]")
                console.print(f"[dim]词性: {word.pos}[/dim]\n")
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
                    rating = 3
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
                console.print(f"[dim]词性: {word.pos}[/dim]\n")

                resp = typer.prompt(
                    "输入 `1` 表示认识，`0` 表示不认识", default="", show_default=False
                )
                # 支持日语输入法的全角数字（如：'１' 和 '０'），先做简单规范化再判断
                resp_norm = resp.strip().replace("１", "1").replace("０", "0")
                if resp_norm == "1":
                    rating = 3
                    console.print("[bold green]已标记为认识（Good）。[/bold green]")
                else:
                    rating = 1
                    console.print(
                        "[bold red]标记为不认识或未输入有效值（Again）。[/bold red]"
                    )

            # 更新进度
            new_progress = engine.review(progress, rating, now)
            progress_repo.save(word.id, new_progress)

            console.print("[dim]进度已更新。[/dim]\n")

        idx += batch_count

        if idx >= total:
            break

        # 批次处理完，询问是否继续
        if not typer.confirm(
            f"已完成 {idx}/{total}。是否继续复习下一批？", default=True
        ):
            console.print("[yellow]已退出复习。下次可继续未完成的复习。[/yellow]")
            return

    console.rule("复习结束")
    console.print("[bold green]所有待复习单词已处理完毕！[/bold green]")


if __name__ == "__main__":
    app()


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
