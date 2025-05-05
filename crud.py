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

# --- CharacterClass ---
def create_character_class(db: Session, char_class: schemas.CharacterClassCreate):
    db_class = models.CharacterClass(**char_class.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def get_character_classes(db: Session):
    return db.query(models.CharacterClass).all()

def get_character_class(db: Session, class_id: int):
    return db.query(models.CharacterClass).filter(models.CharacterClass.id == class_id).first()

# --- ClassLevelAbility ---
def create_class_level_ability(db: Session, cla: schemas.ClassLevelAbilityCreate):
    db_cla = models.ClassLevelAbility(**cla.dict())
    db.add(db_cla)
    db.commit()
    db.refresh(db_cla)
    return db_cla

def get_class_level_abilities_for_class_and_level(db: Session, class_id: int, level: int):
    return db.query(models.ClassLevelAbility).filter_by(class_id=class_id, level=level).all()

# --- Ability ---
def create_ability(db: Session, ability: schemas.AbilityCreate):
    db_ability = models.Ability(**ability.dict())
    db.add(db_ability)
    db.commit()
    db.refresh(db_ability)
    return db_ability

def get_abilities(db: Session):
    return db.query(models.Ability).all()

def get_ability(db: Session, ability_id: int):
    return db.query(models.Ability).filter(models.Ability.id == ability_id).first()

# --- CharacterAbility ---
def add_ability_to_character(db: Session, character_id: int, ca: schemas.CharacterAbilityCreate):
    db_ca = models.CharacterAbility(character_id=character_id, **ca.dict())
    db.add(db_ca)
    db.commit()
    db.refresh(db_ca)
    return db_ca

def get_character_abilities(db: Session, character_id: int):
    return db.query(models.CharacterAbility).filter(models.CharacterAbility.character_id == character_id).all()

def character_has_ability(db: Session, character_id: int, ability_id: int):
    return db.query(models.CharacterAbility).filter_by(character_id=character_id, ability_id=ability_id).first()

# --- Equipment ---
def create_equipment(db: Session, equipment: schemas.EquipmentCreate):
    db_equipment = models.Equipment(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def get_equipments(db: Session):
    return db.query(models.Equipment).all()

def get_equipment(db: Session, equipment_id: int):
    return db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()

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

# --- Level Up Character ---
def level_up_character(db: Session, character_id: int):
    character = db.query(models.Character).filter_by(id=character_id).first()
    if not character:
        return None
    character.level += 1

    # Найти новые способности для этого класса и уровня
    new_abilities = get_class_level_abilities_for_class_and_level(db, character.character_class_id, character.level)
    for cla in new_abilities:
        # Проверить, есть ли уже эта способность у персонажа
        already = character_has_ability(db, character.id, cla.ability_id)
        if not already:
            db_ca = models.CharacterAbility(
                character_id=character.id,
                ability_id=cla.ability_id,
                current_uses=cla.ability.ability.uses if hasattr(cla, 'ability') and cla.ability else -1,
                name=cla.ability.ability.name if hasattr(cla, 'ability') and cla.ability else ""
            )
            db.add(db_ca)
    db.commit()
    db.refresh(character)
    return character
