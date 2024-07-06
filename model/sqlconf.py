from pydantic import PostgresDsn
from pydantic_core import MultiHostUrl
from sqlmodel import create_engine, Session
from contextlib import contextmanager
class Config:

    SCHEME = "postgresql"
    USERNAME = "postgres"
    PASSWORD = "admin1234!"
    HOST = "127.0.0.1"
    PORT = 5432
    PATH = "user"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme=self.SCHEME,
            username=self.USERNAME,
            password=self.PASSWORD,
            host=self.HOST,
            port=self.PORT,
            path=self.PATH,
        )
    
config = Config()
engine = create_engine(str(config.SQLALCHEMY_DATABASE_URI))

@contextmanager
def get_session():
    with Session(engine) as session:
            yield session