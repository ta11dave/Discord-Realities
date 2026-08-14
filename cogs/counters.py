import discord
from discord.ext import commands
import re
import database
import school
import json

class CounterCMDs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("You got a cog to work. Nice.")
    
    @commands.group(invoke_without_command = True, aliases = ("cc",))
    async def CustomCounter(self, ctx, *args):
        if len(args)<1:
            mychar = await database.get_char_data(ctx.author.id)
            # !cc [counter] (mod)
            mycc = json.loads(mychar.counters.replace("'", "\""))
            embedVar = discord.Embed(title=mychar.name +"'s Custom Counters", description=ctx.author, color=0x00ff00)
            embedVar.set_thumbnail(url=mychar.picture)
            for each in mycc:
                embedVar.add_field(name=each["name"], value=f"Min: {each["min"]}\nMax: {each["max"]}\nValue: {each["value"]}", inline=False)
            await ctx.channel.send(embed=embedVar)
        else:
            ctx.send("I haven't gotten this far!")
    
    @CustomCounter.command()
    async def create(self, ctx, *args):
        datab = database.DBManager
        # !cc create [Name] [min] [max] [value]
        # if a name matches then overwrite
        # !cc -name Name -min 0 -max -5 -value 5 (technically in any order or omit)
        arglist = []
        for each in args:
            arglist.append(each) # make something mutable
        ccname = "Counter"
        ccmin = 0
        ccmax = 1
        ccval = ccmax
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
                    ccvalue = int(arglist[1])
                    arglist = arglist[2:]
        except:
            pass
        mycounter={}
        mycounter["name"] = ccname
        mycounter["min"] = ccmin
        mycounter["max"] = ccmax
        mycounter["value"] = ccvalue        
        
        await ctx.send(datab.updatechar(ctx.author.id, ["counter", "+", mycounter]))
    
    @CustomCounter.command()
    async def delete(self, ctx, ccname):
        datab = database.DBManager
        await ctx.send(await datab.updatechar(ctx.author.id, ["counter", "-", ccname]))
    
async def setup(bot):
    await bot.add_cog(CounterCMDs(bot))
