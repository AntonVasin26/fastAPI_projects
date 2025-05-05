import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

# некоторые изменения в сявзяи с проблемами с путями
import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def get_token(username="testuser", password="testpass"):
    client.post("/register", json={"username": username, "password": password})
    resp = client.post("/token", data={"username": username, "password": password})
    return resp.json()["access_token"]

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def create_class_and_character(headers):
    # Создать класс
    resp = client.post("/character_classes/", json={"name": "Hero", "description": "Test"}, headers=headers)
    class_id = resp.json()["id"]
    # Создать персонажа
    char_data = {
        "local_id": 1,
        "name": "Arthur",
        "character_class_id": class_id,
        "level": 1,
        "max_hp": 15,
        "current_hp": 15,
        "armor_class": 10,
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10
    }
    resp = client.post("/characters/", json=char_data, headers=headers)
    return class_id, resp.json()["local_id"]

def test_ability_crud():
    token = get_token("abiluser", "abilpass")
    headers = auth_headers(token)
    # Создать абилку
    resp = client.post("/abilities/", json={
        "name": "Fireball",
        "available_classes": "Hero",
        "uses": 3,
        "description": "Deals fire damage"
    }, headers=headers)
    assert resp.status_code == 200
    ab_id = resp.json()["id"]
    # Получить список абилок
    resp = client.get("/abilities/", headers=headers)
    assert resp.status_code == 200
    assert any(a["id"] == ab_id for a in resp.json())

def test_add_and_remove_ability_to_character():
    token = get_token("abiluser2", "abilpass2")
    headers = auth_headers(token)
    # Абилка
    resp = client.post("/abilities/", json={
        "name": "Heal",
        "available_classes": "Hero",
        "uses": 2,
        "description": "Heals wounds"
    }, headers=headers)
    ab_id = resp.json()["id"]
    # Класс и персонаж
    class_id, local_id = create_class_and_character(headers)
    # Добавить абилку персонажу
    resp = client.post(f"/characters/{local_id}/abilities/", json={"ability_id": ab_id, "current_uses": 2}, headers=headers)
    assert resp.status_code == 200
    # Проверить, что абилка есть
    resp = client.get(f"/characters/{local_id}/abilities/", headers=headers)
    assert any(a["ability"]["id"] == ab_id for a in resp.json())
    # Удалить абилку
    resp = client.delete(f"/characters/{local_id}/abilities/{ab_id}", headers=headers)
    assert resp.status_code == 204
    # Проверить, что абилки нет
    resp = client.get(f"/characters/{local_id}/abilities/", headers=headers)
    assert not any(a["ability"]["id"] == ab_id for a in resp.json())

def test_equipment_crud_and_equip():
    token = get_token("equipuser", "equippass")
    headers = auth_headers(token)
    class_id, local_id = create_class_and_character(headers)
    # Создать предмет
    eq = {
        "name": "Chainmail",
        "cost": 50,
        "rarity": "uncommon",
        "description": "Heavy armor",
        "effects": '{"armor_class": 5, "strength": 2}'
    }
    resp = client.post("/equipment/", json=eq, headers=headers)
    eq_id = resp.json()["id"]
    # Получить список снаряжения
    resp = client.get("/equipment/", headers=headers)
    assert any(e["id"] == eq_id for e in resp.json())
    # Добавить предмет персонажу
    resp = client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq_id, "is_equipped": False}, headers=headers)
    ce_id = resp.json()["id"]
    # Надеть предмет
    resp = client.patch(f"/characters/{local_id}/equipment/{eq_id}/equip", headers=headers)
    assert resp.status_code == 200 and resp.json()["is_equipped"] is True
    # Проверить надетые предметы
    resp = client.get(f"/characters/{local_id}/equipment/equipped/", headers=headers)
    assert any(e["equipment"]["id"] == eq_id for e in resp.json())
    # Проверить эффективные характеристики
    resp = client.get(f"/characters/{local_id}/effective_stats/", headers=headers)
    stats = resp.json()
    assert stats["armor_class"] == 15  # 10 базовый + 5 за Chainmail
    assert stats["strength"] == 12     # 10 базовый + 2 за Chainmail
    # Снять предмет
    resp = client.patch(f"/characters/{local_id}/equipment/{eq_id}/unequip", headers=headers)
    assert resp.status_code == 200 and resp.json()["is_equipped"] is False
    # Проверить что характеристики вернулись к базовым
    resp = client.get(f"/characters/{local_id}/effective_stats/", headers=headers)
    stats = resp.json()
    assert stats["armor_class"] == 10
    assert stats["strength"] == 10
    # Удалить предмет из инвентаря
    resp = client.delete(f"/characters/{local_id}/equipment/{eq_id}", headers=headers)
    assert resp.status_code == 204

def test_equipment_inventory():
    token = get_token("invuser", "invpass")
    headers = auth_headers(token)
    class_id, local_id = create_class_and_character(headers)
    # Создать два предмета
    eq1 = {"name": "Dagger", "cost": 2, "rarity": "common", "description": "Small blade", "effects": '{"dexterity": 1}'}
    eq2 = {"name": "Helmet", "cost": 5, "rarity": "common", "description": "Protects head", "effects": '{"armor_class": 1}'}
    resp1 = client.post("/equipment/", json=eq1, headers=headers)
    resp2 = client.post("/equipment/", json=eq2, headers=headers)
    eq1_id, eq2_id = resp1.json()["id"], resp2.json()["id"]
    # Добавить оба предмета в инвентарь
    client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq1_id, "is_equipped": False}, headers=headers)
    client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq2_id, "is_equipped": False}, headers=headers)
    # Надеть оба
    client.patch(f"/characters/{local_id}/equipment/{eq1_id}/equip", headers=headers)
    client.patch(f"/characters/{local_id}/equipment/{eq2_id}/equip", headers=headers)
    # Проверить эффективные характеристики
    resp = client.get(f"/characters/{local_id}/effective_stats/", headers=headers)
    stats = resp.json()
    assert stats["dexterity"] == 11
    assert stats["armor_class"] == 11
    # Проверить инвентарь
    resp = client.get(f"/characters/{local_id}/equipment/", headers=headers)
    assert len(resp.json()) == 2
    # Проверить только надетые предметы
    resp = client.get(f"/characters/{local_id}/equipment/equipped/", headers=headers)
    assert len(resp.json()) == 2

# проверка классов

def test_character_class_crud():
    token = get_token("classuser3", "classpass3")
    headers = auth_headers(token)
    # Создать класс
    resp = client.post("/character_classes/", json={"name": "Bard", "description": "A charming musician"}, headers=headers)
    assert resp.status_code == 200
    class_id = resp.json()["id"]
    # Получить список классов
    resp = client.get("/character_classes/", headers=headers)
    assert resp.status_code == 200
    classes = resp.json()
    assert any(c["id"] == class_id and c["name"] == "Bard" for c in classes)

# Проверка прогресси уровня

def test_class_progression_crud():
    token = get_token("proguser3", "progpass3")
    headers = auth_headers(token)
    # Создать класс персонажа
    resp = client.post("/character_classes/", json={"name": "Monk", "description": "Master of martial arts"}, headers=headers)
    assert resp.status_code == 200
    class_id = resp.json()["id"]

    # Создать прогрессию для уровня 1
    prog = {
        "character_class_id": class_id,
        "level": 1,
        "hp_bonus": 6,
        "abilities": "[]",
        "other_bonuses": '{"armor_class": 1}'
    }
    resp = client.post("/class_progression/", json=prog, headers=headers)
    assert resp.status_code == 200
    prog_id = resp.json()["id"]

    # Получить прогрессию по id
    resp = client.get(f"/class_progression/{prog_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["character_class_id"] == class_id
    assert data["level"] == 1

    # Обновить прогрессию
    prog["hp_bonus"] = 8
    resp = client.put(f"/class_progression/{prog_id}", json=prog, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["hp_bonus"] == 8

    # Получить список всей прогрессии
    resp = client.get("/class_progression/", headers=headers)
    assert resp.status_code == 200
    assert any(p["id"] == prog_id for p in resp.json())

    # Удалить прогрессию
    resp = client.delete(f"/class_progression/{prog_id}", headers=headers)
    assert resp.status_code == 204

    # Проверить, что прогрессии больше нет
    resp = client.get(f"/class_progression/{prog_id}", headers=headers)
    assert resp.status_code == 404

def test_character_crud_and_access():
    # Регистрация и создание класса персонажа
    token = get_token("charuser3", "charpass3")
    headers = auth_headers(token)
    resp = client.post("/character_classes/", json={"name": "Druid", "description": "Nature priest"}, headers=headers)
    class_id = resp.json()["id"]

    # Создание персонажа
    char_data = {
        "local_id": 1,
        "name": "Radagast",
        "character_class_id": class_id,
        "level": 1,
        "max_hp": 12,
        "current_hp": 12,
        "armor_class": 11,
        "strength": 8,
        "dexterity": 13,
        "constitution": 12,
        "intelligence": 14,
        "wisdom": 16,
        "charisma": 10
    }
    resp = client.post("/characters/", json=char_data, headers=headers)
    assert resp.status_code == 200
    char_id = resp.json()["local_id"]

    # Получение списка персонажей пользователя
    resp = client.get("/characters/", headers=headers)
    assert resp.status_code == 200
    assert any(c["local_id"] == char_id for c in resp.json())

    # Получение персонажа по local_id
    resp = client.get(f"/characters/{char_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Radagast"

    # Обновление персонажа (смена имени)
    char_data["name"] = "Radagast the Brown"
    resp = client.put(f"/characters/{char_id}", json=char_data, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Radagast the Brown"

    # Удаление персонажа
    resp = client.delete(f"/characters/{char_id}", headers=headers)
    assert resp.status_code == 204

    # Проверка отсутствия персонажа
    resp = client.get(f"/characters/{char_id}", headers=headers)
    assert resp.status_code == 404


#Тест персонажей

def test_no_access_to_other_users_character():
    # Пользователь 1 создаёт персонажа
    token1 = get_token("userA", "passA")
    headers1 = auth_headers(token1)
    resp = client.post("/character_classes/", json={"name": "Ranger", "description": ""}, headers=headers1)
    class_id = resp.json()["id"]
    char_data = {
        "local_id": 1,
        "name": "Legolas",
        "character_class_id": class_id,
        "level": 1,
        "max_hp": 10,
        "current_hp": 10,
        "armor_class": 13,
        "strength": 10,
        "dexterity": 17,
        "constitution": 12,
        "intelligence": 12,
        "wisdom": 14,
        "charisma": 11
    }
    resp = client.post("/characters/", json=char_data, headers=headers1)
    assert resp.status_code == 200
    char_id = resp.json()["local_id"]

    # Пользователь 2 пытается получить чужого персонажа
    token2 = get_token("userB", "passB")
    headers2 = auth_headers(token2)
    resp = client.get(f"/characters/{char_id}", headers=headers2)
    assert resp.status_code == 404

    # Пользователь 2 пытается удалить чужого персонажа
    resp = client.delete(f"/characters/{char_id}", headers=headers2)
    assert resp.status_code == 404

#Тесты инвенторя
def test_inventory_add_and_view():
    token = get_token("invuser2", "invpass2")
    headers = auth_headers(token)
    # Создать класс и персонажа
    resp = client.post("/character_classes/", json={"name": "Thief", "description": "Stealthy"}, headers=headers)
    class_id = resp.json()["id"]
    char_data = {
        "local_id": 1,
        "name": "Garrett",
        "character_class_id": class_id,
        "level": 1,
        "max_hp": 8,
        "current_hp": 8,
        "armor_class": 12,
        "strength": 9,
        "dexterity": 15,
        "constitution": 10,
        "intelligence": 13,
        "wisdom": 11,
        "charisma": 12
    }
    resp = client.post("/characters/", json=char_data, headers=headers)
    local_id = resp.json()["local_id"]

    # Создать два предмета
    eq1 = {"name": "Short Sword", "cost": 10, "rarity": "common", "description": "A short blade", "effects": '{"strength": 1}'}
    eq2 = {"name": "Cloak", "cost": 5, "rarity": "common", "description": "Helps to hide", "effects": '{"dexterity": 2}'}
    resp1 = client.post("/equipment/", json=eq1, headers=headers)
    resp2 = client.post("/equipment/", json=eq2, headers=headers)
    eq1_id, eq2_id = resp1.json()["id"], resp2.json()["id"]

    # Добавить оба предмета в инвентарь
    resp = client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq1_id, "is_equipped": False}, headers=headers)
    assert resp.status_code == 200
    resp = client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq2_id, "is_equipped": False}, headers=headers)
    assert resp.status_code == 200

    # Проверить что оба предмета в инвентаре
    resp = client.get(f"/characters/{local_id}/equipment/", headers=headers)
    eq_list = resp.json()
    assert len(eq_list) == 2
    ids = [item["equipment"]["id"] for item in eq_list]
    assert eq1_id in ids and eq2_id in ids

def test_inventory_equip_and_unequip():
    token = get_token("invuser3", "invpass3")
    headers = auth_headers(token)
    # Создать класс и персонажа
    resp = client.post("/character_classes/", json={"name": "Knight", "description": ""}, headers=headers)
    class_id = resp.json()["id"]
    char_data = {
        "local_id": 1,
        "name": "Lancelot",
        "character_class_id": class_id,
        "level": 1,
        "max_hp": 14,
        "current_hp": 14,
        "armor_class": 15,
        "strength": 13,
        "dexterity": 12,
        "constitution": 12,
        "intelligence": 10,
        "wisdom": 11,
        "charisma": 14
    }
    resp = client.post("/characters/", json=char_data, headers=headers)
    local_id = resp.json()["local_id"]

    # Создать предметы
    eq1 = {"name": "Shield", "cost": 15, "rarity": "uncommon", "description": "Blocks attacks", "effects": '{"armor_class": 2}'}
    eq2 = {"name": "Boots", "cost": 7, "rarity": "common", "description": "Fast running", "effects": '{"dexterity": 1}'}
    resp1 = client.post("/equipment/", json=eq1, headers=headers)
    resp2 = client.post("/equipment/", json=eq2, headers=headers)
    eq1_id, eq2_id = resp1.json()["id"], resp2.json()["id"]

    # Добавить в инвентарь
    client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq1_id, "is_equipped": False}, headers=headers)
    client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq2_id, "is_equipped": False}, headers=headers)

    # Надеть только Shield
    resp = client.patch(f"/characters/{local_id}/equipment/{eq1_id}/equip", headers=headers)
    assert resp.status_code == 200
    # Проверить только Shield надет
    resp = client.get(f"/characters/{local_id}/equipment/equipped/", headers=headers)
    equipped = resp.json()
    assert len(equipped) == 1
    assert equipped[0]["equipment"]["id"] == eq1_id

    # Надеть Boots, теперь оба надеты
    resp = client.patch(f"/characters/{local_id}/equipment/{eq2_id}/equip", headers=headers)
    resp = client.get(f"/characters/{local_id}/equipment/equipped/", headers=headers)
    equipped = resp.json()
    ids = [item["equipment"]["id"] for item in equipped]
    assert eq1_id in ids and eq2_id in ids

    # Снять Shield
    resp = client.patch(f"/characters/{local_id}/equipment/{eq1_id}/unequip", headers=headers)
    resp = client.get(f"/characters/{local_id}/equipment/equipped/", headers=headers)
    equipped = resp.json()
    ids = [item["equipment"]["id"] for item in equipped]
    assert eq1_id not in ids and eq2_id in ids

    # Удалить Boots из инвентаря
    resp = client.delete(f"/characters/{local_id}/equipment/{eq2_id}", headers=headers)
    assert resp.status_code == 204
    # Проверить что Boots нет ни в инвентаре, ни в надетых
    resp = client.get(f"/characters/{local_id}/equipment/", headers=headers)
    ids = [item["equipment"]["id"] for item in resp.json()]
    assert eq2_id not in ids
