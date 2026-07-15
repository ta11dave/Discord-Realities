# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
import database
import d20 
import school

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

@bot.command()
async def resetlookup(ctx):
        await database.reset()

@bot.command()
async def sheetimport(ctx):
    # import a sheet by attaching a file
    pass

@bot.command()
async def roll(ctx, stat="", *args):
    if stat == "help":
        await ctx.send("Use `!roll` to roll dice! The standard format should look something like `!roll dex +1 \"Discern Realities\" adv`")
        return
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title=mychar.name +" makes a move!", description=ctx.author, color=0x00ff00)
    embedVar.set_thumbnail(url=mychar.picture)
    stat = stat[:3].lower()
    rollstr = "2d6"
    myargs = []
    i=0
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
        if arg[:1]== ("+" or "-"):
            rollstr=rollstr+str(arg)
        else:
            rollstr = rollstr + " ["+arg+"] "

    if stat == "str":
        rollstr = rollstr + "+"+ str(mychar.mod[0])
    elif stat == "dex":
        rollstr = rollstr + "+"+ str(mychar.mod[1])
    elif stat == "con":
        rollstr = rollstr + "+"+ str(mychar.mod[2])
    elif stat == "int":
        rollstr = rollstr + "+"+ str(mychar.mod[3])
    elif stat == "wis":
        rollstr = rollstr + "+"+ str(mychar.mod[4])
    elif stat == "cha":
        rollstr = rollstr + "+"+ str(mychar.mod[5])
    elif stat == "adv":
        rollstr = "3d6kh2"
    elif stat == "dis":
        rollstr = "3d6kl2"
    else:
        pass
    
    theroll = d20.roll(rollstr)
    
    embedVar.add_field(name="", value=theroll, inline=False)
    if int(theroll.total)<= 6:
        embedVar.add_field(name="Result", value="Oh no. At least you got an XP.", inline=False)
        #add an XP to the character
    elif int(theroll.total) in [7,8,9]:
        embedVar.add_field(name="Result", value="Mixed Success.", inline=False)
    elif int(theroll.total)>9:
        embedVar.add_field(name="Result", value="Full Success!", inline=False)
    else:
        embedVar.add_field(name="Result", value="Something broke", inline=False)
    
    await ctx.channel.send(embed=embedVar)


@bot.command()
async def xp(ctx, amt=0):
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
    oldxp = await datab.XP_view(ctx.author.id)
    if amt == 0:
        embedVar.add_field(name="XP", value="You have "+str(mychar.xp)+" xp.", inline=False)
    else:
        newxp = await datab.updatechar("xp", amt)
        embedVar.add_field(name="XP", value="Your XP went from "+str(oldxp)+" to "+str(mychar.xp)+"!", inline=False)
    await ctx.channel.send(embed=embedVar)

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
    await ctx.send(f"New character made named {charname}")

@char.command()
async def make(ctx, playbook):
    #update all the stuff we already know
    await ctx.send("Under Construction")

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

@char.command()
async def update(ctx, *args):
    datab=database.DBManager
    responcetext = await datab.updatechar(ctx.author.id, args)
    print(responcetext)

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

@char.command()
async def view(ctx):
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
    embedVar.add_field(name="Class", value=mychar.playbook, inline=False)
    embedVar.add_field(name="Name", value=mychar.name, inline=False)
    embedVar.add_field(name="XP", value=mychar.xp, inline=False)
    if len(mychar.notes)>0:
        embedVar.add_field(name="Notes", value=mychar.notes, inline=False)
    await ctx.channel.send(embed=embedVar)

#### SCENE FUNCTIONS #######

@bot.group(invoke_without_command = True)
async def scene(ctx):
    for thescene in scenelist: #checking to make sure there isn't a scene already happening in this channel
        if str(thescene.channel) == str(ctx.channel.id):
            return
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
            await message.unpin()
        i=i+1

@scene.command()
async def join(ctx):
    try:  #if no character, stop
        await ctx.send("gotta pull data from the database now")
        return #remove this when figured out
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
async def info(ctx):
    #print the scene pinned message here
    pass

@scene.command()
async def help(ctx):
    await ctx.send("Use `!scene begin` to start a scene. End the scene with `!scene end`.\nYou can add your active character to the scene with `!scene join`. The DM can add NPCs to the scene with `!scene addnpc [name]`.")

@bot.group(invoke_without_command = True)
async def lookup(ctx):
    await ctx.send("Use `!lookup monster [monster]` to have a monster statblock sent in a private message.\nUse `!lookup item [item]`, Use `!lookup move [move]`, and Use `!lookup playbook [playbook]` to look up other things")

@lookup.command()
async def monster(ctx, searchterm):
    datab = database.DBManager
    result = await datab.monster_lookup(ctx, searchterm)
    print(result)

@lookup.command()
async def item(ctx, searchterm):
    datab = database.DBManager
    result = await datab.eqmt_lookup(ctx, searchterm)
    print(result)

@lookup.command()
async def playbook(ctx, searchterm):
    datab = database.DBManager
    result = await datab.playbook_lookup(ctx, searchterm)
    print(result)

@lookup.command()
async def move(ctx, searchterm):
    datab = database.DBManager
    result = await datab.move_lookup(ctx, searchterm)
    print(result)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(TOKEN)

# https://discord.com/oauth2/authorize?client_id=1517333546153541662&permissions=8&integration_type=0&scope=bot
