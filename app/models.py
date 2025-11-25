from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import (Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Numeric, func)

Base=declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    sku=Column(String(50), nullable=False)
    sku_upper = Column(String(100), generated_always_as=func.upper(sku), stored=True, index=True, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2))
    active=Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Webhook(Base):
    __tablename__ = 'webhooks'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)
    event = Column(String(50), default='product.imported')
    enabled = Column(Boolean, default=True)