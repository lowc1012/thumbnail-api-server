from sqlmodel import Session, SQLModel, create_engine

from app.internal.configuration.settings import Settings

_engine = None


def get_engine(settings: Settings):
    """Create database engine"""
    global _engine
    if _engine is None:
        _engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    return _engine


def create_db_and_tables(settings: Settings):
    """Initialize database and create tables"""
    engine = get_engine(settings)
    SQLModel.metadata.create_all(engine)


def get_session(settings: Settings):
    """Dependency to get database session"""
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session
