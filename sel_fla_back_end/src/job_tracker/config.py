import os
import pathlib

root_dir = pathlib.Path(__file__).parent.resolve()


class BaseConfig:
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class RegularConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URI") or f"sqlite:///{root_dir.joinpath('backend.db')}"
    )
