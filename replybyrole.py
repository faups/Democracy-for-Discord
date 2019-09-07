import asyncio
import datetime
import discord
import firebase_admin
from firebase_admin import db, credentials

file1 = open('tokens.txt', 'r')

TOKEN = file1[0]

cred = credentials.Certificate(file1[1])
firebase_admin.initialize_app(cred)
db = db.client()

BOT_ID = file1[2]
UPVOTE_ID = file1[3]
DOWNVOTE_ID = file1[4]

time_of_ban = 100000000000
DURATION_OF_BAN = 6000 # 86400 is 24 hours in seconds
has_been_notified = False

karma = 0
KARMA_THRESHOLD = -1
UNDER_THRESHOLD_MESSAGE = '<@!{}>\'s karma is too low for today! Their current karma is {}. Their messaging privelages have been revoked until tomorrow.'
CURRENT_KARMA_MESSAGE = '<@!{}>\'s current karma is {}.'

client = discord.Client()

@client.event
async def on_ready():
    print(get_timestamp() + 'Connection Success')

@client.event
async def on_message(message):
    global karma, time_of_ban, has_been_notified, DURATION_OF_BAN, BOT_ID, UPVOTE_ID, DOWNVOTE_ID
    if message.content == '!karma':
        await message.channel.send(CURRENT_KARMA_MESSAGE.format(message.author.id, karma))
    if message.content == '!threshold':
        await message.channel.send('The current karma threshold for a ban is {}.'.format(KARMA_THRESHOLD))
    if message.content == '!duration':
        await message.channel.send('The current default ban duration is {}.'.format(DURATION_OF_BAN))
    if 'jury' in [i.name.lower() for i in message.author.roles]:
        if karma <= KARMA_THRESHOLD:
            if get_time() > time_of_ban + DURATION_OF_BAN: 
                karma = 0
                await message.channel.send('<@!{}> has been unbanned and their karma set to 0.'.format(message.author.id))
                print(get_timestamp() + '{} has been unbanned and their karma set to 0.'.format(message.author.name))
            else:
                await message.delete()
                if not has_been_notified:
                    await message.channel.send('<@!{}> has been banned for {} seconds due to low karma.'.format(message.author.id, DURATION_OF_BAN))
                    print(get_timestamp() + '{} has been banned for {} seconds due to low karma.'.format(message.author.name, DURATION_OF_BAN))
                    time_of_ban = get_time()
                    has_been_notified = True
            # await message.channel.send(UNDER_THRESHOLD_MESSAGE.format(message.author.id, karma))
        else:
            await message.add_reaction(':upvote:' + str(UPVOTE_ID))
            await message.add_reaction(':downvote:' + str(DOWNVOTE_ID))

@client.event
async def on_reaction_add(reaction, user):
    global karma, BOT_ID, UPVOTE_ID, DOWNVOTE_ID
    if user.id != BOT_ID and 'jury' in [i.name.lower() for i in reaction.message.author.roles]:
        if reaction.emoji.id == UPVOTE_ID:
            update_karma(True)
        elif reaction.emoji.id == DOWNVOTE_ID:
            update_karma(False)

@client.event
async def on_raw_reaction_remove(msg):
    global karma, BOT_ID, UPVOTE_ID, DOWNVOTE_ID
    if msg.emoji.id == UPVOTE_ID:
        update_karma(False)
    elif msg.emoji.id == DOWNVOTE_ID:
        update_karma(True)
    # print('karma: ' + str(karma))

def update_karma(upvote):
    global karma
    if upvote:
        karma += 1
    else:
        karma -= 1

def get_time():
    return int(datetime.datetime.timestamp(datetime.datetime.now()))

def get_timestamp():
    return '[' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + '] '

client.run(TOKEN)

# TODO: implement firebase datastore
# TODO: implement multiple users
# TODO: track everyone, only add reactions for those with the role
# TODO: refactor with discord.ext.commands to make commands easier
# TODO: implement more commands