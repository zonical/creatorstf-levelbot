import discord
from discord.ext import commands, tasks
from discord.utils import get
import sys
import os
import json
import random
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

    async def HandleRoleChecks(self, person, count):
        if (count == 60):
            role = get(person.guild.roles, name="Mercenary")
            print(f"[MC] {person.id} has achieved perms level 1!")
            await person.add_roles(role)
            message = "You have gotten the role Mercenary on the Creators.TF Discord. Your new permissions include: \n```-\tSending images and videos everywhere except #general, and #off-topic.\n-\tChange your nickname.\n-\tEmbed Links.\n-\tUser External Emojis\n-\tAdd Reactions.```"
            await person.send(message)

        elif (count == 1000):
            oldrole = get(person.guild.roles, name="Mercenary")
            role = get(person.guild.roles, name="Veteran")
            print(f"[MC] {person.id} has achieved perms level 2!")
            await person.remove_roles(oldrole)
            await person.add_roles(role)
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
            if (finalTime.seconds/60 >= 1):
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
        pass

    #When someone sends a message, process it.
    @commands.Cog.listener()
    async def on_message(self, message):
        await bot.process_commands(message)
        
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
                
                await self.IncrementMessageCount(message.author)
    
    #Shows an image credit for Alibi, who made the icon.
    @commands.command()
    async def avatar(self, ctx):
        await ctx.send("```The user Alibi#6534 is the one responsible for the avatar used by me! Next time you see them, go say thank you! :)")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if (os.path.exists(f"{currentdir}{slash}users{slash}{member.id}.json") == True):
            #Open JSON file.
            with open(f"{currentdir}{slash}users{slash}{member.id}.json", 'r+') as jsonFile:
                jsonObject = json.loads(jsonFile.read())

                score = jsonObject["messagecount"]

                if score >= 60 and score < 1000:
                    role = get(member.guild.roles, name="Mercenary")
                    print(f"[MC] {member.id} has achieved perms level 1!")
                    await member.add_roles(role)
                elif score >= 1000:
                    role = get(member.guild.roles, name="Veteran")
                    print(f"[MC] {member.id} has achieved perms level 2!")
                    await member.add_roles(role)

try:
    bot = commands.Bot(command_prefix='c!', case_insensitive=True)
    bot.add_cog(CreatorsTFLevelBot(bot))
    bot.run(sys.argv[1])
except KeyboardInterrupt:
    quit()
