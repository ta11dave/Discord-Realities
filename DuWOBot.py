# This example requires the 'message_content' intent.
import discord
from discord.ext import commands
from discord.ui import view
import os
from dotenv import load_dotenv
import re
import database
import d20 
import school
import json
import cogs.char
import logging

# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

#secure token stuff
load_dotenv()
TOKEN = os.getenv("TOKEN")

#discord permissions
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

#make sure the data is there in case you messed it up

async def load_cogs():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            try:
                await bot.load_extension("cogs." + f[:-3])
            except Exception as e:
                print(f'Failed to load cog: {e}')

@bot.command()
async def resetlookup(ctx):
    # DO NOT USE UNLESS YOU ARE HOSTING YOUR OWN BOT
    await database.reset()

@bot.command()
async def roll(ctx, *args):
    try:
        #await ctx.message.delete()
        datab = database.DBManager
        mychar = await database.get_char_data(ctx.author.id)
        myargs = []
        if args==():
            myargs=["2d6"]
        else:
            rollstr = ""
            if args[0].lower() == "ouch":
                embedVar = discord.Embed(title=mychar.name +" takes damage!", description=f"<@{ctx.author.id}>", color=0x00ff00)
                embedVar.set_thumbnail(url=mychar.picture)
                #if armor isn't there or is 0
                theroll = d20.roll(args[1])
                embedVar.add_field(name="", value=theroll, inline=False)
                damagedone = theroll.total
                if len(args)>2:
                    damagedone = theroll.total - int(args[2])
                    if damagedone < 0:
                        damagedone = 0
                    embedVar.add_field(name="But you have armor!", value=f"{args[2]} armor!\nYou take {damagedone} damage.", inline=False)
                if mychar.hp-damagedone<=0:
                    embedVar.add_field(name="You are at 0 HP!", value="", inline=False)
                    await datab.updatechar(ctx.author.id,["hp", "0"])
                else:
                    embedVar.add_field(name="Current HP", value=str(mychar.hp-damagedone)+"/"+str(mychar.hpmax), inline=False)
                    await datab.updatechar(ctx.author.id,["hp", "-"+str(int(damagedone))])
                await ctx.channel.send(embed=embedVar)
                return
            
            embedVar = discord.Embed(title=mychar.name +" rolls!", description=f"<@{ctx.author.id}>", color=0x00ff00)
            embedVar.set_thumbnail(url=mychar.picture)
            i=0
            for arg in args:
                if arg in ["dmg", "damage"]:
                    myargs.append(mychar.dmgdie + "[damage]")
                elif arg.lower() == "str":
                    myargs.append("2d6+"+ str(mychar.mod[0]) + " [str] ")
                elif arg.lower() == "dex":
                    myargs.append("2d6+"+ str(mychar.mod[1]) + " [dex] ")
                elif arg.lower() == "con":
                    myargs.append("2d6+"+ str(mychar.mod[2]) + " [con] ")
                elif arg.lower() == "int":
                    myargs.append("2d6+"+ str(mychar.mod[3]) + " [int] ")
                elif arg.lower() == "wis":
                    myargs.append("2d6+"+ str(mychar.mod[4]) + " [wis] ")
                elif arg.lower() == "cha":
                    myargs.append("2d6+"+ str(mychar.mod[5]) + " [cha] ")
                elif arg[:1]=="+" or arg[:1]=="-" or arg[0] == int(arg[0]):
                    myargs.append(str(arg))
                else:
                    myargs.append(" ["+arg+"] ")
        rollstr = "".join(myargs)
        
        theroll = d20.roll(rollstr)
        embedVar = discord.Embed(title=mychar.name +" rolls!", description=f"<@{ctx.author.id}>", color=0x00ff00)
        embedVar.set_thumbnail(url=mychar.picture)
        embedVar.add_field(name="", value=theroll, inline=False)
        
        if "str" in rollstr or "dex" in rollstr or"con" in rollstr or"int" in rollstr or"wis" in rollstr or"cha" in rollstr:
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
    except Exception as e:
        await ctx.send(e)


@bot.command()
async def camp(ctx):
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    if mychar.level >= 10:
        await ctx.send("Level 10 is as high as it goes!")
        return
    if mychar.xp >= mychar.level+7:
        await datab.updatechar(ctx.author.id,["level", mychar.level+1])
        await datab.updatechar(ctx.author.id,["xp", str(mychar.xp-7)])
        await ctx.send(f"Leveled up {mychar.name} to {mychar.level+1}! Increase a stat by one and add a new move!")
    else:
        await ctx.send(f"You have {mychar.xp} XP and need {mychar.level+7} XP to level up!")
    if mychar.hp < mychar.hpmax:
        amt = mychar.hpmax/2
        if amt + mychar.hp > mychar.hpmax:
            amt = mychar.hpmax - mychar.hp
        newhp = await datab.updatechar(ctx.author.id,["hp", "+"+str(int(amt))])
    await ctx.send(newhp)

@bot.command()
async def xp(ctx, amt="0"):
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title=mychar.name, description=f"<@{ctx.author.id}>", color=0x00ff00)
    embedVar.set_thumbnail(url=mychar.picture)
    oldxp = mychar.xp
    if amt == "0":
        embedVar.add_field(name="XP", value="You have "+str(mychar.xp)+" xp.", inline=False)
    else:
        newxp = await datab.updatechar(ctx.author.id,["xp", amt])
        embedVar.add_field(name="XP", value="Your XP went from "+str(oldxp)+" to "+str(newxp)+"!", inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def coin(ctx, amt="0"):
    await ctx.message.delete()
    datab = database.DBManager
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title=mychar.name, description=f"<@{ctx.author.id}>", color=0x00ff00)
    embedVar.set_thumbnail(url=mychar.picture)
    oldcoin = mychar.coin
    if amt == "0":
        embedVar.add_field(name="Coin", value="You have "+str(mychar.coin)+" coin.", inline=False)
    else:
        newcoin = await datab.updatechar(ctx.author.id,["coin", amt])
        embedVar.add_field(name="Coin", value="Ka-Ching! Coin went from "+str(oldcoin)+" to "+str(newcoin)+"!", inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command()
async def movelist(ctx):
    await ctx.message.delete()
    mychar = await database.get_char_data(ctx.author.id)
    embedVar = discord.Embed(title="Move List", description="", color=0x00ff00)
    embedVar.set_thumbnail(url=mychar.picture)
    embedVar.add_field(name="Basic Moves", value="Hack and Slash\nVolley\nDefy Danger\nDefend\nSpout Lore\nDiscern Realities\nParley\nAid or Interfere", inline=False)
    embedVar.add_field(name="Special Moves", value="Last Breath\nEncumberance\nMake Camp\nTake Watch\nUndertake a Perilous Journey\nEnd of Session\nCarouse\nSupply\nRecover\nRecruit\nOutstanding Warrants\nBolster", inline=False)
    embedVar.add_field(name=f"{mychar.name}'s Moves", value=str(mychar.moves).replace("%%", "\n"), inline=False)
    await ctx.channel.send(embed=embedVar)

@bot.command(aliases = ("up",))
async def update(ctx, *args):
    await ctx.message.delete()
    if len(args)<1:
        args = "help"
    datab=database.DBManager
    responcetext = await datab.updatechar(ctx.author.id, args)
    await ctx.send(responcetext)

@bot.command(aliases = ("a",))
async def m(ctx):
    await ctx.message.delete()
    #get all the moves from the person, and then run lookup on them
    mychar = await database.get_char_data(ctx.author.id)
    movelist = mychar.moves.split("%%")
    for each in movelist:
        datab = database.DBManager
        result = await datab.move_lookup(ctx, each)
        try:
            if result[0][1] == 0:
                pass # this should also trigger the crash
            embedVar = discord.Embed(title=result[0][1], description=result[0][2], color=0x00ff00)
            embedVar.set_thumbnail(url=mychar.picture)
        except:
            embedVar = discord.Embed(title="Error", description=result, color=0x00ff00)
        await ctx.author.send(embed=embedVar)
    await ctx.channel.send("Sent you a DM! (It's a lot of embeds)")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        await load_cogs()
    except Exception as e:
        print(f"Error syncing commands: {e}")

# bot.run(TOKEN, log_handler=handler)
bot.run(TOKEN)
# https://discord.com/oauth2/authorize?client_id=1517333546153541662&permissions=8&integration_type=0&scope=bot
