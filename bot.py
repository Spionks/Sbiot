# bot.py
import io
import os
import aiohttp

import discord
from dotenv import load_dotenv
import db
from random import randint
from ast import literal_eval

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# client = discord.Client()
guilds : dict[str, discord.Guild] = {}
db = db.DB()

class Sbiot(discord.Client):

    def __init__(self):
        with open("death_channels.txt","r") as death_channel_file:
            self.death_channels = literal_eval(" ".join(death_channel_file.readlines()))
        with open("user_deaths_to_forward.txt","r") as user_deaths_to_forward_file:
            self.user_deaths_to_forward = literal_eval(" ".join(user_deaths_to_forward_file.readlines()))

        super().__init__()


    async def on_ready(self):
        print(f"Sbiot online")
        for guild in self.guilds:
            print(f"Connected to {guild}")
            guilds[guild.name] = guild

        for server_name, channel in self.death_channels.items():
            channel["channel"] = discord.utils.get(guilds[server_name].channels, name=channel["name"])

    async def on_message(self, message: discord.message.Message):
        lowercase_message = message.content.lower()
        if message.author == self.user:
            return

        if lowercase_message == "test yep":
            await message.channel.send("yep test")

        elif lowercase_message == "increment":
            username = message.author.display_name
            current_val = db.get_record(username, "counting")
            if not current_val:
                current_val = 1
            db.update_record(username, "counting", str(int(current_val)+1))
            await message.reply(f"You have counted to {current_val}")

        elif message.guild.name in self.death_channels \
        and message.channel.name == self.death_channels[message.guild.name]["name"] \
        and message.author.name in self.death_channels[message.guild.name]["authors"]:

            username = message.content[:-12]

            death_record_name = message.guild.name + "_deaths"
            current_death_count = self.increment_record(username, death_record_name, 1)
            await message.reply(f"{username} has died {current_death_count} time{'' if current_death_count == 1 else 's'}")

            if username in self.user_deaths_to_forward and message.guild.name == self.user_deaths_to_forward[username]["from"]:
                for server_to_forward_to in self.user_deaths_to_forward[username]["to"]:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(message.attachments[0].url) as resp:
                            if resp.status != 200:
                                print(f'Could not download file at {message.attachments[0].url}')
                                print(f'Status code: {resp.status}')
                                print(f'Content: {await resp.read()}')
                                return
                            data = io.BytesIO(await resp.read())
                            await self.death_channels[server_to_forward_to]["channel"].send(f"{username} has died lmfao.", file=discord.File(data, "death.png"))
                            death_record_name = server_to_forward_to + "_deaths"
                            current_death_count = self.increment_record(username, death_record_name, 1)
                            await self.death_channels[server_to_forward_to]["channel"].send(f"{username} has died {current_death_count} time{'' if current_death_count == 1 else 's'}")


        elif lowercase_message == "deathcount":
            guildname = message.guild.name
            deaths = db.get_all_users_record(f"{guildname}_deaths")
            if not deaths:
                await message.reply(f"No deaths recorded so far")
                return

            deaths = deaths.items()
            deaths = sorted(deaths, key=lambda x: int(x[1]), reverse=True)
            reply_string = "\n".join(d[0] + ": " + d[1] for d in deaths)
            await message.reply(reply_string)

        elif message.author.name == "RNG Announcer" and message.channel.name == "drop-channel":
            if message.embeds:
                embed = message.embeds[0]
                #print(embed.to_dict())
                rsn = embed.author.name
                discord_name = db.get_discord_name(rsn)
                if not discord_name:
                    return
                index_of_opening_bracket = embed.description.find('[')
                index_of_closing_bracket = embed.description.find(']')
                drop = embed.description[index_of_opening_bracket + 1 : index_of_closing_bracket]
                await message.reply(f"gz <@{discord_name}> on getting {drop}")
            
        elif lowercase_message.split()[0] == "set_rsn":
            rsn = message.content.split(" ", 1)[1]
            print(rsn, message.author.id)
            db.set_rsn(rsn, message.author.id)
            await message.reply(f"Successfully set your rsn as {rsn}")
                
    def increment_record(self, username: str, record_name: str, increment_by: int) -> int:
        current_record = db.get_record(username, record_name)
        if not current_record:
            current_record = 0
        else:
            current_record = int(current_record)
        current_record = current_record + increment_by
        db.update_record(username, record_name, current_record)
        return current_record


if __name__ == "__main__":
    bot = Sbiot()
    bot.run(TOKEN)
