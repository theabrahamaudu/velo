from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from velo.config import DATABASE_URL


class DBConn:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True
        )

    def session(self):
        return scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )


Session = DBConn().session()
