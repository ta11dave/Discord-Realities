# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import d20 #https://d20.readthedocs.io/en/latest/start.html

import school

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

#initialize character registry, a dynamic array of tuples
character_registry = []

#a user registry, also a dynamic array but it'll have the active character for each user
user_registry = []

#where all the character objects are stored
character_pile = []

bot = commands.Bot(command_prefix='!', intents=intents)

## References
# https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
# https://github.com/DungeonPaper/dungeon_world_data/tree/master
# https://gist.github.com/lykn/bac99b06d45ff8eed34c2220d86b6bf4

@bot.command()
async def test(ctx):
    print(f"Character_Registery = {character_registry}")
    # await ctx.send(arg)

@bot.command()
async def newchar(ctx, *, charname):
    if len(character_registry) == 0:
        ident = 1
    else:
        x=[]
        for each in character_registry:
            x.append(each[0])
        ident = max(x)+1
    character_registry.append((ident, ctx.author.id, charname)) #this will have to be replaced (can't change a tuple)
    character_pile.append([ident,0]) 
    await ctx.send(f"New character made, ident is {ident} and the name is {charname}")

@bot.command()
async def charlist(ctx):
    x=[]
    for char in character_registry:
        if char[1]==ctx.author.id:
            x.append(char[2])
    embedVar = discord.Embed(title="Character List", description="The Roster:", color=0x00ff00)
    for guy in x:
        embedVar.add_field(name=guy,value="", inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def viewchar(ctx):
    embedVar = discord.Embed(title="Character Name", description="Heres your guy", color=0x00ff00)
    embedVar.add_field(name="Class", value="Paladin", inline=False)
    embedVar.add_field(name="HP", value="idk like 7", inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

#BROKEN - https://discordpy.readthedocs.io/en/stable/faq.html#why-does-on-message-make-my-commands-stop-working
# don't plan on using this anyway
# @bot.event
# async def on_message(message):
    # if message.author == bot.user:
        # return
        
    # if message.content.startswith('...'):
        # await message.channel.send("whatcha thinking about?")

bot.run(TOKEN)

# https://discord.com/oauth2/authorize?client_id=1517333546153541662&permissions=8&integration_type=0&scope=bot
