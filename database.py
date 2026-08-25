import asyncio
import aiosqlite
import school
import tomes
import re
import json


# https://github.com/omnilib/aiosqlite

#character_registry = [] # initialize character registry, an array of (ident, userid, char_name) **Who owns what character**
#user_registry = {} # a user registry with the active character for each user **Each User's Active Character**
#character_pile = [] # dictionary of idents and character objects (not here, can't store objects in sql) **Character data**

maindb = "my_database.db" # put the filename in one place

class DBManager:   
    
    async def newchar(user_id, charname):
        async with aiosqlite.connect(maindb) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS character_registry (id INTEGER PRIMARY KEY, userid TEXT, charname TEXT)")
            await db.execute("INSERT INTO character_registry (userid, charname) VALUES (?, ?)", (user_id,charname))
            await db.commit()
            cursor = await db.execute("SELECT id FROM character_registry WHERE userid = ? and charname = ?", (user_id,charname))
            char_ident = await cursor.fetchone()
            char_ident = char_ident[0]
            # get id => this is the ident
            # update user registery
            await db.execute("CREATE TABLE IF NOT EXISTS user_registry (id INTEGER PRIMARY KEY, userid TEXT, charid INTEGER)")
            await db.commit()
            #if new user, add user
            async with db.execute("SELECT charid FROM user_registry WHERE userid = ?", (user_id,)) as cursor:
                oldcharid = await cursor.fetchone()
            if oldcharid == None:
                newuser = True
            else:
                newuser = False
            if newuser == True:
                await db.execute("INSERT INTO user_registry (userid, charid) VALUES (?, ?)", (user_id,char_ident))
            else:
                print("old id: "+str(oldcharid)+", new id: "+str(char_ident))
                await db.execute(f"UPDATE user_registry SET charid = {char_ident} WHERE userid = {user_id};")
            await db.commit()
            #update char pile
            await db.execute("CREATE TABLE IF NOT EXISTS char_data (id INTEGER PRIMARY KEY, playbook TEXT, name TEXT, level INTEGER, str INTEGER, dex INTEGER, con INTEGER, int INTEGER, wis INTEGER, cha INTEGER, hp INTEGER, hpmod INTEGER, load INTEGER, dmgdie TEXT, gear TEXT, notes TEXT, moves TEXT, xp INTEGER, picture TEXT, coin INTEGER, counters TEXT)")
            await db.commit()
            # put in a blank character
            await db.execute("INSERT INTO char_data (playbook, name, level, str, dex, con, int, wis, cha, hp, hpmod, load, dmgdie, gear, notes, moves, xp, picture, coin, counters) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ("playbook-blank", charname, 1, 10, 10, 10, 10, 10, 10, 0, 0, 0, "d1", "None", "None", "None", 0, "https://upload.wikimedia.org/wikipedia/commons/7/79/The_Knight%2C_from_The_Dance_of_Death_MET_DP-23045-001.jpg", 0, "{}"))
            await db.commit()

    async def XP_view(user_id):
        async with aiosqlite.connect(maindb) as db:
            char_id = await active_char_id(user_id)
            async with db.execute("SELECT xp FROM char_data WHERE name = ?", (char_id,)) as cursor:
                return cursor
    
    async def del_char(user_id):
        async with aiosqlite.connect(maindb) as db:
            char_id = await active_char_id(user_id)
            await db.execute(f"DELETE FROM character_registry WHERE id = {char_id}")
            await db.execute(f"DELETE FROM char_data WHERE id = {char_id}")
            await db.commit()
            return "The deed is done"
    
        
    #function that returns all characters belonging to a user
    async def charlist(user_id):
        async with aiosqlite.connect(maindb) as db:
            async with db.execute("SELECT id, charname FROM character_registry WHERE userid = ?", (user_id,)) as cursor:
                results = []
                async for row in cursor:
                    results.append(row)
            await db.commit()
            return results
    
    async def set(user_id, char_ident):
        async with aiosqlite.connect(maindb) as db:
            await db.execute(f"UPDATE user_registry SET charid = {char_ident} WHERE userid = {user_id};")
            await db.commit()
        
    async def add_monster(mclass, database_name):
        #a check to make sure there's a database to pull from
        async with aiosqlite.connect(database_name) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS monsters (id INTEGER PRIMARY KEY, name TEXT, desc TEXT, instinct TEXT, armor INTEGER, hp INTEGER, attacks TEXT, tags TEXT, moves TEXT, key TEXT)")
            #unpack into variables
            await db.execute("INSERT INTO monsters (name, desc, instinct, armor, hp, attacks, tags, moves, key) VALUES (?,?,?,?,?,?,?,?,?)", (mclass.name, mclass.description, mclass.instinct, mclass.armor, mclass.hp, str(mclass.attacks), str(mclass.tags), str(mclass.moves), mclass.key))
            await db.commit()
    
    async def remove_monster():
        async with aiosqlite.connect(maindb) as db:
            #remove from database
            pass    

    async def add_playbook(playbookclass, database_name):
        #a check to make sure there's a database to pull from
        async with aiosqlite.connect(database_name) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS playbooks(id INTEGER PRIMARY KEY, name TEXT,description TEXT,load INTEGER,base_hp TEXT,damage TEXT,names TEXT,bonds TEXT,looks TEXT,alignments TEXT,alignments_list TEXT,race_moves TEXT,starting_moves TEXT,advanced_moves TEXT,gear_choices TEXT,key TEXT)")
            #unpack into variables
            await db.execute("INSERT INTO playbooks (name,description,load,base_hp,damage,names,bonds,looks,alignments,alignments_list,race_moves,starting_moves,advanced_moves,gear_choices,key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (playbookclass.name,playbookclass.description,playbookclass.load,playbookclass.base_hp,playbookclass.damage,str(playbookclass.names),str(playbookclass.bonds),str(playbookclass.looks),str(playbookclass.alignments),str(playbookclass.alignments_list),str(playbookclass.race_moves),str(playbookclass.starting_moves),str(playbookclass.advanced_moves),str(playbookclass.gear_choices),playbookclass.key))
            await db.commit()
    
    async def pull_names(ctx, table):
        if table not in ["playbooks", "moves", "eqmt", "monsters"]:
            return ["You're asking for a table that doesn't exist"]
        results = []
        try:
            hbdb = str(ctx.guild.id)+".db"
        except:
            pass
        async with aiosqlite.connect(maindb) as db:
            async with db.execute(f"SELECT name FROM {table}") as cursor:
                async for row in cursor:
                    results.append(row)
        try:
            async with aiosqlite.connect(hbdb) as db:
                async with db.execute(f"SELECT name FROM {table}") as cursor:
                    async for row in cursor:
                        results.append(row)
        except:
            pass
        return results
    
    async def hbview(ctx):
        try:
            hbdb = str(ctx.guild.id)+".db"
        except:
            return "Only works on servers."
        results = []
        for each in ["playbooks", "moves", "eqmt", "monsters"]:
            tableresults = []
            tableresults.append(each)
            try:
                async with aiosqlite.connect(hbdb) as db:
                    async with db.execute(f"SELECT name FROM {each}") as cursor:
                        async for row in cursor:
                            tableresults.append(row[0])
            except:
                pass
            results.append("\n".join(tableresults))
        return results
    
    async def hbdelete(ctx, table, name):
        try:
            hbdb = str(ctx.guild.id)+".db"
        except:
            return "Only works on servers."
        async with aiosqlite.connect(hbdb) as db:
            await db.execute(f"DELETE FROM {table} WHERE name = {name}")
            await db.commit()
            return f"Deleted {name} from {table}"
            
    
    async def add_move(moveclass, database_name):
        async with aiosqlite.connect(database_name) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS moves(id INTEGER PRIMARY KEY, name TEXT, description TEXT, key TEXT)")
            #unpack into variables
            await db.execute("INSERT INTO moves (name,description,key) VALUES (?,?,?)", (moveclass.name, moveclass.description, moveclass.key))
            await db.commit()
    
    async def add_eqmt(eqmtclass, database_name):
        async with aiosqlite.connect(database_name) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS eqmt(id INTEGER PRIMARY KEY, name TEXT, tags TEXT)")
            #unpack into variables
            await db.execute("INSERT INTO eqmt (name,tags) VALUES (?,?)", (eqmtclass.name, str(eqmtclass.tags)))
            await db.commit()
    
    async def move_lookup(ctx, search):
        try:
            hbdb = str(ctx.guild.id)+".db"
        except:
            await ctx.send("FYI Homebrew is locked to a server.")
        movnames = []
        movlist = []
        async with aiosqlite.connect(maindb) as db:
            async with db.execute("SELECT name FROM moves") as cursor:
                async for row in cursor:
                    movnames.append(row)
        try:
            async with aiosqlite.connect(hbdb) as db:
                async with db.execute("SELECT name FROM moves") as cursor:
                    async for row in cursor:
                        movnames.append(row)
        except:
            pass
        exactmatch = False
        for each in movnames:
            if search.lower() == each[0].lower():
                exactmatch = True
                movlist = [each[0]]
            elif re.search(search, each[0], re.I) is not None:
                if exactmatch == False:
                    movlist.append(each[0])
        if len(movlist) == 1:
            try:
                async with aiosqlite.connect(maindb) as db:
                    async with db.execute("SELECT * FROM moves WHERE name = ?", (movlist[0],)) as cursor:
                        results = await cursor.fetchall()
            except: 
                pass
            try:
                async with aiosqlite.connect(hbdb) as db:
                    async with db.execute("SELECT * FROM moves WHERE name = ?", (movlist[0],)) as cursor:
                        hbresults = await cursor.fetchall()
                        if hbresults[0] != None:
                            results = hbresults
            except: 
                pass
        elif len(movlist) >1:
            results = "# Multiple Matches\n"
            for each in movlist:
                results = results + "* "+str(each) + "\n"
        else:
            results = "No Moves found =("
        return results

    async def playbook_lookup(ctx, search):
        try:
            hbdb = str(ctx.guild.id)+".db"
        except:
            await ctx.send("FYI Homebrew is locked to a server.")
        playnames = []
        playlist = []
        async with aiosqlite.connect(maindb) as db:
            async with db.execute("SELECT name FROM playbooks") as cursor:
                async for row in cursor:
                    playnames.append(row)
        try:
            async with aiosqlite.connect(hbdb) as db:
                async with db.execute("SELECT name FROM playbooks") as cursor:
                    async for row in cursor:
                        playnames.append(row)
        except:
            pass
        exactmatch = False
        for each in playnames:
            if search.lower() == each[0].lower():
                exactmatch = True
                playlist = [each[0]]
            elif re.search(search, each[0], re.I) is not None:
                if exactmatch == False:
                    playlist.append(each[0])
        if len(playlist) == 1:
            try:
                async with aiosqlite.connect(maindb) as db:
                    async with db.execute("SELECT * FROM playbooks WHERE name = ?", (playlist[0],)) as cursor:
                        results = await cursor.fetchall()
            except: 
                pass
            try:
                async with aiosqlite.connect(hbdb) as db:
                    async with db.execute("SELECT * FROM playbooks WHERE name = ?", (playlist[0],)) as cursor:
                        hbresults = await cursor.fetchall()
                        if hbresults[0] != None:
                            results = hbresults
            except: 
                pass
        elif len(playlist) >1:
            results = "# Multiple Matches\n"
            for each in playlist:
                results = results + "* "+str(each) + "\n"
        else:
            results = "No Playbooks found =("
        return results

    async def monster_lookup(ctx, search):
        try:
            hbdb = str(ctx.guild.id)+".db"
        except:
            await ctx.send("FYI Homebrew is locked to a server.")
        monnames = []
        monlist = []
        async with aiosqlite.connect(maindb) as db:
            async with db.execute("SELECT name FROM monsters") as cursor:
                async for row in cursor:
                    monnames.append(row)
        try:
            async with aiosqlite.connect(hbdb) as db:
                async with db.execute("SELECT name FROM monsters") as cursor:
                    async for row in cursor:
                        monnames.append(row)
        except:
            pass
        exactmatch = False
        for each in monnames:
            if search.lower() == each[0].lower():
                exactmatch = True
                monlist = [each[0]]
            elif re.search(search, each[0], re.I) is not None:
                if exactmatch == False:
                    monlist.append(each[0])
        if len(monlist) == 1:
            try:
                async with aiosqlite.connect(maindb) as db:
                    async with db.execute("SELECT * FROM monsters WHERE name = ?", (monlist[0],)) as cursor:
                        results = await cursor.fetchall()
            except: 
                pass
            try:
                async with aiosqlite.connect(hbdb) as db:
                    async with db.execute("SELECT * FROM monsters WHERE name = ?", (monlist[0],)) as cursor:
                        hbresults = await cursor.fetchall()
                        if hbresults[0] != None:
                            results = hbresults
            except: 
                pass
        elif len(monlist) >1:
            results = "# Multiple Matches\n"
            for each in monlist:
                results = results + "* "+str(each) + "\n"
        else:
            results = "No Monsters found =("
        return results

    async def eqmt_lookup(ctx, search):
        try:
            hbdb = str(ctx.guild.id)+".db"
        except:
            await ctx.send("FYI Homebrew is locked to a server.")
        itemnames = []
        itemlist = []
        async with aiosqlite.connect(maindb) as db:
            async with db.execute("SELECT name FROM eqmt") as cursor:
                async for row in cursor:
                    itemnames.append(row)
        try:
            async with aiosqlite.connect(hbdb) as db:
                async with db.execute("SELECT name FROM eqmt") as cursor:
                    async for row in cursor:
                        itemnames.append(row)
        except:
            pass
        exactmatch = False
        for each in itemnames:
            if search.lower() == each[0].lower():
                exactmatch = True
                itemlist = [each[0]]
            elif re.search(search, each[0], re.I) is not None:
                if exactmatch == False:
                    itemlist.append(each[0])
        if len(itemlist) == 1:
            try:
                async with aiosqlite.connect(maindb) as db:
                    async with db.execute("SELECT * FROM eqmt WHERE name = ?", (itemlist[0],)) as cursor:
                        results = await cursor.fetchall()
            except: 
                pass
            try:
                async with aiosqlite.connect(hbdb) as db:
                    async with db.execute("SELECT * FROM eqmt WHERE name = ?", (itemlist[0],)) as cursor:
                        hbresults = await cursor.fetchall()
                        if hbresults[0] != None:
                            results = hbresults
            except: 
                pass
        elif len(itemlist) >1:
            results = "# Multiple Matches\n"
            for each in itemlist:
                results = results + "* "+str(each) + "\n"
        else:
            results = "No Items found =("
        return results
    
    async def updatechar(user_id, args):
        mycharid = await active_char_id(user_id)
        if str(args) == "help":
            return "To use this function, you need to have made a character first. Format should look like:`!update playbook Paladin` \n `!update name John Smith` \n `!update stats 12 10 14 16 13 8` \n `!update hp +3` or `!update hp 12` \n `!update load +1` or `!update load 8` \n `!update dmgdie \"1d8+1d4\"` \n `!update gear add \"stuff\"` \n `!update notes add \"notes\"` \n `!update move \"I don't know how to implement this\"` \n `!update xp +1` or `!char update xp 7` \n `!update picture www.pictureurl.com`"
        myargs = str(args[0])
        args = args[1:]
        async with aiosqlite.connect(maindb) as db:
            if myargs == "playbook": #text
                args = str(args)
                await db.execute(f"UPDATE char_data SET playbook = \"{args}\" WHERE id = {mycharid};")
                await db.commit()
                return f"Playbook is now {args}"
            if myargs == "name": #TEXT
                newname = ""
                for each in args:
                    newname=newname+str(each)+" "
                newname = str(newname[:len(newname)-1])
                await db.execute(f"UPDATE char_data SET name = \"{newname}\" WHERE id = {mycharid};")
                await db.commit()
                return f"Name is now {newname}"
            if myargs == "level":
                await db.execute(f"UPDATE char_data SET level = {args[0]} WHERE id = {mycharid};")
                await db.commit()
            if myargs == "stats": #assumes 6 numbers will be coming next
                if len(args) < 6:
                    return
                else:
                    statargs = args[:6]
                    await db.execute(f"UPDATE char_data SET str = \"{statargs[0]}\" WHERE id = {mycharid};")
                    await db.execute(f"UPDATE char_data SET dex = \"{statargs[1]}\" WHERE id = {mycharid};")
                    await db.execute(f"UPDATE char_data SET con = \"{statargs[2]}\" WHERE id = {mycharid};")
                    await db.execute(f"UPDATE char_data SET wis = \"{statargs[3]}\" WHERE id = {mycharid};")
                    await db.execute(f"UPDATE char_data SET int = \"{statargs[4]}\" WHERE id = {mycharid};")
                    await db.execute(f"UPDATE char_data SET cha = \"{statargs[5]}\" WHERE id = {mycharid};")
                    await db.commit()
                return f"stats are now Strength: {statargs[0]}, Dexterity: {statargs[1]}, Constitution: {statargs[2]}, Intelligence: {statargs[3]}, Wisdom: {statargs[4]}, Charisma: {statargs[5]}"
            if myargs == "hp": #INTEGER
                async with db.execute("SELECT hp FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    myhp = await cursor.fetchone()
                    myhp = int(myhp[0])
                try:
                    if args[0][0] == '+':
                        newamt = int(args[0][1:])
                        myhp = myhp + newamt
                    elif args[0][0] == '-':
                        newamt = int(args[0][1:])
                        myhp = myhp - newamt
                    else:
                        myhp = int(args[0])
                except:
                    print("not sure what you're trying to increase your hp by...?")
                await db.execute(f"UPDATE char_data SET hp = {myhp} WHERE id = {mycharid};")
                await db.commit()
                return f"HP is now {myhp}"
            if myargs == "hpmod": #INTEGER - ONLY FROM PLAYBOOK
                async with db.execute("SELECT hpmod FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    myhpmod = await cursor.fetchone()
                    myhpmod = int(myhpmod[0])
                try:
                    if args[0][0] == '+':
                        newamt = int(args[0][1:])
                        myhpmod = myhpmod + newamt
                    elif args[0][0] == '-':
                        newamt = int(args[0][1:])
                        myhpmod = myhpmod - newamt
                    else:
                        myhpmod = int(args[0])
                except:
                    print("not sure what you're trying to increase your hpmod by...?")
                await db.execute(f"UPDATE char_data SET hpmod = {myhpmod} WHERE id = {mycharid};")
                await db.commit()
                return f"HPmod is now {myhpmod}"
            if myargs == "load": #INTEGER
                async with db.execute("SELECT load FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    myload = await cursor.fetchone()
                    myload = int(myload[0])
                try:
                    if args[0][0] == "+" or args[0][0] == "-":
                         myload = myload + int(args[0])
                    else:
                        myload = args[0]
                except:
                    return "Something went wrong with updating Load"
                await db.execute(f"UPDATE char_data SET load = {myload} WHERE id = {mycharid};")
                await db.commit()
                return f"load is now {myload}"
            if myargs == "dmgdie": #TEXT
                await db.execute(f"UPDATE char_data SET dmgdie = \"{args[0]}\" WHERE id = {mycharid};")
                await db.commit()
                return f"Damage Die is now: {args[0]}"
            if myargs == "gear": #TEXT
                async with db.execute("SELECT gear FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    mygear = await cursor.fetchone()
                await db.commit()
                mygear = str(mygear[0])
                if mygear == "None":
                    mygear = ""
                if args[0] == "+" or args[0] == "add":
                    for each in args[1:]:
                        if len(mygear)<1:
                            mygear = str(each)
                        else:
                            mygear = mygear+"%%"+str(each)
                    await db.execute(f"UPDATE char_data SET gear = \"{mygear}\" WHERE id = {mycharid};")
                    await db.commit()
                    return f"Added the following gear: {args[1:]}"
                elif args[0] == "-" or args[0] == "remove":
                    geararray = mygear.split("%%")
                    i = 0
                    removedgear = ""
                    for each in args[1:]:
                        for gear in geararray:
                            if re.search(each, gear, re.I) is not None:
                                removedgear = removedgear + "%%" + gear
                                geararray.pop(i)
                    i=i+1
                    mygear = ",".join(geararray)
                    await db.execute(f"UPDATE char_data SET gear = \"{mygear}\" WHERE id = {mycharid};")
                    await db.commit()
                    return f"Removed gear: {removedgear}"
            if myargs == "note" or myargs == "notes": #TEXT
                async with db.execute("SELECT notes FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    mynotes = await cursor.fetchone()
                await db.commit()
                mynote = str(mynotes[0])
                if mynote == "None":
                    mynote = ""
                if args[0] == "+" or args[0] == "add":
                    for each in args[1:]:
                        if len(mynote)<1:
                            mynote = str(each)
                        else:
                            mynote = mynote+"%%"+str(each)
                    await db.execute(f"UPDATE char_data SET notes = \"{mynote}\" WHERE id = {mycharid};")
                    await db.commit()
                    return f"Added the following note: {args[1:]}"
                elif args[0] == "-" or args[0] == "remove":
                    notearray = mynote.split("%%")
                    i = 0
                    removednote = ""
                    for each in args[1:]:
                        for note in notearray:
                            if re.search(each, note, re.I) is not None:
                                removednote = removednote + ", " + note
                                notearray.pop(i)
                    i=i+1
                    mynote = "%%".join(notearray)
                    await db.execute(f"UPDATE char_data SET note = \"{mynote}\" WHERE id = {mycharid};")
                    await db.commit()
                    return f"Removed note: {removednote}"
            if myargs == "moves" or myargs == "move": #TEXT
                async with db.execute("SELECT moves FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    mymoves = await cursor.fetchone()
                await db.commit()
                mymoves = mymoves[0]
                if mymoves == "None":
                    mymoves = ""
                if args[0] == "+" or args[0] == "add":
                    for each in args[1:]:
                        if len(mymoves)<1:
                            mymoves = str(each)
                        else:
                            mymoves = mymoves+"%%"+str(each)
                    await db.execute(f"UPDATE char_data SET moves = \"{mymoves}\" WHERE id = {mycharid};")
                    await db.commit()
                    return f"Added the following move: {args[1:]}"
                elif args[0] == "-" or args[0] == "remove":
                    movearray = mymoves.split("%%")
                    i = 0
                    removedmove = ""
                    for each in args[1:]:
                        for move in movearray:
                            if re.search(each, move, re.I) is not None:
                                removedmove = removedmove + ", " + move
                                movearray.pop(i)
                    i=i+1
                    mymove = "%%".join(movearray)
                

                await db.execute(f"UPDATE char_data SET moves = \"{mymove}\" WHERE id = {mycharid};")
                await db.commit()
                return f"Removed note: {removedmove}"

            if myargs == "xp": #INTEGER
                async with db.execute("SELECT xp FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    myxp = await cursor.fetchone() #returns a tuple with no second value...?
                    myxp = myxp[0]
                try:
                    if args[0][0] == '+':
                        newamt = int(args[0][1:])
                        myxp = myxp + newamt
                    elif args[0][0] == '-':
                        newamt = int(args[0][1:])
                        myxp = myxp - newamt
                    else:
                        myxp = int(args[0])
                except:
                    print("not sure what you're trying to increase your xp by...?")
                await db.execute(f"UPDATE char_data SET xp = {myxp} WHERE id = {mycharid};")
                await db.commit()
                return myxp
            if myargs == "coin": #INTEGER
                async with db.execute("SELECT coin FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    mycoin = await cursor.fetchone() #returns a tuple with no second value...?
                    mycoin = mycoin[0]
                try:
                    if args[0][0] == '+':
                        newamt = int(args[0][1:])
                        mycoin = mycoin + newamt
                    elif args[0][0] == '-':
                        newamt = int(args[0][1:])
                        mycoin = mycoin - newamt
                    else:
                        mycoin = int(args[0])
                except:
                    print("not sure what you're trying to increase your coin by...?")
                await db.execute(f"UPDATE char_data SET coin = {mycoin} WHERE id = {mycharid};")
                await db.commit()
                return mycoin
            if myargs == "picture": #TEXT
                await db.execute(f"UPDATE char_data SET picture = \"{args[0]}\" WHERE id = {mycharid};")
                await db.commit()
                return f"Picture is now {args[0]}"
            if myargs == "counter": #TEXT
                async with db.execute("SELECT counters FROM char_data WHERE id = ?", (mycharid,)) as cursor:
                    ccstring = await cursor.fetchone()
                storedarray = json.loads(ccstring[0].replace("'", "\""))
                ccarray=[]
                if args[0] == "+" or args[0] == "add":
                    for each in storedarray:
                        eachcounter = {}
                        eachcounter["name"] = each["name"]
                        eachcounter["min"] = each["min"]
                        eachcounter["max"] = each["max"]
                        eachcounter["value"] = each["value"]
                        eachcounter["desc"] = each["desc"]
                        ccarray.append(eachcounter)
                    ccarray.append(args[1])
                    myccs = json.dumps(ccarray).replace("\"", "'")
                    await db.execute(f"UPDATE char_data SET counters = \"{myccs}\" WHERE id = {mycharid};")
                    await db.commit()
                    return f"Created Counter: {args[1]["name"]}"
                elif args[0] == "-" or args[0] == "remove":
                    i=0
                    found = False
                    for each in storedarray:
                        if re.search(each["name"], args[1], re.I) is not None and found == False:
                            found = True
                            i=i+1
                    try:
                        storedarray.pop(i)
                        myccs = json.dumps(storedarray).replace("\"", "'")
                        await db.execute(f"UPDATE char_data SET counters = \"{myccs}\" WHERE id = {mycharid};")
                        await db.commit()
                        return f"Deleted counter: {storedarray[i]["name"]}"
                    except:
                        return f"Couldn't find a counter by the name {args[1]}"
                elif args[0] == "push":
                    try:
                        myccs = json.dumps(args[1]).replace("\"", "'")
                        await db.execute(f"UPDATE char_data SET counters = \"{myccs}\" WHERE id = {mycharid};")
                        await db.commit()
                        return "Pushed"
                    except Exception as e:
                        print("Something happened: ", e)

async def active_char_id(user_id):
    db = await aiosqlite.connect(maindb)
    cursor = await db.execute("SELECT charid FROM user_registry WHERE userid = ?", (user_id,))
    char_id = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return char_id[0]

async def get_char_data(user_id):
    char_id = await active_char_id(user_id)
    async with aiosqlite.connect(maindb) as db:
        async with db.execute("SELECT * FROM char_data WHERE id = ?", (char_id,)) as cursor:
            char_data = await cursor.fetchone()
    return school.Character(char_data[1], char_data[2], char_data[3], char_data[4], char_data[5], char_data[6], char_data[7], char_data[8], char_data[9], char_data[10], char_data[11], char_data[12], char_data[13], char_data[14], char_data[15], char_data[16], char_data[17], char_data[18], char_data[19], char_data[20])
        
async def reset(): #Only use if the database file is deleted to build ot back from the raw json file
    datab = DBManager
    x = await tomes.main()
    mon = x[0]
    cls = x[1]
    eqmt = x[2]
    mvs = x[3]
    for each in cls:
        await datab.add_playbook(each, maindb)
    for each in mon:
        await datab.add_monster(each, maindb)
    for each in mvs:
        await datab.add_move(each, maindb)
    for each in eqmt:
        await datab.add_eqmt(each, maindb)

    
