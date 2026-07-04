#this file is for turning the data from that big ol json 

#https://www.npmjs.com/package/dungeonworld-data?activeTab=code

import json
import school

with open("game_data_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

class Monster:
    def __init__(self, description, instinct, armor, hp, attacks, name, tags, moves, key):
        self.description = description
        self.instinct = instinct
        self.armor = armor
        self.hp = hp
        self.attacks = attacks
        self.name = name
        self.tags = tags
        self.moves = moves
        self.key = key

class Classes:
    def __init__(self,name,description,load,base_hp,damage,names,bonds,looks,alignments,alignments_list,race_moves,starting_moves,advanced_moves_1,advanced_moves_2,gear_choices,key):
        self.name = name
        self.description = description
        self.load = load
        self.base_hp = base_hp
        self.damage = damage
        self.names = names
        self.bonds = bonds
        self.looks = looks
        self.alignments = alignments
        self.alignments_list = alignments_list
        self.race_moves = race_moves
        self.starting_moves = starting_moves
        self.advanced_moves = advanced_moves_1 + advanced_moves_2
        self.gear_choices = gear_choices
        self.key = key

class Equipment:
    def __init__(self, tags, name):
        self.tags = tags
        self.name = name

class Moves:
    def __init__(self, name, description, key):
        self.name = name
        self.description = description
        self.key = key

mon = []
cls = []
eqmt = []
mvs = []

for i in data['monsters']:
    try:
        description = data['monsters'][i]['description']
    except:
        continue
    try:
        instinct = data['monsters'][i]['instinct']
    except:
        continue
    try:
        armor = data['monsters'][i]['armor']
    except:
        armor = 0
    try:
        hp = data['monsters'][i]['hp']
    except:
        continue
    try:
        attacks = data['monsters'][i]['attacks']
    except:
        continue
    try:
        name = data['monsters'][i]['name']
    except:
        continue
    try:
        tags = data['monsters'][i]['tags']
    except:
        continue
    try:
        moves = data['monsters'][i]['moves']
    except:
        continue
    try:
        key = data['monsters'][i]['key']
    except:
        continue
    mon.append(Monster(description, instinct, armor, hp, attacks, name, tags, moves, key))


for i in data['classes']:
    try:
        name = data['classes'][i]['name']
    except:
        continue
    try:
        description = data['classes'][i]['description']
    except:
        continue
    try:
        load = data['classes'][i]['load']
    except:
        continue
    try:
        base_hp = data['classes'][i]['base_hp']
    except:
        continue
    try:
        damage = data['classes'][i]['damage']
    except:
        continue
    try:
        names = data['classes'][i]['names']
    except:
        continue
    try:
        bonds = data['classes'][i]['bonds']
    except:
        continue
    try:
        looks = data['classes'][i]['looks']
    except:
        continue
    try:
        alignments = data['classes'][i]['alignments']
    except:
        continue
    try:
        alignments_list = data['classes'][i]['alignments_list']
    except:
        continue
    try:
        race_moves = data['classes'][i]['race_moves']
    except:
        continue
    try:
        starting_moves = data['classes'][i]['starting_moves']
    except:
        continue
    try:
        advanced_moves_1 = data['classes'][i]['advanced_moves_1']
    except:
        continue
    try:
        advanced_moves_2 = data['classes'][i]['advanced_moves_2']
    except:
        continue
    try:
        gear_choices = data['classes'][i]['gear_choices']
    except:
        continue
    try:
        key = data['classes'][i]['key']
    except:
        continue
    
    cls.append(Classes(name,description,load,base_hp,damage,names,bonds,looks,alignments,alignments_list,race_moves,starting_moves,advanced_moves_1,advanced_moves_2,gear_choices,key)) 

for i in data['equipment']:
    try:
        tags = data['equipment'][i]['tags']
    except:
        continue
    try:
        name = data['equipment'][i]['name']
    except:
        continue
    eqmt.append(Equipment(tags, name))

for i in data['moves']:
    try:
        name = data['moves'][i]['name']
    except:
        continue
    try:
        description = data['moves'][i]['description']
    except:
        continue
    try:
        key = data['moves'][i]['key']
    except:
        continue
    mvs.append(Moves(name, description, key))

