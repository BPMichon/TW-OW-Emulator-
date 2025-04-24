import pytest
from player_p import Monster
import random

# Optional: Seed for reproducibility in shuffle
random.seed(42)

def test_monster_initialization():
    m = Monster("Goblin", 10, "easy")
    
    assert m.name == "Goblin"
    assert m.health == 10
    assert m.difficulty == "easy"
    assert m.alive is True
    assert isinstance(m.hp_deck, list)
    assert isinstance(m.fight_deck, list)

def test_initiate_fight_easy():
    m = Monster("Goblin", 10, "easy")
    m.initiate_fight()
    assert len(m.fight_deck) == 12
    assert sorted(m.fight_deck) == sorted(m.easy_hp)

def test_initiate_fight_medium():
    m = Monster("Orc", 12, "medium")
    m.initiate_fight()
    assert len(m.fight_deck) == 16
    assert sorted(m.fight_deck) == sorted(m.medium_hp)

def test_initiate_fight_hard():
    m = Monster("Dragon", 20, "hard")
    m.initiate_fight()
    assert len(m.fight_deck) == 20
    assert sorted(m.fight_deck) == sorted(m.hard_hp)

def test_play_top_card_returns_dmg():
    m = Monster("Troll", 15, "easy")
    m.initiate_fight()
    initial_len = len(m.fight_deck)
    card = m.play_top_card()
    assert "DMG" in card
    assert isinstance(card["DMG"], int)
    assert len(m.fight_deck) == initial_len - 1

def test_play_top_card_empty_deck():
    m = Monster("Ghost", 5, "easy")
    m.fight_deck = []  # empty it
    card = m.play_top_card()
    assert card == {"DMG": 0}

def test_take_dmg_removes_cards():
    m = Monster("Imp", 10, "easy")
    m.initiate_fight()
    start_len = len(m.fight_deck)
    m.take_dmg(5)
    assert len(m.fight_deck) == max(0, start_len - 5)

def test_take_dmg_more_than_deck():
    m = Monster("Imp", 10, "easy")
    m.initiate_fight()
    m.take_dmg(50)  # more than deck size
    assert len(m.fight_deck) == 0

def test_is_alive_true():
    m = Monster("Imp", 10, "easy")
    m.initiate_fight()
    assert m.is_alive() is True

def test_is_alive_false():
    m = Monster("Imp", 10, "easy")
    m.fight_deck = []
    assert m.is_alive() is False
    assert m.alive is False
