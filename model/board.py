from sqlmodel import Field, SQLModel, Session, select
from model.sqlconf import engine
from model.user import User
from datetime import datetime

class Board(SQLModel, table=True):
    __tablename__ =  "Board"
    no: int = Field(primary_key=True)
    board_name: str = Field(nullable=False)
    owner: str = Field(nullable=False)
    content: str = Field(nullable=False)
    create_time : datetime = Field(nullable=False)
    fixed_time : datetime | None = Field(nullable=True, default= None)
    view : int = Field(nullable=True, default=0)

def selects():
    try:
        with Session(engine) as session:
            try:
                statement = select(Board)
                b = session.exec(statement).all()
                print(f'[DB] [SUCCESS] file : {__file__} , function : selects')
                return b
            except Exception as e:
                session.rollback()
                raise e
    except Exception as e:
        print(f'[DB] [ERROR] file : {__file__} , function : selects , message : {e}')
        
        
def select_one(no:str):
    try:
        with Session(engine) as session:
            statement = select(Board).where(Board.no==no)
            boardinfo = session.exec(statement).one_or_none()
            print(f'[DB] [SUCCESS] file : {__file__} , function : select_one')
            return boardinfo
    except Exception as e:
        print(f'[DB] [ERROR] file : {__file__} , function : insert , message : {e}')
        return False

def insert(b:Board):
    res = True
    error_msg = ''
    try:
        with Session(engine) as session:
            try:
                session.add(b)
                session.commit()
                session.refresh(b)
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