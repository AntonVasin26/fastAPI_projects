from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    characters = relationship("Character", back_populates="owner")

class CharacterClass(Base):
    __tablename__ = "character_classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    characters = relationship("Character", back_populates="character_class")

class Ability(Base):
    __tablename__ = "abilities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    available_classes = Column(String)
    uses = Column(Integer, default=-1)
    description = Column(String)

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    cost = Column(Integer)
    rarity = Column(String)
    description = Column(String)

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)  # глобальный id
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    local_id = Column(Integer, index=True)  # локальный id в системе пользователя

    name = Column(String, nullable=False)
    character_class_id = Column(Integer, ForeignKey("character_classes.id"), nullable=False)

    max_hp = Column(Integer, nullable=False)
    current_hp = Column(Integer, nullable=False)
    armor_class = Column(Integer, nullable=False)

    strength = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    constitution = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    wisdom = Column(Integer, nullable=False)
    charisma = Column(Integer, nullable=False)

    owner = relationship("User", back_populates="characters")
    character_class = relationship("CharacterClass", back_populates="characters")
    abilities = relationship("CharacterAbility", back_populates="character", cascade="all, delete-orphan")
    equipment = relationship("CharacterEquipment", back_populates="character", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('owner_id', 'local_id', name='_owner_localid_uc'),
    )

class CharacterAbility(Base):
    __tablename__ = "character_abilities"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    ability_id = Column(Integer, ForeignKey("abilities.id"))
    current_uses = Column(Integer, default=1)
    name = Column(String)
    character = relationship("Character", back_populates="abilities")
    ability = relationship("Ability")

class CharacterEquipment(Base):
    __tablename__ = "character_equipment"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    is_equipped = Column(Boolean, default=False)
    name = Column(String)
    character = relationship("Character", back_populates="equipment")
    equipment = relationship("Equipment")
