"""CRUD operations for DnD project."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Return user object by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create new user."""
    hashed_password = user.password  # Для настоящего проекта используй хеширование!
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Authenticate user by username and password."""
    user = get_user_by_username(db, username)
    if not user or user.hashed_password != password:
        return None
    return user


def create_character_class(db: Session, char_class: schemas.CharacterClassCreate):
    """Create a new character class, checking for duplicates."""
    existing = db.query(models.CharacterClass).filter(models.CharacterClass.name == char_class.name).first()
    if existing:
        raise ValueError("Class with this name already exists")
    db_class = models.CharacterClass(**char_class.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class



def get_character_classes(db: Session) -> List[models.CharacterClass]:
    """Get all character classes."""
    return db.query(models.CharacterClass).all()


def update_character_class(db: Session, class_id: int, char_class: schemas.CharacterClassCreate) -> Optional[models.CharacterClass]:
    """Update character class by id."""
    db_class = db.query(models.CharacterClass).filter(models.CharacterClass.id == class_id).first()
    if not db_class:
        return None
    for field, value in char_class.dict().items():
        setattr(db_class, field, value)
    db.commit()
    db.refresh(db_class)
    return db_class


def delete_character_class(db: Session, class_id: int) -> Optional[models.CharacterClass]:
    """Delete character class by id."""
    db_class = db.query(models.CharacterClass).filter(models.CharacterClass.id == class_id).first()
    if not db_class:
        return None
    db.delete(db_class)
    db.commit()
    return db_class


def get_class_progressions(db: Session) -> List[models.ClassProgression]:
    """Get all class progressions."""
    return db.query(models.ClassProgression).all()


def get_class_progression(db: Session, progression_id: int) -> Optional[models.ClassProgression]:
    """Get class progression by id."""
    return db.query(models.ClassProgression).filter(models.ClassProgression.id == progression_id).first()


def create_class_progression(db: Session, progression: schemas.ClassProgressionCreate) -> models.ClassProgression:
    """Create a new class progression."""
    db_prog = models.ClassProgression(**progression.dict())
    db.add(db_prog)
    db.commit()
    db.refresh(db_prog)
    return db_prog


def update_class_progression(db: Session, progression_id: int, progression: schemas.ClassProgressionCreate) -> Optional[models.ClassProgression]:
    """Update class progression by id."""
    db_prog = db.query(models.ClassProgression).filter(models.ClassProgression.id == progression_id).first()
    if not db_prog:
        return None
    for field, value in progression.dict().items():
        setattr(db_prog, field, value)
    db.commit()
    db.refresh(db_prog)
    return db_prog


def delete_class_progression(db: Session, progression_id: int) -> Optional[models.ClassProgression]:
    """Delete class progression by id."""
    db_prog = db.query(models.ClassProgression).filter(models.ClassProgression.id == progression_id).first()
    if not db_prog:
        return None
    db.delete(db_prog)
    db.commit()
    return db_prog


def get_progression_for_class_and_level(db: Session, character_class_id: int, level: int) -> Optional[models.ClassProgression]:
    """Get class progression for a given class and level."""
    return db.query(models.ClassProgression).filter(
        models.ClassProgression.character_class_id == character_class_id,
        models.ClassProgression.level == level
    ).first()


def create_ability(db: Session, ability: schemas.AbilityCreate) -> models.Ability:
    """Create a new ability, checking for duplicates by name."""
    existing = db.query(models.Ability).filter(models.Ability.name == ability.name).first()
    if existing:
        raise ValueError("Ability with this name already exists")
    db_ability = models.Ability(**ability.dict())
    db.add(db_ability)
    db.commit()
    db.refresh(db_ability)
    return db_ability



def get_abilities(db: Session) -> List[models.Ability]:
    """Get all abilities."""
    return db.query(models.Ability).all()


def create_equipment(db: Session, equipment: schemas.EquipmentCreate) -> models.Equipment:
    """Create new equipment, checking for duplicates by name."""
    existing = db.query(models.Equipment).filter(models.Equipment.name == equipment.name).first()
    if existing:
        raise ValueError("Equipment with this name already exists")
    db_equipment = models.Equipment(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment



def get_equipments(db: Session) -> List[models.Equipment]:
    """Get all equipment."""
    return db.query(models.Equipment).all()


def create_character(db: Session, character: schemas.CharacterCreate, user_id: int) -> models.Character:
    """Create a new character for a user."""
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


def get_characters_by_user(db: Session, user_id: int) -> List[models.Character]:
    """Get all characters for a user."""
    return db.query(models.Character).filter(models.Character.owner_id == user_id).all()


def get_character_by_local_id(db: Session, user_id: int, local_id: int) -> Optional[models.Character]:
    """Get a character by user id and local_id."""
    return db.query(models.Character).filter(
        models.Character.owner_id == user_id,
        models.Character.local_id == local_id
    ).first()


def update_character(db: Session, character_id: int, character_update: schemas.CharacterCreate) -> Optional[models.Character]:
    """Update a character by id."""
    character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if not character:
        return None
    for field, value in character_update.dict().items():
        if field != "local_id":
            setattr(character, field, value)
    db.commit()
    db.refresh(character)
    return character


def delete_character(db: Session, character_id: int) -> None:
    """Delete a character by id."""
    character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if character:
        db.delete(character)
        db.commit()


def get_character_abilities(db: Session, character_id: int) -> List[models.CharacterAbility]:
    """Get all abilities of a character."""
    return db.query(models.CharacterAbility).filter(models.CharacterAbility.character_id == character_id).all()


def add_ability_to_character(db: Session, character_id: int, ca: schemas.CharacterAbilityCreate) -> models.CharacterAbility:
    """Add an ability to a character, checking for duplicates."""
    existing = db.query(models.CharacterAbility).filter(
        models.CharacterAbility.character_id == character_id,
        models.CharacterAbility.ability_id == ca.ability_id
    ).first()
    if existing:
        raise ValueError("This character already has this ability")
    db_ca = models.CharacterAbility(character_id=character_id, **ca.dict())
    db.add(db_ca)
    db.commit()
    db.refresh(db_ca)
    return db_ca



def remove_ability_from_character(db: Session, character_id: int, ability_id: int) -> Optional[models.CharacterAbility]:
    """Remove an ability from a character."""
    db_ca = db.query(models.CharacterAbility).filter(
        models.CharacterAbility.character_id == character_id,
        models.CharacterAbility.ability_id == ability_id
    ).first()
    if not db_ca:
        return None
    db.delete(db_ca)
    db.commit()
    return db_ca


def get_character_equipments(db: Session, character_id: int) -> List[models.CharacterEquipment]:
    """Get all equipment of a character."""
    return db.query(models.CharacterEquipment).filter(models.CharacterEquipment.character_id == character_id).all()


def get_character_equipped_items(db: Session, character_id: int) -> List[models.CharacterEquipment]:
    """Get all equipped items of a character."""
    return db.query(models.CharacterEquipment).filter(
        models.CharacterEquipment.character_id == character_id,
        models.CharacterEquipment.is_equipped.is_(True)
    ).all()


def add_equipment_to_character(db: Session, character_id: int, ce: schemas.CharacterEquipmentCreate) -> models.CharacterEquipment:
    """Add equipment to a character."""
    db_ce = models.CharacterEquipment(character_id=character_id, **ce.dict())
    db.add(db_ce)
    db.commit()
    db.refresh(db_ce)
    return db_ce


def remove_equipment_from_character(db: Session, character_id: int, equipment_id: int) -> Optional[models.CharacterEquipment]:
    """Remove equipment from a character."""
    db_ce = db.query(models.CharacterEquipment).filter(
        models.CharacterEquipment.character_id == character_id,
        models.CharacterEquipment.equipment_id == equipment_id
    ).first()
    if not db_ce:
        return None
    db.delete(db_ce)
    db.commit()
    return db_ce


def set_equipment_equipped(db: Session, character_id: int, equipment_id: int, equipped: bool) -> Optional[models.CharacterEquipment]:
    """Set equipment as equipped/unequipped for a character."""
    db_ce = db.query(models.CharacterEquipment).filter(
        models.CharacterEquipment.character_id == character_id,
        models.CharacterEquipment.equipment_id == equipment_id
    ).first()
    if not db_ce:
        return None
    db_ce.is_equipped = equipped
    db.commit()
    db.refresh(db_ce)
    return db_ce


def sync_character_level(db: Session, character: models.Character, new_level: int) -> models.Character:
    """Sync character's abilities and bonuses with class progression for new level."""
    db.query(models.CharacterAbility).filter(models.CharacterAbility.character_id == character.id).delete()
    for lvl in range(1, new_level + 1):
        prog = get_progression_for_class_and_level(db, character.character_class_id, lvl)
        if prog and prog.abilities:
            import json
            try:
                abilities = json.loads(prog.abilities)
                for ab_id in abilities:
                    db.add(models.CharacterAbility(character_id=character.id, ability_id=ab_id))
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass
        # Здесь можно добавить обработку других бонусов, например, HP
    character.level = new_level
    db.commit()
    db.refresh(character)
    return character
