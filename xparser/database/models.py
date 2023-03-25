import uuid

from peewee_async import PostgresqlDatabase, Manager
from peewee import (
    Model,
    SmallIntegerField,
    DoubleField,
    UUIDField,
    BooleanField
)


database = PostgresqlDatabase(
            'test',
            user='postgres',
            password='6754321k',
            host='localhost',
            port=5432
        )


class Database:
    manager = Manager(database)

    class BaseModel(Model):
        class Meta:
            database = database

    @classmethod
    def table_factory(cls, symbol_name):
        class Spot(cls.BaseModel):
            unique_id = UUIDField(primary_key=True, default=uuid.uuid4)
            price = DoubleField()
            spot_id = SmallIntegerField()
            ask = BooleanField()

        Spot.Meta.table_name = f'spot_{symbol_name}'
        Spot.create_table()

        return Spot
