from sqlmodel import Field, SQLModel, select
from model.sqlconf import get_session

class User(SQLModel, table=True):
    __tablename__ = "User"
    email: str = Field(unique=True,nullable=False,primary_key=True)
    name: str = Field(nullable=False)
    pw: str = Field(nullable=False)
    
def selects():
    with get_session() as session:
        statement = select(User)
        res = session.exec(statement).all()
        s = {'res':[x.__dict__ for x in res]}
        return s
    
def select_one(email:str):
    try:
        with get_session() as session:
            statement = select(User).where(User.email==email)
            userinfo = session.exec(statement).one_or_none()
            print(f'[DB] [SUCCESS] file : {__file__} , function : select_one')
            return userinfo
    except Exception as e:
        print(f'[DB] [ERROR] file : {__file__} , function : insert , message : {e}')
        return False
    
def insert(u:User):
    res = True
    error_msg = ''
    try:
        with get_session() as session:
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



def update(u:User):
    res = True
    error_msg = ''
    try:
        with get_session() as session:
            session.add(u)
            session.commit()
    except Exception as e:
        session.rollback()
        res = False
        error_msg = e
    finally:
        if res:
            print(f'[DB] [SUCCESS] file : {__file__} , function : update')
        else :
            print(f'[DB] [ERROR] file : {__file__} , function : update , message : {error_msg}')
        return res