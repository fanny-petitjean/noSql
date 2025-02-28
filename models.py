from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    purchases = relationship("Purchase", back_populates="user")
    
    followers = relationship(
        "Follower",
        foreign_keys="[Follower.user_id]",
        back_populates="user"
    )
    following = relationship(
        "Follower",
        foreign_keys="[Follower.follower_id]",
        back_populates="follower"
    )

class Follower(Base):
    __tablename__ = 'followers'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    follower_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="followers")
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(DECIMAL, nullable=False)

    purchases = relationship("Purchase", back_populates="product")

class Purchase(Base):
    __tablename__ = 'purchases'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    purchase_date = Column(TIMESTAMP, nullable=False)
    
    user = relationship("User", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")