from sqlalchemy.orm import Session
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

# --- Global Ability ---
def create_ability(db: Session, ability: schemas.AbilityCreate):
    db_ability = models.Ability(**ability.dict())
    db.add(db_ability)
    db.commit()
    db.refresh(db_ability)
    return db_ability

def get_abilities(db: Session):
    return db.query(models.Ability).all()

# --- CharacterAbility ---
def add_ability_to_character(db: Session, character_id: int, ca: schemas.CharacterAbilityCreate):
    db_ca = models.CharacterAbility(character_id=character_id, **ca.dict())
    db.add(db_ca)
    db.commit()
    db.refresh(db_ca)
    return db_ca

def get_character_abilities(db: Session, character_id: int):
    return db.query(models.CharacterAbility).filter(models.CharacterAbility.character_id == character_id).all()

# --- Global Equipment ---
def create_equipment(db: Session, equipment: schemas.EquipmentCreate):
    db_equipment = models.Equipment(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def get_equipments(db: Session):
    return db.query(models.Equipment).all()

# --- CharacterEquipment ---
def add_equipment_to_character(db: Session, character_id: int, ce: schemas.CharacterEquipmentCreate):
    db_ce = models.CharacterEquipment(character_id=character_id, **ce.dict())
    db.add(db_ce)
    db.commit()
    db.refresh(db_ce)
    return db_ce

def get_character_equipments(db: Session, character_id: int):
    return db.query(models.CharacterEquipment).filter(models.CharacterEquipment.character_id == character_id).all()

# --- Character ---
def create_character(db: Session, character: schemas.CharacterCreate, user_id: int):
    db_character = models.Character(**character.dict(), owner_id=user_id)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def get_characters_by_user(db: Session, user_id: int):
    return db.query(models.Character).filter(models.Character.owner_id == user_id).all()

def get_character(db: Session, character_id: int):
    return db.query(models.Character).filter(models.Character.id == character_id).first()
