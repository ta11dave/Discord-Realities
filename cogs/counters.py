import discord
from discord.ext import commands
import re
import database
import school
import json

class CounterCMDs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("counters init")

    @commands.command()
    async def test(self, ctx):
        await ctx.send("You got a cog to work. Nice.")
    
    @commands.group(invoke_without_command = True, aliases = ("cc",))
    async def CustomCounter(self, ctx, *args):
        datab = database.DBManager
        mychar = await database.get_char_data(ctx.author.id)
        if len(args)<1: # list all CCs
            try:
                embedVar = discord.Embed(title=f"{mychar.name}'s Counters", description=f"<@{ctx.author.id}>", color=0x00ff00)
                embedVar.set_thumbnail(url=mychar.picture)
                for each in mychar.cc:
                    embedVar.add_field(name=each.name, value=f"Min: {each.minimum}, Max: {each.maximum}, Value: {each.value}", inline=False)
                await ctx.channel.send(embed=embedVar)
            except Exception as e:
                await ctx.send(f"You either don't have any counters or ***something went wrong: {e}***.")
        elif len(args) == 1: #show a specific cc
            try:
                for each in mychar.cc:
                    if re.search(args[0], each.name, re.I) is not None:
                        embedVar = discord.Embed(title=f"{mychar.name}'s Counters", description=f"<@{ctx.author.id}>", color=0x00ff00)
                        embedVar.set_thumbnail(url=mychar.picture)
                        embedVar.add_field(name=each.name, value=f"Description: {each.desc}\nMin: {each.minimum}, Max: {each.maximum}, Value: {each.value}", inline=False)
                        await ctx.channel.send(embed=embedVar)
                        return
            except:
                await ctx.send("Couldn't find a counter you were looking for.")
        elif len(args) >1: #assume modifying a cc# 
            try:
                found = False
                for each in mychar.cc:
                    if re.search(args[0], each.name, re.I) is not None and found == False:
                        found = True
                        if args[1][0] == '+':
                            each.value = each.value + int(args[1][1:])
                            if each.value > each.maximum:
                                each.value = each.maximum
                        elif args[1][0] == '-':
                            each.value = each.value - int(args[1][1:])
                            if each.value < each.minimum:
                                each.value = each.minimum
                        else:
                            each.value = int(args[1][1:])
                            if each.value > each.maximum:
                                each.value = each.maximum
                            elif each.value < each.minimum:
                                each.value = each.minimum
                        embedVar = discord.Embed(title=f"{mychar.name}'s Counters", description=f"<@{ctx.author.id}>", color=0x00ff00)
                        embedVar.set_thumbnail(url=mychar.picture)
                        embedVar.add_field(name=each.name, value=f"{each.value}/{each.maximum}", inline=False)
                        await ctx.channel.send(embed=embedVar)
                #make string and push to db
                ccarray = []
                for each in mychar.cc:
                    eachcounter = {}
                    eachcounter["name"] = each["name"]
                    eachcounter["min"] = each["min"]
                    eachcounter["max"] = each["max"]
                    eachcounter["value"] = each["value"]
                    ccarray.append(eachcounter)
                counterstr = json.dumps(ccarray).replace("\"", "'")
                responce = await datab.updatechar(ctx.author.id, ["counter", "push", counterstr])
                if responce != "Pushed":
                    print(responce)
            except Exception as e:
                print("Oh no it failed: ", e)
                

    @CustomCounter.command()
    async def create(self, ctx, *args):
        datab = database.DBManager
        # !cc create [Name] [min] [max] [value]
        # if a name matches then overwrite
        # !cc -name Name -min 0 -max -5 -value 5 -desc "text" (technically in any order or omit)
        arglist = []
        for each in args:
            arglist.append(each) # make something mutable
        ccname = "Counter"
        ccmin = 0
        ccmax = 1
        ccval = 0
        ccdesc = f"Counter for {ccname}"
        try:
            while len(arglist) >= 1:
                if arglist[0] == "-name":
                    ccname = arglist[1]
                    arglist = arglist[2:]
                if arglist[0] == "-min":
                    ccmin = int(arglist[1])
                    arglist = arglist[2:]
                if arglist[0] == "-max":
                    ccmax = int(arglist[1])
                    arglist = arglist[2:]
                if arglist[0] == "-value":
                    ccval = int(arglist[1])
                    arglist = arglist[2:]
                if arglist[0] == "-desc":
                    ccdesc = arglist[1]
                    arglist = arglist[2:]
        except Exception as e:
            print("nice: ", e)
        mycounter={}
        mycounter["name"] = ccname
        mycounter["min"] = ccmin
        mycounter["max"] = ccmax
        if ccval == 0:
            mycounter["value"] = ccmax
        else:
            mycounter["value"] = ccval
        mycounter["desc"] = ccdesc
        result = await datab.updatechar(ctx.author.id, ["counter", "+", mycounter])
        await ctx.send(result)
    
    @CustomCounter.command()
    async def delete(self, ctx, ccname):
        datab = database.DBManager
        await ctx.send(await datab.updatechar(ctx.author.id, ["counter", "-", ccname]))
    
async def setup(bot):
    await bot.add_cog(CounterCMDs(bot))
