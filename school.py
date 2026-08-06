import re
import discord
import database
from discord.ext import commands
from discord.ui import view
#all the classes, of course

class ButtonView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx

    @discord.ui.button(label='Click to Delete', style=discord.ButtonStyle.red)
    async def del_click(self, interaction, button):
        await database.DBManager.del_char(self.ctx.author.id)
        await interaction.response.send_message("DELETED")

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

class Character:
    def __init__(self, playbook, name, level, strength, dexterity, constitution, inteligence, wisdom, charisma, hp, load, dmgdie, gear, notes, moves, xp, picture):
        self.playbook = playbook
        self.name = name
        self.level = level
        self.stats = [strength, dexterity, constitution, inteligence, wisdom, charisma]
        self.mod = [0]*6
        self.hp = hp
        self.load=load
        self.dmgdie = dmgdie
        self.gear = gear
        self.notes = notes
        self.moves = moves
        self.xp = xp
        self.picture=picture
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
        
class Scene:        
    def __init__(self, channel_id, message_id, dm_id):
        self.channel = str(channel_id)  # readonly
        self.summary_message_id = int(message_id)  # readonly
        self.dm_id = int(dm_id)
        self.actors = {} #a dictionary of a player_id and an array of strings
        self.round_num = []
        self.pinned = ""
        
    def update_pinned(self):
        self.pinned = "Scene Summary:\n**********************\n" #clear it
        for actor in self.actors:
            self.pinned = self.pinned + actor + ": " + str(self.actors[actor])+"\n"

    def join(self, player_id):
        self.actors[player_id] = 'No Notes Yet'
    
    def add_npc(self, npc_name):
        self.actors[npc_name] = 'No Notes Yet'
    
    def leave(self, actor_name):
        for actor in self.actors:
            if actor == actor_name:
                self.actors.pop(actor)
                return
            

    def add_note(self, actor_id, note):
        for each in self.actors:
            if each == actor_id:
                if self.actors[each] == 'No Notes Yet':
                    self.actors[each]=note
                else:
                    notestr = self.actors[each]
                    self.actors[each]=notestr+" || "+note
    
    def remove_note(self, actor_id, note):
        for each in self.actors:
            if each == actor_id:
                notestr = self.actors[each]
                notelist = notestr.split(" || ")
                delnote=False
                i=0
                for eachnote in notelist:
                    if delnote == False and re.search(note, eachnote, re.I) is not None:
                        notelist.pop(i)
                        delnote = True
                    else:
                        pass
                    i=i+1
                notestr = ""
                for eachnote in notelist:
                    notestr = notestr+eachnote + " || "
                self.actors[each] = notestr[:len(notestr)-4]
