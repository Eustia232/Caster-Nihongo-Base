from datetime import datetime
from typing import List, Dict, Optional, Union, Any, Tuple
from pydantic import BaseModel, Field, field_validator


ALLOWED_POS = [
    "名词", "名词サ变",
    "动词1", "动词5",
    "自动词", "他动词",
    "形容词", "形容动词", "副词",
]


class Word(BaseModel):
    id: int = Field(..., description="单词唯一标识 ID")
    kanji: str = Field(..., description="日文汉字")
    kana: str = Field(..., description="假名（含音调，如：たべる2）")
    meaning: str = Field(..., description="中文释义")
    pos: List[str] = Field(..., description="词性列表")
    category: Optional[str] = Field(
        None, description="可选：单词分类，例如 JLPT 等级或主题"
    )

    @field_validator("pos", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    @field_validator("pos")
    @classmethod
    def validate_pos_values(cls, v):
        for item in v:
            if item not in ALLOWED_POS:
                raise ValueError(
                    f"非法词性 '{item}'，允许值: {', '.join(ALLOWED_POS)}"
                )
        return v

    @property
    def pos_str(self) -> str:
        return "、".join(self.pos)


class SRSProgress(BaseModel):
    stability: float = Field(..., description="记忆稳定性")
    difficulty: float = Field(..., description="难度系数")
    due: datetime = Field(..., description="下次复习时间")
    last_review: Optional[datetime] = Field(None, description="上次复习时间")
    # Current step within a learning/relearning sequence (e.g. 0,1,...).
    # FSRS expects a non-None `step` when state == Relearning; make this
    # optional here so older progress records remain compatible.
    step: Optional[int] = Field(None, description="学习/再学习步骤索引，可选")
    state: int = Field(
        ..., description="FSRS 状态 (0:New, 1:Learning, 2:Review, 3:Relearning)"
    )
    consecutive_successes: int = Field(0, description="连续正确次数，用于自动归档判断")
    archived: bool = Field(False, description="是否已归档（永不复习）")
    archived_at: Optional[datetime] = Field(None, description="归档时间，可选")
    archived_reason: Optional[str] = Field(
        None, description="归档原因，例如 'auto:6_consecutive' or 'manual'"
    )
