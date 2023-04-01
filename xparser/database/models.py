from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import UUID, Column, DOUBLE_PRECISION, SMALLINT, BOOLEAN
from uuid import uuid4


class Base(DeclarativeBase):
    pass


class Spot(Base):
    __tablename__ = "spot"
    unique_id = Column(UUID, primary_key=True, default=uuid4)
    spot_id = Column(SMALLINT,unique=False)
    symbol_id = Column(SMALLINT,unique=False)
    price = Column(DOUBLE_PRECISION,unique=False)
    ask = Column(BOOLEAN,unique=False)

    def __repr__(self):
        return f'Spot({self.unique_id},{self.spot_id},{self.symbol_id},{self.price},{self.ask})'


class SpotResult(Base):
    __tablename__ = "spot_res"
    unique_id = Column(UUID, primary_key=True, default=uuid4)
    benefit = Column(DOUBLE_PRECISION, unique=False)
    price1 = Column(DOUBLE_PRECISION, unique=False)
    price2 = Column(DOUBLE_PRECISION, unique=False)
    spot_id1 = Column(SMALLINT, unique=False)
    spot_id2 = Column(SMALLINT, unique=False)
    ask = Column(BOOLEAN, unique=False)
