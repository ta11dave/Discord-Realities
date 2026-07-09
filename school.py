import re
#all the classes, of course

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

class Playbook:
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

    def view():
        pass # read a move

    def use():
        pass
        # show text and/or roll 2d6+mod and display result

class Character:
    def __init__(self, playbook, name, strength, dexterity, constitution, inteligence, wisdom, charisma, hp, load, dmgdie, gear, notes, moves, xp):
        self.playbook = playbook
        self.name = name
        self.stats = [strength, dexterity, constitution, inteligence, wisdom, charisma]
        self.mod = [0]*6
        self.hp = hp
        self.load=load
        self.dmgdie = dmgdie
        self.gear = gear
        self.notes = notes
        self.moves = moves
        self.xp = xp
        i = 0
        for stat in self.stats:
            match stat:
                case 7|8:
                    self.mod[i] = -1
                case 9|10|11|12:
                    self.mod[i] = 0
                case 13|14|15:
                    self.mod[i] = 1
                case 16|17:
                    self.mod[i] = 2
                case 18:
                    self.mod[i] = 3
            i=i+1
        self.hpmod = self.mod[2]
        self.hpmax = self.stats[2]+self.hpmod 

    def view():
        pass # something to show the character sheet, maybe as an embed

    def edit(comp, newval):
        pass # update stats
        
class Scene:        
    def __init__(self, channel_id, message_id, dm_id):
        self.channel = str(channel_id)  # readonly
        self.summary_message_id = int(message_id)  # readonly
        self.dm_id = int(dm_id)
        self.actors = {} #a dictionary of a player_id and an array of strings
        self.round_num = []
        self.pinned = ""
        
    def update_pinned(self):
        self.pinned = "" #clear it
        for actor in self.actors:
            print(actor)
            self.pinned = self.pinned + actor + ": "
        
    def join(self, player_id):
        self.actors[player_id] = []
    
    def add_npc(self, npc_name):
        self.actors[npc_name]=[]
    
    def leave(self, player_id):
        i=0
        for actor in self.actors:
            if actor[0] == player_id:
                self.actors.pop(i)
            i=i+1

    def add_note(self, actor_id, note):
        for actor in self.actors:
            if actor[0] == actor_id:
                self.actor[1].append(note)
    
    def remove_note(self, actor_id, note):
        for actor in self.actors:
            if actor[0] == actor_id:
                i=0
                for eachnote in actor[1]:
                    if re.search(note, eachnote, re.I) is not None:
                        actor[1].pop(i) 
                    i=i+1
