import os
import random
from collections import Counter
import discord
from discord.ext import commands
from pysaucenao import SauceNao, PixivSource, BooruSource, AnimeSource, MangaSource, errors
from pybooru import Danbooru, exceptions
from pygelbooru import Gelbooru

class WeebImages(commands.Cog):
    embedColour = discord.Colour.from_rgb(241,199,209)

    def __init__(self, client):
        self.client = client

    @commands.command(brief = "Probably better than bread.", usage = "| optional*<query_tags>")
    @commands.cooldown(5, 300,commands.cooldowns.BucketType.user)
    async def wada(self,ctx,*tagsInput):
        danbooru = Danbooru('danbooru')

        tags = set(tag.lower() for tag in tagsInput)
        validTags = "" if any(x in tags for x in ['rating:safe','rating:questionable','rating:explicit']) else "rating:safe "
        invalidTags = ""
        for tag in tags:
            if danbooru.tag_related(query = tag.lstrip('~-'))['tags'] and tag.lstrip('~-') not in ['loli','shota','toddlercon']:
                validTags += f"{tag} "
            else:
                invalidTags += f"{tag}, "

        try:
            posts = danbooru.post_list(tags = validTags, random = True)
            filteredPosts = [post for post in posts if 'file_url' in post]
            for i in range(3):
                if not filteredPosts and posts:
                    posts = danbooru.post_list(tags = validTags, random = True)
                    filteredPosts = [post for post in posts if 'file_url' in post]
                else: 
                    break
        except exceptions.PybooruHTTPError: 
            filteredPosts = []

        if invalidTags:
            msg = f"Couldn't find these tags: ```{invalidTags.rstrip(', ')}```"
            for inapropriate in ['loli','shota','toddlercon']:
                if inapropriate in invalidTags:
                    msg += '\nALSO WTF!! NO PEDOPHILIA ALLOWED BAKAYARÔ!'
                    break
            await ctx.send(msg)
        elif not filteredPosts:
            await ctx.send("BAKAA! Your tags suck! Can't find anything!")
        else:
            post = random.choice(filteredPosts)

            fileURL = post['large_file_url'] if 'large_file_url' in post else post['file_url']

            if post['pixiv_id'] and 'bad_pixiv_id' not in post['tag_string_meta']:
                sourceURL = f"https://www.pixiv.net/en/artworks/{str(post['pixiv_id'])}"
            elif post['source'].startswith('https') and 'bad_id' not in post['tag_string_meta']:
                sourceURL = post['source']
            else:
                sourceURL = f"https://danbooru.donmai.us/posts/{post['id']}"

            postEmbed = discord.Embed(title = post['tag_string_artist'],url = sourceURL, colour = WeebImages.embedColour)

            material = post['tag_string_copyright'].replace(' ', ', ') if 'original' not in post['tag_string_copyright'] and post['tag_string_copyright'] else 'OC'
            postEmbed.add_field(name = "Material", value = material, inline = False)

            characters = post['tag_string_character'].replace(' ', ', ') if post['tag_string_character'] else "OC"
            postEmbed.add_field(name = "Characters", value = characters, inline = False)
            
            if fileURL.endswith('jpg') or fileURL.endswith('png') or fileURL.endswith('jpeg'):
                postEmbed.set_image(url = fileURL)
                await ctx.send(embed = postEmbed)
            else:
                await ctx.send(embed = postEmbed)
                await ctx.send(fileURL)

        danbooru = None

    @commands.command(brief = "Quick and clogging.", usage = "| optional*<query_tags>")
    async def cola(self,ctx,*tagsInput):
        gelbooru = Gelbooru(os.getenv('GEL_API'), os.getenv('GEL_ID'))

        tags = set(tag.lower() for tag in tagsInput)
        validTags = [] if any(x in tags for x in ['rating:safe','rating:questionable','rating:explicit']) else ["rating:safe"]
        invalidTags = []
        for tag in tags:
            valid = await gelbooru.random_post(tags = [tag])
            if valid:
                validTags.append(tag)
            else:
                invalidTags.append(tag)

        post = await gelbooru.random_post(tags=validTags)

        if invalidTags:
            msg = f"Couldn't find these tags: ```{', '.join(invalidTags)}```"
            await ctx.send(msg)
        elif not post:
            await ctx.send("BAKAA! Your tags suck! Can't find anything!")
        else:
            fileURL = post.file_url
            if fileURL.endswith('jpg') or fileURL.endswith('png') or fileURL.endswith('jpeg'):
                sourceURL = post.source if post.source else f'https://gelbooru.com/index.php?page=post&s=view&id={post.id}'
                site = getSiteName(sourceURL)
                postEmbed = discord.Embed(title = site, url = sourceURL, colour = WeebImages.embedColour)
                postEmbed.set_image(url = fileURL)
                await ctx.send(embed = postEmbed)
            else:
                await ctx.send(fileURL)

        gelbooru = None

    @commands.command(brief = "When da pasta isa dry.", usage = "| <image_url_or_attatchment>")
    async def sauce(self,ctx, URL = ""):
        try:
            sauce = SauceNao(api_key = os.getenv('SAUCE_API'),min_similarity = 70.0)
            imageURL = URL if URL.startswith("https://") else ctx.message.attachments[0].url
            results = await sauce.from_url(imageURL)

            author, authorURL = "", ""
            urls, authorTitles, material, characters = [], [], [], []
            for result in results:
                if isinstance(result,AnimeSource):
                    author  = getAnimeSauce(result, author, urls)
                elif isinstance(result,MangaSource):
                    author = getMangaSauce(result, author, urls)
                else:
                    author, authorURL = getImageSauce(author, authorURL, urls, authorTitles, material, characters)      

            if not author and authorTitles:
                authorTitles = Counter(authorTitles)
                author = authorTitles.most_common(1)[0][0]

            postEmbed = discord.Embed(title = f"Author: {author}", colour = WeebImages.embedColour)
            if authorURL:
                postEmbed.url = authorURL
            if material: 
                postEmbed.add_field(name = "Material", value = ", ".join(set(material)), inline = False)
            if characters: 
                postEmbed.add_field(name = "Characters", value = ", ".join(set(characters)), inline = False)
            postEmbed.add_field(name = "Sources", value = '\n'.join(urls))
            postEmbed.set_thumbnail(url = results[0].thumbnail)
            await ctx.send(embed = postEmbed)
                
            sauce = None
        except IndexError:
            await ctx.send("Couldn't find sauce. Must be some Wonderbread you got.")
        except errors.InvalidImageException:
            await ctx.send("What did you even send?")

    @commands.command(brief = "This is the good stuff.")
    @commands.cooldown(3, 30,commands.cooldowns.BucketType.user)
    async def sendhotpics(self,ctx):
        privateSelect = os.listdir('important files')
        expertRecommendation = str(random.choice(privateSelect))
        await ctx.send(file = discord.File(f"important files/{expertRecommendation}"))

def getSiteName(url):
        site = url.replace('https://','').replace('www.','')
        site = site[:site.index('/')]
        return site

async def getAnimeSauce(result, author, urls):
    await result.load_ids()
    author = result.title
    line = f'[myanimelist.net]({result.mal_url}) {result.similarity}%' if result.mal_url else f'[{getSiteName(result.url)}]({result.url}) {result.similarity}%'
    line += f'\nEp - {result.episode}, {result.timestamp}, {result.year}\n'
    urls.append(line)
    return author

def getMangaSauce(result, author, urls):
    if not author: 
        author = result.author_name
    site = getSiteName(result.url)
    urls.append( f'[{site}]({result.url}) {result.similarity}%\n{result.title} {result.chapter}\n')
    return author

def getImageSauce(result, author, authorURL, urls, authorTitles, material, characters):
    if result.urls:
        for url in result.urls:
            site = getSiteName(url)
            urls.append( f'[{site}]({url}) {result.similarity}%')

    if isinstance(result,PixivSource):
        authorURL = result.author_url
        author = result.author_name
    elif result.author_name:
        authorTitles += result.author_name.split(', ')

    if isinstance(result,BooruSource):
        material += result.material 
        characters += result.characters 
    else:
        if 'material' in result.data:
            material += result.data['material'].split(', ')
        if 'characters' in result.data:
            characters += result.data['characters'].split(', ')

    return author, authorURL

def setup(client):
    client.add_cog(WeebImages(client))