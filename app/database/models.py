import peewee
from os import environ


class BaseModel(peewee.Model):
    """Базовый класс для моделей с бд SQLite"""
    id = peewee.PrimaryKeyField(null=False)

    class Meta:
        # Ниже представлен небольшой костыль, ибо записывание переменных из config.env в переменные среды
        # происходит позже, чем инициализация пакетов и этих моделей. Следовательно, сюда передавались None..
        database = peewee.SqliteDatabase(database=environ.get('SQLITE_PATH'), pragmas={'foreign_keys': 1})


class Host(BaseModel):
    """Модель таблицы Хостов"""
    hostname = peewee.CharField(null=False, unique=True, verbose_name="Хост")


class IpAddress(BaseModel):
    """Модель таблицы IP адресов"""
    hostname_id = peewee.ForeignKeyField(model=Host, to_field='id', on_delete='cascade', on_update='cascade',
                                         null=False, verbose_name="ID Хоста")
    ip_address = peewee.IPField(null=False, verbose_name="IP Адрес")
