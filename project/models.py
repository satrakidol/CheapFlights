from flask_login import UserMixin
from . import db
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, sessionmaker
from sqlalchemy import String, DateTime, ForeignKey, Integer
from typing import List

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary key
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")

from sqlalchemy import create_engine
import pandas as pd


db_name = 'instance/db.sqlite'
engine = create_engine(f'sqlite:///{db_name}')

Airlines_file = 'project/IATA Codes/Airlines.csv'  
df_airlines_file = pd.read_csv(Airlines_file)

AirportCity_file = 'project/IATA Codes/AirportCity.csv'  
df_AirportCity_file = pd.read_csv(AirportCity_file)

Cities_file = 'project/IATA Codes/Cities.csv'  
df_Cities_file = pd.read_csv(Cities_file)


class Base(DeclarativeBase):
    pass

class Airlines(Base):
    __tablename__ = 'airlines'
    id: Mapped[int] = mapped_column(primary_key=True)
    airline: Mapped[str] = mapped_column(String(20), unique=True,nullable=False)
    codes: Mapped[str] = mapped_column(String(20), unique=True,nullable=False)
   
    def __str__(self):
        return self.airline

class Cities(Base):
    __tablename__ = 'cities'
    id: Mapped[int] = mapped_column(primary_key=True)
    codes: Mapped[str] = mapped_column(String(20), unique=True,nullable=False)
    city: Mapped[str] = mapped_column(String(20), unique=False,nullable=False)
    country: Mapped[str] = mapped_column(String(20), unique=False,nullable=False)

    def __str__(self):
        return f"<Cities codes={self.codes}, city = {self.city}"

class Airports(Base):
    __tablename__ = 'airports'
    id: Mapped[int] = mapped_column(primary_key=True)
    codes: Mapped[str] = mapped_column(String(20), unique=True,nullable=False)
    airport: Mapped[str] = mapped_column(String(20), unique=False,nullable=False)

    def __str__(self):
        return self.airport

class Notification(db.Model):
    __tablename__ = 'notification'
    notificationID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, ForeignKey("user.id"))  # ForeignKey to User.id
    user = relationship("User", back_populates="notifications")
    origin = db.Column(db.String)
    destination = db.Column(db.String)
    minDate = db.Column(db.String)
    maxDate = db.Column(db.String)
    priceGo = db.Column(db.Integer)
    priceReturn = db.Column(db.Integer)
    

Session = sessionmaker(bind=engine)
session = Session()

# Create tables
Base.metadata.create_all(engine)

# # Insert data into the Airlines table
# for index, row in df_airlines_file.iterrows():
#     airline = Airlines(airline=row['airline'], codes=row['codes'])
#     session.add(airline)

# # Insert data into the Cities table
# for index, row in df_Cities_file.iterrows():
#     city = Cities(codes=row['Codes'], city=row['City'], country=row['Country'])
#     session.add(city)

# # Insert data into the Airports table
# for index, row in df_AirportCity_file.iterrows():
#     airport = Airports(airport=row['airport'], codes=row['codes'])
#     session.add(airport)

# Commit the changes and close the session
session.commit()
session.close()
