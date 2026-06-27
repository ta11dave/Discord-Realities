# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import d20 #https://d20.readthedocs.io/en/latest/start.html
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

bot = commands.Bot(command_prefix='!', intents=intents)

## References
# https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
# https://github.com/DungeonPaper/dungeon_world_data/tree/master
# https://gist.github.com/lykn/bac99b06d45ff8eed34c2220d86b6bf4

@bot.command()
async def test(ctx):
    print("\n*\ncharacter_registry: ", character_registry)
    print("character_pile: ", character_pile)
    print("user_registry: ", user_registry, "\n*\n")
    # await ctx.send(arg)

@bot.command()
async def char(ctx, *, args):
    args = args.split()
    # a new character
    if args[0] == "new":
        charname = ""
        for each in args[1:]:
            charname= charname+each+" "
        charname = charname[:len(charname)-1] #taking the space out
        if len(character_registry) == 0:
            ident = 0
        else:
            x=[]
            for each in character_registry:
                x.append(each[0])
            ident = max(x)+1
        character_registry.append((ident, ctx.author.id, charname)) #this will have to be replaced (can't change a tuple)
        
        #make new character, here's a placeholder
        placeholderchar = school.Character('Thief','Johnson the '+str(ident),'Fabulous',[10,10,10,10,10,10], "+6", "d8", "Human", "stuff", "Notes")
        character_pile.append([ident,placeholderchar])
        user_registry[ctx.author.id] = ident
        await ctx.send(f"New character made, ident is {ident} and the name is {charname}")
        
        
    elif args[0] == "view":
        await viewchar(ctx)
    elif args[0] == "list":
        await charlist(ctx)
    else:
        await charlist(ctx)


@bot.event
async def charlist(ctx):
    x=[]
    for char in character_registry:
        if char[1]==ctx.author.id:
            x.append(char[2])
    embedVar = discord.Embed(title="Character List", description="The Roster:", color=0x00ff00)
    for guy in x:
        embedVar.add_field(name=guy,value="", inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.event
async def viewchar(ctx):
    ident = user_registry[ctx.author.id] # get active character
    mychar = character_pile[ident][1] # refer to their sheet
    embedVar = discord.Embed(title=mychar.name, description="", color=0x00ff00)
    embedVar.add_field(name="Class", value=mychar.title, inline=False)
    embedVar.add_field(name="Name", value=mychar.name, inline=False)
    embedVar.add_field(name="Look", value=mychar.look, inline=False)
    if len(mychar.notes)>0:
        embedVar.add_field(name="Notes", value=mychar.notes, inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def moves(ctx, aname):
     embedVar = discord.Embed(title="Move Lookup", description="", color=0x00ff00)
     try:
        for move in mvs:
            if move.name == aname:
                embedVar.add_field(name=move.name, value=move.description, inline=False)
     except:
         embedVar.add_field(name="Idk man", value="No idea whatcha talking about", inline=False)
     await ctx.channel.send(embed=embedVar)

@bot.command()
async def monster(ctx, aname):
     embedVar = discord.Embed(title="Monster Lookup", description=aname, color=0x00ff00)
     try:
        for guy in mon:
            if guy.name == aname:
                embedVar.add_field(name="Description from the book", value=guy.description, inline=False)
                embedVar.add_field(name="Instinct", value=guy.instinct, inline=False)
                for attack in guy.attacks:
                    attackname = attack['name']
                    attackdamage = attack['damage']
                    attacktags = attack['tags']
                embedVar.add_field(name="Attacks", value=f"{attackname}: {attackdamage}. Tags:{attacktags}", inline=False)
     except:
         embedVar.add_field(name="Idk man", value="No idea whatcha talking about", inline=False)
     await ctx.channel.send(embed=embedVar)

@bot.command()
async def Equipment(ctx, aname):
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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(f"Error syncing commands: {e}")


bot.run(TOKEN)

# https://discord.com/oauth2/authorize?client_id=1517333546153541662&permissions=8&integration_type=0&scope=bot
