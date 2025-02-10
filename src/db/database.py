from datetime import datetime

import yaml
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import User, Pairs, Base
from .utils import get_frequencies


class DataBase:
    def __init__(self, config_path: str = './configs/config.yaml'):
        self.config = self.load_config(path=config_path)
        database_url = f"sqlite:///./{self.config['db']['name']}"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db: Session = session_local()
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def load_config(path: str):
        try:
            with open(path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Config file not found.")
        except yaml.YAMLError:
            raise HTTPException(status_code=500, detail="Error parsing config file.")

    def add_user(self, username: int):
        try:
            new_user = User(username=username)
            if self.db.query(User).filter(User.username == username).first():
                print('user already in db')
            else:
                self.db.add(new_user)
                self.db.commit()
                self.db.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error adding channel '{username}': {str(e)}"
            )

    def add_pairs(self, written: str, intended: str, datetime_: datetime, username: int):
        try:
            user_obj = self.db.query(User).filter(User.username == username).first()
            if not user_obj:
                raise HTTPException(
                    status_code=404, detail=f"User '{username}' not found."
                )
            written_ipm, intended_ipm, wi_ratio = get_frequencies(written, intended)
            pairs_item = Pairs(
                written=written,
                intended=intended,
                datetime=datetime_,
                written_ipm=written_ipm,  # TODO: keep a separate table for word scores
                intended_ipm=intended_ipm,
                wi_ratio=wi_ratio,
                user_id=user_obj.id,
            )
            self.db.add(pairs_item)
            self.db.commit()
            self.db.refresh(pairs_item)
            return pairs_item
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error adding news: {str(e)}"
            )

    def select_pairs(self, username: int):
        try:
            user_obj = self.db.query(User).filter(User.username == username).first()
            if not user_obj:
                raise HTTPException(
                    status_code=404, detail=f"User '{username}' not found."
                )
            pairs = (
                self.db.query(Pairs)
                .filter(Pairs.user_id == user_obj.id)
                .all()
            )
            return pairs
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching news for the time period: {str(e)}",
            )

