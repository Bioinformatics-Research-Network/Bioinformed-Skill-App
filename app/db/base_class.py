from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

# Declare Base class for sqlalchemy models
@as_declarative()
class Base:
    id: Any
    __name__: str
    # create __tablename__ automatically for new tables
    @declared_attr
    def __tablename__(cls) -> str: 
        return cls.__name__.lower()