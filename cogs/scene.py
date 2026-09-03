import asyncio
import aiosqlite
import discord
from discord.ext import commands
import re
import database
import school
import json

scenedb = "scenes.db"

class Scene(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("scene init")

    #### SCENE FUNCTIONS #######

    @commands.group(invoke_without_command = True, aliases = ("s",))
    async def scene(self, ctx):
        pass

    @scene.command()
    async def begin(self, ctx):
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)}") as cursor:
                    async for row in cursor:
                        pass
            await ctx.send("There is already a scene happening in this channel!")
            return
        except:
            await ctx.message.delete()
            message = await ctx.channel.send(f"```Start of a new scene!```")
            await message.pin()
            async with aiosqlite.connect(scenedb) as db:
                await db.execute(f"CREATE TABLE IF NOT EXISTS scene_{str(ctx.channel.id)} (id INTEGER PRIMARY KEY, userid TEXT, actors TEXT, turn INTEGER, notes TEXT, pin_ID TEXT, chartype TEXT)")
                await db.execute(f"INSERT INTO scene_{str(ctx.channel.id)} (userid, actors, turn, notes, pin_ID, chartype) VALUES (?, ?, ?, ?, ?, ?)", (str(ctx.author.id), "", 0, "", str(message.id), "DM"))
                await db.commit()

    @scene.command()
    async def end(self, ctx):
        await ctx.message.delete()
        async with aiosqlite.connect(scenedb) as db:
            async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)} WHERE id = 1") as cursor:
                DMrow = await cursor.fetchone()
        message = await ctx.fetch_message(int(DMrow[5]))
        await message.unpin()
        async with aiosqlite.connect(scenedb) as db:
            await db.execute(f"DROP TABLE scene_{str(ctx.channel.id)}")
            await db.commit()
        await ctx.send("## Scene has ended\nRecap: \n"+str(message.content))

    @scene.command()
    async def join(self, ctx):
        await ctx.message.delete()
        datab = database.DBManager
        try:  #if no character, stop
            mychar = await database.get_char_data(ctx.author.id)
        except:
            await ctx.send("Need a character to join!")
            return        
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)}") as cursor:
                    async for row in cursor:
                        pass
        except:
            await ctx.send("No scene to join!")
        async with aiosqlite.connect(scenedb) as db:
            await db.execute(f"INSERT INTO scene_{str(ctx.channel.id)} (userid, actors, turn, notes, pin_ID, chartype) VALUES (?, ?, ?, ?, ?, ?)", (str(ctx.author.id), mychar.name, 0, "", "", "PC"))
            await db.commit()
            await UpdatePin(ctx)
        await ctx.send(f"`{mychar.name} has joined the scene!`")

    @scene.command()
    async def leave(self, ctx):
        await ctx.message.delete()
        datab = database.DBManager
        try:  #if no character, stop
            mychar = await database.get_char_data(ctx.author.id)
        except:
            await ctx.send("Need a character to leave!")
            return        
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)}") as cursor:
                    async for row in cursor:
                        pass
        except:
            await ctx.send("No scene to leave!")
            return
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT actors FROM scene_{str(ctx.channel.id)}") as cursor:
                    results = await cursor.fetchall()
                    results.pop(0) # taking out the DM
                    found = False
                    for each in results:
                        if mychar.name == each[0]:
                            found = True
                    if found == False:
                        raise Exception(f"{mychar.name} isn't in this scene!")
        except Exception as e:
            await ctx.send(e)
            return
        async with aiosqlite.connect(scenedb) as db:
            await db.execute(f"DELETE FROM scene_{str(ctx.channel.id)} WHERE actors = \"{mychar.name}\"")
            await db.commit()
        await UpdatePin(ctx)
        await ctx.send(f"{mychar.name} has left the scene")
    
    @scene.command(invoke_without_command = True, aliases = ("n",))
    async def next(self, ctx):
        # marks your turn as taken on the 
        await ctx.message.delete()
        datab = database.DBManager
        try:  #if no character, stop
            mychar = await database.get_char_data(ctx.author.id)
        except:
            await ctx.send("Need a character to mark a turn!")
            return        
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)}") as cursor:
                    async for row in cursor:
                        pass
        except:
            await ctx.send("Can't mark a turn if there's no scene!")
            return
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT actors FROM scene_{str(ctx.channel.id)}") as cursor:
                    results = await cursor.fetchall()
                    results.pop(0) # taking out the DM
                    found = False
                    for each in results:
                        if mychar.name == each[0]:
                            found = True
                    if found == False:
                        raise Exception(f"{mychar.name} isn't in this scene!")
        except Exception as e:
            await ctx.send(e)
            return 
        try:
            async with aiosqlite.connect(scenedb) as db:
                await db.execute(f"UPDATE scene_{str(ctx.channel.id)} SET turn = 1 WHERE actors = \"{mychar.name}\";")
                await db.commit()
            await UpdatePin(ctx)
        except Exception as e:
            await ctx.send(e)
            
        
    @scene.command()
    async def addnpc(self, ctx, *, npc_name = "NPC"):
        await ctx.message.delete()
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)} WHERE id = 1") as cursor:
                    DMrow = await cursor.fetchone()
                if DMrow[1] != ctx.author.id:
                    raise 1
        except Exception as e:
            if e==1:
                await ctx.send(f"Hey hey Buddy, you're not the DM. That would be <@{int(DMrow[1])}> because they started the scene.")
                return
            else:
                await ctx.send("No scene to join!")
        async with aiosqlite.connect(scenedb) as db:
            await db.execute(f"INSERT INTO scene_{str(ctx.channel.id)} (userid, actors, turn, notes, pin_ID, chartype) VALUES (?, ?, ?, ?, ?, ?)", ("", npc_name, 0, "", "", "NPC"))
            await db.commit()
            await UpdatePin(ctx)
        await ctx.send(f"`{npc_name} has joined the scene!`")
        
        
    @scene.command()
    async def npcleave(self, ctx, *, npc_name):
        await ctx.message.delete()
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)} WHERE id = 1") as cursor:
                    DMrow = await cursor.fetchone()
                if str(DMrow[1]) != str(ctx.author.id):
                    await ctx.send(f"Hey hey Buddy, you're not the DM. That would be <@{int(DMrow[1])}> because they started the scene.")
                    return
        except Exception as e:
            await ctx.send(e)
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT actors FROM scene_{str(ctx.channel.id)}") as cursor:
                    actorlist = await cursor.fetchall()
            for each in actorlist:
                if re.search(npc_name, each[0], re.I) is not None:
                    my_npc = each[0]
        except Exception as e:
            await ctx.send("No NPC by that name in this scene! or "+str(e))
            return
        async with aiosqlite.connect(scenedb) as db:
            await db.execute(f"DELETE FROM scene_{str(ctx.channel.id)} WHERE actors = \"{my_npc}\"")
            await db.commit()
        await UpdatePin(ctx)
        await ctx.send(f"{npc_name} has left the scene")

    @scene.command()
    async def info(self, ctx):
        await UpdatePin(ctx)
        async with aiosqlite.connect(scenedb) as db:
            async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)} WHERE id = 1") as cursor:
                DMrow = await cursor.fetchone()
        message = await ctx.fetch_message(int(DMrow[5]))
        await ctx.send(message.content)

    @scene.command()
    async def help(self, ctx):
        await ctx.send("Use `!scene begin` to start a scene. End the scene with `!scene end`.\nYou can add your active character to the scene with `!scene join`. The DM can add NPCs to the scene with `!scene addnpc [name]`.")

    @scene.command()
    async def note(self, ctx, cmd, *notes):
        async with aiosqlite.connect(scenedb) as db:
            async with db.execute(f"SELECT notes FROM scene_{str(ctx.channel.id)} WHERE userid = ?", (ctx.author.id,)) as cursor:
                mynotes = await cursor.fetchone()
                if mynotes in [None, "None"]:
                    mynote = ""
                else:
                    mynote = str(mynotes[0])
        if cmd in ["+","add"]:
            for note in notes:
                if len(mynote)<1:
                    mynote = str(note)
                else:
                    mynote = mynote+"%%"+str(note)
                async with aiosqlite.connect(scenedb) as db:
                    await db.execute(f"UPDATE scene_{str(ctx.channel.id)} SET notes = \"{mynote}\" WHERE userid = {ctx.author.id};")
                    await db.commit()
                await UpdatePin(ctx)
                await ctx.send(f"Added the following note: {note}")
        elif cmd in ["-","remove"]:
            for note in notes:
                notearray = mynote.split("%%")
                removednote = ""
                i=0
                for each in notearray:
                    if re.search(note, each, re.I) is not None:
                        removednote = note
                        notearray.pop(i)
                    else:
                        i=i+1
                mynote = "%%".join(notearray)
                async with aiosqlite.connect(scenedb) as db:
                    await db.execute(f"UPDATE scene_{str(ctx.channel.id)} SET notes = \"{mynote}\" WHERE userid = {ctx.author.id};")
                    await db.commit()
                await UpdatePin(ctx)
                await ctx.send(f"Removed note: {removednote}")
        elif cmd == "edit":
            notearray = mynote.split("%%")
            i=0
            for each in notearray:
                if re.search(notes[0], each, re.I) is not None:
                    savei = i
                else:
                    i=i+1
            newnote = ""
            for each in notes[1:]:
                newnote = newnote+" "+each
            notearray[savei] = newnote
            mynote = "%%".join(notearray)
            async with aiosqlite.connect(scenedb) as db:
                await db.execute(f"UPDATE scene_{str(ctx.channel.id)} SET notes = \"{mynote}\" WHERE userid = {ctx.author.id};")
                await db.commit()
            await UpdatePin(ctx)
            await ctx.send("Edited note!")

    @scene.command()
    async def npcnote(self, ctx, npc, cmd, *notes):
        await ctx.message.delete()
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)} WHERE id = 1") as cursor:
                    DMrow = await cursor.fetchone()
                if str(DMrow[1]) != str(ctx.author.id):
                    await ctx.send(f"Hey hey Buddy, you're not the DM. That would be <@{int(DMrow[1])}> because they started the scene.")
                    return
        except Exception as e:
            await ctx.send(e)
        try:
            async with aiosqlite.connect(scenedb) as db:
                async with db.execute(f"SELECT actors FROM scene_{str(ctx.channel.id)}") as cursor:
                    actorlist = await cursor.fetchall()
            for each in actorlist:
                if re.search(npc, each[0], re.I) is not None:
                    my_npc = each[0]
        except Exception as e:
            await ctx.send("No NPC by that name in this scene! or "+str(e))
            return
        async with aiosqlite.connect(scenedb) as db:
            async with db.execute(f"SELECT notes FROM scene_{str(ctx.channel.id)} WHERE actors = ?", (my_npc,)) as cursor:
                mynotes = await cursor.fetchone()
                if mynotes in [None, "None"]:
                    mynote = ""
                else:
                    mynote = str(mynotes[0])
        if cmd in ["+","add"]:
            for note in notes:
                if len(mynote)<1:
                    mynote = str(note)
                else:
                    mynote = mynote+"%%"+str(note)
                async with aiosqlite.connect(scenedb) as db:
                    await db.execute(f"UPDATE scene_{str(ctx.channel.id)} SET notes = \"{mynote}\" WHERE actors = \"{my_npc}\";")
                    await db.commit()
                await UpdatePin(ctx)
                await ctx.send(f"Added the following note: {note}")
        elif cmd in ["-","remove"]:
            for note in notes:
                notearray = mynote.split("%%")
                removednote = ""
                i=0
                for each in notearray:
                    if re.search(note, each, re.I) is not None:
                        removednote = note
                        notearray.pop(i)
                    else:
                        i=i+1
                mynote = "%%".join(notearray)
                async with aiosqlite.connect(scenedb) as db:
                    await db.execute(f"UPDATE scene_{str(ctx.channel.id)} SET notes = \"{mynote}\" WHERE actors = \"{my_npc}\";")
                    await db.commit()
                await UpdatePin(ctx)
                await ctx.send(f"Removed note: {removednote}")
        elif cmd == "edit":
            notearray = mynote.split("%%")
            i=0
            for each in notearray:
                if re.search(notes[0], each, re.I) is not None:
                    savei = i
                else:
                    i=i+1
            newnote = ""
            for each in notes[1:]:
                newnote = newnote+" "+each
            notearray[savei] = newnote
            mynote = "%%".join(notearray)
            async with aiosqlite.connect(scenedb) as db:
                await db.execute(f"UPDATE scene_{str(ctx.channel.id)} SET notes = \"{mynote}\" WHERE actors = \"{my_npc}\";")
                await db.commit()
            await UpdatePin(ctx)
            await ctx.send("Edited note!")


async def UpdatePin(ctx):
    async with aiosqlite.connect(scenedb) as db:
        async with db.execute(f"SELECT * FROM scene_{str(ctx.channel.id)} WHERE id = 1") as cursor:
                DMrow = await cursor.fetchone()
        messageid = int(DMrow[5])
        async with db.execute(f"SELECT actors, turn, notes, chartype FROM scene_{str(ctx.channel.id)}") as cursor:
            results = await cursor.fetchall() #[(actors, turn, note, chartype), (actor, turn, note, chartype), ...]
    results = results[1:] #removing DM row
    newpin = ""
    PCturnreset = 0
    for each in results:
        turn = each[1]
        notes=each[2].split("%%")
        chartype = each[3]
        actorline = ""
        if turn == 1 and chartype == "PC":
            actorline = "(*) "
        elif turn == 0 and chartype == "PC":
            actorline = "( ) "
            PCturnreset = PCturnreset + 1
        else:
            pass
        actorline = actorline + each[0] + ": "
        for every in notes:
            if every == notes[0]:
                actorline = actorline+every
            else:
                actorline = actorline+", "+every
        actorline = actorline + "\n"
        newpin = newpin + actorline
    if PCturnreset == 0:
        for each in results:
            if each[3] == "PC":
                async with aiosqlite.connect(scenedb) as db:
                    await db.execute(f"UPDATE scene_{str(ctx.channel.id)} SET turn = 0 WHERE actors = \"{each[0]}\";")
                    await db.commit()
        await UpdatePin(ctx)
        await ctx.send("All players have taken a turn. Love you guys 😁")
        return
    message = await ctx.fetch_message(messageid)
    await message.edit(content="```\n"+newpin+"\n```")


async def setup(bot):
    await bot.add_cog(Scene(bot))
