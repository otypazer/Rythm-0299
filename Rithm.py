import discord
import asyncio
import time
import youtube_dl
from random import*
from discord.ext import commands
default_intents = discord.Intents.default()
default_intents.members = True
client = discord.Client(intents=default_intents)
ytdl = youtube_dl.YoutubeDL()



#=============================================================== Class Musique ===============================================================#

class Musique :
    def __init__(self):
        self.client = -1
        self.Playlist = []              # Url des musiques
        self.playlist = []              # Noms des musiques
        self.EnTrainDeJouer = False
    def init(self, client):
        self.client = client
    def JouerMusique(self, ctx = []):
        Recherche = getLink(ctx)
        if Recherche :
            self.Playlist += [Recherche]
            self.playlist += [getTitre(Recherche)]
        if self.client != -1 :
            if self.Playlist != []:
                if self.EnTrainDeJouer == False :
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(getUrl(self.Playlist[0]), executable="C:/ffmpeg/bin/ffmpeg.exe", before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
                    self.client.play(source, after=lambda x: self.BoucleMusique())
                    del self.Playlist[0]
                    del self.playlist[0]
                    self.EnTrainDeJouer = True
    def BoucleMusique(self):
        self.EnTrainDeJouer = False
        self.JouerMusique()
    def Suivante(self):
        self.client.stop()
    def Pause(self):
        self.client.pause()
    def Reprendre(self):
        self.client.resume()
    def JouerMaintenant(self, ctx):
        self.Playlist.insert(0, getLink(ctx))
        self.playlist.insert(0, getTitre(getLink(ctx)))
        self.client.stop()
    def JouerPl(self, ctx):
        self.Playlist += [LirePl(ctx)]
        self.playlist += [getTitre(LirePl(ctx))]


        

#Déclaration des variables
musique = Musique()
vclient = -1

#========================================================= Définitions des fonctions =========================================================#

def getUrl(link):
    return (ytdl.extract_info(link, download=False)["formats"][0])["url"]

def getLink(Recherche):
    if len(Recherche) > 1 :
        try :
            video = ytdl.extract_info(Recherche[1], download=False)
            return Recherche[1]
        except :
            recherche = ""
            for mot in Recherche[1:len(Recherche)+1] :
                recherche += mot + " "
            return (ytdl.extract_info("ytsearch:" + recherche, download=False)["entries"][0])["webpage_url"]
    else :
        return False

def getTitre(link):
    return (ytdl.extract_info(link, download = False).get('title', 0))

def getDuree(link):
    return (ytdl.extract_info(link, download = False).get('duration', 0))

def getArtiste(link):
    return (ytdl.extract_info(link, download = False).get('uploader', 0))

def getMiniature(link):
    return (ytdl.extract_info(link, download = False).get('thumbnail', 0))

def Duree(link):
    heures = getDuree(link)//3600
    minutes = getDuree(link)//60
    minutes2 = minutes - heures*60
    secondes = getDuree(link)%60
    if minutes == 0 and heures == 0 :
        return str(secondes) + " secondes"
    elif heures == 0 :
        return str(minutes) + " minutes " + str(secondes) + " secondes"
    return str(heures) + " heure(s) " + str(minutes2) + " minute(s) " + str(secondes) + " secondes"

def EmbedLecture(link):
    embedLecture = discord.Embed(title = '**En cours de lecture :**', description = getTitre(link))
    embedLecture.add_field(name = 'Le lien :', value = link, inline = False)
    embedLecture.set_thumbnail(url = getMiniature(link))
    embedLecture.add_field(name = 'Artiste :', value = getArtiste(link))
    embedLecture.add_field(name = 'Durée :', value = Duree(link))
    return embedLecture

def EmbedPlaylist():
    liste_musiques = musique.playlist
    ListeMusiques = ""
    for musiques in liste_musiques :
        ListeMusiques = ListeMusiques + musiques + " \n"
    return discord.Embed(title = '**Playlist :**', description = ListeMusiques)

def LirePl(fichier):
    FichierPl = open(fichier, 'r')
    Pl = FichierPl.read().split(",")
    FichierPl.close()
    return Pl

#============================================================== Le "on_ready" ================================================================#

@client.event
async def on_ready():
    print("Rithm v.4 lancé")

#============================================================== Les commandes ================================================================#

@client.event
async def on_message(message):
    ctx = message.content.split()
    ctx[0] = ctx[0].lower()
    
#Variables globales :
    
    global musique
    global vclient

#Pour éviter des bugs :

    if message.author == 'Rithm#0299':
        return
    if message.content == '':
        return

#Commandes :

    if ctx[0] == '?help':
        return

    if ctx[0] == '?p':
        await message.delete()
        vclient = message.guild.voice_client
        if not vclient.is_paused():
            musique.Pause()
            await message.channel.send(f"""Musique en **pause**.""")
            print('*** PAUSE ***')

    if ctx[0] == '?r':
        await message.delete()
        vclient = message.guild.voice_client
        if vclient.is_paused():
            musique.Reprendre()
            await message.channel.send(f"""La musique **reprend**.""")
            print('*** REPREND ***')

    if ctx[0] == '?pl':
        await message.delete()
        if musique.playlist !=  []:
            await message.channel.send(embed = EmbedPlaylist())
        else :
            await message.channel.send(f"""**La playlist est vide.**""")

    if ctx[0] == '?s':
        await message.delete()
        musique.Suivante()
        await message.channel.send(f"""Musique **passée**.""")
        print('*** MUSIQUE PASSEE   ***')

    if ctx[0] == '?jm':
        await message.delete()
        await message.channel.send(embed = EmbedLecture(getLink(ctx)))
        musique.JouerMaintenant(ctx)
        
    if ctx[0] == '?j':
        await message.delete()
        try :
            channel = message.author.voice.channel
        except :
            await message.channel.send(f"""Vous n'êtes pas connecté(e) dans un salon.""")
        try :
            vclient = await channel.connect()
        except :
            pass
        if musique.EnTrainDeJouer == False :
            await message.channel.send(embed = EmbedLecture(getLink(ctx)))
        else :
            await message.channel.send(f""":musical_note:  _**{getTitre(getLink(ctx))}**_  :musical_note: ajouté à la playlist.""")
        musique.init(vclient)
        musique.JouerMusique(ctx)

    if ctx[0] == '?pt':
        await message.delete()
        try :
            channel = message.author.voice.channel
        except :
            await message.channel.send(f"""Vous n'êtes pas connecté(e) dans un salon.""")
        try :
            vclient = await channel.connect()
        except :
            pass
        musique.JouerPl(ctx[1] + '.txt')

            

    if ctx[0] == '?ping':
        await message.delete()
        ping = round(client.latency * 1000)
        await message.channel.send(f"""Le **ping** est de : {ping} ms.""")


    if ctx[0] == '!blm':
        await message.channel.send("Bot Lives Matter !!!")

client.run ("ODMyNzEzNzM0NTgwMzM4Njg4.YHnzGQ.OltnCDDEN75qA_6Sk99W6jEaurE")




                             
