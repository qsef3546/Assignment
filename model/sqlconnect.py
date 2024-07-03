from sqlmodel import Field, SQLModel, create_engine, Session, select
from model.sqlconf import config
from error_code import error
from inspect import currentframe, getframeinfo
engine = create_engine(str(config.SQLALCHEMY_DATABASE_URI))
SQLModel.metadata.create_all(engine)

class user(SQLModel, table=True):
    email: str = Field(unique=True,nullable=False,primary_key=True)
    name: str = Field(nullable=False)
    pw: str = Field(nullable=False)
    
def selects():
    with Session(engine) as session:
        statement = select(user)
        res = session.exec(statement).all()
        s = {'res':[x.__dict__ for x in res]}
        return s
    
def select_one(email:str):
    try:
        with Session(engine) as session:
            statement = select(user).where(user.email==email)
            userinfo = session.exec(statement).one_or_none()
            print(f'[DB] [SUCCESS] file : {__file__} , function : select_one')
            return userinfo
    except Exception as e:
        print(f'[DB] [ERROR] file : {__file__} , function : insert , message : {e}')
        return False
    
def insert(u:user):
    res = True
    error_msg = ''
    try:
        with Session(engine) as session:
            try:
                session.add(u)
                session.commit()
                session.refresh(u)
            except Exception as e:
                session.rollback()
                raise e
    except Exception as e:
        res = False
        error_msg = e
    finally:
        if res:
            print(f'[DB] [SUCCESS] file : {__file__} , function : insert')
        else :
            print(f'[DB] [ERROR] file : {__file__} , function : insert , message : {error_msg}')
        return res



def update(u:user):
    res = True
    error_msg = ''
    try:
        with Session(engine) as session:
            session.add(u)
            session.commit()
    except Exception as e:
        res = False
        error_msg = e
    finally:
        if res:
            print(f'[DB] [SUCCESS] file : {__file__} , function : insert')
        else :
            print(f'[DB] [ERROR] file : {__file__} , function : insert , message : {error_msg}')
        return res