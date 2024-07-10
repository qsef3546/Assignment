from sqlmodel import Field, SQLModel, select, update
from model.pg_sqlconf import get_session
from datetime import datetime


RECENTLY = 1
VIEW = 2

PAGEOFFSET = 5
class Board(SQLModel, table=True):
    __tablename__ =  "Board"
    no: int = Field(primary_key=True)
    board_name: str = Field(nullable=False)
    owner: str = Field(nullable=False)
    email : str =Field(nullable=False)
    content: str = Field(nullable=False)
    create_time : datetime = Field(nullable=False)
    fixed_time : datetime | None = Field(nullable=True, default= None)
    view : int = Field(nullable=True, default=0)

def selects(type:int,pageoffset:int):
    try:
        with get_session() as session:
            try:
                statement = select(Board)
                if type == VIEW:
                    statement = statement.order_by(Board.view.desc())
                statement = statement.offset(pageoffset*PAGEOFFSET).limit(PAGEOFFSET)
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
        with get_session() as session:
            statement = select(Board).where(Board.no==no)
            boardinfo = session.exec(statement).one_or_none()
            print(f'[DB] [SUCCESS] file : {__file__} , function : select_one')
            if boardinfo:
                try:
                    boardinfo.view += 1
                    session.add(boardinfo)
                    session.commit()
                    session.refresh(boardinfo)
                except Exception as e:
                    session.rollback()
                    raise e
            return boardinfo
    except Exception as e:
        print(f'[DB] [ERROR] file : {__file__} , function : insert , message : {e}')
        return False

def insert(b:Board):
    res = True
    error_msg = ''
    try:
        with get_session() as session:
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

        
def update_one(b:Board):
    res = True
    error_msg = ''
    try:
        with get_session() as session:
            session.add(b)
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

def delete(no:int):
    res = True
    try:
        with get_session() as session:
            try:
                statement = select(Board).where(Board.no==no)
                deleteboard = session.exec(statement).one()
                session.delete(deleteboard)
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