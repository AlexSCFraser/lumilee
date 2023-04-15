import discord
import logging
import os
import json
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

client = discord.Client()

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('$hello'):
		await message.channel.send('Hello!')
		
@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('$debug'):
		print("Client:\n", client)
		print("Message:\n", message)
		await message.channel.send('The bugs are gone fishin\'')

@client.event
async def on_voice_state_update(member, before, after):
	old_user_channel = before.channel
	new_user_channel = after.channel
	
	print("Voice state update before:", before)
	print("Voice state update after:", after)

	if old_user_channel == None and new_user_channel != None:
		rule_object = server_info["voice_channel_role_pings"][str(new_user_channel.id)]
		channel_send = client.get_channel(rule_object["channel_send"])

		await channel_send.send(rule_object["message"])


client.run(api_key)
