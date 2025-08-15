from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase

_engine = None
SessionLocal = None

class Base(DeclarativeBase):
    pass

def init_engine_and_session(database_url: str):
    global _engine, SessionLocal
    _engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal = scoped_session(sessionmaker(bind=_engine, autoflush=False, autocommit=False))

def get_session():
    if SessionLocal is None:
        raise RuntimeError("Database session is not initialized")
    return SessionLocal

def remove_scoped_session():
    if SessionLocal is not None:
        SessionLocal.remove()

def get_engine():
    if _engine is None:
        raise RuntimeError("Engine not initialized")
    return _engine
