import discord
import logging
import os
import re
import json
import random
from inspect import getsourcefile
from dotenv import load_dotenv

curr_dir = os.path.dirname(getsourcefile(lambda: 0))
env_filepath = os.path.join(curr_dir, ".env")
json_filepath = os.path.join(curr_dir, "server_info.json")
load_dotenv(env_filepath)
if "DISCORD_API_KEY" in os.environ:
    api_key = os.environ["DISCORD_API_KEY"]
else:
    api_key = None

with open(json_filepath, 'r', encoding="utf-8") as file:
    server_info = json.loads(file.read())

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
dice_regex = re.compile(r"(?P<count>\d+)?d(?P<sides>\d+)")


def format_dice_rolls(rolls):
    max_roll = max(rolls)
    width = len(str(max_roll)) + 2
    border = "+" + "-" * width + "+"
    output = [border]

    for roll in rolls:
        output.append("| " + str(roll).rjust(width - 2) + " |")

    output.append(border)
    message = "```\n" + ("\n".join(output)) + "```"
    return message


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        print(message.content)
        return

    for embed in message.embeds:
        if embed.video and embed.video.url.__contains__("twitter.com"):
            embed_dict = embed.to_dict()
            await message.edit(suppress=True)
            await message.channel.send(embed_dict["url"].replace("twitter.com", "vxtwitter.com"))

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    elif message.content.startswith('$debug'):
        print("Client:\n", client)
        print("Message:\n", message)
        await message.channel.send('The bugs are gone fishin\'')
    elif message.content.startswith('$roll'):
        result = dice_regex.search(string=message.content)
        if result:
            sides = int(result.group("sides"))
            if result.group("count") is None:
                count = 1
            else:
                count = int(result.group("count"))
            roll = random.choices(range(1, sides+1), k=count)
            await message.channel.send(format_dice_rolls(roll))
        else:
            await message.channel.send("No dice! Try '$roll 2d6'")


@client.event
async def on_voice_state_update(member, before, after):
    old_user_channel = before.channel
    new_user_channel = after.channel

    print(member)
    print("Voice state update before:", before)
    print("Voice state update after:", after)

    if old_user_channel is None and new_user_channel is not None:
        rule_object = server_info["voice_channel_role_pings"][str(new_user_channel.id)]
        channel_send = client.get_channel(rule_object["channel_send"])

        await channel_send.send(rule_object["message"])


client.run(api_key)
