# -*- coding: utf-8 -*-
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from discord.voice_client import VoiceClient
import _thread as thread
import random

import pyspeedtest
st = pyspeedtest.SpeedTest()
conCooldown = False
#from secrets import * #Token will be stored in here so I don't accidentally leak the admin token for my Discord again...

gate =  440205836208439348
casual = 473276007860797453

disabled_commands = []

cooldown = []
ignore_list = ["388022143931383818", "426489102838530050", "427869023552667649"]

Client = discord.Client()
bot_prefix = "//"
client = commands.Bot(command_prefix=bot_prefix)

def info(text): #Info Level Log Output
    print("[" +str(time.ctime()) +"] [INFO] " +text)

def warn(text): #Warn Level Log Output
    print("[" +str(time.ctime()) +"] [WARNING] " +text)

def error(text): #Error Level Log Output
    print("[" +str(time.ctime()) +"] [ERROR] " +text)

def debug(text): #Error Level Log Output
    print("[" +str(time.ctime()) +"] [DEBUG] " +text)  

#SQL
import sqlite3

def execute_query(table, query):
    conn = sqlite3.connect(table)
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    c.close()
    conn.close()

def db_query(table, query):
    conn = sqlite3.connect(table)
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    c.close()
    conn.close()
    return result

#Declarations & Assignments
invite_link = "https://discord.gg/bjyxUn6"

@client.event
async def on_ready():
    print("active")
    #await client.change_presence(status=discord.Status.invisible)

def insert_db_user(member):
    try:
        execute_query("varsity.db", "INSERT INTO Members (UserID) VALUES ('%s')" % (member.id))
    except:
        warn("User already exists in Database")
        try:
            info(member.name)
        except:
            pass
        
def set_coins(user, coins):
    user_id = user.id
    execute_query("varsity.db", "UPDATE Members SET Balance = %s WHERE UserID = %s" % (str(coins), str(user_id)))


def fetch_coins(user):
    user_id = user.id
    coins = db_query("varsity.db", "SELECT Balance FROM Members WHERE UserID = %s" % (str(user_id)))[0][0]
    return coins

def add_coins(user, amount):
    current_coins = fetch_coins(user)
    new_coins = int(current_coins) + int(amount)
    set_coins(user, new_coins)


def get_profile(userID):
    profile = db_query("varsity.db", "SELECT Balance, Rank, Tier, Staff, YouTuber, ValuedMember, Veteran FROM Members WHERE UserID = %s" % (userID))[0]
    return profile

def get_rank(user):
    rank = []
    if "Owner" in [role.name for role in user.roles]:
        rank.append("Owner")
        rank.append("https://cdn.discordapp.com/emojis/486269879327129601.png")
    elif "Admin" in [role.name for role in user.roles]:
        rank.append("Admin")
        rank.append("https://cdn.discordapp.com/emojis/486269879327129601.png")
    elif "Senior Moderator" in [role.name for role in user.roles]:
        rank.append("Senior Moderator")
        rank.append("https://cdn.discordapp.com/emojis/486269879327129601.png")
    elif "Moderator" in [role.name for role in user.roles]:
        rank.append("Moderator")
        rank.append("https://cdn.discordapp.com/emojis/486269879327129601.png")
    elif "Helper" in [role.name for role in user.roles]: #deprecated (this role is being removed soon)
        rank.append("Helper")
        rank.append("https://cdn.discordapp.com/emojis/486269879327129601.png")
    elif "Contributor" in [role.name for role in user.roles]:
        rank.append("Contributor")
        rank.append("https://cdn.discordapp.com/emojis/486265111795728384.png")
    elif "Artist" in [role.name for role in user.roles]:
        rank.append("Artist")
        rank.append("https://cdn.discordapp.com/emojis/486266771418906626.png")
    else:
        rank.append("Member")
        rank.append("https://cdn.discordapp.com/emojis/486269178047627266.png")

    return rank

async def error(reason, channel):
    em = discord.Embed(title="Error", description="An error occurred when attempting to perform that request.\nError: `%s`" % reason, colour=0xFF5555)
    msg = await channel.send(embed=em)
    await asyncio.sleep(15)
    await msg.delete()
        
        
        
        
    

@client.event
async def on_message(message):
    try:

        global conCooldown
        global disabled_commands

        args = message.content.split(" ")

        if args[0].lower() in disabled_commands:
            await error("[423] This command is currently disabled", message.channel)
            return False

        

        channel = message.channel
        settings = channel.overwrites
        

        
        

        if message.content.upper().startswith("!ADDROLE"):
            if message.author.id == "345514405775147023":
                if len(args) <= 2:
                    role = discord.utils.get(message.server.roles, name=args[1])
                    await client.add_roles(message.author, role)
                    await client.send_message(message.channel, "Success! Added **%s** to your permission groups!" % (args[1]))
                else:
                    role = discord.utils.get(message.server.roles, name=args[1])
                    user = discord.utils.get(message.server.members, mention=args[2])
                    await client.add_roles(user, role)
                    await client.send_message(message.channel, "Success! Added **%s** to **%s**'s permission groups!" % (args[1], user.name))
                    
                
        if message.channel.id == gate:
            await message.delete()        

        if message.content.upper() == "!ACCEPT":
            if message.channel.id == gate:
                await user_accept_rules(message.author)

        if message.content.upper() == "!DECLINE":
            if message.channel.id == gate:
                await message.author.kick()

        
        if message.content.upper().startswith("!PROFILE"):
            if len(args) <= 1:
                user = message.author
                profile = get_profile(str(message.author.id))
            else:
                user = discord.utils.get(message.guild.members, mention=args[1])
                profile = get_profile(str(user.id))
                if user.id == 472063067014823938:
                    await error("[418] I'm a teapot", message.channel)
                    return 
            em = discord.Embed(title=user.name, colour=0x00AA00)

            rank = get_rank(user)
            em.set_author(name=rank[0], icon_url=rank[1])

            badges = "_ _ _ _"
            if profile[3] == 1:
                badges = badges + " <:Staff:486271130148012055> _ _"
            if profile[4] == 1:
                badges = badges + " <:YouTuber:472150144243204096> _ _"
            if profile[5] == 1:
                badges = badges + " <:ValuedMember:472151449267339270> _ _"
            if profile[6] == 1:
                badges = badges + " <:Veteran:472849525732671510> _ _"
                
            
            em.add_field(name=badges, value="_ _ _ _ ")

            em.add_field(name="Rank", value=profile[1])
            em.add_field(name="Tier", value=profile[2])


            em.add_field(name="_ _", value="_ _")
            em.add_field(name="Member Since", value=str(user.joined_at)[0:19])
            em.add_field(name="Balance", value="$"+str(int(profile[0])))
             
            await message.channel.send(embed=em)

        elif message.content.upper().startswith("!BADGE"):
            if "Admin" in [role.name for role in message.author.roles] or "Owner" in [role.name for role in message.author.roles]:
                if args[1].upper() == "ADD":
                    if args[2] in ["Staff", "YouTuber", "ValuedMember", "Veteran"]:
                        user = discord.utils.get(message.guild.members, mention = args[3])
                        execute_query("varsity.db", "UPDATE Members SET %s = 1 WHERE UserID = %s" % (args[2], str(user.id)))
                        await message.channel.send("Sucessfully applied **%s Badge** to %s!" % (args[2], user.mention))
                if args[1].upper() == "REMOVE":
                    if args[2] in ["Staff", "YouTuber", "ValuedMember", "Veteran"]:
                        user = discord.utils.get(message.guild.members, mention = args[3])
                        execute_query("varsity.db", "UPDATE Members SET %s = 0 WHERE UserID = %s" % (args[2], str(user.id)))
                        await message.channel.send("Sucessfully removed **%s Badge** from %s!" % (args[2], user.mention))


        elif message.content.upper().startswith("!RANKUP"):
            rank = db_query("varsity.db", "SELECT Rank from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
            tier = db_query("varsity.db", "SELECT Tier from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
            if rank == "X":
                em = discord.Embed(title="Error!", description="You've already reached the highest rank. Try **!prestige**", colour=0xFF5555)
                await message.channel.send(embed=em)
            else:
                cost = db_query("varsity.db", "SELECT RankUpCost_%s FROM ranks WHERE RankID = '%s'" % (str(tier), str(db_query("varsity.db", "SELECT RankID FROM ranks WHERE RankName = '%s'" % (rank))[0][0]+1)))[0][0]
                balance = fetch_coins(message.author)
                if cost > balance:
                    em = discord.Embed(title="Insufficient Funds!", description="You currently have $%s\nYou need $%s more to rank up!" % (str(balance), str(cost-balance)), colour=0xFF5555)
                    await message.channel.send(embed=em)
                else:
                    em = discord.Embed(title="Rank Up", description="You currently have $%s\nAfter you rank up you will have $%s\n\nAre you sure you want to rank up?*" % (str(balance), str(balance-cost)), colour=0x55FF55)
                    confirmation = await message.channel.send(embed=em)
                    await confirmation.add_reaction("\U0001F44D")
                    await confirmation.add_reaction("\U0001F44E")

                    def check(reaction, user):
                        return user == message.author and (str(reaction.emoji) == '\U0001F44D' or str(reaction.emoji) == "\U0001F44E")
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await message.channel.send('Timed Out')
                    else:
                        if str(reaction.emoji) == "\U0001F44D":
                            new_rank = db_query("varsity.db", "SELECT RankName FROM ranks WHERE RankID = '%s'" % (str(db_query("varsity.db", "SELECT RankID FROM ranks WHERE RankName = '%s'" % (rank))[0][0]+1)))[0][0]
                            add_coins(message.author, -cost)
                            execute_query("varsity.db", "UPDATE Members SET Rank = '%s' WHERE UserID = %s" % (new_rank, str(message.author.id)))
                            em = discord.Embed(title="Success!", description="Congratulations! You've ranked up to Rank %s" % (new_rank), colour=0x55FFFF)
                            await message.channel.send(embed=em)
                        elif str(reaction.emoji) == "\U0001F44E":
                            await message.channel.send("Rankup Declined")
                        await confirmation.clear_reactions()

        elif message.content.upper().startswith("!PAY"):
            balance = fetch_coins(message.author)
            if int(args[2]) > balance:
                await message.channel.send("Transaction Rejected\n_ - _ `Insufficient Funds`")
            else:
                user = discord.utils.get(message.guild.members, mention=args[1])
                if int(args[2]) < 0:
                    await error("[400] Amount cannot be negative", message.channel)
                    return False
                else:
                    amount = args[2]
                    
                em = discord.Embed(title="Transaction", description="Please confirm your payment of $%s to %s **Y/N**" % (str(amount), str(user.mention)), colour=0x55FF55)
                await message.channel.send(embed=em)

                def check(m):
                    return m.author.id == message.author.id

                try:
                    msg = await client.wait_for('message', check=check, timeout=30.0)
                except asyncio.TimeoutError:
                    await channel.send("No Response - Transaction Cancelled")
                else:
                    if msg.content.upper() == "Y" or msg.content.upper() == "YES":
                        add_coins(message.author, -int(amount))
                        add_coins(user, int(amount))
                        await message.channel.send(":ok_hand: Transaction Complete")
                    elif msg.content.upper() == "N" or msg.content.upper() == "NO":
                            await message.channel.send("Transaction Declined")
                    else:
                        await message.channel.send("Invalid Response - Transaction Cancelled")

        elif message.content.upper().startswith("!RANSACK"):
            await error("[501] Not Implemented", message.channel)
            

        elif message.content.upper().startswith("!PRESTIGE"):
            rank = db_query("varsity.db", "SELECT Rank from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
            tier = db_query("varsity.db", "SELECT Tier from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
            if not rank == "X":
                pass
            else:
                if tier == 3:
                    pass
                else:
                    em = discord.Embed(title="WARNING", description="Prestiging will reset your balance and rank back to defaults but will upgrade your tier and unlock new perks.\n\nRanking up again will cost more than it did last time!\n\nAre you sure you want to prestige? **Y/N**", colour=0xFF5555) 
                    await message.channel.send(embed=em)

                    def check(m):
                        return m.author.id == message.author.id

                    try:
                        msg = await client.wait_for('message', check=check, timeout=30.0)
                    except asyncio.TimeoutError:
                        await channel.send("Did not respond in time, please try again!")
                    else:
                        if msg.content.upper() == "Y" or msg.content.upper() == "YES":
                            add_coins(message.author, -fetch_coins(message.author))
                            new_tier = tier + 1
                            execute_query("varsity.db", "UPDATE Members SET Tier = %s, Rank = 'I' where UserID = %s" % (str(new_tier), str(message.author.id)))
                            if new_tier == 1:
                                await message.author.add_roles(discord.utils.get(message.guild.roles, id=472094980350148608))
                            if new_tier == 2:
                                await message.author.add_roles(discord.utils.get(message.guild.roles, id=472095274618060831))
                            if new_tier == 3:
                                await message.author.add_roles(discord.utils.get(message.guild.roles, id=472095322378600458))
                            em = discord.Embed(title="Success!", description="Congratulations! You've prestiged to Tier %s!" % (new_tier), colour=0x55FFFF)
                            await message.channel.send(embed=em)
                            
                        elif msg.content.upper() == "N" or msg.content.upper() == "NO":
                            await message.channel.send("Rankup Declined")
                        else:
                            await message.channel.send("Invalid Response")
            
        elif message.content.upper().startswith("!HUG"):
            if "Staff" in [role.name for role in message.author.roles]:
                hug_type = random.choice(["just gave you a big hug!", "just gave you a big big hug!", "just gave you a tight squeeze!", "just gave you a bog standard hug!"])
                await message.channel.send("%s - %s %s :hugging:" % (args[1], message.author.mention, hug_type))
            else:
                await error("[403] You do not have permission to use this command")

        elif message.content.upper().startswith("!FIGHT"):
            if "Staff" in [role.name for role in message.author.roles]:
                loss = 0
                init = message.author.mention
                target = args[1]

                while not loss == 1: 
                    fight = random.choice(["%s threw a chair at %s" % (init, target), "%s whacked %s with a stick" % (init, target), "%s slapped %s to the floor" % (init, target), "%s threw %s through a wall" % (init, target)])
                    await message.channel.send(fight)
                    await asyncio.sleep(2)
                    loss = random.randint(1, 3)
                    if loss == 1:
                        await message.channel.send("%s accepts defeat! %s has won the fight!" % (target, init))
                    else:
                        await message.channel.send("%s does not giveup and continues the fight!" % (target))
                        
                    temp = target
                    target = init
                    init = temp
                    await asyncio.sleep(4)
            else:
                await error("[403] You do not have permission to use this command")

        elif message.content.upper().startswith("!PING"):
            start = time.time() * 1000
            msg = await message.channel.send("Pong!")
            end = time.time() * 1000
            await msg.edit(content="Pong! `%sms`" % (str(int(round(end-start, 0)))))

        elif message.content.upper().startswith("!CONNECTION"):
            if not conCooldown:
                conCooldown = True
                async with channel.typing():
                    ping = str(int(round(st.ping(), 0)))
                    down = round((st.download()/1000000), 2)
                    up = round((st.upload()/1000000), 2)
                    em = discord.Embed(title="Connection Statistics", description="Current Connection Statistics", color=0x1671db)
                    em.add_field(name="Ping", value="`%sms`" % ping)
                    em.add_field(name="Download", value="`%s mbps`" % down)
                    em.add_field(name="Upload", value="`%s mbps`" % up)
                    await message.channel.send(embed=em)
                await asyncio.sleep(300)
                conCooldown = False
            else:
                await error("[429] Please wait before using this command again", message.channel) 
                

        elif message.content.upper().startswith("!WINDOWS"):
            role = discord.utils.get(message.guild.roles, name="Windows Insiders")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Windows Insiders** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Windows Insiders** announcement group")

        elif message.content.upper().startswith("!APPLE"):
            role = discord.utils.get(message.guild.roles, name="Apple Developers")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Apple Developers** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Apple Developers** announcement group")
        elif message.content.upper().startswith("!ANDROID"):
            role = discord.utils.get(message.guild.roles, name="Android Beta")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Android Beta** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Android Beta** announcement group")
        elif message.content.upper().startswith("!TECH"):
            role = discord.utils.get(message.guild.roles, name="Technology")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Technology** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Technology** announcement group")
        elif message.content.upper().startswith("!SERVER"):
            role = discord.utils.get(message.guild.roles, name="Server Announcements")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Server Announcements** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Server Announcements** announcement group")

        elif message.content.upper().startswith("!DISABLE"):
            if "Admin" in [role.name for role in message.author.roles] or "Owner" in [role.name for role in message.author.roles]:
                command = "!"+args[1].lower()
                if not command in disabled_commands:
                    disabled_commands.append(command)
                    await message.channel.send(":ok_hand: Successfully disabled `%s`" % command)
                else:
                    await error("[409] This command is already disabled", message.channel) 
        elif message.content.upper().startswith("!ENABLE"):
            if "Admin" in [role.name for role in message.author.roles] or "Owner" in [role.name for role in message.author.roles]:
                command = "!"+args[1]
                if command in disabled_commands:
                    disabled_commands.remove(command)
                    await message.channel.send(":ok_hand: Successfully enabled `%s`" % command)
                else:
                    await error("[409] This command is already enabled", message.channel) 
            

        elif message.content.upper().startswith("W!UPDATE"):
            for member in message.guild.members:
                insert_db_user(member)
                await member.add_roles(discord.utils.get(member.guild.roles, name="-----===== Notif Roles =====-----"))

        if not str(message.author.id) in ignore_list:
            if not message.author.id in cooldown:
                cooldown.append(message.author.id)
                exp_add = random.randint(25,50)
                add_coins(message.author, exp_add)
                await asyncio.sleep(30)
                cooldown.remove(message.author.id)

    except Exception as e:
        await error("[500] %s" % (e), message.channel)
        




@client.event
async def on_member_join(member):
    insert_db_user(member)

        
async def user_accept_rules(member):
    channel = client.get_channel(casual)
    em = discord.Embed(title="Welcome!", description="Hello %s, Welcome to **Varsity Discord**! - Make sure you read all the information in <#473284512378388481>! We hope you enjoy your time here!" % (member.name), colour=0x55FF55)
    em.set_footer(text="We now have %s Members!" % (len(member.guild.members)))
    await channel.send(embed=em)
    reg_role = discord.utils.get(member.guild.roles, name="Member")
    default_role = discord.utils.get(member.guild.roles, name="Regular")
    await member.add_roles(default_role)
    await member.add_roles(reg_role)        
        
        
        
        
        


    
print("Test")    
client.run("") #logs into the bot
