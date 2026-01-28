from datetime import datetime
from typing import List, Dict, Optional, Union, Any, Tuple
from pydantic import BaseModel, Field


class Word(BaseModel):
    id: int = Field(..., description="单词唯一标识 ID")
    kanji: str = Field(..., description="日文汉字")
    kana: str = Field(..., description="假名（含音调，如：たべる2）")
    meaning: str = Field(..., description="中文释义")
    pos: str = Field(..., description="词性")
    category: Optional[str] = Field(
        None, description="可选：单词分类，例如 JLPT 等级或主题"
    )


class SRSProgress(BaseModel):
    stability: float = Field(..., description="记忆稳定性")
    difficulty: float = Field(..., description="难度系数")
    due: datetime = Field(..., description="下次复习时间")
    last_review: Optional[datetime] = Field(None, description="上次复习时间")
    state: int = Field(
        ..., description="FSRS 状态 (0:New, 1:Learning, 2:Review, 3:Relearning)"
    )
