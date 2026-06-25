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
    def __init__(self, hype, name, look, stats, hpmod, dmgdie, race, gear, notes):
        self.hype = hype
        self.name = name
        self.look = look
        self.stats = [0]*6  #16 (+2), 15 (+1), 13 (+1), 12 (+0), 9 (+0), 8 (-1) 
        self.mod = [0]*6
        self.hp = hpmax
        self.dmgdie = dmgdie
        self.gear = [] 
        self.notes = []

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
