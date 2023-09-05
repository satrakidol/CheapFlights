from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker
from . models import Base
from . config import connection_string

print(connection_string)
engine = create_engine(connection_string, echo=True)
Session = scoped_session(sessionmaker())

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)