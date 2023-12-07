from typing import Optional
from starlette import status


class CustomException(Exception):
    def __init__(
            self,
            status_code: Optional[status] = None,
            error_code: Optional[str] = None,
            msg: Optional[str] = None,
    ):
        self.msg = msg or "Internal Server Error"
        self.status_code = status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
        self.error_code = error_code or "000000"


class BadRequestException(CustomException):
    def __init__(self, error_code: str, msg: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            msg=msg,
        )


class UnauthorizedException(CustomException):
    def __init__(self, error_code: str, msg: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            msg=msg,
        )


class NotFoundException(CustomException):
    def __init__(self, error_code: str, msg: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            msg=msg,
        )
