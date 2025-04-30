from player_p import Monster
import random

## This is used for same randomness
random.seed(42)

## Is the Monster Initialised Properly
def test_monster_initialization():
    m = Monster("Monster", "easy")
    
    assert m.name == "Monster"
    assert m.difficulty == "easy"
    assert m.alive is True
    assert isinstance(m.hp_deck, list)
    assert isinstance(m.fight_deck, list)

## Is the easy fighting deck prepared correctly
def test_initiate_fight_easy():
    m = Monster("Monster", "easy")
    m.initiate_fight()
    assert len(m.fight_deck) == 12
    assert sorted(m.fight_deck) == sorted(m.easy_hp)

## Is the medium fighting deck prepared correctly
def test_initiate_fight_medium():
    m = Monster("Monster", "medium")
    m.initiate_fight()
    assert len(m.fight_deck) == 16
    assert sorted(m.fight_deck) == sorted(m.medium_hp)

## Is the hard fighting deck prepared correctly
def test_initiate_fight_hard():
    m = Monster("Monster", "hard")
    m.initiate_fight()
    assert len(m.fight_deck) == 20
    assert sorted(m.fight_deck) == sorted(m.hard_hp)

## Does the top card return DMG
def test_play_top_card_returns_dmg():
    m = Monster("Monster", "easy")
    m.initiate_fight()
    initial_len = len(m.fight_deck)
    card = m.play_top_card()
    assert "DMG" in card
    assert isinstance(card["DMG"], int)
    assert len(m.fight_deck) == initial_len - 1

## Test if if playing top card from empty deck breaks it
def test_play_top_card_empty_deck():
    m = Monster("Monster", "easy")

    m.fight_deck = []
    card = m.play_top_card()
    assert card == {"DMG": 0}

## Check if taking damage correctly removes cards from deck
def test_take_dmg_removes_cards():
    m = Monster("Monster", "easy")
    m.initiate_fight()
    start_len = len(m.fight_deck)
    m.take_dmg(5)
    assert len(m.fight_deck) == max(0, start_len - 5)

## Tests if the code runs okay if we take more damage than the is acrds 
## in deck
def test_take_dmg_more_than_deck():
    m = Monster("Monster", "easy")
    m.initiate_fight()
    m.take_dmg(50)  # more than deck size
    assert len(m.fight_deck) == 0

## Checks if the Alive function works when cards are in the deck
def test_is_alive_true():
    m = Monster("Monster", "easy")
    m.initiate_fight()
    assert m.is_alive() is True

## Checks if the Alive function correctly returns false 
## if deck is empty
def test_is_alive_false():
    m = Monster("Monster", "easy")
    m.fight_deck = []
    assert m.is_alive() is False
    assert m.alive is False
