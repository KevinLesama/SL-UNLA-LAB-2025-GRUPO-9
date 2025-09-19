from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine("sqlite:///mi_base.bd", echo=True)
Base=declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()