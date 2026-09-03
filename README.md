# Discord-Realities

A discord bot that can be used to play Dungeon World. Includes a character builder, a character manager, and all the reference material. Huge shoutout to https://www.npmjs.com/package/dungeonworld-data for doing all the data entry for me.

### Documentation (kinda)

Anything in \[brackets] are required, and anything in (parenthesis) are optional

## General Commands

### !roll (modifiers)

common usage: !roll (mod)
Can also do:
!roll damage
!roll (3d8 or another string)
!roll ouch 1d8 (armor)

#### !camp

This command will level you up if you have the XP and will heal you up to half your max HP.



### !xp (value)

!xp will show how much xp you have.
!xp (n) will set your xp to that number
!xp (+n) will add that much xp, works with -n too



### !coin (value)

!coin will show how much coin you have.
!coin (n) will set your coin to that number
!coin (+n) will add that much coin, works with -n too



### !movelist

shows a list of all the basic/special moves and your active character's moves

### !update \[component] (command) \[value] or !up \[component] (command) \[value]

* Can be used to update anything on your character sheet. This command has a lot going on. To use this function, you need to have made a character first. Format should look like:
* !update playbook Paladin
* !update name John Smith
* !update stats 12 10 14 16 13 8
* !update hp +3 or !update hp 12
* !update load +1 or !update load 8
* !update dmgdie "1d8+1d4"
* !update gear add "stuff"
* !update notes add "notes" "other notes"
* !update move add "Arcane Art"
* !update xp +1 or !char update xp 7
* !update picture www.pictureurl.com

## Character Commands

### !char

Shows your active character

### !char new \[Name]

Makes a new empty sheet.
Format is: !char new Character Name
Note that Character Name has no quotes, so don't add them unless you want quotes in your name.

### !char make \[playbook]

Playbook is case sensitive (currently). Will pre-fill out a bunch of the character sheet stuff. Reccomended to at least do "!update stats x x x x x x" first.

### !char delete

Exactly what it looks like.

### !char levelup

Cashes in XP for a levelup.

### !char set \[name]

changes your active character

### !char list

Shows your active character

### !char view (args)

Shows your character sheet. Leave args blank to see the whole thing, or write only the args you want to see.

Args are: basic, stats, hp, gear, moves, notes

!char view basic hp moves

## Scene Commands

### !scene

Starts a Scene by invoking the new command below. The person who starts the scene is considered the DM, and is the only person who can do anything with NPCs in the scene.

### !scene begin

Starts a scene. Makes a pinned post that tracks characters in the scene and notes. Only one per channel. The person who starts the scene is considered to be the DM. Only a DM can do anything with NPCs.

### !scene end

Ends the scene and unpins the post.

### !scene join

Makes your active character join the scene.

### !scene leave

Makes your active character leave the scene.

### !scene addnpc (NPC name)

If the name is blank it'll add "NPC"

### !scene npcleave \[npc name]

Causes NPCs to leave the scene

### !scene info

Prints the pinned post in case you want to see what's on there.

### !scene help

Shows a help message.

### !scene note \[add/remove/+/-/edit] \[note] (edited note)

Adds a note about your character to the pinned post

### !scene npcnote \[npc name] \[add/remove/+/-/edit] \[note] (edited note)

Adds a note about an NPC to the pinned post. (DM only!)

## Utils

### !lookup \[monster/item/playbook/move] (search)

If there's no search item it'll make a list of all available.

### !monster (search) or !mon (search)

DMs you the monster OR returns a list of things you might have meant. Run in a DM with the bot to be safe.

### !item (search) or !gear (search)

Returns the tags for items or a list of things you might have meant.

### !playbook (search)

Returns the an embed about a certain playbook or a list of things you might have meant.

### !move (search)

Returns a move or a list of things you might have meant.

### !m

This will send you all of your active character's moves written out in DMs. For this to work, the move must be on your sheet exactly as it's shown in the lookup.

## !homebrew (!hb)

This is complicated but you can import monster/item/playbook/move with this command. All homebrew items will only work on the discord server they are imported on. There are a bunch of issues still with monster and playbook imports due to JSON import issues.

### !hb view (playbooks/moves/eqmt/monsters) (another...)

Shows all homebrew that's been added to the server.

example: !hb view moves eqmt

### !hp create

Adds things to the game database.

!hb create move \[Move Name] \[description]

!hb create item \[name] \[tag1] (tag2) (tag3)...

### !hb delete \[table] \[name]

Tables are playbooks/moves/eqmt/monsters. Name has to be Exact.

!hb delete moves "Black Magic"

