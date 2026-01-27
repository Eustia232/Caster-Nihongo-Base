import os
import yaml
from typing import List, Dict, Optional, Union, Any, Tuple
from src.data.models import Word


class WordRepository:
    """管理单词数据的 YAML 持久化层"""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_all(self) -> List[Word]:
        """从 YAML 文件加载所有单词"""
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f) or []
                return [Word(**item) for item in data]
            except Exception:
                return []
