import datetime

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship

from .db import Base


# ---- game content (seeded from data/wiki/*.json) ----

class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True)
    wiki_page_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)
    rarity = Column(Integer)
    element = Column(String)
    role = Column(String)
    profile_text = Column(Text)
    power = Column(Integer)
    power_max = Column(Integer)
    hp = Column(Integer)
    hp_max = Column(Integer)
    atk = Column(Integer)
    atk_max = Column(Integer)
    def_ = Column("def", Integer)
    def_max = Column(Integer)
    agl = Column(Integer)
    agl_max = Column(Integer)
    crt = Column(Integer)
    crt_max = Column(Integer)

    skins = relationship("ChildSkin", back_populates="child")


class ChildSkin(Base):
    __tablename__ = "child_skins"

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    tab_index = Column(Integer, nullable=False)
    tab_label = Column(String)
    variant_name = Column(String)
    image = Column(String)
    caption = Column(Text)

    child = relationship("Child", back_populates="skins")


class SoulCarta(Base):
    __tablename__ = "soul_carta"

    id = Column(Integer, primary_key=True)
    wiki_page_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)
    rarity = Column(Integer)
    restriction = Column(String)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    wiki_page_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text)


# ---- player state ----

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    platform_id = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


class PlayerProfile(Base):
    __tablename__ = "player_profile"

    account_id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    gold = Column(Integer, default=0)
    gems = Column(Integer, default=0)


class PlayerChild(Base):
    __tablename__ = "player_children"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    level = Column(Integer, default=1)
    stars = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    equipped_soul_carta_id = Column(Integer, ForeignKey("player_soul_carta.id"))
    acquired_at = Column(DateTime, default=datetime.datetime.utcnow)


class PlayerSoulCarta(Base):
    __tablename__ = "player_soul_carta"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    soul_carta_id = Column(Integer, ForeignKey("soul_carta.id"), nullable=False)
    level = Column(Integer, default=1)
    enchant_level = Column(Integer, default=0)


class PlayerItem(Base):
    __tablename__ = "player_items"

    account_id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    quantity = Column(Integer, default=0)
