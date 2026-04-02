import datetime
from enum import Enum
from typing import List, TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Boolean, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from flask_login import UserMixin
from sqlalchemy import Integer


class DeviceType(Enum):
    ГАЗ = 'Газ'
    ЭЛЕКТРИЧЕСТВО = 'Электричество'
    ХОЛОДНАЯВОДА = 'Холодная вода'
    ГОРЯЧАЯВОДА = 'Горячая вода'


class BaseModel(DeclarativeBase):
    __abstract__ = True  # mark this as an abstract base class

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class User(UserMixin, BaseModel):

    __tablename__ = 'users'

    fullname: Mapped[str] = mapped_column(String(250))
    login: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(200))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    user_devices: Mapped[List["UserDevice"]] = relationship('UserDevice', back_populates='user')

    def __str__(self):
        return self.fullname + ' ' + self.login


class Device(BaseModel):
    __tablename__ = 'devices'
    
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[DeviceType] = mapped_column(String(50), default=DeviceType.ГАЗ)
    file: Mapped[str] = mapped_column(String(250), server_default="", default="")


class UserDevice(BaseModel):
    __tablename__ = 'user_devices'

    number: Mapped[str] = mapped_column(String(50))

    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id", ondelete="CASCADE"))
    device: Mapped["Device"] = relationship('Device')
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship('User', back_populates='user_devices')

    indicators: Mapped[List["Indicator"]] = relationship('Indicator', back_populates='user_device')


class Indicator(BaseModel):
    __tablename__ = 'indicators'

    create_date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)
    value: Mapped[int] = mapped_column(Integer, CheckConstraint('value > 0'))
    
    user_device_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_devices.id", ondelete="CASCADE"))
    user_device: Mapped["UserDevice"] = relationship('UserDevice', back_populates='indicators')
