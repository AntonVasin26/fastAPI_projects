from sqlalchemy import Column, Integer, String, ForeignKey, Text
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
    description = Column(Text)
    characters = relationship("Character", back_populates="character_class_rel")
    level_abilities = relationship("ClassLevelAbility", back_populates="character_class")

class Ability(Base):
    __tablename__ = "abilities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    available_classes = Column(String)
    uses = Column(Integer, default=-1)
    description = Column(Text)

class ClassLevelAbility(Base):
    __tablename__ = "class_level_abilities"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("character_classes.id"))
    level = Column(Integer)
    ability_id = Column(Integer, ForeignKey("abilities.id"))

    character_class = relationship("CharacterClass", back_populates="level_abilities")
    ability = relationship("Ability")

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    cost = Column(Integer)
    rarity = Column(String)
    description = Column(Text)

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    race = Column(String)
    background = Column(String)
    character_class_id = Column(Integer, ForeignKey("character_classes.id"))
    level = Column(Integer, default=1)
    armor_class = Column(Integer, default=10)
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="characters")
    character_class_rel = relationship("CharacterClass", back_populates="characters")
    abilities = relationship("CharacterAbility", back_populates="character", cascade="all, delete-orphan")
    equipment = relationship("CharacterEquipment", back_populates="character", cascade="all, delete-orphan")

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
    is_equipped = Column(Integer, default=0)
    name = Column(String)
    character = relationship("Character", back_populates="equipment")
    equipment = relationship("Equipment")
