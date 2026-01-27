import os
import yaml
import json
from datetime import datetime
from typing import List, Dict, Optional, Union, Any, Tuple
from src.data.models import Word, SRSProgress


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


class ProgressRepository:
    """管理 SRS 进度的 JSON 持久化层"""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def _load_all_raw(self) -> Dict[str, Any]:
        """加载原始 JSON 数据"""
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}

    def load(self, word_id: int) -> Optional[SRSProgress]:
        """加载特定单词的进度"""
        data = self._load_all_raw()
        item = data.get(str(word_id))
        if not item:
            return None
        return SRSProgress(**item)

    def save(self, word_id: int, progress: SRSProgress):
        """保存单词的进度"""
        data = self._load_all_raw()
        # model_dump() 默认不会将 datetime 转换为 iso 字符串，
        # 但 Pydantic 的 model_dump(mode="json") 可以处理，或者我们手动处理。
        # 为了兼容性，我们使用 model_dump(mode="json")。
        data[str(word_id)] = progress.model_dump(mode="json")

        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
