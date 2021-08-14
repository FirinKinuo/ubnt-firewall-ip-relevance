from os import environ
from app.database import Database
from app.ubnt import UbntService


DATABASE = Database(database=environ.get("SQLITE_PATH"))
DATABASE.init()
UBNT = UbntService(
    host=environ.get("UBNT_HOST"),
    login=environ.get("UBNT_USER"),
    password=environ.get("UBNT_PASSWORD"),
    port=int(environ.get("UBNT_PORT")),
    key=environ.get("UBNT_PRIVATE_KEY"),
    firewall_group=environ.get("UBNT_FIREWALL_GROUP")
)
