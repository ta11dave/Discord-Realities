import discord
from discord.ext import commands
import re
import database
import school
import json

scenelist = [] #all the scenes going on at any one time

class Scene(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("scene init")

    #### SCENE FUNCTIONS #######

    @commands.group(invoke_without_command = True)
    async def scene(self, ctx):
        await self.new(ctx)

    @scene.command()
    async def new(self, ctx):
        await ctx.message.delete()
        for thescene in scenelist: #checking to make sure there isn't a scene already happening in this channel
            if str(thescene.channel) == str(ctx.channel.id):
                return
        message = await ctx.channel.send(f"```Start of a new scene!```")
        myscene = school.Scene(ctx.channel.id, message.id, ctx.author.id)
        scenelist.append(myscene)
        await message.pin()

    @scene.command()
    async def end(self, ctx):
        await ctx.message.delete()
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
    async def leave(self, ctx):
        await ctx.message.delete()
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
    async def join(self, ctx):
        await ctx.message.delete()
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
                await ctx.send(f"`{mychar.name} has joined the scene!`")
        
    @scene.command()
    async def addnpc(self, ctx, *, npc_name = "NPC"):
        await ctx.message.delete()
        for thescene in scenelist:
            if str(thescene.channel) == str(ctx.channel.id):
                if ctx.author.id != thescene.dm_id:
                    ctx.send(f"Hey {ctx.author.id}, you didn't start this scene so you can't add NPCs!")
                    return
                thescene.add_npc(npc_name)
                message = await ctx.fetch_message(thescene.summary_message_id)
                thescene.update_pinned()
                await message.edit(content="```\n"+thescene.pinned+"\n```") 
                await ctx.send(f"`{npc_name} has joined the scene!`")

    @scene.command()
    async def npcleave(self, ctx, *, npc_name):
        await ctx.message.delete()
        for thescene in scenelist:
            if str(thescene.channel) == str(ctx.channel.id):
                if ctx.author.id != thescene.dm_id:
                    ctx.send(f"Hey {ctx.author.id}, you didn't start this scene so you can't control NPCs!")
                    return
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
    async def info(self, ctx):
        await ctx.message.delete()
        for thescene in scenelist:
            if str(thescene.channel) == str(ctx.channel.id):
                await ctx.channel.send("```\n"+thescene.pinned+"\n```")

    @scene.command()
    async def help(self, ctx):
        await ctx.send("Use `!scene begin` to start a scene. End the scene with `!scene end`.\nYou can add your active character to the scene with `!scene join`. The DM can add NPCs to the scene with `!scene addnpc [name]`.")

    @scene.command()
    async def note(self, ctx, cmd, note):
        await ctx.message.delete()
        datab = database.DBManager
        mychar = await database.get_char_data(ctx.author.id)
        for thescene in scenelist:
            if str(thescene.channel) == str(ctx.channel.id):
                if cmd == "add" or cmd == "+":
                    thescene.add_note(mychar.name, note)
                    await ctx.send(f"Added note about {mychar.name}:\n`{note}`")
                elif cmd == "remove" or cmd == "-":
                    thescene.remove_note(mychar.name, note)
                    await ctx.send(f"Removed note about {mychar.name}:\n`{note}`")
                else:
                    pass
                message = await ctx.fetch_message(thescene.summary_message_id)
                thescene.update_pinned()
                await message.edit(content="```\n"+thescene.pinned+"\n```")
                

    @scene.command()
    async def npcnote(self, ctx, npc, cmd, note):
        await ctx.message.delete()
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
                    await ctx.send(f"Added note about {npc}:\n`{note}`")
                elif cmd == "remove" or cmd == "-":
                    thescene.remove_note(npc, note)
                    await ctx.send(f"Removed note about {npc}:\n`{note}`")
                else:
                    pass
                message = await ctx.fetch_message(thescene.summary_message_id)
                thescene.update_pinned()
                await message.edit(content="```\n"+thescene.pinned+"\n```")


async def setup(bot):
    await bot.add_cog(Scene(bot))
