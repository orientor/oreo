import os
import discord
from dotenv import load_dotenv
from sqlitedict import SqliteDict
from fuzzywuzzy import process

mydict = SqliteDict('./my_db.sqlite', autocommit=True)

load_dotenv()
lwe = {}
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    cnt = 1
    if message.content.startswith("!coreo "):
        if len(message.content) < 8:
            return
        xo = message.content[7:]
    elif message.content.startswith("!coreo"):
        if len(message.content) < 7:
            return
        xo = message.content[6:]
    else:
        return
    author_id = message.author.id
    x = '**Channel List**\n'
    channelList = []
    channelmention = {}
    for channel in message.guild.channels:
        if type(channel) != discord.channel.TextChannel:
            continue
        channelList.append(channel.name)
        channelmention[channel.name] = channel.mention
    for channel, weight in process.extract(xo, channelList):
        if weight > 0:
            x += (
                f"> {channelmention[channel]}\n")
            cnt += 1
    if len(x) > 0:
        x += f"**Hit like to create channel '*{xo}*'**"
        sent = await message.channel.send(x)
        await sent.add_reaction('\N{THUMBS UP SIGN}')
        if message.channel.category_id is None:
            mydict[sent.id] = [xo, author_id, False, None]
        else:
            mydict[sent.id] = [xo, author_id,
                               False, message.channel.category_id]
    else:
        sent = await message.channel.send(f"**No results. Hit like to create channel '*{xo}*'.**")
        await sent.add_reaction('\N{THUMBS UP SIGN}')
        if message.channel.category_id is None:
            mydict[sent.id] = [xo, author_id, False, None]
        else:
            mydict[sent.id] = [xo, author_id,
                               False, message.channel.category_id]


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if reaction.message.id not in mydict:
        return
    if user.id != mydict[reaction.message.id][1]:
        return
    if mydict[reaction.message.id][2] is True:
        return
    temp_list = mydict[reaction.message.id].copy()
    temp_list[2] = True
    mydict[reaction.message.id] = temp_list
    if mydict[reaction.message.id][3] is None:
        await reaction.message.guild.create_text_channel(mydict[reaction.message.id][0])
    else:
        category_list = reaction.message.guild.by_category()
        category = None
        for entry in category_list:
            if entry[0] is None:
                continue
            if entry[0].id == mydict[reaction.message.id][3]:
                category = entry[0]
        await reaction.message.guild.create_text_channel(mydict[reaction.message.id][0], category=category)

client.run(TOKEN)
