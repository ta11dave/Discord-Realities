import discord
from discord.ext import commands
import re
import database
import school
import json

class Look(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command = True)
    async def lookup(self, ctx, *args):
        await ctx.message.delete()
        if len(args) == 0:
            await ctx.send("Use `!lookup monster [monster]` to have a monster statblock sent in a private message.\nUse `!lookup item [item]`, Use `!lookup move [move]`, and Use `!lookup playbook [playbook]` to look up stuff on the playbook\nYou can also use `!monster [monster]`, `!playbook [playbook]`, `!item [item]`, and `!move [move]` if that's easier for ya. \nI guess the lookup command is depreciated but idk")    
        if args[0] == "monster":
            args = args[1:]
            searchterm = (" ").join(args)
            monster(ctx,searchterm)
        elif args[0] == "item":
            args = args[1:]
            searchterm = (" ").join(args)
            item(ctx,searchterm)
        elif args[0] == "playbook":
            args = args[1:]
            searchterm = (" ").join(args)
            playbook(ctx,searchterm)
        elif args[0] == "move" or args[0] == "moves":
            args = args[1:]
            searchterm = (" ").join(args)
            move(ctx,searchterm)
        else:
            await ctx.send("Use `!lookup monster [monster]` to have a monster statblock sent in a private message.\nUse `!lookup item [item]`, Use `!lookup move [move]`, and Use `!lookup playbook [playbook]` to look up stuff on the playbook\nYou can also use `!monster [monster]`, `!playbook [playbook]`, `!item [item]`, and `!move [move]` if that's easier for ya. \nI guess the lookup command is depreciated but idk")

    @commands.command(aliases=("mon",))
    async def monster(ctx, searchterm = "None"):
        datab = database.DBManager
        if searchterm == "None":
            namestr = ""
            listonames = await datab.pull_names(ctx,"monsters")
            for each in listonames:
                namestr = namestr + str(each)[2:len(each)-3] + "\n"
            if len(namestr) > 5000:
                embedVar = discord.Embed(title="Too many monsters to fit in one embed", description="I have no intention to make this work right now", color=0x00ff00)
            else:
                embedVar = discord.Embed(title="List of all monsters", description=namestr, color=0x00ff00)
            await ctx.send(embed=embedVar)
            return
        result = await datab.monster_lookup(ctx, searchterm)
        embedVar = discord.Embed(title=result[0][1], description=result[0][2], color=0x00ff00)
        embedVar.add_field(name="Impulse", value=result[0][3], inline=False)
        embedVar.add_field(name="Armor", value=result[0][4], inline=False)
        embedVar.add_field(name="HP", value=result[0][5], inline=False)
        attackstring = result[0][6]
        attackstring=attackstring[1:-1]
        attacks=json.loads(attackstring.replace("'", "\""))
        attackname = attacks['name']
        attackdmg = attacks['damage']
        attacktags = ""
        for tag in attacks['tags']:
            attacktags = attacktags+"\n"+tag
        embedVar.add_field(name=attackname, value=f"Damage: {attackdmg}\nAttack Tags: {attacktags}", inline=False)
        tagoptions = result[0][7].replace("'", "\"")
        tagoptions = json.loads(tagoptions)
        tagstr = ""
        for opt in tagoptions:
            tagstr = tagstr + opt+"\n"
        embedVar.add_field(name="Creature Tags", value=tagstr, inline=False)
        moveoptions = result[0][8].replace("'", "\"")
        moveoptions = json.loads(moveoptions)
        movestr = ""
        for opt in moveoptions:
            movestr = movestr + opt+"\n"
        embedVar.add_field(name="Moves", value=movestr, inline=False)
        await ctx.message.delete()
        await ctx.author.send(embed=embedVar)
        await ctx.channel.send("Sent you a DM!")

    @commands.command(aliases=("gear",))
    async def item(ctx, searchterm = "None"):
        datab = database.DBManager
        if searchterm == "None":
            namestr = ""
            listonames = await datab.pull_names(ctx,"eqmt")
            for each in listonames:
                namestr = namestr + str(each)[2:len(each)-3] + "\n"
            if len(namestr) > 5000:
                embedVar = discord.Embed(title="Too many moves to fit in one embed", description="I have no intention to make this work right now", color=0x00ff00)
            else:
                embedVar = discord.Embed(title="List of all items", description=namestr, color=0x00ff00)
            await ctx.send(embed=embedVar)
            returnresult = await datab.eqmt_lookup(ctx, searchterm)
        tagdict = json.loads(result[0][2].replace("'", "\""))
        tagstr = ""
        for each in tagdict:
            tagstr=tagstr+"\n"
        embedVar = discord.Embed(title="Item: "+result[0][1], description="Tags: \n"+tagstr, color=0x00ff00)
        await ctx.channel.send(embed=embedVar)
        
    @commands.command(aliases = ("pb",))
    async def playbook(ctx, searchterm = "None"):
        datab = database.DBManager
        if searchterm == "None":
            namestr = ""
            listonames = await datab.pull_names(ctx,"playbooks")
            for each in listonames:
                namestr = namestr + str(each)[2:len(each)-3] + "\n"
            embedVar = discord.Embed(title="Available Playbooks", description=namestr, color=0x00ff00)
            await ctx.send(embed=embedVar)
            return
        result = await datab.playbook_lookup(ctx, searchterm)
        embedVar1 = discord.Embed(title=result[0][1], description=result[0][2], color=0x00ff00)
        embedVar1.add_field(name="Load", value=result[0][3], inline=False)
        embedVar1.add_field(name="Damage Die", value=result[0][5], inline=False)
        embedVar1.add_field(name="Example Names", value=result[0][6], inline=False)
        embedVar1.add_field(name="Example Bonds", value=result[0][7], inline=False)
        embedVar1.add_field(name="Example Character Descriptors", value=result[0][8], inline=False)
        embedVar1.add_field(name="Alignment", value=result[0][9] + result[0][10], inline=False)
        embedVar1.add_field(name="Race Moves", value=result[0][11], inline=False)
        await ctx.author.send(embed=embedVar1)
        
        startmvs = json.loads(result[0][12].replace("'", "\""))
        for mv in startmvs:
            embedVar = discord.Embed(title=result[0][1]+" Continued", description="", color=0x00ff00)
            embedVar.add_field(name=mv['name'], value=mv['description'], inline=False)
            await ctx.author.send(embed=embedVar)
        await ctx.channel.send("Sent you a DM! (Wouldn't want to clog up chat...)")

    @commands.command()
    async def move(ctx, searchterm="None"):
        datab = database.DBManager
        if searchterm == "None":
            namestr = ""
            listonames = await datab.pull_names(ctx,"moves")
            for each in listonames:
                namestr = namestr + str(each)[2:len(each)-3] + "\n"
            if len(namestr) > 5000:
                embedVar = discord.Embed(title="Too many moves to fit in one embed", description="I have no intention to make this work right now", color=0x00ff00)
            else:
                embedVar = discord.Embed(title="List of all moves", description=namestr, color=0x00ff00)
            await ctx.send(embed=embedVar)
            return
        result = await datab.move_lookup(ctx, searchterm)
        try:
            if result[0][1] == 1:
                pass # this only exists to crash
            embedVar = discord.Embed(title=result[0][1], description=result[0][2], color=0x00ff00)
        except:
            embedVar = discord.Embed(title="", description=result, color=0x00ff00)
        await ctx.channel.send(embed=embedVar)
        try:
            await ctx.message.delete()
        except:
            pass

async def setup(bot):
    await bot.add_cog(Look(bot))
