from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, String
from sqlmodel import SQLModel, Field


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: Optional[str] =Field(
        sa_column=Column("id", String(255), primary_key=True, nullable=False)
    )
    path: Optional[str] = Field(None, nullable=False)
    size: int = Field(None, nullable=False)
    mime_type: Optional[str]
    filter: Optional[str]
    modified_at: datetime = Field(
        sa_column=Column(
            DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
        )
    )
