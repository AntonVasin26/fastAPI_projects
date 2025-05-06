import os
import sys
import os as os2

# Удаляем test.db до создания engine/соединения
if os.path.exists("test.db"):
    os.remove("test.db")

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

sys.path.append(os2.path.abspath(os2.path.join(os2.path.dirname(__file__), '..')))

from main import app
from database import Base, engine
from fastapi.testclient import TestClient

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def get_token(username, password):
    """Получить JWT токен для пользователя."""
    client.post("/register", json={"username": username, "password": password})
    resp = client.post("/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def auth_headers(token):
    """Сформировать headers с авторизацией."""
    return {"Authorization": f"Bearer {token}"}

def create_class_and_character(headers):
    """Создать класс и персонажа, вернуть их id."""
    resp = client.post(
        "/character_classes/", json={"name": "Fighter", "description": "Strong"}, headers=headers
    )
    class_id = resp.json()["id"]
    char_data = {
        "local_id": 1,
        "name": "Hero",
        "character_class_id": class_id,
        "level": 1,
        "max_hp": 10,
        "current_hp": 10,
        "armor_class": 10,
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10
    }
    resp = client.post("/characters/", json=char_data, headers=headers)
    local_id = resp.json()["local_id"]
    return class_id, local_id

def test_equipment_crud_and_effects():
    """Тест CRUD для предметов и их влияние на характеристики персонажа."""
    token = get_token("equser", "eqpass")
    headers = auth_headers(token)
    _, local_id = create_class_and_character(headers)
    eq = {
        "name": "Chainmail",
        "cost": 50,
        "rarity": "uncommon",
        "description": "Heavy armor",
        "effects": '{"armor_class": 5, "strength": 2}'
    }
    resp = client.post("/equipment/", json=eq, headers=headers)
    assert resp.status_code == 200
    eq_id = resp.json()["id"]
    resp = client.get("/equipment/", headers=headers)
    assert any(e["id"] == eq_id for e in resp.json())
    resp = client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq_id, "is_equipped": False}, headers=headers)
    assert resp.status_code == 200
    resp = client.patch(f"/characters/{local_id}/equipment/{eq_id}/equip", headers=headers)
    assert resp.status_code == 200 and resp.json()["is_equipped"] is True
    resp = client.get(f"/characters/{local_id}/equipment/equipped/", headers=headers)
    assert any(e["equipment"]["id"] == eq_id for e in resp.json())
    resp = client.get(f"/characters/{local_id}/effective_stats/", headers=headers)
    stats = resp.json()
    assert stats["armor_class"] == 15
    assert stats["strength"] == 12
    resp = client.patch(f"/characters/{local_id}/equipment/{eq_id}/unequip", headers=headers)
    assert resp.status_code == 200 and resp.json()["is_equipped"] is False
    resp = client.get(f"/characters/{local_id}/effective_stats/", headers=headers)
    stats = resp.json()
    assert stats["armor_class"] == 10
    assert stats["strength"] == 10
    resp = client.delete(f"/characters/{local_id}/equipment/{eq_id}", headers=headers)
    assert resp.status_code == 204

def test_equipment_inventory():
    """Тест инвентаря и экипировки."""
    token = get_token("invuser", "invpass")
    headers = auth_headers(token)
    _, local_id = create_class_and_character(headers)
    eq1 = {"name": "Dagger", "cost": 2, "rarity": "common", "description": "Small blade", "effects": '{"dexterity": 1}'}
    eq2 = {"name": "Helmet", "cost": 5, "rarity": "common", "description": "Protects head", "effects": '{"armor_class": 1}'}
    resp1 = client.post("/equipment/", json=eq1, headers=headers)
    resp2 = client.post("/equipment/", json=eq2, headers=headers)
    eq1_id, eq2_id = resp1.json()["id"], resp2.json()["id"]
    client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq1_id, "is_equipped": False}, headers=headers)
    client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq2_id, "is_equipped": False}, headers=headers)
    client.patch(f"/characters/{local_id}/equipment/{eq1_id}/equip", headers=headers)
    client.patch(f"/characters/{local_id}/equipment/{eq2_id}/equip", headers=headers)
    resp = client.get(f"/characters/{local_id}/effective_stats/", headers=headers)
    stats = resp.json()
    assert stats["dexterity"] == 11
    assert stats["armor_class"] == 11
    resp = client.get(f"/characters/{local_id}/equipment/", headers=headers)
    assert len(resp.json()) == 2
    resp = client.get(f"/characters/{local_id}/equipment/equipped/", headers=headers)
    assert len(resp.json()) == 2

def test_character_class_crud():
    """Тест CRUD для классов персонажей."""
    token = get_token("classuser3", "classpass3")
    headers = auth_headers(token)
    resp = client.post("/character_classes/", json={"name": "Bard", "description": "A charming musician"}, headers=headers)
    assert resp.status_code == 200
    class_id = resp.json()["id"]
    resp = client.get("/character_classes/", headers=headers)
    assert resp.status_code == 200
    classes = resp.json()
    assert any(c["id"] == class_id and c["name"] == "Bard" for c in classes)

def test_class_progression_crud():
    """Тест CRUD для прогрессии класса."""
    token = get_token("proguser3", "progpass3")
    headers = auth_headers(token)
    resp = client.post("/character_classes/", json={"name": "Monk", "description": "Master of martial arts"}, headers=headers)
    assert resp.status_code == 200
    class_id = resp.json()["id"]
    prog = {
        "character_class_id": class_id,
        "level": 1,
        "hp_bonus": 6,
        "other_bonuses": '{"armor_class": 1}'
    }
    resp = client.post("/class_progression/", json=prog, headers=headers)
    assert resp.status_code == 200
    prog_id = resp.json()["id"]
    resp = client.get(f"/class_progression/{prog_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["character_class_id"] == class_id
    assert data["level"] == 1
    prog["hp_bonus"] = 8
    resp = client.put(f"/class_progression/{prog_id}", json=prog, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["hp_bonus"] == 8
    resp = client.get("/class_progression/", headers=headers)
    assert resp.status_code == 200
    assert any(p["id"] == prog_id for p in resp.json())
    resp = client.delete(f"/class_progression/{prog_id}", headers=headers)
    assert resp.status_code == 204
    resp = client.get(f"/class_progression/{prog_id}", headers=headers)
    assert resp.status_code == 404

def test_character_crud_and_access():
    """Тест CRUD и доступа к персонажам."""
    token = get_token("charuser3", "charpass3")
    headers = auth_headers(token)
    resp = client.post("/character_classes/", json={"name": "Druid", "description": "Nature priest"}, headers=headers)
    class_id = resp.json()["id"]
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
    resp = client.get("/characters/", headers=headers)
    assert resp.status_code == 200
    assert any(c["local_id"] == char_id for c in resp.json())
    resp = client.get(f"/characters/{char_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Radagast"
    char_data["name"] = "Radagast the Brown"
    resp = client.put(f"/characters/{char_id}", json=char_data, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Radagast the Brown"
    resp = client.delete(f"/characters/{char_id}", headers=headers)
    assert resp.status_code == 204
    resp = client.get(f"/characters/{char_id}", headers=headers)
    assert resp.status_code == 404

def test_no_access_to_other_users_character():
    """Тест ограничения доступа к чужим персонажам."""
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
    token2 = get_token("userB", "passB")
    headers2 = auth_headers(token2)
    resp = client.get(f"/characters/{char_id}", headers=headers2)
    assert resp.status_code == 404
    resp = client.delete(f"/characters/{char_id}", headers=headers2)
    assert resp.status_code == 404

def test_inventory_add_and_view():
    """Тест добавления предметов в инвентарь и просмотра."""
    token = get_token("invuser2", "invpass2")
    headers = auth_headers(token)
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

    eq1 = {"name": "Short Sword", "cost": 10, "rarity": "common", "description": "A short blade", "effects": '{"strength": 1}'}
    eq2 = {"name": "Cloak", "cost": 5, "rarity": "common", "description": "Helps to hide", "effects": '{"dexterity": 2}'}
    resp1 = client.post("/equipment/", json=eq1, headers=headers)
    resp2 = client.post("/equipment/", json=eq2, headers=headers)
    eq1_id, eq2_id = resp1.json()["id"], resp2.json()["id"]

    resp = client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq1_id, "is_equipped": False}, headers=headers)
    assert resp.status_code == 200
    resp = client.post(f"/characters/{local_id}/equipment/", json={"equipment_id": eq2_id, "is_equipped": False}, headers=headers)
    assert resp.status_code == 200

    resp = client.get(f"/characters/{local_id}/equipment/", headers=headers)
    eq_list = resp.json()
    assert len(eq_list) == 2
    ids = [item["equipment"]["id"] for item in eq_list]
    assert eq1_id in ids and eq2_id in ids

def test_inventory_equip_and_unequip():
    """Тест надевания и снятия предметов."""
    token = get_token("invuser3", "invpass3")
    headers = auth_headers(token)
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

    eq1 = {"name": "Shield", "cost": 15, "rarity": "uncommon", "description": "Blocks attacks", "effects": '{"armor_class": 2}'}
    eq2 = {"name": "Boots", "cost": 7, "rarity": "common", "description": "Fast running", "effects": '{"dexterity": 1}'}
    resp1 = client.post("/equipment/", json=eq1, headers=headers)
    resp2 = client.post("/equipment/", json=eq2, headers=headers)
    eq1_id, eq2_id = resp1.json()["id"], resp2.json()["id"]

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

def test_level_up_gives_abilities():
    """Тест автоматической выдачи способностей при повышении уровня."""
    token = get_token("lvluser", "lvlpass")
    headers = auth_headers(token)

    # Создать класс
    resp = client.post("/character_classes/", json={"name": "Sorcerer", "description": "Magic user"}, headers=headers)
    class_id = resp.json()["id"]

    # Создать способность
    resp = client.post("/abilities/", json={"name": "Fireball", "available_classes": "Sorcerer", "uses": 1, "description": "Throws fire"}, headers=headers)
    ability_id = resp.json()["id"]

    # Создать progression для 2 уровня
    progression = {
        "character_class_id": class_id,
        "level": 2,
        "hp_bonus": 5,
        "other_bonuses": '{"armor_class": 1}'
    }
    resp = client.post("/class_progression/", json=progression, headers=headers)
    progression_id = resp.json()["id"]

    # Связать progression и ability
    resp = client.post(f"/class_progression/{progression_id}/add_ability/{ability_id}", headers=headers)
    assert resp.status_code == 200

    # Создать персонажа 1 уровня
    char_data = {
        "local_id": 1,
        "name": "Gandalf",
        "character_class_id": class_id,
        "level": 1,
        "max_hp": 10,
        "current_hp": 10,
        "armor_class": 10,
        "strength": 8,
        "dexterity": 10,
        "constitution": 12,
        "intelligence": 16,
        "wisdom": 14,
        "charisma": 15
    }
    resp = client.post("/characters/", json=char_data, headers=headers)
    local_id = resp.json()["local_id"]

    # Повысить уровень
    resp = client.post(f"/characters/{local_id}/level_up", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["level"] == 2

    # Проверить, что способность появилась
    resp = client.get(f"/characters/{local_id}/abilities/", headers=headers)
    ability_ids = [a["ability"]["id"] for a in resp.json()]
    assert ability_id in ability_ids

#