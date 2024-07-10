from pydantic import MongoDsn
from pydantic_core import MultiHostUrl

class Config:

    SCHEME = "mongodb"
    HOST = "127.0.0.1"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MongoDsn:
        return MultiHostUrl.build(
            scheme=self.SCHEME,
            host=self.HOST,
        )
    
config = Config()
