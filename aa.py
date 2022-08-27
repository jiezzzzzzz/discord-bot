import discord
from discord.ext import commands
import os
import json
import string
import sqlite3

bot = commands.Bot(command_prefix='!', intense=discord.Intents.all())


@bot.event
async def on_ready():
    print('я запустился')
    global base, cur
    base = sqlite3.connect('название.db')
    cur = base.cursor()
    if base:
        print('соединение с базой')



@bot.command()
async def test(ctx):
    await ctx.send('message')


@bot.event
async def on_message(message):
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(' ')}\
        .intersection(set(json.load(open('s.json')))) != set:
        await message.channel.send(f'{message.author.mention} сообщение')
        await message.delete()

        name = message.guild.name
        base.execute('CREATE TABLE IF NOT EXIST {} (userid INT, count INT)'.format(name))
        base.commit()

        warning = cur.execute('SELECT * FROM {} WHERE userid  == ?'.format(name), (message.author.id)\
                              .fetchone())
        if warning == None:
            cur.execute('INSERT INTO {} VALUES(?, ?)'.format(name), (1, message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention} первое предупреждение')

        elif warning[1] == 1:
            cur.execute('UPDATE {} SET count == ? WHERE userid == ?'.\
                        format(name), (2, message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention} второе предупреждение')

        elif warning[1] == 2:
            cur.execute('UPDATE {} SET count == ? WHERE userid == ?'.\
                        format(name), (3, message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention} забанен')
            await message.author.ban(reason='Нецензурные выражения')


@bot.command()
async def status(ctx):
    base.execute('CREATE TABLE IF NOT EXIST {} (userid INT, count INT)'.format(ctx.message.guild))
    base.commit()
    warning = cur.execute('SELECT * FROM {} WHERE userid = ?'.format(ctx.message.guild.name), (ctx.message.author.id).fetchone())
    if warning == None:
        await ctx.send(f'{ctx.message.author.mention} у вас нет предупреждений')
    else:
        await ctx.send(f'{ctx.message.author.mention} у вас {warning[1]} предупреждений')


@bot.event
async def on_member_join(member):
    await member.send('сообщение')
    for i in bot.get_guild(member.guild.id).channels:
        if i.name == 'название сервера':
            await bot.get_channel(i.id).send('поприветствуем его!')


@bot.event
async def on_member_remove(member):
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == 'название сервера':
            await bot.get_channel(ch.id).send(f'{member} плохо что ты ушел')


bot.run(os.getenv('TOKEN'))




