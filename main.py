## Begining Implementation of the Witcher: Old World

## To Do:

## Location Matrix 
LocMatrix = [
  [4,8,11,12], #0
  [2,5,6,9], #1
  [1,3,6,7], #2
  [2,4,7], #3
  [3,7,8,0], #4
  [1,6,9], #5
  [1,2,5,7,9], #6
  [2,3,4,6,8,9,10,11], #7
  [4,7,11,0], #8
  [1,5,6,7,10,13], #9
  [7,9,11,13,15], #10
  [7,8,10,12,15,16,0], #11
  [11,16,0], #12
  [9,10,14,15], #13
  [13,15,17], #14
  [10,11,13,14,16,17,18], #15
  [11,12,15,18], #16
  [14,15,18], #17
  [15,16,17], #18
]

## Location Class? 
## Uses Location Matrix to determine location Adjacency 
## Class Defines Terrain Type, Vendors and Quests
LocationNames = [
  'Behelt Nar','Kaer Seren','Hengfors','Kaer Morhen','Ban Ard',
  'Cidaris','Novigrad','Vizima','Vengerberg','Cintra',
  'Haern Caduch','Beauclair','Glenmore','Doldeth','Loc Ichaer',
  'Gorthur Guaed','Dhuwod','Stygga','Ard Modron'
]

LocationTerrains = [
  'ALL',
  'SEA',
  'MOUNTAIN',
  'MOUNTAIN',
  'SEA',
  'SEA',
  'FOREST',
  'FOREST',
  'FOREST',
  'MOUNTAIN',
  'FOREST',
  'MOUNTAIN',
  'SEA',
  'MOUNTAIN',
  'SEA',
  'SEA',
  'FOREST',
  'FOREST',
  'MOUNTAIN'
]

class Location:
    def __init__(self, id, name, terrain, adjacent_locations):
        self.id = id
        self.name = name
        self.terrain = terrain
        self.adjacent_locations = adjacent_locations
        self.vendors = []  
        self.quests  = []   

    def add_vendor(self, vendor):
        """Add a vendor to this location."""
        self.vendors.append(vendor)

    def add_quest(self, quest):
        """Add a quest to this location."""
        self.quests.append(quest)

    def state(self):
        print(f"Location(id={self.id}, name='{self.name}', terrain='{self.terrain}', "
              f"adjacent_locations={self.adjacent_locations}, vendors={self.vendors}, quests={self.quests})")


# Map Data Setup
locations = []
for idx, (name, terrain, adjacents) in enumerate(zip(LocationNames, LocationTerrains, LocMatrix)):
    location = Location(id=idx, name=name, terrain=terrain, adjacent_locations=adjacents)
    locations.append(location)


# Add a vendor and quest to a location
# locations[0].add_vendor("Blacksmith")
# locations[0].add_quest("Find the Lost Relic")


## Cards are what the player uses for its movement, hp, and to fight
##
## Effects -  These are explained under Card Icons:
## Damage: Inflict Damage (Resolves First)
## Shield: Raise Shield Level
## DiscardDraw: Draw the top card from the discard pile
## DiscardSearch: Look at one card from discard and take it
## Return: Return this Card to the players Hand
## DrawMore: After fight turn, draw more cards
## DrawLess: After fight turn, draw less cards

class Card:
    def __init__(self, color, effect, terrain):
        self.color = color
        self.effect = effect
        self.terrain = terrain

    def state(self):
        print(f"Card(color={self.color}, effect={self.effect})")

card_1 = Card('Damage','Red','FOREST')
card_2 = Card('Damage','Blue','MOUNTAIN')
card_3 = Card('Damage','Green','SEA')


## Player Class
## Need to be able to store current deck and stats such as Gold,Items and Level
class Player:
  def __init__(self, name, gold, current_location):
    self.name = name
    self.gold = gold
    self.current_location = current_location
    self.hand = [card_1, card_1, card_2]
    self.discard = []


  def discard_card(self,card):
      """discards a card to your discard pile"""
      if card in self.hand:
          self.hand.remove(card)
          self.discard.append(card)  

  def state(self):
      """prints the whole player state"""
      print("\n")
      print("Player:", self.name ," ")
      print("Current Location:", self.current_location.name)
      print("\n")

  def move_location(self,location : Location):
      self.current_location = location

  def avaiable_terrain(self):
      forest_count = 0
      sea_count = 0
      mountain_count = 0
      wild_count = 0

      for card in self.hand:
          print("Terrain:",card.terrain,"")
          if card.terrain == "FOREST":
            forest_count +=1
          elif card.terrain == "MOUNTAIN":
            mountain_count +=1
          elif card.terrain == "SEA":
              sea_count += 1
          else:
              wild_count += 1

      return {'FOREST': forest_count,"MOUNTAIN":mountain_count,"SEA":sea_count,"WILD":wild_count}
        
  def decide_where_to_move(self):
    for loc in  self.current_location.adjacent_locations:
        # Move to a location for 1 Card First, then prioritize 1 card 1 gold, then 2 cards
        # Assign value to location based on if they are traversable
        # Choose the lowest value
        # Then Discard Card (Which one to discard? Check strength between cards?? Evaluate Hand Strength)
        pass

  def evaluate_hand_strength(self):
      # Evaluate Hand Combo Strength
      pass
  def worst_card_in_hand(self,terrain):
        #Look at your hand and given a terrain, find the worst card in the hand 
        # (minimizes hand strength loss)
        pass

# View the data
for loc in locations:
    loc.state()


Player1 = Player("Wolf", 2, locations[3])
Player1.state()
Player1.decide_where_to_move()
Player1.avaiable_terrain()
print(Player1.avaiable_terrain())