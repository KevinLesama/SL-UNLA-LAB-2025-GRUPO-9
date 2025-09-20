from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from models import Persona, Turnos

engine = create_engine("sqlite:///mi_base.bd", echo=True)

Session = sessionmaker(bind=engine)
session = Session()