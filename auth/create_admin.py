import typer
from functools import wraps
from asyncio import run
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import create_admin_user_if_not_exist, async_session
from src.core import config
from src.core.logger import logger

app = typer.Typer()


def async_command(app, *args, **kwargs):
    def decorator(async_func):
        @wraps(async_func)
        def sync_func(*_args, **_kwargs):
            return run(async_func(*_args, **_kwargs))

        app.command(*args, **kwargs)(sync_func)
        return async_func

    return decorator


typer.Typer.async_command = async_command


@app.async_command()
async def create_admin(login: str = None, password: str = None):
    """
    Creates an administrator user in the system.

    :param login: The login of the administrator. If None, the value from the configuration will be used.
    :param password: The password of the administrator. If None, the value from the configuration will be used.
    """
    if login is None or password is None:
        fast_api_conf = config.get_config()
        login = fast_api_conf.admin_login
        password = fast_api_conf.admin_passwd

    async with async_session() as session:
        await create_admin_user_if_not_exist(session, login, password)
        logger.info(f"Admin {login} created / updated.")


if __name__ == "__main__":
    app()
