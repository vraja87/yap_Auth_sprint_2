from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import DDL, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core import config

db_conf = config.DbConf()
Base = declarative_base()

DSN = f"postgresql+asyncpg://{db_conf.user}:{db_conf.password}@{db_conf.host}:{db_conf.port}/{db_conf.db}"
engine = create_async_engine(DSN, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def create_admin_role_if_not_exist(db: AsyncSession):
    from src.models.entity import Role
    result = await db.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalars().first()
    if not admin_role:
        new_admin_role = Role(name="admin", description="Administrator role with all permissions")
        db.add(new_admin_role)
        await db.commit()
        return new_admin_role
    return admin_role


async def create_admin_user_if_not_exist(db: AsyncSession, login: str, password: str) -> None:
    from src.models.entity import User, UserRoles

    try:
        result = await db.execute(select(User).where(User.login == login))
        admin_user = result.scalars().first()
        admin_role = await create_admin_role_if_not_exist(db)

        if admin_user is None:
            admin_user = User(login=login, password=password)
            db.add(admin_user)
        else:
            temp_user = User(login=login, password=password)
            if admin_user.password != temp_user.password:
                admin_user.password = temp_user.password

        admin_user_role = await db.execute(
            select(UserRoles).where(UserRoles.user_id == admin_user.id, UserRoles.role_id == admin_role.id)
        )
        admin_user_role = admin_user_role.scalars().first()
        if admin_user_role is None:
            user_role = UserRoles(user_id=admin_user.id, role_id=admin_role.id)
            db.add(user_role)

        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def create_database() -> None:
    from src.models.entity import (LoginHistory, RefreshToken, Role, User,
                                   UserRoles)

    async with engine.begin() as conn:
        await conn.execute(DDL('CREATE SCHEMA IF NOT EXISTS content'))
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    from src.models.entity import (LoginHistory, RefreshToken, Role, User,
                                   UserRoles)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
