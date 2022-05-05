from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Base class for the tables generated in the database"""

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generates the name for the tables
        """
        return cls.__name__.lower()
