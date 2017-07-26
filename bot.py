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

    username = message.author.name

    if message.content.startswith('!droneweather'):
        await client.send_message(message.channel, get_weather())
    else:
        if not username in users:
            users[username] = {
                "links": 0,
                "not-links": 0,
                "linksinarow": 0,
                "warned": False
            }

        messagelinks = re.findall("http[s]?://",message.content)

        if message.content.startswith("!rep"):
            await client.send_message(message.channel, "You're sitting at " +
                str(users[username]["links"]) + " links, and " +
                str(users[username]["not-links"]) + " not-links.")
        elif message.content.startswith("!allrep"):
            output = ['```']
            for key, value in users.items():
                output.append(key+":\n")
                output.append("\tlinks: "+str(value["links"])+"\n")
                output.append("\tnotlinks: "+str(value["not-links"])+"\n")
                output.append("\tlinksinarow: "+str(value["linksinarow"])+"\n")
                output.append("\twarned: "+str(value["warned"])+"\n")
                output.append('\n')
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

                if (users[username]["not-links"] > 0
                and (users[username]["links"] / users[username]["not-links"] > warnlinkratio)):
                    if (users[username]["links"] / users[username]["not-links"] > maxlinkratio):
                        if users[username]["linksinarow"] == 2:
                            await client.send_message(message.channel, message.author.mention+" ALL YOU DO IS LINK, STAHP.  REEEEEEEEEEE " + adminrole.mention)

                        elif users[username]["linksinarow"] >= 3:
                            if users[username]["warned"] == True:
                                await client.send_message(message.channel, "kickin fuck outta " + message.author.mention)
                                await client.kick(message.author)
                                await client.send_message(message.channel, "so say we all")

                            else:
                                await client.send_message(message.channel, message.author.mention+", "+adminrole.mention+" arming kick button, you've been warned")
                                users[username]["warned"] = True

                    else:
                        if users[username]["linksinarow"] == 2:
                            await client.send_message(message.channel, "Hey "+message.author.mention+", watch that link spam boyo")

                        elif users[username]["linksinarow"] >= 3:
                            await client.send_message(message.channel, message.author.mention+" STAHP")

                users[username]["lastmessage"] = "linked"

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

credfile=open("cred.txt","r")
cred=str(credfile.read()).strip()
client.run(cred)
