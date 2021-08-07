from os import environ

from app.database import database
from app.utils import load_env_file
from asyncio import get_event_loop

if __name__.endswith("__main__"):
    load_env_file()
    db = database.Database(database=environ.get('SQLITE_PATH'))

    async_loop = get_event_loop()
    async_loop.create_task(db.init())
    async_loop.run_forever()

