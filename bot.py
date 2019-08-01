import asyncio
import discord
import os
import time

from discord.ext.commands import Bot
from worker import add_to_queue, get_queue, get_current, buff_time_remaining, get_completed, remove_from_queue, clear_queue, clear_current, get_not_found, update_current, get_unknown

TOKEN = os.environ["TAH_TOKEN"]
BOT_PREFIX = ("!")

client = Bot(command_prefix=BOT_PREFIX)

def has_PO_role(user):
    roles = user.roles
    for role in roles:
        if role.name == "PO":
            return True
    return False


"""
Functions for Discord bot.
"""
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.channel.name != "buff-requests":
        return

    if message.content == ('!hello'):
        msg = 'Hello {0}'.format(message.author.mention)
        print(message.author.mention)
        await client.send_message(message.channel, msg)

    elif message.content == "!clear":
        if has_PO_role(message.author):
            clear_queue()
            msg = "Queue has been cleared."
        else:
            msg = "Sorry, but you don't have permissions for that command."
        await client.send_message(message.channel, msg)

    elif message.content == "!clear_current":
        if has_PO_role(message.author):
            clear_current()
            msg = "Current has been cleared."
        else:
            msg = "Sorry, but you don't have permissions for that command."
        await client.send_message(message.channel, msg)

    elif message.content == "!commands":
        msg = """!commands: print available commands
!current: view current buff assignments and how long the role is locked
!queue: view the queue for buff requests
!request: request a specific role in the format of !request | [userName] | [buff]
!done: indicate that you are done with your current buff (setting lock timer to 0)"""
        await client.send_message(message.channel, msg)

    elif message.content == "!queue":
        queue = get_queue()
        msg = ""
        for rank, request in enumerate(queue):
            if request["state"] == "processing":
                msg += """**Position %d**: %s - %s - %s\n""" % (rank, request["user"], request["role"], request["state"])
            else:
                msg += """**Position %d**: %s - %s\n""" % (rank, request["user"], request["role"])
        if msg == "":
            msg = "Queue is empty."
        await client.send_message(message.channel, msg)

    elif message.content == "!done":
        current = get_current() 
        for role, info in current.items():
            user = info["user"]
            mention = info["mention"]
            if message.author.mention == mention:
                update_current(user, role, 0, mention)
                msg = "Understood, the role of {0} has been unlocked. Previous holder: {1} {2}".format(role, user, mention)
                await client.send_message(message.channel, msg)
                return

        msg = "You don't currently hold any titles {0}".format(message.author.mention)
        await client.send_message(message.channel, msg)

    elif message.content == "!current":
        current = get_current()
        research = current.get("research", {"user": "None", "start": 0})
        builder = current.get("builder", {"user": "None", "start": 0})
        training = current.get("training", {"user": "None", "start": 0})

        msg = """**Research**: %s - %d seconds remaining
**Builder**: %s - %d seconds remaining
**Training**: %s - %d seconds remaining""" % (
            research["user"], buff_time_remaining(research["start"]),
            builder["user"], buff_time_remaining(builder["start"]),
            training["user"], buff_time_remaining(training["start"]),
            )

        await client.send_message(message.channel, msg)

    elif message.content.startswith('!request'):
        contents = message.content.split("|")
        if len(contents) != 3:
            msg = "Please send requests in the format '!request | [userName] | [buff]'. The current buffs are research, training, and builder."
            await client.send_message(message.channel, msg)
            return

        user = contents[1].strip()
        buff = contents[2].strip()
        valid_buffs = {"training", "builder", "research"}
        if buff not in valid_buffs:
            msg = "You have requested an invalid buff. The buff types are research, builder, and training."
            await client.send_message(message.channel, msg)
            return
        elif buff in valid_buffs:

            not_handled = {
                "Formin": "Lord Commander",
                "RAMSICO": "Most Devout",
                "VN Valar I": "Master of Ships",
                "Nugury": "Master of Coin"
            }
            if user in not_handled.keys():
                msg = "Sorry {0}, because you're the current {1}, I can't process your request.".format(user, not_handled[user])
                await client.send_message(message.channel, msg);
                return

            queue = get_queue()
            for request in queue:
                if request["user"] == user:
                    msg = "You can only request one buff at a time. Wait for your current request to complete before requesting another one, thanks."
                    await client.send_message(message.channel, msg);
                    return

            add_to_queue(user, buff, message.author.mention)
            msg = 'Added to queue {0} for {1} {2.author.mention}'.format(buff, user, message)
            await client.send_message(message.channel, msg)
            """
            try:
                confer_training(user)
                msg = 'Done conferring training {0.author.mention}'.format(message)
                await client.send_message(message.channel, msg)
            except ValueError as e:
                msg = "There was an error in finding your user name in search."
                await client.send_message(message.channel, msg)
            """
        else:
            msg = "Unknown error with your request format."
            await client.send_message(message.channel, msg)
            return
    else:
        triggers = {"please", "pleas", "ships", "training", "build", "builder", "building", "train", "master",
            "maester", "chief", "grand", "whisperers", "buff", "buf", "plz", "research"}
        if any(trigger in message.content.lower() for trigger in triggers):
            msg = "It looks like you might be trying to request a buff {0}. You can request a buff using **!request** or find additional commands using **!commands**".format(message.author.mention)
            await client.send_message(message.channel, msg)




async def message_completed():
    channel = discord.Object(id="593142521664766010")
    while True:
        completed = get_completed()
        not_found = get_not_found()
        unknown_error = get_unknown()  


        if len(completed) != 0:
            task = completed[0]
            msg = 'Your request for {0} to {1} has been completed {2}'.format(task["role"], task["user"], task["mention"])
            remove_from_queue(task["user"])
            await client.send_message(channel, msg);
        elif len(not_found) != 0:
            task = not_found[0]
            msg = 'The user {0} was not found {1}'.format(task["user"], task["mention"])
            remove_from_queue(task["user"])
            await client.send_message(channel, msg);
        elif len(unknown_error) != 0:
            task = unknown_error[0]

            role = task["role"]
            user = task["user"]
            mention = task["mention"]
            
            msg = 'The {0} request for {1} resulted in an unknown error. The current buffs have also been cleared in a full reset. Please send another !request {2}'.format(role, user, mention)
            remove_from_queue(task["user"])
            await client.send_message(channel, msg);

        await asyncio.sleep(15)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    channel = discord.Object(id="593142521664766010")
    msg = "I'm online to handle your buff requests."
    await client.send_message(channel, msg)
    client.loop.create_task(message_completed())


client.run(TOKEN)





