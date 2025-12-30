from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    balance = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    referral_code = Column(String(20), unique=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    registered_at = Column(DateTime, default=datetime.now)
    is_admin = Column(Boolean, default=False)
    referrals = relationship("User", backref="referrer", remote_side=[id])
    transactions = relationship("Transaction", back_populates="user")
    completed_tasks = relationship("CompletedTask", back_populates="user")
    withdrawal_requests = relationship("Withdrawal", back_populates="user")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    type = Column(String(20))
    description = Column(String(255))
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("User", back_populates="transactions")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    reward = Column(Float)
    category = Column(String(50))
    url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    max_completions = Column(Integer, default=0)
    current_completions = Column(Integer, default=0)
    completions = relationship("CompletedTask", back_populates="task")

class CompletedTask(Base):
    __tablename__ = 'completed_tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    screenshot = Column(String(500), nullable=True)
    status = Column(String(20), default='pending')
    completed_at = Column(DateTime, default=datetime.now)
    reviewed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="completed_tasks")
    task = relationship("Task", back_populates="completions")

class Withdrawal(Base):
    __tablename__ = 'withdrawals'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    method = Column(String(50))
    details = Column(String(500))
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.now)
    processed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="withdrawal_requests")
