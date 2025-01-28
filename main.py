## Begining Implementation of the Witcher: Old World

## To Do:

## Location Matrix 
LocMatrix = [
  [], #0
  [], #1
  [], #2
  [], #3
  [], #4
  [], #5
  [], #6
  [], #7
  [], #8
  [], #9
  [], #10
  [], #11
  [], #12
  [], #13
  [], #14
  [], #15
  [], #16
  [], #17
  [], #18
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


class Location:
  def __init__(self,name):
    self.name = name
    
##For Loop
LocArray = []

for i in LocationNames:
  Loc = Location(i)
  LocArray.append(Loc)


## Player Class
## need to be able to store current deck and stats such as Gold,Items and Level
class Player:
  def __init__(self,name,gold,location):
    self.name = name
    self.gold = gold
    self.location = location



p1 = Player("Wolf",2,LocArray[3])
print(p1.name)
print(LocArray[3].name)

##Clears the Array of Locations
LocArray.clear()
