import discord
from discord.ui import Button, View
from discord.ext import tasks, commands
import os
from random import randint, shuffle, random
import random
from peewee import *
import requests
from bs4 import BeautifulSoup
import asyncio

bot = discord.Bot()
db = SqliteDatabase('database/database.sqlite')

class Guilds(Model):
    user_name = IntegerField()
    user_xp = IntegerField()
    guild_id = IntegerField()

    class Meta:
        database = db

class Servers(Model):
    guild_name = TextField()

    class Meta:
        database = db

async def update_activity():
    while True:
        servers_count = Servers.select(fn.Count(Servers.guild_name)).scalar()
        await bot.change_presence(activity=discord.Game(name=f'/help | Servers: {servers_count}'))
        await asyncio.sleep(3600)  # Затримка 3600 секунд (1 година)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    bot.loop.create_task(update_activity())
    # await bot.change_presence(activity=discord.Game(name=f'/help | Servers: {Servers.select(fn.Count(Servers.guild_name)).scalar()}'))

@bot.event
async def on_guild_join(guild):
    Servers.create(guild_name=guild.name)

@bot.event
async def on_guild_remove(guild):
    Servers.delete().where(Servers.guild_name == guild.name).execute()

@bot.slash_command(name='help', description='Use, that see all commands')
async def help(ctx):
    embed = discord.Embed(
        title="Commands:",
        description="""
        `/ping` - Latency of the bot
        `/roll` - Random number from 1 to 100
        `/message` - You can send anonymously message to someone
        `/leaderboard` - The best 3 people on leaderboard
        `/xp` - Your xp
        `/userinfo` - Gets info about a user
        `/google` - Search information in Google
        `/weather` - See the weather in all world
        `/xkcd` - Random comics from xkcd.com
        `/8ball` - Ask the magik 8ball a questions
        `/games` - See all games
        `/suggest` - Community ideas for this bot
        `/support` - Support the bot author""",
        color=discord.Color.random()
    )
 
    await ctx.respond(embed=embed)

@bot.slash_command(name='weather', description='See the weather in all world')
async def weather(ctx, *, location):
    api_key = '904a4e1652b455eeb21929452738bd7d'  # Підставте сюди свій API ключ з OpenWeatherMap
    base_url = 'http://api.openweathermap.org/data/2.5/weather?'

    complete_url = f"{base_url}q={location}&appid={api_key}&units=metric"

    response = requests.get(complete_url)
    data = response.json()

    embed_2 = discord.Embed(
        title='I did not find such a place',
        description="",
        color=discord.Color.random()
    )

    if data['cod'] == '404':
        await ctx.respond(embed=embed_2)

    city_name = data['name']
    weather_desc = data['weather'][0]['description']
    temp = data['main']['temp']
    humidity = data['main']['humidity']

    weather_info = f"Weather in {city_name}: {weather_desc}\nTemperature: {temp}°C\nHumidity: {humidity}%"
    embed = discord.Embed(
        title=f'Weather in {city_name}: {weather_desc}',
        description=f"Temperature: {temp}°C\nHumidity: {humidity}%",
        color=discord.Color.random()
    )
    await ctx.respond(embed=embed)

@bot.slash_command(name='ping', description='Latency of the bot')
async def ping(ctx):
    ping = bot.ws.latency
    embed = discord.Embed(
        title=f'Pong! `{ping * 1000:.0f}ms` :ping_pong:',
        description="",
        color=discord.Color.random()
    )
    await ctx.respond(embed=embed)

@bot.slash_command(name='roll', description='Random number from 1 to 100')
async def roll(ctx):
    embed = discord.Embed(
        title="Roll",
        description=f"{randint(1, 100)}",
        color=discord.Color.random()
    )
    await ctx.respond(embed=embed)

@bot.slash_command(name='message', description='You can send anonymously message to someone')
async def message(ctx, user: discord.User, text: str):
    embed = discord.Embed(
        title="The messsage was sended",
        description="",
        color=discord.Color.random()
    )
    embed_2 = discord.Embed(
        title="Anonymously message to you:",
        description=text,
        color=discord.Color.random()
    )
    await user.send(embed=embed_2)
    await ctx.respond(embed=embed)

@bot.slash_command(name='xp', description='Your xp')
async def xp(ctx, user: discord.User):
    try:
        guild = user.guild
        guild_name = guild.name
        guild_id = guild.id
        embed = discord.Embed(
            title="User xp:",
            description=f"{read_from_user_db(user.id, guild_id).user_xp}",
            color=discord.Color.random()
        )
        await ctx.respond(embed=embed)
    except:
        guild = user.guild
        guild_name = guild.name
        guild_id = guild.id
        embed = discord.Embed(
            title="User xp:",
            description="0",
            color=discord.Color.random()
        )
        await ctx.respond(embed=embed)


@bot.slash_command(name='leaderboard', description='The best 3 people on leaderboard')
async def leaderboard(ctx):
    guild = ctx.guild
    guild_name = guild.name
    guild_id = guild.id
    users_xp_list = list()
    for user in read_all_users_from_one_guild(guild_id):
        users_xp_list.append([user.user_name, user.user_xp])
    sorted_data = sorted(users_xp_list, key=lambda x: x[1], reverse=True)
    try:
        embed = discord.Embed(
            title="Leaderboard",
            description=f"1.<@{sorted_data[0][0]}> - {sorted_data[0][1]}\n2.<@{sorted_data[1][0]}> - {sorted_data[1][1]}\n3.<@{sorted_data[2][0]}> - {sorted_data[2][1]}",
            color=discord.Color.random()
        )
    except:
        try:
            embed = discord.Embed(
                title="Leaderboard",
                description=f"1.<@{sorted_data[0][0]}> - {sorted_data[0][1]}\n2.<@{sorted_data[1][0]}> - {sorted_data[1][1]}\n3.Nobody",
                color=discord.Color.random()
            )
        except:
            try:
                embed = discord.Embed(
                    title="Leaderboard",
                    description=f"1.<@{sorted_data[0][0]}> - {sorted_data[0][1]}\n2.Nobody\n3.Nobody",
                    color=discord.Color.random()
                )
            except:
                embed = discord.Embed(
                    title="Leaderboard",
                    description=f"1.Nobody\n2.Nobody\n3.Nobody",
                    color=discord.Color.random()
                )
    await ctx.respond(embed=embed)

@bot.slash_command(name="userinfo", description="Gets info about a user.")
async def userinfo(ctx: discord.ApplicationContext, user: discord.Member = None):
    user = (
        user or ctx.author
    )  # If no user is provided it'll use the author of the message
    embed = discord.Embed(
        fields=[
            discord.EmbedField(name="ID", value=str(user.id), inline=False),  # User ID
            discord.EmbedField(
                name="Created",
                value=discord.utils.format_dt(user.created_at, "F"),
                inline=False,
            ),  # When the user's account was created
        ],
    )
    embed.set_author(name=user.name)
    embed.set_thumbnail(url=user.display_avatar.url)

    if user.colour.value:  # If user has a role with a color
        embed.colour = user.colour

    if isinstance(user, discord.User):  # Checks if the user in the server
        embed.set_footer(text="This user is not in this server.")
    else:  # We end up here if the user is a discord.Member object
        embed.add_field(
            name="Joined",
            value=discord.utils.format_dt(user.joined_at, "F"),
            inline=False,
        )  # When the user joined the server

    await ctx.respond(embeds=[embed])  # Sends the embed

@bot.slash_command(name='support', description='Support the bot author')
async def support(ctx):
    support_embed = discord.Embed(
        title='Support the Author',
        description='You can support the bot author by donating to their PayPal account.',
        color=discord.Color.random()
    )
    support_embed.add_field(
        name='PayPal',
        value='[Donate Here](https://www.paypal.com/donate/?hosted_button_id=6V7YR4M8R9GF2)'
    )
    await ctx.respond(embed=support_embed)

import requests

# @bot.slash_command(name='meme', description='Generate a meme')
# async def meme(ctx):
#     url = "https://ronreiter-meme-generator.p.rapidapi.com/meme"

#     querystring = {
#         "top": "Top Text",
#         "bottom": "Bottom Text",
#         "meme": "Condescending-Wonka",
#         "font_size": "50",
#         "font": "Impact"
#     }

#     headers = {
#         "X-RapidAPI-Key": "529db806d7mshf647499ca507ea4p1413edjsnd8e908396cc2",
#         "X-RapidAPI-Host": "ronreiter-meme-generator.p.rapidapi.com"
#     }

#     response = requests.get(url, headers=headers, params=querystring)

#     # Check if the request was successful (status code 200)
#     if response.status_code == 200:
#         try:
#             # json_data = response.json()
#             # meme_image_file = discord.File(response.content, filename="meme.jpg")
#             # embed = discord.Embed(
#             #     title='Your meme:',
#             #     description='',
#             #     color=discord.Color.random()
#             # )
#             # embed.set_image(url="attachment://meme.jpg")
#             # ctx.respond(embed=embed, file=meme_image_file)
#             # print(json_data)
#             file = discord.File(response.content, filename='meme.jpg')

#             # Create the embed with the file attachment
#             embed = discord.Embed(title='Your meme:', description='')
#             embed.set_image(url='attachment://meme.jpg')

#             # Send the embed with the attached image
#             await ctx.send(file=file, embed=embed)
#         except requests.exceptions.JSONDecodeError as e:
#             print("Error decoding JSON response:", e)
#             print("Raw response content:", response.content)
#             # embed = discord.Embed(
#             #     title='Your meme:',
#             #     description='',
#             #     color=discord.Color.random()
#             # )
#             # embed.set_image(response.content)
#             # ctx.respond(embed=embed)
#     else:
#         print("Request failed with status code:", response.status_code)
#         print("Raw response content:", response.content)

@bot.slash_command(name='google', description='Search information in Google')
async def google(ctx, *, query: str):
    api_key = 'AIzaSyCuopenRPft8TOjP7DOuZ3_jjzlGHiQFUc'  # Замените на ваш ключ API Google Custom Search
    search_engine_id = '179af0d047e444a3e'  # Замените на ваш идентификатор поисковой системы Google

    url = f'https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}'
    response = requests.get(url).json()

    if 'items' in response:
        search_results = response['items']
        result_count = min(len(search_results), 5)  # Ограничиваем количество результатов до 5

        embed = discord.Embed(title='Result of Google searching', color=0x00ff00)
        for i in range(result_count):
            result = search_results[i]
            title = result['title']
            link = result['link']
            snippet = result['snippet']
            embed.add_field(name=f'Result {i+1}', value=f'**[{title}]({link})**\n{snippet}', inline=False)

        await ctx.respond(embed=embed)
    else:
        await ctx.respond('Nothink searched')

@bot.slash_command(name='suggest', description='Community ideas for this bot')
async def suggest(ctx, *, text):
    embed = discord.Embed(
        title='Your offer has been successfully sent',
        description=text,
        color=discord.Color.random()
    )
    embed_2 = discord.Embed(
        title=f'Offer from {ctx.author}:',
        description=text,
        color=discord.Color.random()
    )
    user_id = 961544577494450207
    user = await bot.fetch_user(user_id)

    if user:
        await user.send(embed=embed_2)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("Error")

@bot.slash_command(name='8ball', description='Ask the magik 8ball a questions')
async def ball8(ctx, question):
    answer = str()
    number = randint(1,4)
    if number == 1:
        answer = 'Yes'
    elif number == 2:
        answer = 'No'
    elif number == 3:
        answer = 'Maybe'
    else:
        answer = 'I think, you can'
    embed = discord.Embed(
        title='8ball',
        description=f'<@{ctx.user.id}>: {question}\n8ball: {answer}',
        color=discord.Color.random()
    )
    await ctx.respond(embed=embed)

@bot.slash_command(name='xkcd', description='Random comics from xkcd.com')
async def xkcd(ctx):
    comics_number = randint(1, 2800)
    session = requests.session()
    resp = session.get(f'https://xkcd.com/{comics_number}/info.0.json').json()
    embed = discord.Embed(
        title='Xkcd comics',
        description='',
        color=discord.Color.random()
        )
    embed.set_image(url=resp['img'])
    await ctx.respond(embed=embed)

@bot.slash_command(name='games', description='See all games')
async def games(ctx):
    embed = discord.Embed(
        title="Games:",
        description="""
        `/cubes` - Fight with other users on your xp""",
        color=discord.Color.random()
        )
    await ctx.respond(embed=embed)

@bot.slash_command(name='cubes', description='Fight with other users on your xp')
async def cubes(ctx, user: discord.User, points: int):
    author = ctx.author
    guild = ctx.guild
    guild_name = guild.name
    guild_id = guild.id
    user_info = read_from_user_db(author.id, guild_id)
    enemy_info = read_from_user_db(user.id, guild_id)
    embed = discord.Embed(
        title="You don't have enough xp to play",
        description='',
        color=discord.Color.random()
        )
    if user_info.user_xp < points:
        await ctx.respond(embed=embed)
    elif enemy_info.user_xp < points:
        embed.title = f"`{str(user).replace('#0', '')}` don't have enough xp to play"
        await ctx.respond(embed=embed)
    else:
        yes_b = Button(style=discord.ButtonStyle.green, label="Yes", custom_id="cubes_yes")
        no_b = Button(style=discord.ButtonStyle.red, label="No", custom_id="cubes_no")
        view = View()
        view.add_item(yes_b)
        view.add_item(no_b)
        embed.title = 'Cubes'
        embed.description = f"Offer to <@{user.id}> was sended"
        await ctx.respond(embed=embed)
        embed.description = f"<@{ctx.user.id}> from `{ctx.guild.name}` sent you to play cubes on {points} xp.\nYour xp: {enemy_info.user_xp}"
        await user.send(embed=embed, view=view)
        async def button_callback_yes(interaction):
            author_number = randint(1, 6)
            enemy_number = randint(1, 6)
            if author_number > enemy_number:
                embed.title = 'Cubes'
                embed.description = f'<@{ctx.user.id}>, you got {author_number}.\nYour enemy got: {enemy_number}.\nYou won {points} xp!'
                author_db = read_from_user_db(author.id, guild_id)
                author_db.user_xp += int(points)
                author_db.save()

                enemy_db = read_from_user_db(user.id, guild_id)
                enemy_db.user_xp -= int(points)
                enemy_db.save()

                await ctx.send(embed=embed)
                embed.description = f'You got {enemy_number}.\nYour enemy got: {author_number}.\nYou lost {points} xp!'
                await user.send(embed=embed)
            else:
                embed.description = f'<@{ctx.user.id}>, you got {author_number}.\nYour enemy got: {enemy_number}.\nYou lost {points} xp!'
                author_db = read_from_user_db(author.id, guild_id)
                author_db.user_xp -= int(points)
                author_db.save()

                enemy_db = read_from_user_db(user.id, guild_id)
                enemy_db.user_xp += int(points)
                enemy_db.save()

                await ctx.send(embed=embed)
                embed.description = f'You got {enemy_number}.\nYour enemy got: {author}.\nYou won {points} xp!'
                await user.send(embed=embed)
        async def button_callback_no(interaction):
            embed.title = 'Cubes'
            embed.description = f'<@{ctx.user.id}>, your opponent refused to play'
            await ctx.respond(embed=embed)
            embed.description = 'You refused to play'
            await user.send(embed=embed)

        yes_b.callback = button_callback_yes
        no_b.callback = button_callback_no

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    author = message.author
    guild = message.guild
    guild_name = guild.name
    guild_id = guild.id

    write_to_database(author.id, guild_id)

def write_to_database(author, guild_id):
    if read_from_user_db(author, guild_id) != None:
        obj = read_from_user_db(author, guild_id)
        obj.user_xp += 1
        obj.save()
    else:
        Guilds.create(user_name=author, user_xp=1, guild_id=guild_id)

def read_from_user_db(author, guild_id):
    user_inf = Guilds.get_or_none((Guilds.user_name == author) & (Guilds.guild_id == guild_id))
    return user_inf

def read_all_users_from_one_guild(guild_id):
    all_users = Guilds.select().where(Guilds.guild_id == guild_id)
    return all_users

try:
    Guilds.create_table()
except:
    pass


try:
    Servers.create_table()
except:
    pass

# bot.run(os.getenv('TOKEN'))
bot.run('MTEyOTUxNzUwOTk3NzA2Nzc0MQ.G8wMGj.GcDH30hq4_QuNg2EEzqCDiucShD1jvDuHZT47Y')