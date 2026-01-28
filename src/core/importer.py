from typing import List, Dict, Optional, Union, Any, Tuple
from src.data.models import Word


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

        parts = line.split("|")
        if len(parts) != 4:
            raise ValueError(f"格式错误，应为 '汉字|假名+音调|释义|词性': {line}")

        return Word(
            id=word_id,
            kanji=parts[0],
            kana=parts[1],
            meaning=parts[2],
            pos=parts[3],
            category=None,
        )

    def process_file(self, content: str, start_id: int) -> List[Word]:
        """批量处理文件内容"""
        words = []
        current_id = start_id
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            words.append(self.parse_line(line, current_id))
            current_id += 1
        return words
