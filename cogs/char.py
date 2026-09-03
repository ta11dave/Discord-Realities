import discord
from discord.ext import commands
import re
import database
import school
import json

class Char(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("char init")

    @commands.group(invoke_without_command = True, aliases = ("c",))
    async def char(self, ctx):
        try:
            mychar = await database.get_char_data(ctx.author.id)
            embedVar = discord.Embed(title=f"Active Character: {mychar.name}!", description=f"<@{ctx.author.id}>", color=0x00ff00)
            embedVar.set_thumbnail(url=mychar.picture)
            await ctx.channel.send(embed=embedVar)
        except:
            await ctx.send("Use `!char new [name]` to make a new character, `!char list` to see all your characters, and `char view` to see your current character.")
        
    @char.command()
    async def new(self, ctx, *args):
        await ctx.message.delete()
        charname = ""
        for each in args:
            charname= charname+each+" "
        if charname == "":
            await ctx.send("Gotta enter a name, choose wisely!\n You don't need quotes either, `!char new Billy Bob` works fine")
            return
        charname = charname[:len(charname)-1] #taking the space out
        datab = database.DBManager
        await datab.newchar(ctx.author.id,charname)
        embedVar = discord.Embed(title=f"New Character: {charname}!", description="", color=0x00ff00)
        embedVar.add_field(name="Your new character Exists!",value="You can update what's on your sheet with `!update`. You can also change to another character you may have with `!char set [name]` \nAlso, don't forget racial features, alignment, and bonds. These things are all good items to put in the notes section of the sheet.\n\nYou can also use `!char make [Playbook]` to speed up the process.", inline=False)
        await ctx.channel.send(embed=embedVar)
        

    @char.command()
    async def make(self, ctx, playbook):
        await ctx.message.delete()
        datab = database.DBManager
        myplaybook = await datab.playbook_lookup(ctx,playbook)
        mychar = await database.get_char_data(ctx.author.id)
        if str(playbook).lower() in str(mychar.playbook):
            await ctx.send("You're already using that playbook")
        else:
            myplaybook = myplaybook[0]
            # name,description,load,base_hp,damage,names,bonds,looks,alignments,alignments_list,race_moves,starting_moves,advanced_moves_1,advanced_moves_2,gear_choices,key
            plbkobj= school.Playbook(myplaybook[1],myplaybook[2],myplaybook[3],myplaybook[4],myplaybook[5],myplaybook[6],myplaybook[7],myplaybook[8],myplaybook[9],myplaybook[10],myplaybook[11],myplaybook[12],myplaybook[13],myplaybook[14],myplaybook[15],myplaybook[1])
            # args expects strings
            await datab.updatechar(ctx.author.id, ["playbook", plbkobj.name])
            await datab.updatechar(ctx.author.id, ["hpmod", plbkobj.base_hp])
            startinghp = int(plbkobj.base_hp)+int(mychar.stats[2])
            await datab.updatechar(ctx.author.id, ["hp", str(startinghp)])
            await datab.updatechar(ctx.author.id, ["load", str(mychar.mod[0] + int(plbkobj.load))])
            await datab.updatechar(ctx.author.id, ["dmgdie", "1"+plbkobj.damage])
            starting_moves = plbkobj.starting_moves.replace("\'","\"")
            starting_moves = json.loads(starting_moves, strict=False)
            for each in starting_moves:
                await datab.updatechar(ctx.author.id, ["move","add", each["name"]])
            embedVar = discord.Embed(title=f"{mychar.name} is now a {plbkobj.name}! Next Steps", description="Your playbook, hp, load, Damage die, and starting moves have been imported.\nCheck the playbook itself if there's a move you should *not* have, since some have you make a choice between two.\n\nThe rest of this stuff goes in your notes, which you can update with `!update note add [info]`", color=0x00ff00)
            looksdmp = json.loads(plbkobj.looks.replace("'", "\""), strict=False)
            try:
                looksstr = ""
                for each in looksdmp:
                    looksstr = looksstr + str(each) + "\n"
                embedVar.add_field(name="Look",value=looksstr, inline=False)
            except:
                embedVar.add_field(name="Look",value=plbkobj.looks, inline=False)
            try:
                racedmp = json.loads(str(plbkobj.race_moves).replace("'", "\""), strict=False)
                racestr = ""
                for each in racedmp:
                    racestr = racestr + each['name']+": "+each['description'] + "\n"
                embedVar.add_field(name="Race",value=racestr, inline=False)
            except:
                embedVar.add_field(name="Race",value=plbkobj.race_moves, inline=False)
            try:
                alignmentdmp = json.loads(str(plbkobj.alignments_list).replace("'", "\""), strict=False)
                alignmentstr = ""
                for each in alignmentdmp:
                    alignmentstr = alignmentstr + each['name']+": "+each['description']+ "\n"
                embedVar.add_field(name="Alignments",value=alignmentstr, inline=False)
            except:
                embedVar.add_field(name="Alignments",value=plbkobj.alignments_list, inline=False)
            try:
                bonddmp = json.loads(str(plbkobj.bonds).replace("'", "\""), strict=False)
                bondstr = ""
                for each in bonddmp:
                    bondstr = bondstr + each+"\n"
                embedVar.add_field(name="Example Bonds",value=bondstr, inline=False)
            except:
                embedVar.add_field(name="Example Bonds",value=plbkobj.bonds, inline=False)
            embedVar.add_field(name="Gear",value="Look at the playbook to see what gear is available. You can add it with `!update gear add [item]`. It works like the note module, but know you can use `!lookup item [item] to get names and tags of things.`", inline=False)
            await ctx.channel.send(embed=embedVar)

    @char.command()
    async def delete(self, ctx):
        mychar = await database.get_char_data(ctx.author.id)
        datab = database.DBManager
        myview = school.ButtonView(ctx)
        await ctx.send(f"Do you want to delete your current active character: {mychar.name}?",view = myview, ephemeral=True)
        
    @char.command()
    async def levelup(self, ctx):
        await ctx.message.delete()
        datab = database.DBManager
        mychar = await database.get_char_data(ctx.author.id)#get current charname
        if mychar.level >= 10:
            await ctx.send("Level 10 is as high as it goes!")
            return
        if mychar.xp >= mychar.level+7:
            await datab.updatechar(ctx.author.id,["level", mychar.level+1])
            await datab.updatechar(ctx.author.id,["xp", str(mychar.xp-7)])
            await ctx.send(f"Leveled up {mychar.name} to {mychar.level+1}! Increase a stat by one and add a new move!")
        else:
            await ctx.send(f"You have {mychar.xp} XP and need {mychar.level+7} XP to level up!")

    @char.command()
    async def set(self, ctx, charname):
        await ctx.message.delete()
        datab = database.DBManager
        try:
            mychar = await database.get_char_data(ctx.author.id)#get current charname
            oldcharname = mychar.name
        except:
            oldcharname = "Deleted character"
        charlist = await datab.charlist(ctx.author.id)
        for guy in charlist:
            if re.search(charname,guy[1]) is not None:
                charname = guy[1]
                await datab.set(ctx.author.id, guy[0])
        await ctx.send(f"Switched from {oldcharname} to {charname}")
        
    @char.command()
    async def list(self, ctx):
        await ctx.message.delete()
        datab = database.DBManager
        charlist = await datab.charlist(ctx.author.id)
        embedVar = discord.Embed(title="Character List", description="", color=0x00ff00)
        namelist = ""
        for guy in charlist:
            namelist = namelist+ str(guy[1])+"\n"
        embedVar.add_field(name="Roster:",value=namelist, inline=False)
        await ctx.channel.send(embed=embedVar)
        
    @char.command()
    async def view(self, ctx, *args):
        await ctx.message.delete()
        datab = database.DBManager
        if len(args)==0:
            args=("basic", "stats", "hp", "gear", "move", "note")
        else:
            newargs=[]
            for each in args:
                newargs.append(str(each).lower())
            args = newargs
        try:
            mychar = await database.get_char_data(ctx.author.id)
            embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
            embedVar.set_thumbnail(url=mychar.picture)
        except Exception as e:
            await ctx.send("You don't have an active character to view or this:\n"+str(e))
            return
        if "basic" in args:
            playbookstr = str(mychar.playbook)[2:len(mychar.playbook)-2]
            datastr = f"Playbook: {playbookstr}\nName: {mychar.name}\nLevel: {mychar.level}\nXP: {mychar.xp}\nDamage Die: {mychar.dmgdie}\nCoin: {mychar.coin}"
            embedVar.add_field(name="Basic Info", value=datastr, inline=False)
        if "stats" in args:
            statstr = f"Strength: {mychar.stats[0]} ({mychar.mod[0]}), Dexterity: {mychar.stats[1]} ({mychar.mod[1]}), Constitution: {mychar.stats[2]} ({mychar.mod[2]}), Wisdom: {mychar.stats[3]} ({mychar.mod[3]}), Intelligence: {mychar.stats[4]} ({mychar.mod[4]}), Charisma: {mychar.stats[5]} ({mychar.mod[5]})"
            embedVar.add_field(name="Stats", value=statstr, inline=False)
        if "hp" in args:
            embedVar.add_field(name="Health", value=f"{mychar.hp} of {mychar.hpmax} HP", inline=False)
        if "gear" in args or "item" in args or "items" in args:
            mygear=mychar.gear.replace("%%","\n* ")
            embedVar.add_field(name="Inventory", value=mygear+f"\n\nLoad:{mychar.load}", inline=False)
        if "move" in args or "moves" in args:
            mymoves="* " + mychar.moves.replace("%%","\n* ")
            embedVar.add_field(name="Moves", value=mymoves, inline=False)
        if "note" in args or "notes" in args:
            mynotes="* "+mychar.notes.replace("%%","\n* ")
            embedVar.add_field(name="Notes", value=mynotes, inline=False)
        if "help" in args:
            ctx.send("Use `!char view` to see your sheet.\n\nYou can also be more specific with: \n`!char view basic`\n`!char view stats`\n`!char view hp`\n`!char view gear`\n`!char view move`\n`!char view notes`")
        await ctx.channel.send(embed=embedVar)
        try:
            await ctx.message.delete()
        except:
            pass


async def setup(bot):
    await bot.add_cog(Char(bot))
