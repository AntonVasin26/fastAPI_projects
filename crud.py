from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- User ---
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

# --- CharacterClass ---
def get_character_class_by_name(db: Session, name: str):
    return db.query(models.CharacterClass).filter(models.CharacterClass.name == name).first()

def create_character_class(db: Session, char_class: schemas.CharacterClassCreate):
    if get_character_class_by_name(db, char_class.name):
        raise ValueError("Character class with this name already exists")
    db_class = models.CharacterClass(**char_class.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def get_character_classes(db: Session):
    return db.query(models.CharacterClass).all()

# --- Ability ---
def get_ability_by_name(db: Session, name: str):
    return db.query(models.Ability).filter(models.Ability.name == name).first()

def create_ability(db: Session, ability: schemas.AbilityCreate):
    if get_ability_by_name(db, ability.name):
        raise ValueError("Ability with this name already exists")
    db_ability = models.Ability(**ability.dict())
    db.add(db_ability)
    db.commit()
    db.refresh(db_ability)
    return db_ability

def get_abilities(db: Session):
    return db.query(models.Ability).all()

# --- Equipment ---
def get_equipment_by_name(db: Session, name: str):
    return db.query(models.Equipment).filter(models.Equipment.name == name).first()

def create_equipment(db: Session, equipment: schemas.EquipmentCreate):
    if get_equipment_by_name(db, equipment.name):
        raise ValueError("Equipment with this name already exists")
    db_equipment = models.Equipment(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def get_equipments(db: Session):
    return db.query(models.Equipment).all()

# --- Character ---
def create_character(db: Session, character: schemas.CharacterCreate, user_id: int):
    last_local = db.query(func.max(models.Character.local_id)).filter(models.Character.owner_id == user_id).scalar()
    next_local_id = 1 if last_local is None else last_local + 1
    db_character = models.Character(
        **character.dict(exclude={"local_id"}),
        owner_id=user_id,
        local_id=next_local_id
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def get_characters_by_user(db: Session, user_id: int):
    return db.query(models.Character).filter(models.Character.owner_id == user_id).all()

def get_character_by_local_id(db: Session, owner_id: int, local_id: int):
    return db.query(models.Character).filter(
        models.Character.owner_id == owner_id,
        models.Character.local_id == local_id
    ).first()

def delete_character(db: Session, character_id: int):
    character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if character:
        db.delete(character)
        db.commit()

def update_character(db: Session, character_id: int, character_update: schemas.CharacterCreate):
    character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if not character:
        return None
    for field, value in character_update.dict().items():
        if field != "local_id":
            setattr(character, field, value)
    db.commit()
    db.refresh(character)
    return character

# --- CharacterAbility ---
def add_ability_to_character(db: Session, character_id: int, ca: schemas.CharacterAbilityCreate):
    exists = db.query(models.CharacterAbility).filter_by(character_id=character_id, ability_id=ca.ability_id).first()
    if exists:
        raise ValueError("This character already has this ability")
    db_ca = models.CharacterAbility(character_id=character_id, **ca.dict())
    db.add(db_ca)
    db.commit()
    db.refresh(db_ca)
    return db_ca

def get_character_abilities(db: Session, character_id: int):
    return db.query(models.CharacterAbility).filter(models.CharacterAbility.character_id == character_id).all()

def remove_ability_from_character(db: Session, character_id: int, ability_id: int):
    ca = db.query(models.CharacterAbility).filter_by(character_id=character_id, ability_id=ability_id).first()
    if not ca:
        return None
    db.delete(ca)
    db.commit()
    return ca

# --- CharacterEquipment ---
def add_equipment_to_character(db: Session, character_id: int, ce: schemas.CharacterEquipmentCreate):
    db_ce = models.CharacterEquipment(character_id=character_id, **ce.dict())
    db.add(db_ce)
    db.commit()
    db.refresh(db_ce)
    return db_ce

def get_character_equipments(db: Session, character_id: int):
    return db.query(models.CharacterEquipment).filter(models.CharacterEquipment.character_id == character_id).all()

def get_character_equipped_items(db: Session, character_id: int):
    return db.query(models.CharacterEquipment).filter_by(character_id=character_id, is_equipped=True).all()

def remove_equipment_from_character(db: Session, character_id: int, equipment_id: int):
    ce = db.query(models.CharacterEquipment).filter_by(character_id=character_id, equipment_id=equipment_id).first()
    if not ce:
        return None
    db.delete(ce)
    db.commit()
    return ce

def set_equipment_equipped(db: Session, character_id: int, equipment_id: int, equipped: bool):
    ce = db.query(models.CharacterEquipment).filter_by(character_id=character_id, equipment_id=equipment_id).first()
    if not ce:
        return None
    ce.is_equipped = equipped
    db.commit()
    db.refresh(ce)
    return ce
