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

class CreatorsTFLevelBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def HandleRoleChecks(self, person, count):
        if (count == 60):
            role = get(person.guild.roles, name="Mercenary")
            print(f"[MC] {person.id} has achieved perms level 1!")
            await person.add_roles(role)
            message = "You have gotten the role Mercenary on the Creators.TF Discord. Your new permissions include: \n```-\tSending images and videos everywhere except #general.\n-\tChange your nickname.\n-\tEmbed Links.\n-\tUser External Emojis\n-\tAdd Reactions.```"
            await person.send(message)

        elif (count == 1000):
            oldrole = get(person.guild.roles, name="Mercenary")
            role = get(person.guild.roles, name="Veteran")
            print(f"[MC] {person.id} has achieved perms level 2!")
            await person.remove_roles(oldrole)
            await person.add_roles(role)
            await person.send("You have gotten the role Veteran on the Creators.TF Discord. Your new permissions include: \n```\n-\tSending images and videos everywhere.```")

    #Update the status of the bot with the amount of files we're looking over.
    async def UpdateStatus(self):
        randomNumber = random.randint(0, 2)
        print(randomNumber)

        #Show the number of people with a file in the system.
        if randomNumber == 0:
            number = len(os.listdir(currentdir + f"{slash}users"))

            activity = discord.Activity(name=f'over {number} peoples scores...', 
            type=discord.ActivityType.watching)
            await bot.change_presence(activity=activity)
        #Show the number of people with the Mercenary role.
        elif randomNumber == 1:
            creatorsTFGuild = bot.get_guild(644801566234378240)

            role = get(creatorsTFGuild.roles, name="Mercenary")
            numofmembers_WithMerc = len(role.members)

            activity = discord.Activity(name=f'with {numofmembers_WithMerc} mercenaries!', 
            type=discord.ActivityType.playing)
            await bot.change_presence(activity=activity)
        #Show the number of people with the Veteran role.
        elif randomNumber == 2:
            creatorsTFGuild = bot.get_guild(644801566234378240)

            role = get(creatorsTFGuild.roles, name="Veteran")
            numofmembers_WithVet = len(role.members)

            activity = discord.Activity(name=f'with {numofmembers_WithVet} veterans!', 
            type=discord.ActivityType.playing)
            await bot.change_presence(activity=activity)


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
        
        await self.UpdateStatus()

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

bot = commands.Bot(command_prefix='c!', case_insensitive=True)
bot.add_cog(CreatorsTFLevelBot(bot))
bot.run(sys.argv[1])

