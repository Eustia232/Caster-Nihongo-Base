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

        new_words = importer.process_file(content, start_id)

        if not new_words:
            console.print("[yellow]没有发现可导入的有效单词。[/yellow]")
            return

        # 合并并保存
        all_words = existing_words + new_words

        console.print(f"[green]解析成功！准备导入 {len(new_words)} 个单词。[/green]")

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
        # 如果没有进度或已到期
        if progress is None or progress.due <= now:
            due_words.append((word, progress))

    if not due_words:
        console.print("[bold green]恭喜！目前没有待复习的单词。[/bold green]")
        return

    random.shuffle(due_words)
    total = len(due_words)
    console.print(f"[bold blue]待复习单词数量: {total}[/bold blue]\n")

    count = 0
    for word, progress in due_words:
        count += 1
        console.rule(f"复习中 ({count}/{total})")

        # 显示题目
        console.print(f"\n[bold white]汉字: {word.kanji}[/bold white]")
        console.print(f"[dim]词性: {word.pos}[/dim]\n")

        user_answer = typer.prompt(
            "请输入假名答案 (直接回车跳过)", default="", show_default=False
        )

        # 显示正确答案
        console.print(f"[bold green]正确假名: {word.kana}[/bold green]")
        console.print(f"[bold cyan]释义: {word.meaning}[/bold cyan]\n")

        # 归一化对比 (去除 [n] 或末尾数字格式的音调标记)
        def normalize(s: str) -> str:
            # 去除 [0], [1] 格式
            s = re.sub(r"\[\d+\]", "", s)
            # 去除末尾的单个数字格式 (如 べんきょうする0 -> べんきょうする)
            s = re.sub(r"\d+$", "", s)
            return s.strip()

        if user_answer.strip() == "":
            # 用户选择跳过，设为 Again
            rating = 1
            console.print("[yellow]已跳过，记为错误。[/yellow]")
        elif normalize(user_answer) == normalize(word.kana):
            rating = 3  # Good
            console.print("[bold green]回答正确！[/bold green]")
        else:
            rating = 1  # Again
            console.print(f"[bold red]回答错误。你的输入: {user_answer}[/bold red]")

        # 更新进度
        new_progress = engine.review(progress, rating, now)
        progress_repo.save(word.id, new_progress)

        console.print("[dim]进度已更新。[/dim]\n")

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
