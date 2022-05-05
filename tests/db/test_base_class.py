from app.db.base_class import Base


class test_Base:
    test_Base = Base
    assert type(test_Base) == type(Base)
    assert type(test_Base.__tablename__) == str
