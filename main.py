import discord
from discord.ext import commands, tasks
from discord.utils import get
import sys
import os
import json
import random
import asyncio
from datetime import datetime

currentdir = os.path.dirname(os.path.abspath(__file__))

if os.name == "nt":
    slash = "\\"
else:
    slash = "/"

if not os.path.exists(currentdir + slash + "users"):
    os.makedirs(currentdir + slash + "users")

class CreatorsTFLevelBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #This function handles the giving of roles.
    async def HandleRoleChecks(self, person, count):
        #Level 1: Mercenary. Required score, 45 or above.
        if (count >= 30 and count < 150):
            print(f"[MC] {person.id} is eligble for level 2!")
            membersRoles = person.roles
            mercRole = get(person.guild.roles, name="Mercenary")

            #This person does NOT have the role, give it to them.
            if mercRole not in membersRoles:
                print(f"[MC] {person.id} has achieved perms level 1!")
                await person.add_roles(mercRole)
                message = "You have gotten the role Mercenary on the Creators.TF Discord. Your new permissions include: \n```-\tSending images and videos everywhere except #general, and #off-topic.\n-\tChange your nickname.\n-\tEmbed Links.\n-\tUser External Emojis\n-\tAdd Reactions.```"
                await person.send(message)

        #Level 2: Veteran. Required score, 750 or above.
        elif (count >= 150):
            print(f"[MC] {person.id} is eligble for level 2!")
            membersRoles = person.roles
            oldrole = get(person.guild.roles, name="Mercenary")
            vetRole = get(person.guild.roles, name="Veteran")

            #This person does NOT have the role, give it to them.
            if vetRole not in membersRoles:
                print(f"[MC] {person.id} has achieved perms level 2!")
                await person.remove_roles(oldrole)
                await person.add_roles(vetRole)
                await person.send("You have gotten the role Veteran on the Creators.TF Discord. Your new permissions include: \n```\n-\tSending images and videos everywhere.```")

    async def IncrementMessageCount(self, person):
        #Check if the JSON file exists.
        #File doesn't exist, lets create it and set a basic template.
        if (os.path.exists(f"{currentdir}{slash}users{slash}{person.id}.json") == False):
            print(f"[MC] {person}'s file doesn't exist, creating!")
            with open(f"{currentdir}{slash}users{slash}{person.id}.json", 'w+') as jsonFile:
                message = {
                    "messagecount": 1,
                    "lastvalidtime": datetime.strftime(datetime.now(), "%H:%M:%S")
                }

                #Write initial JSON:
                jsonFile.write(json.dumps(message))
                jsonFile.close()
            return
            
        #Open JSON file.
        with open(f"{currentdir}{slash}users{slash}{person.id}.json", 'r+') as jsonFile:
            jsonObject = json.loads(jsonFile.read())
            
            #So we have a time, let's set our comparison.
            lasttime = jsonObject["lastvalidtime"]
            lasttime = datetime.strptime(lasttime, "%H:%M:%S")
            finalTime = datetime.now() - lasttime

            #Is it equal to or over a minute?
            if (finalTime.seconds/10 >= 1):
                #Add a point, set the last valid time to now.
                print(f"[MC] Adding to {person.id}'s current message count...")
                jsonObject["messagecount"] += 1
                jsonObject["lastvalidtime"] = datetime.strftime(datetime.now(), "%H:%M:%S")

                await self.HandleRoleChecks(person, jsonObject["messagecount"])

            #Write and close.
            jsonFile.seek(0)
            json.dump(jsonObject, jsonFile)
            jsonFile.truncate()
            jsonFile.close()
        
        #await self.UpdateStatus()

    @commands.Cog.listener()
    async def on_ready(self):
        print("[MC] Bot started!")
        self.StatusUpdate_Loop.start()

    #When someone sends a message, process it.
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return

        #Bots don't count.
        if message.author.bot == False:
            print(f'[MC] Message from {message.author.id}: {message.content}')
            #Our message needs to be greater than 3 characters.
            if len(message.content) >= 3:
                #Our message can't be just an emoji or a mention.
                characters = [('<', '>'), (':', ':')]

                for char in characters:
                    if message.content.startswith(char[0]) == True and message.content.endswith(char[1]) == True:
                        return
                
                #Passed the checks? Lets deal with the file side now.
                await self.IncrementMessageCount(message.author)
    
    #Shows an image credit for Alibi, who made the icon.
    @commands.command()
    async def avatar(self, ctx):
        await ctx.send("```The user Alibi#6534 is the one responsible for the avatar used by me! Next time you see them, go say thank you! :)```")

    @commands.command()
    async def score(self, ctx):
        if (os.path.exists(f"{currentdir}{slash}users{slash}{ctx.author.id}.json") == True):
            #Open JSON file.
            with open(f"{currentdir}{slash}users{slash}{ctx.author.id}.json", 'r+') as jsonFile:
                jsonObject = json.loads(jsonFile.read())

                score = jsonObject["messagecount"]
                howmanyTimes = round(score/150, 3)

                embedMessage = discord.Embed(title="Creators.TF Utility Bot.")
                embedMessage.add_field(name="Your score:", value=f"Your current score is {score}. That is {howmanyTimes}x the points of Veteran (150).",inline=False)

                await ctx.send(f"<@{ctx.author.id}>", embed=embedMessage)
    lastRandomNumber = -1

    #This will change our status every so often to show certain statistics.
    @tasks.loop(seconds=30)
    async def StatusUpdate_Loop(self):
        number = len(os.listdir(currentdir + f"{slash}users"))

        activity = discord.Activity(name=f'over {number} peoples scores...', 
        type=discord.ActivityType.watching)
        await self.bot.change_presence(activity=activity)

    #This function assigns roles automatically when someone has joined the server.
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        userId = before.id #Doesn't really matter which one we go with.
        pendingVerificationRole = get(before.guild.roles, name="Pending Verification")

        #Now check to see if the role was in the before and not in the after.
        if pendingVerificationRole in before.roles and pendingVerificationRole not in after.roles:
            #Success! Let's assign the roles.
            #Because of how AltDentifier works, we don't need to handle removing Pending Verification
            #and also assigning the Member role for us.
            if (os.path.exists(f"{currentdir}{slash}users{slash}{member.id}.json") == True):
                #Open JSON file.
                with open(f"{currentdir}{slash}users{slash}{member.id}.json", 'r+') as jsonFile:
                    jsonObject = json.loads(jsonFile.read())

                    score = jsonObject["messagecount"]
                    role = None

                    #Lets give them the roles depending on their score.
                    if score >= 30 and score < 150:
                        role = get(member.guild.roles, name="Mercenary")
                        print(f"[MC] {member.id} has achieved perms level 1!")
                    elif score >= 150:
                        role = get(member.guild.roles, name="Veteran")
                        print(f"[MC] {member.id} has achieved perms level 2!")
                    
                    #We're giving a role?
                    if role != None:
                        await member.add_roles(role)

class CreatorsTFNicknameManagerBot(commands.Cog):
    badwords = []
    logchannelID = -1
    def __init__(self, bot):
        self.bot = bot

        #Because github won't probably like us having tons of bad words
        #on our repo, a private file is hosted where it grabs a list of
        #explicit words to look out for. This is based off of our Dyno blacklist.
        with open(currentdir + "/config/badwords.json") as file:
            #Load into JSON, then parse:
            jsonObj = json.load(file)
            for word in jsonObj["words"]:
                self.badwords.append(word)

            self.logchannelID = jsonObj["logchannel"]

        print("Loaded bad words: ", self.badwords)

    @commands.Cog.listener()
    async def on_ready(self):
        print("[NICK] Bot started!")
    @commands.Cog.listener()
    async def on_member_update(self, before : discord.Member, after : discord.Member):
        username = before.name
        
        beforeNickname = before.nick
        afterNickname = after.nick

        if afterNickname:
            #Loop through our list of bad words.
            for word in self.badwords:
                if word in afterNickname.lower(): #Is this bad word in our nickname?
                    print(f"[NICK] {before} has changed their nickname to a bad word: {beforeNickname} -> {afterNickname}")
                    #Edit nickname.
                    await after.edit(nick=username)

                    #channel = bot.get_channel(self.logchannelID)
                    #Construct embed to send.
                    #embedMessage = discord.Embed(title="Creators.TF Utility Bot.")
                    #embedMessage.add_field(name="A username tried to use a blacklisted name", value=f"User: <@{before.id}",inline=False)
                    #embedMessage.add_field(name="Before nickname:", value=f"{beforeNickname}",inline=False)
                    #embedMessage.add_field(name="After nickname:", value=f"{afterNickname}",inline=False)
                    #await channel.send(embed=embedMessage)

try:
    bot = commands.Bot(command_prefix='c!', case_insensitive=True)
    bot.remove_command("help")
    bot.add_cog(CreatorsTFLevelBot(bot))
    bot.add_cog(CreatorsTFNicknameManagerBot(bot))
    bot.run(sys.argv[1])
except KeyboardInterrupt:
    quit()
