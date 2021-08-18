from app.utils import background_checking_relevance
from app.file.file_watchdog import HostFileWatchdog
from asyncio import get_event_loop
from os import environ


if __name__.endswith("__main__"):
    WATCHDOG = HostFileWatchdog(file_path=environ.get('HOSTS_FILE_PATH'))

    async_loop = get_event_loop()
    async_loop.create_task(WATCHDOG.start())
    async_loop.create_task(background_checking_relevance(hours=int(environ.get("AUTOCHECK_PERIOD", "1"))))
    async_loop.run_forever()
