import re
#all the classes, of course

class Moves:
    def __init__(self, name, desc, mod, success, mixed, fail):
        self.name = name
        self.desc = desc
        self.mod = mod
        self.success = success
        self.mixed = mixed
        self.fail = fail

    def view():
        pass # read a move

    def use():
        pass
        # show text and/or roll 2d6+mod and display result

class Character:
    def __init__(self, title, name, look, stats, hpmod, dmgdie):
        self.title = title
        self.name = name
        self.look = look
        self.stats = [0]*6  #16 (+2), 15 (+1), 13 (+1), 12 (+0), 9 (+0), 8 (-1) 
        self.mod = [0]*6
        self.hp = hpmod
        self.dmgdie = dmgdie
        self.gear = [] 
        self.notes = []
        self.moves = []

    def update():
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
        
    def update_message():
        self.pinned = "" #clear it
        for actor in self.actors:
            charname = user_registry[actor[0]]
            self.pinned = self.pinned + charname + ": "
            if len(actor[1])==1:
                self.pinned = self.pinned + actor[1][0]
            elif len(actor[1])>1:
                for eachnote in actor[1]:
                    self.pinned = self.pinned + ", " + eachnote 
        return self.pinned
        
    def join(player_id):
        self.actors.append([player_id, []])
    
    def add_npc(npc_name):
        self.actors.append([npc_name, []])
    
    def leave(player_id):
        i=0
        for actor in self.actors:
            if actor[0] == player_id:
                self.actors.pop(i)
            i=i+1

    def add_note(actor_id, note):
        for actor in self.actors:
            if actor[0] == actor_id:
                self.actor[1].append(note)
    
    def remove_note(actor_id, note):
        for actor in self.actors:
            if actor[0] == actor_id:
                i=0
                for eachnote in actor[1]:
                    if re.search(note, eachnote, re.I) is not None:
                        actor[1].pop(i) 
                    i=i+1
