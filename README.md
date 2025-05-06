[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/yfSNuVM-)

# Project Overview

## Requirements
Requirements can be found in requirements.txt Install it on to your system via pip or other installers

## File Structure & Purpose
### Main Emulator Logic (main/)

These files implement core game mechanics:

    board.py – Manages the board state and player interactions with it.

    card.py – Defines card class.

    locations.py – Handles in-game map loading with data from json.

    player_p.py – Represents the player and their available actions or stats.

### Game Data (Game_Data/)

JSON files used to populate game elements:

    action_cards.json – Implemented all card information.

    bear_cards.json – Contains bear school card data.

    wolf_cards.json – Contains wolf school card data.

    location.json – Contains location definitions.

### Pytest Files (main/)

Used for automated testing of game components:

    test_location.py – Tests for the location loading.

    test_monster.py – Tests for monster/enemy logic and interactions.

### Game Stat Samplers (main/)

Files used to simulate and gather gameplay statistics:

    sampler.py – Runs a set number of simulation in parallel (no user input therefore ai only).

    solo_sampler.py – Simulates game for humans, could not use parallisation.

