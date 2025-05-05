from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt

import models, schemas, crud, auth
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

# --- Авторизация и регистрация ---
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

# --- CharacterClass ---
@app.post("/character_classes/", response_model=schemas.CharacterClass)
def create_character_class(char_class: schemas.CharacterClassCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    try:
        return crud.create_character_class(db, char_class)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/character_classes/", response_model=List[schemas.CharacterClass])
def get_character_classes(db: Session = Depends(get_db)):
    return crud.get_character_classes(db)

# --- ClassLevelAbility ---
@app.post("/class_level_abilities/", response_model=schemas.ClassLevelAbility)
def create_class_level_ability(cla: schemas.ClassLevelAbilityCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.create_class_level_ability(db, cla)

# --- Ability ---
@app.post("/abilities/", response_model=schemas.Ability)
def create_ability(ability: schemas.AbilityCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    try:
        return crud.create_ability(db, ability)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/abilities/", response_model=List[schemas.Ability])
def get_abilities(db: Session = Depends(get_db)):
    return crud.get_abilities(db)

# --- Equipment ---
@app.post("/equipment/", response_model=schemas.Equipment)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    try:
        return crud.create_equipment(db, equipment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/equipment/", response_model=List[schemas.Equipment])
def get_equipments(db: Session = Depends(get_db)):
    return crud.get_equipments(db)

# --- Character ---
@app.post("/characters/", response_model=schemas.Character)
def create_character(character: schemas.CharacterCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.create_character(db, character, user.id)

@app.get("/characters/", response_model=List[schemas.Character])
def get_characters(db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.get_characters_by_user(db, user.id)

@app.get("/characters/{character_id}", response_model=schemas.Character)
def get_character(character_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    character = crud.get_character(db, character_id)
    if character is None or character.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@app.post("/characters/{character_id}/levelup", response_model=schemas.Character)
def level_up_character(character_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    character = crud.get_character(db, character_id)
    if character is None or character.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.level_up_character(db, character_id)

# --- CharacterAbility ---
@app.post("/characters/{character_id}/abilities/", response_model=schemas.CharacterAbility)
def add_ability_to_character(character_id: int, ca: schemas.CharacterAbilityCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    character = crud.get_character(db, character_id)
    if character is None or character.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.add_ability_to_character(db, character_id, ca)

@app.get("/characters/{character_id}/abilities/", response_model=List[schemas.CharacterAbility])
def get_character_abilities(character_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    character = crud.get_character(db, character_id)
    if character is None or character.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.get_character_abilities(db, character_id)

# --- CharacterEquipment ---

@app.post("/characters/{character_id}/equipment/", response_model=schemas.CharacterEquipment)
def add_equipment_to_character(
    character_id: int,
    ce: schemas.CharacterEquipmentCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    character = crud.get_character(db, character_id)
    if character is None or character.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.add_equipment_to_character(db, character_id, ce)

@app.get("/characters/{character_id}/equipment/", response_model=List[schemas.CharacterEquipment])
def get_character_equipments(
    character_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    character = crud.get_character(db, character_id)
    if character is None or character.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.get_character_equipments(db, character_id)
