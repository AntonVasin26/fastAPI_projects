"""Main FastAPI application for DnD project."""

import json
from typing import Any, Dict, List

from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

import models
import schemas
import crud
import auth
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """User login and token generation."""
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    """Get current user info."""
    return current_user

@app.post("/character_classes/", response_model=schemas.CharacterClass)
def create_character_class(
    char_class: schemas.CharacterClassCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    try:
        return crud.create_character_class(db, char_class)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    """Create a new character class."""
    try:
        return crud.create_character_class(db, char_class)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/character_classes/", response_model=List[schemas.CharacterClass])
def get_character_classes(db: Session = Depends(get_db)):
    """Get all character classes."""
    return crud.get_character_classes(db)

@app.get("/class_progression/", response_model=List[schemas.ClassProgression])
def get_class_progressions(db: Session = Depends(get_db)):
    """Get all class progressions."""
    return crud.get_class_progressions(db)

@app.get("/class_progression/{prog_id}", response_model=schemas.ClassProgression)
def get_class_progression(prog_id: int, db: Session = Depends(get_db)):
    """Get class progression by id."""
    prog = crud.get_class_progression(db, prog_id)
    if not prog:
        raise HTTPException(status_code=404, detail="Not found")
    return prog

@app.post("/class_progression/", response_model=schemas.ClassProgression)
def create_class_progression(
    prog: schemas.ClassProgressionCreate,
    db: Session = Depends(get_db)
):
    """Create a new class progression."""
    return crud.create_class_progression(db, prog)

@app.put("/class_progression/{prog_id}", response_model=schemas.ClassProgression)
def update_class_progression(
    prog_id: int,
    prog: schemas.ClassProgressionCreate,
    db: Session = Depends(get_db)
):
    """Update class progression."""
    updated = crud.update_class_progression(db, prog_id, prog)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@app.delete("/class_progression/{prog_id}", status_code=204)
def delete_class_progression(prog_id: int, db: Session = Depends(get_db)):
    """Delete class progression."""
    deleted = crud.delete_class_progression(db, prog_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(status_code=204)

@app.post("/abilities/", response_model=schemas.Ability)
def create_ability(
    ability: schemas.AbilityCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Create an ability."""
    try:
        return crud.create_ability(db, ability)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/abilities/", response_model=List[schemas.Ability])
def get_abilities(db: Session = Depends(get_db)):
    """Get all abilities."""
    return crud.get_abilities(db)

@app.post("/equipment/", response_model=schemas.Equipment)
def create_equipment(
    equipment: schemas.EquipmentCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Create equipment."""
    try:
        return crud.create_equipment(db, equipment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/equipment/", response_model=List[schemas.Equipment])
def get_equipments(db: Session = Depends(get_db)):
    """Get all equipment."""
    return crud.get_equipments(db)

@app.post("/characters/", response_model=schemas.Character)
def create_character(
    character: schemas.CharacterCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Create a character."""
    return crud.create_character(db, character, user.id)

@app.get("/characters/", response_model=List[schemas.Character])
def get_characters(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Get all characters of the current user."""
    return crud.get_characters_by_user(db, user.id)

@app.get("/characters/{local_id}", response_model=schemas.Character)
def get_character(
    local_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Get a character by local_id."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@app.delete("/characters/{local_id}", status_code=204)
def delete_character(
    local_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Delete a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    crud.delete_character(db, character.id)
    return Response(status_code=204)

@app.put("/characters/{local_id}", response_model=schemas.Character)
def update_character(
    local_id: int,
    character_update: schemas.CharacterCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Update a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.update_character(db, character.id, character_update)

@app.patch("/characters/{local_id}/set_level")
def set_character_level(
    local_id: int,
    new_level: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Set character level and sync abilities/bonuses."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    character = crud.sync_character_level(db, character, new_level)
    return character

@app.post("/characters/{local_id}/level_up")
def level_up_character(
    local_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Increase character level by 1 and sync abilities/bonuses."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    new_level = character.level + 1
    character = crud.sync_character_level(db, character, new_level)
    return character

@app.get("/characters/{local_id}/abilities/", response_model=List[schemas.CharacterAbility])
def get_character_abilities(
    local_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Get abilities of a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.get_character_abilities(db, character.id)

    @app.post("/characters/{local_id}/abilities/", response_model=schemas.CharacterAbility)
    def add_ability_to_character(
            local_id: int,
            ca: schemas.CharacterAbilityCreate,
            db: Session = Depends(get_db),
            user: schemas.User = Depends(get_current_user)
    ):
        character = crud.get_character_by_local_id(db, user.id, local_id)
        if character is None:
            raise HTTPException(status_code=404, detail="Character not found")
        try:
            return crud.add_ability_to_character(db, character.id, ca)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    """Add an ability to a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    try:
        return crud.add_ability_to_character(db, character.id, ca)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.delete("/characters/{local_id}/abilities/{ability_id}", status_code=204)
def delete_ability_from_character(
    local_id: int,
    ability_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Delete an ability from a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    result = crud.remove_ability




    """Delete an ability from a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    result = crud.remove_ability_from_character(db, character.id, ability_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Ability not found for this character")
    return Response(status_code=204)

@app.get("/characters/{local_id}/equipment/", response_model=List[schemas.CharacterEquipment])
def get_character_equipments(
    local_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Get all equipment of a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.get_character_equipments(db, character.id)

@app.get("/characters/{local_id}/equipment/equipped/",
         response_model=List[schemas.CharacterEquipment])
def get_character_equipped_items(
    local_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Get all equipped items of a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.get_character_equipped_items(db, character.id)

@app.post("/characters/{local_id}/equipment/", response_model=schemas.CharacterEquipment)
def add_equipment_to_character(
    local_id: int,
    ce: schemas.CharacterEquipmentCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Add equipment to a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.add_equipment_to_character(db, character.id, ce)

@app.delete("/characters/{local_id}/equipment/{equipment_id}", status_code=204)
def delete_equipment_from_character(
    local_id: int,
    equipment_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Delete equipment from a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    result = crud.remove_equipment_from_character(db, character.id, equipment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Equipment not found for this character")
    return Response(status_code=204)

@app.patch("/characters/{local_id}/equipment/{equipment_id}/equip",
           response_model=schemas.CharacterEquipment)
def equip_equipment(
    local_id: int,
    equipment_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Equip an item to a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    ce = crud.set_equipment_equipped(db, character.id, equipment_id, True)
    if ce is None:
        raise HTTPException(status_code=404, detail="Equipment not found for this character")
    return ce

@app.patch("/characters/{local_id}/equipment/{equipment_id}/unequip",
           response_model=schemas.CharacterEquipment)
def unequip_equipment(
    local_id: int,
    equipment_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Unequip an item from a character."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    ce = crud.set_equipment_equipped(db, character.id, equipment_id, False)
    if ce is None:
        raise HTTPException(status_code=404, detail="Equipment not found for this character")
    return ce

@app.get("/characters/{local_id}/effective_stats/", response_model=Dict[str, Any])
def get_effective_stats(
    local_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Get effective stats of a character with equipment bonuses."""
    character = crud.get_character_by_local_id(db, user.id, local_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    equipped_items = crud.get_character_equipped_items(db, character.id)
    stats = {
        "armor_class": character.armor_class,
        "strength": character.strength,
        "dexterity": character.dexterity,
        "constitution": character.constitution,
        "intelligence": character.intelligence,
        "wisdom": character.wisdom,
        "charisma": character.charisma,
        "max_hp": character.max_hp,
        "current_hp": character.current_hp,
    }
    for item in equipped_items:
        if item.equipment and item.equipment.effects:
            try:
                effects = json.loads(item.equipment.effects)
                for key, value in effects.items():
                    if key in stats:
                        stats[key] += value
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass

@app.post("/class_progression/{progression_id}/add_ability/{ability_id}")
def add_ability_to_progression(
    progression_id: int,
    ability_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Add an ability to a class progression (admin endpoint)."""
    cpa = models.ClassProgressionAbility(
        class_progression_id=progression_id,
        ability_id=ability_id
    )
    db.add(cpa)
    db.commit()
    db.refresh(cpa)
    return cpa

@app.delete("/class_progression/{progression_id}/remove_ability/{ability_id}", status_code=204)
def remove_ability_from_progression(
    progression_id: int,
    ability_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    """Remove an ability from a class progression (admin endpoint)."""
    cpa = db.query(models.ClassProgressionAbility).filter(
        models.ClassProgressionAbility.class_progression_id == progression_id,
        models.ClassProgressionAbility.ability_id == ability_id
    ).first()
    if not cpa:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(cpa)
    db.commit()
    return Response(status_code=204)

