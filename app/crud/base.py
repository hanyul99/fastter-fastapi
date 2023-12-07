from typing import TypeVar, Generic, Type, Optional, Sequence

from sqlalchemy import select, and_, insert, delete, update
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import Session

from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, session: Session, id: int) -> Optional[ModelType]:
        result = session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_by(self, session: Session, **kwargs) -> Optional[ModelType]:
        query = select(self.model)
        if kwargs:
            conditions = [getattr(self.model, key) == value for key, value in kwargs.items()]
            query = query.where(and_(*conditions))

        result = session.execute(query)
        try:
            created_object = result.scalars().first()
        except ResourceClosedError:
            created_object = None

        return created_object

    async def create(self, session: Session, commit: bool = False, **kwargs) -> ModelType:
        create_statement = insert(self.model).values(**kwargs)
        result = session.execute(create_statement)
        lastrowid = result.lastrowid
        if commit:
            session.commit()
        else:
            session.flush()

        return await self.get_by_id(session, lastrowid)

    async def delete(self, session: Session, commit: bool = False, **kwargs) -> None:
        filters = [getattr(self.model, key) == value for key, value in kwargs.items()]
        delete_statement = delete(self.model).where(and_(*filters))
        session.execute(delete_statement)
        session.flush()
        if commit:
            session.commit()

    async def get_all(
        self, session: Session, page: int = 1, page_size: int = 10, use_page: bool = True, **kwargs
    ) -> Sequence[ModelType]:
        filters = [getattr(self.model, key) == value for key, value in kwargs.items()]

        select_statement = select(self.model).where(and_(*filters))
        if use_page:
            select_statement = select_statement.offset((page - 1) * page_size).limit(page_size)

        result = session.execute(select_statement)

        return result.scalars().all()
