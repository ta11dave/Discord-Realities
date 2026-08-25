import discord
from discord.ext import commands
import re
import database
import school
import json

class Homebrew(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("homebrew init")
    
    @commands.group(invoke_without_command = True, aliases = ("hb",))
    async def homebrew(self, ctx):
        await ctx.send("You can `!hb view`, `!hb create [table] ...info`, and `!hb delete [table] [name]`")
    
    @homebrew.command()
    async def view(self, ctx, *args):
        datab = database.DBManager
        myhb = await datab.hbview(ctx)
        if len(myhb)<1:
            await ctx.send("No homebrew yet!")
            return
        if len(args)<1:
            args = ["playbooks", "moves", "eqmt", "monsters"]
        embedVar = discord.Embed(title=f"{ctx.guild} Homebrew", description="", color=0x00ff00)
        for each in myhb:
            if each[:4] == "play":
                embedVar.add_field(name="Playbooks", value=each[10:], inline=False)
            if each[:4] == "move":
                embedVar.add_field(name="Moves", value=each[6:], inline=False)
            if each[:4] in ["item", "gear", "eqmt"]:
                 embedVar.add_field(name="Items", value=each[5:], inline=False)
            if each[:4] == "mons":
                embedVar.add_field(name="Monsters", value=each[9:], inline=False)
        await ctx.channel.send(embed=embedVar)
    
    @homebrew.command()
    async def create(self, ctx, *args):
        #importing moves, monsters, playbooks, and items
        dbname = str(ctx.guild.id)+".db"
        datab = database.DBManager
        if args[0] in ["move", "moves"]:
            try:
                name = args[1]
                description = args[2]
                key = name
                mymove = school.Moves(name, description, key)
                await datab.add_move(mymove,dbname)
                await ctx.send(f"Added homebrew move {name} to server database!")
            except:
                await ctx.send("move help message")
        elif args[0] == "monster":
            try:
                name = args[1]
                description = args[2]
                instinct = args[3]
                armor = args[4]
                hp = args[5]
                attacks = args[6]
                tags = args[7]
                moves = args[8]
                key = name
                mymon = school.Monster(description, instinct, armor, hp, attacks, name, tags, moves, key)
                await datab.add_monster(mymon,dbname)
                await ctx.send(f"Added homebrew monster {name} to server database!")
            except:
                await ctx.send("Format is: `!hbimport monster [name] [descrition] [instinct] [armor (integer)] [hp (integer)] [attacks (json as a string)] [moves]")
                await ctx.send("The [attack] should be formatted like: `[{'name': 'Sword', 'damage': 'd6', 'tags': ['close']}]`")
                await ctx.send("The [tags] and [moves] should be formatted like: `['Steal something', 'Demand tribute']`")
        elif args[0] == "playbook":        
            try:
                name = args[1]
                description = args[2]
                load = args[3]
                base_hp = args[4]
                damage = args[5]
                names = args[6]
                bonds = args[7]
                looks = args[8]
                alignments = args[9]
                alignments_list = args[10]
                race_moves = args[11]
                starting_moves = args[12]
                advanced_moves_1 = args[13]
                advanced_moves_2 = args[14]
                gear_choices = args[15]
                key = name
                myPlaybook =school.Playbook(name,description,load,base_hp,damage,names,bonds,looks,alignments,alignments_list,race_moves,starting_moves,advanced_moves_1,advanced_moves_2,gear_choices,key)
                await datab.add_playbook(myPlaybook,dbname)
                await ctx.send(f"Added homebrew playbook {name} to server database!")
            except:
                await ctx.send("playbook help message")
        elif args[0] in ["item", "items", "equipment"]:
            try:
                name = args[1]
                tags = []
                for each in args[2:]:
                    tags.append(each)
                tags = json.loads(tags)
                myitem = school.Equipment(tags, name)
                await datab.add_eqmt(myitem,dbname)
                await ctx.send(f"Added homebrew item {name} to server database")
            except:
                await ctx.send("item help message")
        else:
            await ctx.send("This needs polish. Go check out the Github page, maybe that'll help? Idk. I just work here.")


    @homebrew.command()
    async def delete(self, ctx, table, name):
        #importing moves, monsters, playbooks, and items
        datab = database.DBManager
        result = await datab.hbdelete(ctx, table, name)
        await ctx.send(result)


async def setup(bot):
    await bot.add_cog(Homebrew(bot))
