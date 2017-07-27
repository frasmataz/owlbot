import discord
import asyncio
import requests
import datetime
import calendar
import json
import pprint
import re
import subprocess
import sys

linktrigger = 2
warnlinkratio = 0.2
maxlinkratio = 0.6
client = discord.Client()
users = {}
onewordeachrecording = False
onewordeachbuffer = []
onewordchannel = ''

botmessages = {
    'storystart':   'tell me a story daddy',
    'storyend':     'wow that was really good thanks, here it is agen',
    'storyinspire': 'oh boy here we go story time',
    'storycancel':  'ok jees i will',
    'myrep':        'You\'re sitting at {} links, and {} not-links.',
    'allrep':       '{}:\n\tlinks: {}\n\tnot-links: {}\n\tlinksinarow: {}\n\twarned: {}\n\n',
    'linkwarn1':    'Hey {}, watch that link spam boyo',
    'linkwarn2':    '{} STAHP',
    'linkwarn3':    '{} always with the linking REEEEEEEEEEEEE {}',
    'linkwarn4':    '{} arming kick button, last warning. {}',
    'linkkick':     'kicking {}, so say we all',
    'updating':     'Updating owlbot..',
    'version':      'Git revision: {},
    'restart':      'killing self brb'
}


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    global users
    global onewordeachrecording
    global onewordeachbuffer
    global onewordchannel

    for role in message.server.roles:
        if role.name == 'admin':
            adminrole = role

    username = message.author.name

    if message.content.startswith('!droneweather'):
        await client.send_message(message.channel, get_weather())

    elif message.content.startswith('!start'):
        await client.send_message(message.channel, botmesaages['storystart'])
        onewordeachrecording = True
        onewordchannel = message.channel.name
        onewordeachbuffer = []
        onewordeachbuffer.append('```')

    elif message.content.startswith('!inspireme'):
        await client.send_message(message.channel, botmessages['storyinspire'])
        word = str(requests.get("http://setgetgo.com/randomword/get.php").text)
        onewordeachrecording = True
        onewordchannel = message.channel.name
        onewordeachbuffer = []
        onewordeachbuffer.append('```')
        await client.send_message(message.channel, word)
        onewordeachbuffer.append(word + ' ')

    elif message.content.startswith('!stop'):
        onewordeachbuffer.append('```')
        onewordeachrecording = False
        fullstory = ''.join(onewordeachbuffer)
        await client.send_message(message.channel, botmessages['storyend'])
        msg = await client.send_message(message.channel, fullstory)
        await client.pin_message(msg)
        onewordeachbuffer = []

    elif message.content.startswith('!fuckoff'):
        onewordeachrecording = False
        await client.send_message(message.channel, botmessages['storycancel'])
        onewordeachbuffer = []

    elif message.content.startswith('!update') and adminrole in message.author.roles:
        await client.send_message(message.channel, botmessages['updating'])
        gitout = subprocess.check_output(["git", "pull", "origin", "master"]).decode('UTF-8')
        await client.send_message(message.channel, gitout)
        await client.send_message(message.channel, botmessages['restart'])
        subprocess.Popen(['python3', './bot.py'])
        sys.exit(0)

    elif message.content.startswith('!version') and adminrole in message.author.roles:
        v = subprocess.check_output(["git", "describe", "--always"])
        await client.send_message(message.channel, botmessages['version'].format(v.decode('UTF-8')))

    else:
        if (onewordeachrecording and
                message.channel.name == onewordchannel and not
                username.startswith('owlbot')):
            onewordeachbuffer.append(message.content)
            onewordeachbuffer.append(' ')

        if not username in users:
            users[username] = {
                "links": 0,
                "not-links": 0,
                "linksinarow": 0,
                "warned": False
            }

        messagelinks = re.findall("http[s]?://", message.content)

        if message.content.startswith("!rep"):
            await client.send_message(message.channel, botmessages['myrep'].format(users[username]["links"], users[username]["not-links"]))

        elif message.content.startswith("!allrep") and adminrole in message.author.roles:
            output = ['```']
            for key, value in users.items():
                output.append(botmessages['allrep'].format(
                    key,
                    value["links"],
                    value["not-links"],
                    value["linksinarow"],
                    value["warned"]
                ))
            output.append('```')
            await client.send_message(message.channel, ''.join(output))

        elif message.content.startswith("!reset") and adminrole in message.author.roles:
            users = {}

        else:
            if not messagelinks:
                users[username]["not-links"] += 1
                users[username]["linksinarow"] = 0
                users[username]["warned"] = False

            else:
                users[username]["links"] += 1
                users[username]["linksinarow"] += 1

                if (users[username]["not-links"] > 0 and
                        (users[username]["links"] / users[username]["not-links"] > warnlinkratio)):
                    if (users[username]["links"] / users[username]["not-links"] > maxlinkratio):
                        if users[username]["linksinarow"] == linktrigger:
                            await client.send_message(message.channel, botmessages['linkwarn3'].format(message.author.mention, adminrole.mention))

                        elif users[username]["linksinarow"] >= linktrigger + 1:
                            if users[username]["warned"] == True:
                                await client.send_message(message.channel, botmessages['linkkick'].format(message.author.mention))
                                await client.kick(message.author)

                            else:
                                await client.send_message(message.channel, botmessages['linkwarn3'].format(message.author.mention, adminrole.mention))
                                users[username]["warned"] = True

                    else:
                        if users[username]["linksinarow"] == linktrigger:
                            await client.send_message(message.channel, botmessages['linkwarn1'].format(message.author.mention))

                        elif users[username]["linksinarow"] >= linktrigger + 1:
                            await client.send_message(message.channel, botmessages['linkwarn2'].format(message.author.mention))

                users[username]["lastmessage"] = "linked"


def get_weather():
    forecastdayname = calendar.day_name[(
        datetime.datetime.now() + datetime.timedelta(days=2)).weekday()]
    forecastday = (datetime.datetime.now() + datetime.timedelta(days=2)).day
    print(forecastday)
    r = requests.get(
        "http://api.wunderground.com/api/156083f0b1191a7a/hourly10day/q/gb/edinburgh.json")

    f = None

    for forecast in r.json()['hourly_forecast']:
        if (forecast['FCTTIME']['mday'] == str(forecastday)) and (forecast['FCTTIME']['hour'] == '18'):
            f = forecast

    rain = (f['qpf']['metric'] != '0')
    windspd = f['wspd']['metric']

    output = (forecastdayname + ' 18:00: ' +
              ('raining, ' if rain else 'not raining, ') +
              ('windy' if int(windspd) > 15 else 'not windy'))
    pprint.pprint(f)
    return str(output)


credfile = open("cred.txt", "r")
cred = str(credfile.read()).strip()
client.run(cred)
