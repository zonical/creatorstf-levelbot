import discord
from discord.ext import commands, tasks
from discord.utils import get
import sys
import os
import json
from datetime import datetime

currentdir = os.path.dirname(os.path.abspath(__file__))

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

    async def IncrementMessageCount(self, person):
        #Check if the JSON file exists.
        #File doesn't exist, lets create it and set a basic template.
        if (os.path.exists(f"{currentdir}\\users\\{person.id}.json") == False):
            print(f"[MC] {person}'s file doesn't exist, creating!")
            with open(f"{currentdir}\\users\\{person.id}.json", 'w+') as jsonFile:
                message = {
                    "messagecount": 1,
                    "lastvalidtime": datetime.strftime(datetime.now(), "%H:%M:%S")
                }

                #Write initial JSON:
                jsonFile.write(json.dumps(message))
                jsonFile.close()
            return
            
        #Open JSON file.
        with open(f"{currentdir}\\users\\{person.id}.json", 'r+') as jsonFile:
            jsonObject = json.loads(jsonFile.read())

            #Check to see if we have an initial time
            if ("lastvalidtime" in jsonObject):
                temp = jsonObject["lastvalidtime"]
                lasttime = datetime.strptime(temp, "%H:%M:%S")
            else:
                #We don't have an existing time, so we'll just add a point to the message count and set the time here.
                jsonObject["messagecount"] += 1
                jsonObject["lastvalidtime"] = datetime.strftime(datetime.now(), "%H:%M:%S")
                
                #Write and close.
                jsonFile.seek(0)
                json.dump(jsonObject, jsonFile)
                jsonFile.truncate()
                jsonFile.close()
                return
            
            #So we have a time, let's set our comparison.
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

    #We give credit to Alibi here for making our amazing profile pic.
    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Activity(name=f'the thanking game for Alibi#6534 who made the avatar!', type=discord.ActivityType.playing)
        await bot.change_presence(activity=activity)

    #When someone sends a message, process it.
    @commands.Cog.listener()
    async def on_message(self, message):
        #Bots don't count.
        if message.author.bot == False:
            print(f'[MC] Message from {message.author.id}: {message.content}')
            #Our message needs to be greater than 3 characters.
            if len(message.content) >= 3:
                #Our message can't be just an emoji or a mention.
                if message.content.startswith('<') == False and message.content.endswith('>') == False:
                    await self.IncrementMessageCount(message.author)

bot = commands.Bot(command_prefix='c!', case_insensitive=True)
bot.add_cog(CreatorsTFLevelBot(bot))
bot.run(sys.argv[1])

