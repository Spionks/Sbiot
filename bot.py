# bot.py
import io
import os
import aiohttp

import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import db
from random import random

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
intents.integrations = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# client = discord.Client()
guilds : dict[int, nextcord.Guild] = {}
db = db.DB()

class Sbiot(nextcord.Client):

    def __init__(self):
        self.sbiot_id = 979775602859061248
        self.spionk_id = 223824127197184001
        self.ello_server_id = 893568164909174835
        self.ello_death_channel_id = 988070592131510303
        self.adorablehq_server_id = 957585958990127144
        self.adorablehq_death_id = 975039863130832966
        self.cuties_server_id = 1002860611409039400
        self.cuties_becs_and_blemma_deaths_id = 1005575341672247408
        self.cuties_community_deaths_id = 1242169746972082327
        self.death_channels = {self.adorablehq_server_id : [{"id" : self.adorablehq_death_id, "authors": ["The Grim Reaper"]}],
            self.ello_server_id : [{"id": self.ello_death_channel_id, "authors": ["sit", "Sbiot"]}],
            self.cuties_server_id : [{"id": self.cuties_becs_and_blemma_deaths_id, "authors": ["Sbiot", "Cutie Bot"]},
                                     {"id": self.cuties_community_deaths_id, "authors": ["Sbiot", "Cutie Bot"]}] }
        self.user_deaths_to_forward = {
            "Spionks" : {"from":self.adorablehq_server_id, "to":[(self.ello_server_id, self.ello_death_channel_id),
                                                                 (self.cuties_server_id, self.cuties_community_deaths_id)]},
            "Chionk" : {"from":self.adorablehq_server_id, "to":[(self.ello_server_id, self.ello_death_channel_id)]},
            "Spuimk" : {"from":self.adorablehq_server_id, "to":[(self.ello_server_id, self.ello_death_channel_id)]},
            "Lietre" : {"from":self.adorablehq_server_id, "to":[(self.ello_server_id, self.ello_death_channel_id)]},
            "blemma" : {"from":self.adorablehq_server_id, "to":[(self.cuties_server_id, self.cuties_becs_and_blemma_deaths_id)]},
            "becs tasty" : {"from":self.adorablehq_server_id, "to":[(self.cuties_server_id, self.cuties_becs_and_blemma_deaths_id),
                                                                    (self.ello_server_id, self.ello_death_channel_id)]}
        }
        self.maki_bot_id = 563434444321587202
        self.maki_hall_of_fame_channel_id = 1206574323717111829
        self.maki_hall_of_fame_channel : nextcord.channel.TextChannel
        super().__init__(intents=intents)


    async def on_ready(self):
        print(f"Sbiot online")
        for guild in self.guilds:
            print(f"Connected to {guild}")
            guilds[guild.id] = guild

        for server_id, channels in self.death_channels.items():
            for channel in channels:
                channel["channel"] = nextcord.utils.get(guilds[server_id].channels, id=channel["id"])
        
        self.maki_hall_of_fame_channel = self.get_channel(self.maki_hall_of_fame_channel_id)

    async def on_message(self, message: nextcord.message.Message):
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

        elif message.guild.id in self.death_channels \
        and message.channel.id in [ channel["id"] for channel in self.death_channels[message.guild.id] if message.author.name in channel["authors"] ]:

            username = message.content[:-12]

            death_record_name = message.guild.name + "_deaths"
            current_death_count = self.increment_record(username, death_record_name, 1)
            await message.reply(f"{username} has died {current_death_count} time{'' if current_death_count == 1 else 's'}")

            if username in self.user_deaths_to_forward and message.guild.id == self.user_deaths_to_forward[username]["from"]:
                for server_to_forward_to, channel_to_forward_to in self.user_deaths_to_forward[username]["to"]:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(message.attachments[0].url) as resp:
                            if resp.status != 200:
                                print(f'Could not download file at {message.attachments[0].url}')
                                return
                            data = io.BytesIO(await resp.read())
                            channel = None
                            for c in self.death_channels[server_to_forward_to]:
                                if c["id"] == channel_to_forward_to:
                                    channel = c["channel"]
                            await channel.send(f"{username} has died lmfao.", file=nextcord.File(data, "death.png"))
                            death_record_name = guilds[server_to_forward_to].name + "_deaths"
                            current_death_count = self.increment_record(username, death_record_name, 1)
                            await channel.send(f"{username} has died {current_death_count} time{'' if current_death_count == 1 else 's'}")


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

        elif lowercase_message[0:5] == "!roll":
            roll_string = lowercase_message[6:]
            dice_strings = roll_string.split("+")
            result_strings = []
            total = 0
            for dice_string in dice_strings:
                dice_string_split = dice_string.split("d")
                if len(dice_string_split) == 1:
                    try:
                        total += int(dice_string)
                    except ValueError:
                            await message.reply(f"{dice_string} is not a valid number")
                            return
                    result_strings.append(dice_string)
                elif len(dice_string_split) == 2:
                    n_dice = 0
                    try:
                        dice_sides = int(dice_string_split[1])
                        if dice_sides > 256:
                            await message.reply(f"{dice_string_split[1]} would make the dice's numbers too small!")
                            return
                        elif dice_sides < 1:
                            await message.reply(f"A dice can not have {dice_string_split[1]} sides!")
                            return
                    except ValueError:
                            await message.reply(f"{dice_string_split[1]} is not a valid number of sides for dice")
                            return
                    if dice_string_split[0] == 0:
                        n_dice = 1
                    else:
                        if dice_string_split[0] == "":
                            n_dice = 1
                        else:
                            try:
                                n_dice = int(dice_string_split[0])
                            except ValueError:
                                await message.reply(f"{dice_string_split[0]} is not a valid number of dice")
                                return
                        if n_dice > 100:
                            await message.reply("Too many dice!!!")
                            return
                        elif n_dice < 1:
                            await message.reply(f"{dice_string_split[0]} is not a valid number of dice")
                            return
                    for i in range(n_dice):
                        roll = int(random() * dice_sides + 1)
                        total += roll
                        result_strings.append(f"d{dice_sides}: {roll}")
            if len(result_strings) == 0:
                await message.reply(f"Invalid format")
                return
            result_string = f"You rolled: {total} ({' + '.join(result_strings)})"
            await message.reply(result_string)
        
        elif lowercase_message[0:17] == "!download_history":
            if message.author.id != self.spionk_id:
                await message.reply("You are not frog enough to do that 🐸")
                return
            
            parent_folder = "downloaded_message_history"
            if not os.path.exists(parent_folder):
                os.makedirs(parent_folder)

            n_channels = len(message.guild.text_channels)

            reply_message = await message.reply(f"Downloading... 0/{n_channels}")
            for i, channel in enumerate(message.guild.text_channels):
                folder = parent_folder + "/" + channel.name
                if not os.path.exists(folder):
                    os.makedirs(folder)

                meta_file_path = folder + "/meta"
                with open(meta_file_path, "w") as meta_file:
                    meta_file.write(f"message_id, jump_url, message_author_name, n_attachments, n_reactions\n")
                    async for message_iter in channel.history(limit=None):
                        meta_file.write(f"{message_iter.id}, {message_iter.jump_url}, {message_iter.author}, {len(message.attachments)}, {len(message.reactions)}\n")
                        
                        message_file_path = folder + "/" + str(message_iter.id)
                        with open(message_file_path, "w") as file:
                            file.write(f"{message_iter.content}\n")

                reply_message = await reply_message.edit(content=f"Downloading... {i}/{n_channels}")

            await reply_message.edit(content="Download complete 🐸")
                    



    def increment_record(self, username: str, record_name: str, increment_by: int) -> int:
        current_record = db.get_record(username, record_name)
        if not current_record:
            current_record = 0
        else:
            current_record = int(current_record)
        current_record = current_record + increment_by
        db.update_record(username, record_name, current_record)
        return current_record

class MakiCog(commands.Cog):
    def __init__(self, bot :Sbiot):
        self.bot :Sbiot = bot

    @nextcord.slash_command(name="inspire", description="Generates a very inspirational quote")
    async def maki_inspire(self, interaction: nextcord.Interaction):
        """
        Mimics the old Maki /inspire command.
        """
        generate_url = "https://inspirobot.me/api?generate=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(generate_url) as response:
                if response.status != 200:
                    await interaction.send(f"Failed to generate inspirational quote, please dm <@{self.bot.spionk_id}>")
                    await interaction.send(f"Status: {response.status}")
                    return

                image_url_bytes = await response.read()
                image_url = image_url_bytes.decode("utf-8")

            async with session.get(image_url) as response:
                if response.status != 200:
                    await interaction.send(f"Failed to fetch inspirational quote, please dm <@{self.bot.spionk_id}>")
                    await interaction.send(f"Status: {response.status}")
                    return
                
                image = io.BytesIO(await response.read())
                await interaction.send(file=nextcord.File(fp=image, filename="generated.jpg"))


    @nextcord.message_command(name="submit to hall of fame")
    async def submit_maki_hall_of_fame(self, interaction: nextcord.Interaction, message: nextcord.message.Message):
        """
        Submits an image from the /inspire channel to the hall of fame
        """

        if len(message.attachments) == 0:
            await interaction.response.send_message("You must submit an image, you silly potato.", ephemeral=True)
            return

        author_display_name = message.author.global_name
        author_guild_nick_name = interaction.guild.get_member(message.author.id).nick

        if (author_display_name == "Sbiot" or author_guild_nick_name == "Sbiot") and message.author.id != self.bot.sbiot_id:
            await interaction.response.send_message("Changing your name to \"Sbiot\" won't trick me!", ephemeral=True)
            return
        
        if message.author.id != self.bot.sbiot_id:
            await interaction.response.send_message("That is not a message sent by Sbiot, you silly billy.", ephemeral=True)
            return        
       
        await interaction.response.send_message("Submitted!", ephemeral=True)
        image_file = message.attachments[0]
        image_bytes = await image_file.read()
        await self.bot.maki_hall_of_fame_channel.send(f"<@{interaction.user.id}> submitted {message.jump_url}:", 
                                                      file = nextcord.File(fp=io.BytesIO(image_bytes), filename=image_file.filename), 
                                                      suppress_embeds=True)


class MaffyCog(commands.Cog):
    def __init__(self, bot :Sbiot):
        self.bot :Sbiot = bot

    @nextcord.slash_command(name="update_maffy_tasks", description="Updates the wheel with the current tasks, separate tasks with semicolon")
    async def update_maffy_tasks(self, interaction: nextcord.Interaction, tasks: str):
        current_tasks = tasks.split(";")
        current_tasks = [ s.strip() for s in current_tasks ]
        previous_tasks = [ task["task"] for task in db.get_all_maffy_tasks() ]
        
        completed_tasks = [ task for task in previous_tasks if task not in current_tasks and task != "" ]
        added_tasks = [ task for task in current_tasks if task not in previous_tasks and task != "" ]

        for task in completed_tasks:
            db.set_maffy_task_completed(task)
        
        for task in added_tasks:
            db.add_maffy_task(task)
        
        await interaction.response.send_message(f"{len(completed_tasks)} tasks marked as completed, {len(added_tasks)} new tasks added.")

    @nextcord.slash_command(name="view_maffy_tasks", description="Shows all Maffy's tasks currently on the wheel")
    async def view_maffy_tasks(self, interaction: nextcord.Interaction):
        tasks = db.get_all_maffy_tasks()
        if len(tasks) == 0:
            await interaction.response.send_message("There are no tasks on the wheel, go to https://www.twitch.tv/maffychew and give him some new tasks! 🐸")
        tasks_str = [ f"{task['task']}, added: {task['added']}, completed: {task['completed']}" for task in tasks ]

        responses = []
        length = 0
        responded = False
        for task in tasks_str:
            length += len(task)
            # divide message into chunks of max 2000 characters (1950 to give some margin for the extra linebreaks etc)
            if length >= 1950:
                if not responded:
                    await interaction.response.send_message("\n".join(responses))
                    responded = True
                else:
                    await interaction.channel.send("\n".join(responses))
                responses.clear()
                length = 0
            responses.append(task)

        if not responded:
            await interaction.response.send_message("\n".join(responses))
            responded = True
        else:
            await interaction.channel.send("\n".join(responses))

    @nextcord.slash_command(name="delete_maffy_tasks", description="Delete a task from the wheel, separate tasks with semicolon")
    async def delete_maffy_tasks(self, interaction: nextcord.Interaction, tasks: str):
        tasks = tasks.split(";")
        tasks = [ s.strip() for s in tasks ]
        for task in tasks:
            db.remove_maffy_task(task)
        await interaction.response.send_message(f"{len(tasks)} tasks successfully deleted.")


if __name__ == "__main__":
    bot = Sbiot()
    bot.add_cog(MakiCog(bot))
    bot.add_cog(MaffyCog(bot))
    bot.run(TOKEN)
