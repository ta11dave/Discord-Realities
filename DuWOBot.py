# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
import database
import d20 
import school
import json

#secure token stuff
load_dotenv()
TOKEN = os.getenv("TOKEN")

#discord permissions
intents = discord.Intents.default()
intents.message_content = True

scenelist = [] #all the scenes going on at any one time

bot = commands.Bot(command_prefix='!', intents=intents)

## References
# https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
# https://github.com/DungeonPaper/dungeon_world_data/tree/master
# https://github.com/omnilib/aiosqlite
# https://gist.github.com/lykn/bac99b06d45ff8eed34c2220d86b6bf4
# https://d20.readthedocs.io/en/latest/start.html

#make sure the data is there in case you messed it up

@bot.command()
async def test(ctx):
        print("scenelist: ", scenelist , "\n*\n")
        mychar = await database.get_char_data(ctx.author.id)
        print(mychar.playbook, " playbook")
        print(mychar.name, " name")
        print(mychar.level, " level")
        print(mychar.stats, " stats")
        print(mychar.mod, " mod")
        print(mychar.hp, " hp")
        print(mychar.load, " load")
        print(mychar.dmgdie, " dmgdie")
        print(mychar.gear, "gear")
        print(mychar.notes, " notes")
        print(mychar.moves, " moves")
        print(mychar.xp, " xp")
        print(mychar.picture, " picture")
        print(mychar.hpmod, " hpmod")
        print(mychar.hpmax, " hpmax")
        print(ctx.guild.id)

@bot.command()
async def resetlookup(ctx):
        await database.reset()

@bot.command()
async def roll(ctx, *args):
    await ctx.message.delete()
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title=mychar.name +" makes a move!", description=ctx.author, color=0x00ff00)
    embedVar.set_thumbnail(url=mychar.picture)
    rollstr = "2d6"
    myargs = []
    i=0
    if args==():
        args=["flat"]
    if args[0][:3].lower() == "dmg" or args[0].lower() == "damage":
        rollstr = mychar.dmgdie
    if args[0][:3].lower() in ["str","dex","con","wis","int","cha"]:
        stat = args[0][:3].lower()
        args = args[1:]
        if stat == "hel":
            await ctx.send("Use `!roll` to roll dice! The standard format should look something like `!roll dex +1 \"Discern Realities\" adv`")
            return
        elif stat == "str":
            rollstr = rollstr + "+"+ str(mychar.mod[0]) + " [str] "
        elif stat == "dex":
            rollstr = rollstr + "+"+ str(mychar.mod[1]) + " [dex] "
        elif stat == "con":
            rollstr = rollstr + "+"+ str(mychar.mod[2]) + " [con] "
        elif stat == "int":
            rollstr = rollstr + "+"+ str(mychar.mod[3]) + " [int] "
        elif stat == "wis":
            rollstr = rollstr + "+"+ str(mychar.mod[4]) + " [wis] "
        elif stat == "cha":
            rollstr = rollstr + "+"+ str(mychar.mod[5]) + " [cha] "
    for each in args:
        myargs.append(each)
    for arg in myargs:
        if arg == "adv":
            rollstr = "3d6kh2"
            myargs.pop(i)
        elif arg == "dis":
            rollstr = "3d6kl2"
            myargs.pop(i)
        i=i+1
    for arg in myargs:
        if arg[:1]=="+" or arg[:1]=="-":
            rollstr=rollstr+str(arg)
        else:
            rollstr = rollstr + " ["+arg+"] "
    
    theroll = d20.roll(rollstr)
    embedVar.add_field(name="", value=theroll, inline=False)
    
    if "damage" not in rollstr:
        if int(theroll.total)<= 6:
            embedVar.add_field(name="Result", value="Oh no. At least you got an XP.", inline=False)
            await datab.updatechar(ctx.author.id,["xp", "+1"])
        elif int(theroll.total) in [7,8,9]:
            embedVar.add_field(name="Result", value="Mixed Success.", inline=False)
        elif int(theroll.total)>9:
            embedVar.add_field(name="Result", value="Full Success!", inline=False)
        else:
            embedVar.add_field(name="Result", value="Something broke", inline=False)
    
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def xp(ctx, amt="0"):
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
    oldxp = mychar.xp
    if amt == "0":
        embedVar.add_field(name="XP", value="You have "+str(mychar.xp)+" xp.", inline=False)
    else:
        newxp = await datab.updatechar(ctx.author.id,["xp", amt])
        embedVar.add_field(name="XP", value="Your XP went from "+str(oldxp)+" to "+str(newxp)+"!", inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def movelist(ctx):
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title="Move List", description="", color=0x00ff00)
    embedVar.add_field(name="Basic Moves", value="Hack and Slash\nVolley\nDefy Danger\nDefend\nSpout Lore\nDiscern Realities\nParley\nAid or Interfere", inline=False)
    embedVar.add_field(name="Special Moves", value="Last Breath\nEncumberance\nMake Camp\nTake Watch\nUndertake a Perilous Journey\nEnd of Session\nCarouse\nSupply\nRecover\nRecruit\nOutstanding Warrants\nBolster", inline=False)
    # might have to stringify the character moves
    embedVar.add_field(name=f"{mychar.name}'s Moves", value=mychar.moves, inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def update(ctx, *args):
    if len(args)<1:
        args = "help"
    datab=database.DBManager
    responcetext = await datab.updatechar(ctx.author.id, args)
    await ctx.send(responcetext)

@bot.group(invoke_without_command = True)
async def char(ctx):
    await ctx.send("Use `!char new [name]` to make a new character, `!char list` to see all your characters, and `char view` to see your current character.")
    
@char.command()
async def new(ctx, *args):
    charname = ""
    for each in args:
        charname= charname+each+" "
    if charname == "":
        await ctx.send("Gotta enter a name, choose wisely!")
        return
    charname = charname[:len(charname)-1] #taking the space out
    datab = database.DBManager
    await datab.newchar(ctx.author.id,charname)
    embedVar = discord.Embed(title=f"New Character: {charname}!", description="", color=0x00ff00)
    embedVar.add_field(name="Your new character Exists!",value="You can update what's on your sheet with `!update`. You can also change to another character you may have with `!char set [name]` \nAlso, don't forget racial features, alignment, and bonds. These things are all good items to put in the notes section of the sheet.", inline=False)
    await ctx.channel.send(embed=embedVar)

@char.command()
async def levelup(ctx):
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
async def set(ctx, charname):
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)#get current charname
    oldcharname = mychar.name
    charlist = await datab.charlist(ctx.author.id)
    for guy in charlist:
        if re.search(charname,guy[1]) is not None:
            newcharname = guy[1]
            await datab.set(ctx.author.id, guy[0])
    await ctx.send(f"Switched from {oldcharname} to {newcharname}")
    await ctx.message.delete()

@char.command()
async def list(ctx):
    datab = database.DBManager
    charlist = await datab.charlist(ctx.author.id)
    embedVar = discord.Embed(title="Character List", description="", color=0x00ff00)
    namelist = ""
    for guy in charlist:
        namelist = namelist+ str(guy[1])+"\n"
    embedVar.add_field(name="Roster:",value=namelist, inline=False)
    await ctx.channel.send(embed=embedVar)
    await ctx.message.delete()

@char.command()
async def view(ctx):
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
    datastr = f"Playbook: {mychar.playbook}\nName: {mychar.name}\nLevel: {mychar.level}\nXP: {mychar.xp}\nDamage Die: {mychar.dmgdie}"
    embedVar.add_field(name="Basic Info", value=datastr, inline=False)
    statstr = f"Strength: {mychar.stats[0]} ({mychar.mod[0]}), Dexterity: {mychar.stats[1]} ({mychar.mod[1]}), Constitution: {mychar.stats[2]} ({mychar.mod[2]}), Wisdom: {mychar.stats[3]} ({mychar.mod[3]}), Intelligence: {mychar.stats[4]} ({mychar.mod[4]}), Charisma: {mychar.stats[5]} ({mychar.mod[5]})"
    embedVar.add_field(name="Stats", value=statstr, inline=False)
    embedVar.add_field(name="Health", value=f"{mychar.hp} of {mychar.hpmax} HP", inline=False)
    embedVar.add_field(name="Inventory", value=mychar.gear+f"\n\nLoad:{mychar.load}", inline=False)
    mymoves=mychar.moves.replace("||","\n")
    embedVar.add_field(name="Moves", value=mymoves, inline=False)
    mynotes=mychar.notes.replace("||","\n")
    embedVar.add_field(name="Notes", value=mynotes, inline=False)
    embedVar.set_thumbnail(url=mychar.picture)
    await ctx.channel.send(embed=embedVar)
    await ctx.message.delete()

#### SCENE FUNCTIONS #######

@bot.group(invoke_without_command = True)
async def scene(ctx):
    await new(ctx)

@scene.command()
async def new(ctx):
    for thescene in scenelist: #checking to make sure there isn't a scene already happening in this channel
        if str(thescene.channel) == str(ctx.channel.id):
            return
    message = await ctx.channel.send(f"```Start of a new scene!```")
    myscene = school.Scene(ctx.channel.id, message.id, ctx.author.id)
    scenelist.append(myscene)
    await message.pin()

@scene.command()
async def end(ctx):
    i=0
    for thescene in scenelist:
        if str(thescene.channel) == str(ctx.channel.id):
            scenelist.pop(i)
            message = await ctx.fetch_message(thescene.summary_message_id)
            await ctx.send("`Scene Over! Recap:`")
            await ctx.send("```\n"+thescene.pinned+"\n```")
            await message.unpin()
        i=i+1

@scene.command()
async def leave(ctx):
    datab = database.DBManager
    try:  #if no character, stop
        mychar = await database.get_char_data(ctx.author.id)
    except:
        await ctx.send("Need a character!")
        return
    for thescene in scenelist:
        if str(thescene.channel) == str(ctx.channel.id):
            thescene.leave(mychar.name)
            await ctx.send(f"`{mychar.name} has left the scene.`")
            message = await ctx.fetch_message(thescene.summary_message_id)
            thescene.update_pinned()
            await message.edit(content="```\n"+thescene.pinned+"\n```")

@scene.command()
async def join(ctx):
    datab = database.DBManager
    try:  #if no character, stop
        mychar = await database.get_char_data(ctx.author.id)
    except:
        await ctx.send("Need a character to join!")
        return
    for thescene in scenelist:
        if str(thescene.channel) == str(ctx.channel.id):
            thescene.join(mychar.name)
            message = await ctx.fetch_message(thescene.summary_message_id)
            thescene.update_pinned()
            await message.edit(content="```\n"+thescene.pinned+"\n```") 
    
@scene.command()
async def addnpc(ctx, *, npc_name = "NPC"):
    for thescene in scenelist:
        if str(thescene.channel) == str(ctx.channel.id):
            thescene.add_npc(npc_name)
            message = await ctx.fetch_message(thescene.summary_message_id)
            thescene.update_pinned()
            await message.edit(content="```\n"+thescene.pinned+"\n```") 

@scene.command()
async def npcleave(ctx, *, npc_name):
    for thescene in scenelist:
        if str(thescene.channel) == str(ctx.channel.id):
            npcfound = False
            for each in thescene.actors:
                if npcfound == False and re.search(npc_name, each, re.I) is not None:
                    npc_name = each
                    npcfound = True
            thescene.leave(npc_name)
            await ctx.send(f"`{npc_name} has left the scene`")
            message = await ctx.fetch_message(thescene.summary_message_id)
            thescene.update_pinned()
            await message.edit(content="```\n"+thescene.pinned+"\n```")

@scene.command()
async def info(ctx):
    for thescene in scenelist:
        if str(thescene.channel) == str(ctx.channel.id):
            await cxt.send("```\n"+thescene.pinned+"\n```")

@scene.command()
async def help(ctx):
    await ctx.send("Use `!scene begin` to start a scene. End the scene with `!scene end`.\nYou can add your active character to the scene with `!scene join`. The DM can add NPCs to the scene with `!scene addnpc [name]`.")

@scene.command()
async def note(ctx, cmd, note):
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    for thescene in scenelist:
        if str(thescene.channel) == str(ctx.channel.id):
            if cmd == "add" or cmd == "+":
                thescene.add_note(mychar.name, note)
            elif cmd == "remove" or cmd == "-":
                thescene.remove_note(mychar.name, note)
            else:
                pass
            message = await ctx.fetch_message(thescene.summary_message_id)
            thescene.update_pinned()
            await message.edit(content="```\n"+thescene.pinned+"\n```")
            

@scene.command()
async def npcnote(ctx, npc, cmd, note):
    for thescene in scenelist:
        if str(thescene.channel) == str(ctx.channel.id):
            if ctx.author.id != thescene.dm_id:
                ctx.send(f"Hey {ctx.author.id}, you didn't start this scene so you can't edit NPC notes")
                return
            npcfound = False
            for each in thescene.actors:
                if npcfound == False and re.search(npc, each, re.I) is not None:
                    npc = each
                    npcfound = True
            if cmd == "add" or cmd == "+":
                thescene.add_note(npc, note)
            elif cmd == "remove" or cmd == "-":
                thescene.remove_note(npc, note)
            else:
                pass
            message = await ctx.fetch_message(thescene.summary_message_id)
            thescene.update_pinned()
            await message.edit(content="```\n"+thescene.pinned+"\n```")

@bot.group(invoke_without_command = True)
async def lookup(ctx):
    await ctx.send("Use `!lookup monster [monster]` to have a monster statblock sent in a private message.\nUse `!lookup item [item]`, Use `!lookup move [move]`, and Use `!lookup playbook [playbook]` to look up stuff on the playbook")

@lookup.command()
async def monster(ctx, searchterm):
    datab = database.DBManager
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

@lookup.command()
async def item(ctx, searchterm):
    datab = database.DBManager
    result = await datab.eqmt_lookup(ctx, searchterm)
    tagdict = json.loads(result[0][2].replace("'", "\""))
    tagstr = ""
    for each in tagdict:
        tagstr=tagstr+"\n"
    embedVar = discord.Embed(title="Item: "+result[0][1], description="Tags: \n"+tagstr, color=0x00ff00)
    await ctx.channel.send(embed=embedVar)
    
@lookup.command()
async def playbook(ctx, searchterm):
    datab = database.DBManager
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

@lookup.command()
async def move(ctx, searchterm):
    datab = database.DBManager
    result = await datab.move_lookup(ctx, searchterm)
    print(result)
    try:
        print(result[0][1])
        embedVar = discord.Embed(title=result[0][1], description=result[0][2], color=0x00ff00)
    except:
        embedVar = discord.Embed(title="", description=result, color=0x00ff00)
    await ctx.channel.send(embed=embedVar)
    await ctx.message.delete()

#*********** QOL Commands and homebrew ******************

@bot.command()
async def moves(ctx):
    #get all the moves from the person, and then run lookup on them
    pass

@bot.group(invoke_without_command = True)
async def hbimport(ctx, *args):
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
            await ctx.send("monster help message")
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
        print("General import help message")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(TOKEN)

# https://discord.com/oauth2/authorize?client_id=1517333546153541662&permissions=8&integration_type=0&scope=bot
