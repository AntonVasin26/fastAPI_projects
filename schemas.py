"""Pydantic schemas for DnD project."""

from typing import List, Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    """Base schema for User."""
    username: str

class UserCreate(UserBase):
    """Schema for creating a new User."""
    password: str

class User(UserBase):
    """Schema for returning a User."""
    id: int

    class Config:
        from_attributes = True

class CharacterClassBase(BaseModel):
    """Base schema for CharacterClass."""
    name: str
    description: Optional[str] = None

class CharacterClassCreate(CharacterClassBase):
    """Schema for creating a CharacterClass."""
    pass

class CharacterClass(CharacterClassBase):
    """Schema for returning a CharacterClass."""
    id: int

    class Config:
        from_attributes = True

class ClassProgressionBase(BaseModel):
    """Base schema for ClassProgression."""
    character_class_id: int
    level: int
    hp_bonus: int = 0
    other_bonuses: Optional[str] = None

class ClassProgressionCreate(ClassProgressionBase):
    """Schema for creating a ClassProgression."""
    pass

class ClassProgression(ClassProgressionBase):
    """Schema for returning a ClassProgression."""
    id: int

    class Config:
        from_attributes = True

class AbilityBase(BaseModel):
    """Base schema for Ability."""
    name: str
    available_classes: Optional[str] = None
    uses: int = -1
    description: Optional[str] = None

class AbilityCreate(AbilityBase):
    """Schema for creating an Ability."""
    pass

class Ability(AbilityBase):
    """Schema for returning an Ability."""
    id: int

    class Config:
        from_attributes = True

class EquipmentBase(BaseModel):
    """Base schema for Equipment."""
    name: str
    cost: int
    rarity: Optional[str] = None
    description: Optional[str] = None
    effects: Optional[str] = None  # JSON-строка

class EquipmentCreate(EquipmentBase):
    """Schema for creating Equipment."""
    pass

class Equipment(EquipmentBase):
    """Schema for returning Equipment."""
    id: int

    class Config:
        from_attributes = True

class CharacterBase(BaseModel):
    """Base schema for Character."""
    local_id: int
    name: str
    character_class_id: int
    level: int
    max_hp: int
    current_hp: int
    armor_class: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

class CharacterCreate(CharacterBase):
    """Schema for creating a Character."""
    pass

class CharacterAbilityBase(BaseModel):
    """Base schema for CharacterAbility."""
    ability_id: int
    current_uses: Optional[int] = None

class CharacterAbilityCreate(CharacterAbilityBase):
    """Schema for adding an Ability to a Character."""
    pass

class CharacterAbility(CharacterAbilityBase):
    """Schema for returning a Character's Ability."""
    id: int
    name: Optional[str] = None
    ability: Optional[Ability] = None

    class Config:
        from_attributes = True

class CharacterEquipmentBase(BaseModel):
    """Base schema for CharacterEquipment."""
    equipment_id: int
    is_equipped: Optional[bool] = False

class CharacterEquipmentCreate(CharacterEquipmentBase):
    """Schema for adding Equipment to a Character."""
    pass

class CharacterEquipment(CharacterEquipmentBase):
    """Schema for returning CharacterEquipment."""
    id: int
    name: Optional[str] = None
    equipment: Optional[Equipment] = None

    class Config:
        from_attributes = True

class Character(CharacterBase):
    """Schema for returning a Character."""
    id: int
    owner_id: int
    abilities: List[CharacterAbility] = []
    equipment: List[CharacterEquipment] = []
    character_class: Optional[CharacterClass] = None

    class Config:
        from_attributes = True
