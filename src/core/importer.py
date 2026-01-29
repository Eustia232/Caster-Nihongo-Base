from typing import List, Dict, Optional, Union, Any, Tuple
import re
from src.data.models import Word
from src.core.accents import fill_pitch_for_content


class WordImporter:
    """处理单词导入逻辑"""

    def parse_line(self, line: str, word_id: int) -> Word:
        """
        解析单行文本为 Word 对象
        格式: 汉字|假名+音调|释义|词性
        """
        line = line.strip()
        if not line:
            raise ValueError("Empty line")

        parts = [p.strip() for p in line.split("|")]
        if len(parts) not in (4, 5):
            raise ValueError(
                f"格式错误，应为 '汉字|假名+音调|释义|词性' 或加上可选 'category': {line}"
            )

        category = None
        if len(parts) == 5:
            category = parts[4] if parts[4] != "" else None

        return Word(
            id=word_id,
            kanji=parts[0],
            kana=parts[1],
            meaning=parts[2],
            pos=parts[3],
            category=category,
        )

    def process_file(self, content: str, start_id: int) -> List[Word]:
        """批量处理文件内容"""
        # 自动补全音调：使用 accents.txt（仓库根目录）
        try:
            content = fill_pitch_for_content(content, "accents.txt")
        except Exception:
            # 如果填充失败，回退到原始内容并继续解析
            pass
        words = []
        current_id = start_id
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            words.append(self.parse_line(line, current_id))
            current_id += 1
        return words

    def process_markdown(self, content: str, start_id: int) -> List[Word]:
        """解析由 exporter.generate_markdown 导出的 Markdown 表格格式。

        预期格式（节选）:
        词汇表

        | 汉字 | 假名 | 释义 |
        |---|---|---|
        | **pos / category** |  |  |
        | kanji | kana | meaning |

        返回值为 Word 列表，按表格顺序分配连续 id，从 start_id 开始。
        """
        lines = content.splitlines()
        # 找到表格 header 的起始行 (包含 汉字 假名 释义)
        table_start = None
        header_re = re.compile(r"^\|\s*汉字\s*\|\s*假名\s*\|\s*释义\s*\|$")
        for i, ln in enumerate(lines):
            if header_re.match(ln.strip()):
                table_start = i
                break

        if table_start is None:
            # 兼容性：如果没找到表头，返回空列表
            return []

        # 主体从表头下一行开始（跳过分隔行）
        idx = table_start + 2
        current_id = start_id
        words: List[Word] = []

        # 正则：分类行 | **分类名** |  |  |
        class_re = re.compile(r"^\|\s*\*\*(?P<cls>.+?)\*\*\s*\|\s*\|\s*\|\s*$")
        # 单词行：| kanji | kana | meaning |
        word_re = re.compile(
            r"^\|\s*(?P<kanji>.*?)\s*\|\s*(?P<kana>.*?)\s*\|\s*(?P<meaning>.*?)\s*\|\s*$"
        )

        current_pos: Optional[str] = None
        current_category: Optional[str] = None

        def unescape_cell(s: str) -> str:
            if s is None:
                return ""
            # 反转义导出时的转义：\| -> | ; <br> -> \n
            return s.replace("\\|", "|").replace("<br>", "\n").strip()

        while idx < len(lines):
            ln = lines[idx].rstrip()  # 保留前导空格已在正则中处理
            idx += 1
            if not ln.strip():
                continue

            mcls = class_re.match(ln)
            if mcls:
                cls = mcls.group("cls").strip()
                if " / " in cls:
                    pos, cat = [p.strip() for p in cls.split("/", 1)]
                    current_pos = pos
                    current_category = cat
                else:
                    current_pos = cls
                    current_category = None
                continue

            mw = word_re.match(ln)
            if mw:
                kanji = unescape_cell(mw.group("kanji"))
                kana = unescape_cell(mw.group("kana"))
                meaning = unescape_cell(mw.group("meaning"))

                # 如果当前分类未设置，尝试从单元格中识别（若导出不规范）
                pos = current_pos or ""
                category = current_category

                words.append(
                    Word(
                        id=current_id,
                        kanji=kanji,
                        kana=kana,
                        meaning=meaning,
                        pos=pos,
                        category=category,
                    )
                )
                current_id += 1
                continue

            # 非法行：忽略

        return words
