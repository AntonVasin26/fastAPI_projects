from pydantic import BaseModel, Field
from typing import List, Optional

# Глобальная способность
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
        orm_mode = True

# Индивидуальная способность персонажа
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
        orm_mode = True

# Глобальное снаряжение
class EquipmentBase(BaseModel):
    name: str
    cost: int
    rarity: str
    description: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: int
    class Config:
        orm_mode = True

# Индивидуальное снаряжение персонажа
class CharacterEquipmentBase(BaseModel):
    equipment_id: int
    is_equipped: int = 0
    name: Optional[str] = None

class CharacterEquipmentCreate(CharacterEquipmentBase):
    pass

class CharacterEquipment(CharacterEquipmentBase):
    id: int
    equipment: Equipment
    class Config:
        orm_mode = True

# Персонаж
class CharacterBase(BaseModel):
    name: str
    race: str
    background: str
    character_class: str
    level: int = Field(ge=1)
    armor_class: int
    strength: int = Field(ge=1, le=30)
    dexterity: int = Field(ge=1, le=30)
    constitution: int = Field(ge=1, le=30)
    intelligence: int = Field(ge=1, le=30)
    wisdom: int = Field(ge=1, le=30)
    charisma: int = Field(ge=1, le=30)

class CharacterCreate(CharacterBase):
    pass

class Character(CharacterBase):
    id: int
    abilities: List[CharacterAbility] = []
    equipment: List[CharacterEquipment] = []
    owner_id: int
    class Config:
        orm_mode = True

# Пользователь
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True