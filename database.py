import asyncio
import aiosqlite
import school
import tomes

# https://github.com/omnilib/aiosqlite

#character_registry = [] # initialize character registry, an array of (ident, userid, char_name) **Who owns what character**
#user_registry = {} # a user registry with the active character for each user **Each User's Active Character**
#character_pile = [] # dictionary of idents and character objects (not here, can't store objects in sql) **Character data**

mydb = "my_database.db" # put the filename in one place

class DBManager:
    
    async def newchar(user_id, charname):
        async with aiosqlite.connect(mydb) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS character_registry (id INTEGER PRIMARY KEY, userid TEXT, charname TEXT)")
            await db.execute("INSERT INTO character_registry (userid, charname) VALUES (?, ?)", (user_id,charname))
            await db.commit()
            cursor = await db.execute("SELECT id FROM character_registry WHERE userid = ? and charname = ?", (user_id,charname))
            char_ident = cursor.fetchone()
            # get id => this is the ident
            # update user registery
            await db.execute("CREATE TABLE IF NOT EXISTS user_registry (id INTEGER PRIMARY KEY, userid TEXT, charid INTEGER)")
            #if new user, add user
            async with db.execute("SELECT charname FROM user_registry WHERE userid = ?", (user_id,)) as cursor:
                try:
                    for row in cursor:
                        print(row)
                    newuser = False
                except:
                    newuser = True
            if newuser == True:
                await db.execute("INSERT INTO user_registry (userid, charid) VALUES (?, ?)", (user_id,charname))
            else:
                await db.execute(f"UPDATE user_registry SET charid = {char_ident} WHERE userid = {user_id};")
            #update char pile
            await db.execute("CREATE TABLE IF NOT EXISTS char_data (id INTEGER PRIMARY KEY, playbook TEXT, name TEXT, str INTEGER, dex INTEGER, con INTEGER, int INTEGER, wis INTEGER, cha INTEGER, hp INTEGER, load INTEGER, dmgdie TEXT, gear TEXT, notes TEXT, moves TEXT, xp INTEGER)")
            # put in a blank character
            await db.execute("INSERT INTO char_data (playbook, name, str, dex, con, int, wis, cha, hp, load, dmgdie, gear, notes, moves, xp) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ("playbook-blank", charname, 10, 10, 10, 10, 10, 10, 0, 0, "d1", "None", "None", "None", 0))
            await db.commit()

                
    async def XP_view(user_id):
        char_id = await active_char(user_id)
        async with db.execute("SELECT xp FROM char_data WHERE name = ?", (char_id,)) as cursor:
                return cursor
        
    async def XP_update(ctx):
        pass
        
    #function that returns all characters belonging to a user
    async def charlist(user_id):
        async with aiosqlite.connect(mydb) as db:
            async with db.execute("SELECT id, charname FROM character_registry WHERE userid = ?", (user_id,)) as cursor:
                results = []
                async for row in cursor:
                    results.append(row)
            return results
    
    #function to update user registry (change character)

    async def add_monster(mclass):
        #a check to make sure there's a database to pull from
        async with aiosqlite.connect(mydb) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS monsters (id INTEGER PRIMARY KEY, name TEXT, desc TEXT, instinct TEXT, armor INTEGER, hp INTEGER, attacks TEXT, tags TEXT, moves TEXT, key TEXT)")
            #unpack into variables
            await db.execute("INSERT INTO monsters (name, desc, instinct, armor, hp, attacks, tags, moves, key) VALUES (?,?,?,?,?,?,?,?,?)", (mclass.name, mclass.description, mclass.instinct, mclass.armor, mclass.hp, str(mclass.attacks), str(mclass.tags), str(mclass.moves), mclass.key))
            await db.commit()
    
    async def remove_monster():
        async with aiosqlite.connect(mydb) as db:
            #remove from database
            pass    

    async def add_playbook(playbookclass):
        #a check to make sure there's a database to pull from
        async with aiosqlite.connect(mydb) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS playbooks(id INTEGER PRIMARY KEY, name TEXT,description TEXT,load INTEGER,base_hp TEXT,damage TEXT,names TEXT,bonds TEXT,looks TEXT,alignments TEXT,alignments_list TEXT,race_moves TEXT,starting_moves TEXT,advanced_moves TEXT,gear_choices TEXT,key TEXT)")
            #unpack into variables
            await db.execute("INSERT INTO playbooks (name,description,load,base_hp,damage,names,bonds,looks,alignments,alignments_list,race_moves,starting_moves,advanced_moves,gear_choices,key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (playbookclass.name,playbookclass.description,playbookclass.load,playbookclass.base_hp,playbookclass.damage,str(playbookclass.names),str(playbookclass.bonds),str(playbookclass.looks),str(playbookclass.alignments),str(playbookclass.alignments_list),str(playbookclass.race_moves),str(playbookclass.starting_moves),str(playbookclass.advanced_moves),str(playbookclass.gear_choices),playbookclass.key))
            await db.commit()
    
    async def add_move(moveclass):
        async with aiosqlite.connect(mydb) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS moves(id INTEGER PRIMARY KEY, name TEXT, description TEXT, key TEXT)")
            #unpack into variables
            await db.execute("INSERT INTO moves (name,description,key) VALUES (?,?,?)", (moveclass.name, moveclass.description, moveclass.key))
            await db.commit()

    async def add_eqmt(eqmtclass):
        async with aiosqlite.connect(mydb) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS eqmt(id INTEGER PRIMARY KEY, name TEXT, tags TEXT)")
            #unpack into variables
            await db.execute("INSERT INTO eqmt (name,tags) VALUES (?,?)", (eqmtclass.name, str(eqmtclass.tags)))
            await db.commit()
    
    async def move_lookup(search):
        async with aiosqlite.connect(mydb) as db:
            async with db.execute("SELECT name, description FROM moves WHERE name = ?", (search,)) as cursor:
                results = []
                async for row in cursor:
                    results.append(row)
        return results

    async def playbook_lookup(search):
        async with aiosqlite.connect(mydb) as db:
            async with db.execute("SELECT name, description FROM playbook WHERE name = ?", (search,)) as cursor:
                results = []
                async for row in cursor:
                    results.append(row)
        return results

    async def monster_lookup(search):
        async with aiosqlite.connect(mydb) as db:
            async with db.execute("SELECT * FROM monsters WHERE name = ?", (search,)) as cursor:
                results = []
                async for row in cursor:
                    results.append(row)
                print(results)
        return results

    async def eqmt_lookup(search):
        async with aiosqlite.connect(mydb) as db:
            async with db.execute("SELECT * FROM eqmt WHERE name = ?", (search,)) as cursor:
                results = []
                async for row in cursor:
                    results.append(row)
        return results

async def active_char_id(user_id):
    db = await aiosqlite.connect(mydb)
    cursor = await db.execute("SELECT id FROM user_registry WHERE userid = ?", (user_id,))
    char_id = await cursor.fetchone() #comes out as a tuple for some reason
    await cursor.close()
    await db.close()
    return char_id[0]

async def get_char_data(user_id):
    char_id = await active_char_id(user_id)
    async with aiosqlite.connect(mydb) as db:
        async with db.execute("SELECT * FROM char_data WHERE id = ?", (char_id,)) as cursor:
            char_data = await cursor.fetchone()
    return school.Character(char_data[1], char_data[2], char_data[3], char_data[4], char_data[5], char_data[6], char_data[7], char_data[8], char_data[9], char_data[10], char_data[11], char_data[12], char_data[13], char_data[14], char_data[15])
        
async def reset(): #Only use if the database file is deleted to build ot back from the raw json file
    datab = DBManager
    x = await tomes.main()
    mon = x[0]
    cls = x[1]
    eqmt = x[2]
    mvs = x[3]
    for each in cls:
        await datab.add_playbook(each)
    for each in mon:
        await datab.add_monster(each)
    for each in mvs:
        await datab.add_move(each)
    for each in eqmt:
        await datab.add_eqmt(each)


