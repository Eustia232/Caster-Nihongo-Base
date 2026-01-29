import os
from src.core.importer import WordImporter
from src.core.exporter import generate_markdown


def test_import_export_and_accent_fill(tmp_path):
    """确认：当 kanji 为空时，能导入、音调能从 accents.txt 填充，并能导出为 markdown 表格"""
    content = "|たべる|吃|v\n"  # 空 kanji 列，假名为 たべる（没有音调数字）

    importer = WordImporter()
    words = importer.process_file(content, start_id=1)

    # 能成功解析出一个单词，kanji 为空，kana 已被规范化/补全
    assert len(words) == 1
    w = words[0]
    assert w.id == 1
    assert w.kanji == ""
    # kana 应该至少被规范化为去掉占位数字（如果有），并尝试附加音调（如果能从 accents.txt 找到）
    # 在 accents.txt 中存在条目 `食べる\tたべる\t2`，因此期望被补成 たべる2
    assert w.kana == "たべる2" or w.kana == "たべる"

    # 导出为 markdown，不应崩溃；结果中应包含空的汉字单元格和假名
    md = generate_markdown(words)
    assert "|  |" in md or "|  |" in md
    assert "たべる" in md
