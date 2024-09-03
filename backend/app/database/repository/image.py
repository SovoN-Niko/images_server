from typing import List
from sqlalchemy.future import select

from app.config import db, commit_rollback
from app.database.model.image import Image
from app.database.repository.base_repo import BaseRepo


class ImageRepository(BaseRepo):
    model = Image

    @staticmethod
    async def find_by_path(path: str):
        query = select(Image).where(Image.path == path)
        return (await db.execute(query)).scalar_one_or_none()
