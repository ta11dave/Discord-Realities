# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
#import d20 #https://d20.readthedocs.io/en/latest/start.html this is for rolling dice
import school
from tomes import mon, cls, eqmt, mvs

#secure token stuff
load_dotenv()
TOKEN = os.getenv("TOKEN")

#discord permissions
intents = discord.Intents.default()
intents.message_content = True

character_registry = [] # initialize character registry, an array of (ident, userid, char_name)
user_registry = {} # a user registry with the active character for each user
character_pile = [] # dictionary of idents and character objects
scenelist = [] #all the scenes going on at any one time

bot = commands.Bot(command_prefix='!', intents=intents)

## References
# https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
# https://github.com/DungeonPaper/dungeon_world_data/tree/master
# https://gist.github.com/lykn/bac99b06d45ff8eed34c2220d86b6bf4

@bot.command()
async def test(ctx):
    print("\n*\ncharacter_registry: ", character_registry)
    print("character_pile: ", character_pile)
    print("user_registry: ", user_registry)
    print("scenelist: ", scenelist , "\n*\n")

@bot.command()
async def xp(ctx, amt=0):
    try:
        ident = user_registry[ctx.author.id]
        mychar = character_pile[ident][1]
        mychar.myxp = mychar.myxp + amt
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
    if len(character_registry) == 0:
        ident = 0
    else:
        x=[]
        for each in character_registry:
            x.append(each[0])
        ident = max(x)+1
    character_registry.append((ident, ctx.author.id, charname)) #this will have to be replaced (can't change a tuple)
    
    #make new character, start with blanks
    placeholderchar = school.Character("",charname,"",[10,10,10,10,10,10], "", "")
    character_pile.append([ident,placeholderchar])
    user_registry[ctx.author.id] = ident
    await ctx.send(f"New character made, ident is {ident} and the name is {charname}")

@char.command()
async def make(ctx, playbook):
    for aclass in cls:
        if re.search(playbook,aclass.name,re.I) is not None:
            myclass = aclass
    #update all the stuff we already know
    ident = user_registry[ctx.author.id] # get active character
    mychar = character_pile[ident][1] # refer to their sheet
    mychar.load = myclass.load
    mychar.dmgdie = myclass.damage
    #bonds
    #looks
    #alignments
    #for each in myclass.starting_moves:
    #alignments_list
    #race_moves
    #gear_choices
    
    embedVar = discord.Embed(title=f"Make a {myclass.name}", description="Step by step things", color=0x00ff00)
    embedVar.add_field(name="New Moves!",value=f"You gained the moves: {mychar.moves}", inline=False)
    embedVar.add_field(name="Damage Die!",value=f"Your damage die is now: {mychar.dmgdie}", inline=False)
    
    await ctx.channel.send(embed=embedVar)

@char.command()
async def list(ctx):
    x=[]
    for char in character_registry:
        if char[1]==ctx.author.id:
            x.append(char[2])
    embedVar = discord.Embed(title="Character List", description="The Roster:", color=0x00ff00)
    for guy in x:
        embedVar.add_field(name=guy,value="", inline=False)
    await ctx.channel.send(embed=embedVar)

@char.command()
async def change(ctx, *, newcharname):
    old = user_registry[ctx.author.id]
    x=[]
    for char in character_registry:
        if char[1]==ctx.author.id:
            x.append(char) #a list of ident and charname
    for char in x:
        if re.search(newcharname,char[2],re.I) is not None:
            user_registry[ctx.author.id] = char[0]
    await ctx.send("Character changed to "+str((character_pile[user_registry[ctx.author.id]][1]).name))

@char.command()
async def view(ctx):
    ident = user_registry[ctx.author.id] # get active character
    mychar = character_pile[ident][1] # refer to their sheet
    embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
    embedVar.add_field(name="Class", value=mychar.title, inline=False)
    embedVar.add_field(name="Name", value=mychar.name, inline=False)
    embedVar.add_field(name="Look", value=mychar.look, inline=False)
    embedVar.add_field(name="XP", value=mychar.myxp, inline=False)
    if len(mychar.notes)>0:
        embedVar.add_field(name="Notes", value=mychar.notes, inline=False)
    await ctx.channel.send(embed=embedVar)

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
        ident = user_registry[ctx.author.id]
        mychar = character_pile[ident][1]
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
