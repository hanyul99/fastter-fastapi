import os
from pathlib import Path
from typing import Optional, Literal

from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """
    LocalSettings, DevSettings, 나아가 PrdSettings 에서 사용될 공통 BaseSettings를 만들어 줍니다.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DB_ECHO: bool = False
    OPEN_API_URL: Optional[str] = "/api/openapi.json"
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"


class DevSettings(Settings):
    """
    Settings를 상속받아 이 세팅에서 역시 BASE_DIR을 사용할 수 있습니다.
    """

    ENV: str = "DEV"
    SECRET_KEY: str

    class Config:
        """
        추가적인 설정은 .env 파일을 통해서 설정할 수 있습니다.
        """

        env_file = "dev.env"


class PrdSettings(Settings):
    ENV: str = "PRD"
    OPEN_API_URL: Optional[str] = None
    DOCS_URL: Optional[str] = None
    REDOC_URL: Optional[str] = None
    SECRET_KEY: str

    class Config:
        env_file = "prd.env"


class LocalSettings(Settings):
    """
    로컬 세팅에서는 로컬 데이터베이스 연결을 위한 설정을 진행합니다.
    """

    ENV: str = "LOCAL"
    DB_URL: str
    DB_ECHO: bool = True
    DEBUG: bool
    SECRET_KEY: str

    class Config:
        env_file = "local.env"


class TestSettings(Settings):
    """
    로컬 세팅에서는 로컬 데이터베이스 연결을 위한 설정을 진행합니다.
    """

    ENV: str = "TEST"
    DB_URL: str = "mysql+pymysql://root@localhost/fastter_test?charset=utf8mb4"
    DB_ECHO: bool = True
    DEBUG: bool = False
    SECRET_KEY: str = "test"


def get_settings(force_env: Literal["TEST", "LOCAL", "DEV", "PRD"] = None):
    """
    ENV 라는 환경변수를 사용해서 알맞은 설정 값을 불러오는 함수
    :return:
    """
    env: str = os.environ.get("ENV", "LOCAL") if not force_env else force_env
    config_classes = {
        "TEST": TestSettings,
        "LOCAL": LocalSettings,
        "DEV": DevSettings,
        "PRD": PrdSettings,
    }

    # 환경 설정 클래스를 리턴하기 전에 인스턴스화 하기 위해 뒤에 ()괄호를 사용해서 클래스 인스턴스를 생성해 줍니다.
    # env 값이 LOCAL일 경우 config_classes['LOCAL']을 값을 가지고 옵니다.
    return config_classes[env]()


# get_settings()를 불러올 수 있는 변수를 하나 생성합니다.
settings = get_settings()
