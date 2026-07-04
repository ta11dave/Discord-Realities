# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
import database
#import d20 #https://d20.readthedocs.io/en/latest/start.html this is for rolling dice
import school
from tomes import mon, cls, eqmt, mvs

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
# https://gist.github.com/lykn/bac99b06d45ff8eed34c2220d86b6bf4

@bot.command()
async def test(ctx):
    database.restore_lookup()
    print("scenelist: ", scenelist , "\n*\n")

@bot.command()
async def xp(ctx, amt=0):
    try:
        #get xp from database
        #update new xp
        embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
        embedVar.add_field(name="XP", value=mychar.myxp, inline=False)
        await ctx.channel.send(embed=embedVar)
    except:
        await ctx.send("Something went wrong, no xp for you")

@bot.group(invoke_without_command = True)
async def char(ctx):
    await ctx.send("Use `!char new [name]` to make a new character, `!char list` to see all your characters, and `char view` to see your current character.")
    
@char.command()
async def new(ctx, *args):
    charname = ""
    for each in args:
        charname= charname+each+" "
    if charname == "":
        await ctx.send("GOtta enter a name, choose wisely!")
        return
    charname = charname[:len(charname)-1] #taking the space out
    datab = database.DBManager
    await datab.newchar(ctx.author.id, charname)
    await ctx.send(f"New character made named {charname}")

@char.command()
async def make(ctx, playbook):
    #update all the stuff we already know
    await ctx.send("Under Construction")

@char.command()
async def list(ctx):
    datab = database.DBManager
    test = await datab.charlist(ctx.author.id)
    # get data from db
    embedVar = discord.Embed(title="Character List", description="", color=0x00ff00)
    namelist = ""
    for guy in test:
        namelist = namelist+ str(guy[1])+"\n"
    embedVar.add_field(name="Roster:",value=namelist, inline=False)
    await ctx.channel.send(embed=embedVar)

@char.command()
async def change(ctx, *, newcharname):
    # this needs to be totally redone
    #await ctx.send("Character changed to "+str((character_pile[user_registry[ctx.author.id]][1]).name))
    pass

@char.command()
async def view(ctx):
    # mychar = from database
    embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
    embedVar.add_field(name="Class", value=mychar.title, inline=False)
    embedVar.add_field(name="Name", value=mychar.name, inline=False)
    embedVar.add_field(name="Look", value=mychar.look, inline=False)
    embedVar.add_field(name="XP", value=mychar.myxp, inline=False)
    if len(mychar.notes)>0:
        embedVar.add_field(name="Notes", value=mychar.notes, inline=False)
    await ctx.channel.send(embed=embedVar)

####  LOOKUP FUNCTIONS #######

@bot.command()
async def moves(ctx, aname):
    embedVar = discord.Embed(title="Move Lookup", description="", color=0x00ff00)
    results= []
    foundit = False
    for move in mvs:
        if re.search(aname,move.name,re.I) is not None and foundit == False:
            results.append(move)
        if aname == move.name:
            foundit = True
            results = [move]
    if len(results)==0:
        await ctx.channel.send("Not found")
    elif len(results)==1:
        embedVar.add_field(name=results[0].name, value=results[0].description, inline=False)
    elif len(results)>24:
        embedVar.add_field(name="Hold up", value="Too many results; this breaks the embed.", inline=False)
    else:
        embedVar.add_field(name="*Multiple Options, Choose one and try again!*", value="", inline=False)
        answer=""
        for result in results:
            answer=answer+result+"\n"
        embedVar.add_field(name="Options:", value=answer, inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def monster(ctx, aname):
    embedVar = discord.Embed(title="Monster Lookup", description=aname, color=0x00ff00)
    results=[]
    foundit = False
    for guy in mon:
        if re.search(aname,guy.name,re.I) is not None and foundit == False:
            results.append(guy) #the whole object this time
        if aname == guy.name:
            foundit = True
            results = [guy]
    if len(results)==0:
        await ctx.channel.send("Not found")
    elif len(results)==1:
        guy = results[0]
        embedVar.add_field(name="Description from the book", value=guy.description, inline=False)
        embedVar.add_field(name="Instinct", value=guy.instinct, inline=False)
        for attack in guy.attacks:
            attackname = attack['name']
            attackdamage = attack['damage']
            attacktags = attack['tags']
        embedVar.add_field(name="Attacks", value=f"{attackname}: {attackdamage}. Tags:{attacktags}", inline=False)
    elif len(results)>24:
        embedVar.add_field(name="Hold up", value="Too many results; this breaks the embed.", inline=False)
    else:
        embedVar.add_field(name="*Multiple Options, Choose one and try again!*", value="", inline=False)
        answer=""
        for result in results:
            answer=answer+result.name+"\n"
        embedVar.add_field(name="Options:", value=answer, inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def items(ctx, aname):
    embedVar = discord.Embed(title="Equipment Lookup", description=aname, color=0x00ff00)
    if aname == 'list':
        x=""
        for thing in eqmt:
            x= x+thing.name+"\n"
        embedVar.add_field(name="Items", value=x, inline=False)
        pass
    try:
        for thing in eqmt:
            if thing.name == aname:
                embedVar.add_field(name="Tags", value=thing.tags, inline=False)
    except:
        embedVar.add_field(name="Idk man", value="No idea whatcha talking about", inline=False)
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


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(f"Error syncing commands: {e}")


bot.run(TOKEN)

# https://discord.com/oauth2/authorize?client_id=1517333546153541662&permissions=8&integration_type=0&scope=bot
