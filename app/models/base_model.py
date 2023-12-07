from sqlalchemy import Column, BIGINT, DateTime, func
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    id = Column(BIGINT, primary_key=True, index=True)
    created_at = Column(
        DateTime, nullable=False, server_default=func.current_timestamp(), default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, server_default=func.current_timestamp(), default=func.current_timestamp()
    )
