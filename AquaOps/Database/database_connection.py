from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from AquaOps.Database.Config.database_config import DatabaseConfig

def build_engine(db: DatabaseConfig):
    url = (
        f"postgresql+asyncpg://{db.username}:{db.password}"
        f"@{db.host}:{db.port}/{db.name}"
    )
    return create_async_engine(
        url,
        pool_size=db.pool.max_connections,
        pool_timeout=db.pool.connection_timeout_seconds,
    )