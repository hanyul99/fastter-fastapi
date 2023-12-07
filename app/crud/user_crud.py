from typing import Optional

from sqlalchemy.orm import Session

from app.core.contants import UserLoginType
from app.crud.base import CRUDBase
from app.models import User
from app.schemas import CreateUserIn


class CRUDUser(CRUDBase[User]):
    async def get_by_email(self, session: Session, email: str) -> Optional[User]:
        return await self.get_by(session, email=email)

    @staticmethod
    async def registration(
        session: Session, user_in: CreateUserIn, login_type: UserLoginType = UserLoginType.EMAIL
    ) -> User:
        user = User()
        user.username = user_in.username
        user.email = user_in.email
        user.password = user_in.password
        user.user_login_type = login_type

        session.add(user)
        session.commit()
        session.refresh(user)
        return user


users = CRUDUser(User)
