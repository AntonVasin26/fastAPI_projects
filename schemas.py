from pydantic import BaseModel
from typing import List, Optional

# --- CharacterClass ---
class CharacterClassBase(BaseModel):
    name: str
    description: Optional[str] = None

class CharacterClassCreate(CharacterClassBase):
    pass

class CharacterClass(CharacterClassBase):
    id: int
    class Config:
        from_attributes = True

# --- Ability ---
class AbilityBase(BaseModel):
    name: str
    available_classes: str
    uses: int
    description: Optional[str] = None

class AbilityCreate(AbilityBase):
    pass

class Ability(AbilityBase):
    id: int
    class Config:
        from_attributes = True

# --- Equipment ---
class EquipmentBase(BaseModel):
    name: str
    cost: int
    rarity: str
    description: Optional[str] = None
    effects: Optional[str] = None  # JSON-строка с модификаторами

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: int
    class Config:
        from_attributes = True

# --- CharacterAbility ---
class CharacterAbilityBase(BaseModel):
    ability_id: int
    current_uses: int
    name: Optional[str] = None

class CharacterAbilityCreate(CharacterAbilityBase):
    pass

class CharacterAbility(CharacterAbilityBase):
    id: int
    ability: Ability
    class Config:
        from_attributes = True

# --- CharacterEquipment ---
class CharacterEquipmentBase(BaseModel):
    equipment_id: int
    is_equipped: bool = False
    name: Optional[str] = None

class CharacterEquipmentCreate(CharacterEquipmentBase):
    pass

class CharacterEquipment(CharacterEquipmentBase):
    id: int
    equipment: Equipment
    class Config:
        from_attributes = True

# --- Character ---
class CharacterBase(BaseModel):
    local_id: int
    name: str
    character_class_id: int
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
    pass

class Character(CharacterBase):
    id: int
    owner_id: int
    abilities: List[CharacterAbility] = []
    equipment: List[CharacterEquipment] = []
    character_class: Optional[CharacterClass] = None
    class Config:
        from_attributes = True

# --- User ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True
