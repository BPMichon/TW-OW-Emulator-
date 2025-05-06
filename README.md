[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/yfSNuVM-)

# Project Overview

### Requirements
Requirements can be found in `requirements.txt` Install it on to your system via pip or other installers

  
## File Structure & Purpose
### Main Emulator Logic (`main/`)

These files implement core game mechanics:

    board.py – Manages the board state and player interactions with it.

    card.py – Defines card class.

    locations.py – Handles in-game map loading with data from json.

    player_p.py – Represents the player and their available actions or stats.

### Game Data (`Game_Data/`)

JSON files used to populate game elements:

    action_cards.json – Implemented all card information.

    bear_cards.json – Contains bear school card data.

    wolf_cards.json – Contains wolf school card data.

    location.json – Contains location definitions.

### Pytest Files (`main/`)

Used for automated testing of game components:

    test_location.py – Tests for the location loading.

    test_monster.py – Tests for monster/enemy logic and interactions.

### Game Stat Samplers (`main/`)

Files used to simulate and gather gameplay statistics:

    sampler.py – Runs a set number of simulation in parallel (no user input therefore ai only).

    solo_sampler.py – Simulates game for humans, could not use parallisation.

## How to run the different parts of the emulator
### The Game Itself
To run the game itself it is needed to have a seperate file which collects the needed
class initialisation and launches the game, an example file can be found in `main/` directory called `main.py`.

It is recommended to play the game with a witcher:old world map, 
as this will ease the difficulty of orientating yourself with the souranding as well as 
allow for better planning in your own games. I had access to the physical map, which definitely
made it easier for me to play the game using the emulator. I however could not find any online sources of the map.

### Sampler
The sampler can sample large number of games in succession, it does use concurency features to run
in parallel. Because of this non AI players cannot occur as user input breaks parallisation.

The sampler settings have to be changed within the sampler file.

Line 55 - chnage which agents strat the game  
Line 67 - change the number of players  
Line 145 - change the number of samples  
Line 146 - change the turn limit  

The final data get calculated and stored in `player_stats.csv`

### Sampler-Solo
This is a copy of sampler that does not include parallisation in order to allow human players, still samples
a number of games, games occur after eachgother in succession. 

Line 55 - chnage which agents strat the game  
Line 67 - change the number of players  
Line 143 - change the number of samples  
Line 144 - change the turn limit  


The final data gets collected and written in `player_stats.scv`

### PyTest
To run pytest we just need to run 'pytest' from project directory, make sure you ahve `pytest` installed on your system.  



