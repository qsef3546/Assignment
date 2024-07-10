from sqlmodel import Field, SQLModel, select,update,delete
from model.pg_sqlconf import get_session
from model.board import Board
class User(SQLModel, table=True):
    __tablename__ = "User"
    email: str = Field(unique=True,nullable=False,primary_key=True)
    name: str = Field(nullable=False)
    pw: str = Field(nullable=False)
        
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



def update_one(u:User):
    res = True
    error_msg = ''
    try:
        with get_session() as session:
            session.add(u)
            board_statement = (
                update(Board).where(Board.email == u.email).values(owner=u.name)
            )
            session.exec(board_statement)
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

def withdrawal(email:str):
    res = True
    try :
        with get_session() as session:
            try:
                user_statement = delete(User).where(User.email==email)
                
                board_statement = (
                    update(Board)
                    .where(Board.email == email)
                    .values(owner="탈퇴한 유저")
                )
                session.exec(user_statement)
                session.exec(board_statement)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
    except Exception as e:
        res = False
        error_msg = e
    finally:
        if res:
            print(f'[DB] [SUCCESS] file : {__file__} , function : delete')
        else :
            print(f'[DB] [ERROR] file : {__file__} , function : delete , message : {error_msg}')
        return res