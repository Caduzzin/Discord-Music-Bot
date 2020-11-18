from discord.ext import commands
import discord
import asyncio
import youtube_dl
import asyncio
import urllib.request
import re
import secreto

client = commands.Bot(command_prefix='?',
                      case_insensitive=True, status=discord.Status.idle)


@client.event

# function to warn that the bot is on

async def on_ready():
    print('BOT ONLINE - OLÁ MUNDO!')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="uma música..."))


@client.command(pass_context=True)

# function for the bot to enter the voice channel you are

async def entrar(ctx):
    try:
        canal = ctx.author.voice.channel
        await canal.connect()
    except AttributeError:
        channel = ctx.channel
        await channel.send("Você precisa estar conectado a um canal de voz!")


@client.command(pass_context=True)

# function for the bot to leave the voice channel

async def sair(ctx):
    server = ctx.message.guild.voice_client
    await server.disconnect()


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ydl = youtube_dl.YoutubeDL({
            'format': 'bestaudio/best',
            'quiet': 'true',
            'outtmpl': 'OneDrive/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        })
        self.queue = None

    # function to search for music on youtube

    def search_youtube(self, query):
        html = urllib.request.urlopen(
            "https://www.youtube.com/results?search_query=" + query)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        return "https://www.youtube.com/watch?v=" + video_ids[0]

    # function to start music
    @client.command(name='play', help='play music')
    async def play(self, song):

        # download music in you computer

        ydl = youtube_dl.YoutubeDL({
            'format': 'bestaudio/best',
            'quiet': 'true',
            'outtmpl': 'OneDrive/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        })

        loop = asyncio.get_event_loop()
        voice_channel = ""
        try:
            voice_channel = self.author.voice.channel
        except:
            await self.send(":notes: Entre em um canal de voz!")
            return

        voice = self.channel.guild.voice_client
        url = Music.search_youtube(self, song.replace(" ", "+"))
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url=url, download=True))
        if 'entries' in data:
            data = data['entries'][0]

        await self.send(f':notes: Adicionado a fila: **{data["title"]}**')

        filename = ydl.prepare_filename(data)

        if voice is None:
            voice = await voice_channel.connect()

        if voice.channel.id != voice_channel.id:
            await voice.move_to(voice_channel)

        await self.send(f':notes: Tocando: **{data["title"]}**')
        voice.play(discord.FFmpegPCMAudio(
            executable=r"C:\\Users\\Usuario\\Documents\\Projects\\src\\ffmpeg.exe", source=filename))

    @client.command(name='stop', help='stop music', )

    # function to stop music
    async def stop(ctx):
        voice = ctx.channel.guild.voice_client
        voice.stop()
        await ctx.send('**:notes: Ok, parou de tocar!!**')


def setup(bot):
    bot.add_cog(Music(bot))
    print('Music bot loaded.')


token = secreto.otoken()
client.run(token)
