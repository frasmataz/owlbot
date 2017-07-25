import discord
import asyncio
import requests
import datetime
import calendar
import json
import pprint
import re

linksinarowtotrigger = 2
warnlinkratio = 0.2
maxlinkratio = 0.6
client = discord.Client()
users = {}

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    global users
    for role in message.server.roles:
        if role.name == 'admin':
            adminrole = role

    if message.content.startswith('!droneweather'):
        await client.send_message(message.channel, get_weather())
    else:
        if not message.author.name in users:
            users[message.author.name] = {
                "linkedmessages": 0,
                "unlinkedmessages": 0,
                "linksinarow": 0
            }

        messagelinks = re.findall("http[s]?://",message.content)

        if message.content.startswith("!rep"):
            await client.send_message(message.channel, "You're sitting at " +
                str(users[message.author.name]["linkedmessages"]) + " links, and " +
                str(users[message.author.name]["unlinkedmessages"]) + " not-links.")
        elif message.content.startswith("!reset") and adminrole in message.author.roles:
            users = {}
        else:
            if not messagelinks:
                users[message.author.name]["unlinkedmessages"] += 1
                users[message.author.name]["linksinarow"] = 0
                users[message.author.name]["warned"] = False
            else:
                users[message.author.name]["linkedmessages"] += 1
                users[message.author.name]["linksinarow"] += 1
                if (users[message.author.name]["unlinkedmessages"] > 0
                and (users[message.author.name]["linkedmessages"] / users[message.author.name]["unlinkedmessages"] > warnlinkratio)):
                    if (users[message.author.name]["linkedmessages"] / users[message.author.name]["unlinkedmessages"] > maxlinkratio):
                        if users[message.author.name]["linksinarow"] == 2:
                            await client.send_message(message.channel, message.author.mention+" ALL YOU DO IS LINK, STAHP.  REEEEEEEEEEE " + adminrole.mention)
                        elif users[message.author.name]["linksinarow"] >= 3:
                            if users[message.author.name]["warned"] == True:
                                await client.send_message(message.channel, "kickin fuck outta " + message.author.mention)
                                await client.kick(message.author)
                                await client.send_message(message.channel, "so say we all")
                            else:
                                await client.send_message(message.channel, message.author.mention+", "+adminrole.mention+" arming kick button, you've been warned")
                                users[message.author.name]["warned"] = True
                    else:
                        if users[message.author.name]["linksinarow"] == 2:
                            await client.send_message(message.channel, "Hey "+message.author.mention+", watch that link spam boyo")
                        elif users[message.author.name]["linksinarow"] >= 3:
                            await client.send_message(message.channel, message.author.mention+" STAHP")

                users[message.author.name]["lastmessage"] = "linked"

def get_weather():
    forecastdayname = calendar.day_name[(datetime.datetime.now() + datetime.timedelta(days=2)).weekday()]
    forecastday = (datetime.datetime.now() + datetime.timedelta(days=2)).day
    print(forecastday)
    r = requests.get("http://api.wunderground.com/api/156083f0b1191a7a/hourly10day/q/gb/edinburgh.json")

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

client.run('MzE2NTc4MDE0Mzk5ODIzODcy.DEGnGw.2pygp0pUFXbD01OD73gh6LuibGw')
