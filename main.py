from discord.ext.commands import Bot
import discord
from discord import Embed
import random, os, json
from discord.ext.commands import CommandNotFound
from googleapiclient.discovery import build
from numpy import diff
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from dotenv import load_dotenv

load_dotenv()

sns.set_style("whitegrid")
sns.set_palette("mako")

if not os.path.exists("Images"):
    os.mkdir("Images")


def getstacksearchresults(query):
    resource = build("customsearch", "v1", developerKey=os.environ["api_key"]).cse()
    out = resource.list(q=query, cx=os.environ["cse_key"]).execute()
    if items in out.keys():
        items = out["items"]
        print(items)
        embed = Embed(title=f'Results for "{query}"', color=discord.color.green())
        for i in range(4):
            try:
                embed.add_field(name=items[i]["title"], value=items[i]["link"])
                return embed
            except Exception:
                pass
    else:
        embed = Embed(title=f":warning: Status Code: WARNING", description="No results found")
        return embed

def get_problem(problems):
    randint = random.randint(0, len(problems))
    problem = problems[randint]
    title = problem[2]
    problem = problems[randint]
    link = f"https://codeforces.com/problemset/problem/{problem[0]}/{problem[1]}"
    return title, link


with open("problems.json", "r") as f:
    problems = json.loads(json.load(f))

client = Bot(command_prefix=">")
client.remove_command("help")

supported_commands = [">help", ">stacksearch", ">algorithm", ">barplot"]


@client.command()
async def help(ctx):

    embed = Embed(
        title="spartaKus - BETA",
        description="A Discord bot made to assist programmers. Creator of the bot: https://prmethus.github.io",
    )
    embed.add_field(name=">help", value="Show the supported commands and bot info.")
    embed.add_field(
        name=">stacksearch",
        value="Get solution to your problem from StachOverflow. Uses Google Custom Search API. \nExample: >stacksearch OSError Python",
    )
    embed.add_field(
        name=">algorithm",
        value="Uses Codeforces API to get Algorithmtic questions. Example: >algorithm medium\nSupported Difficulties: [easy, medium, hard]",
    )
    embed.add_field(
        name=">barplot",
        value="Creates a Bar Plot NOTE: THE y VALUES MUST BE NUMERIC. Example: >barplot Hello=123 World=150",
    )
    await ctx.send(content=ctx.author.mention, embed=embed)


@client.command()
async def algorithm(ctx, difficulty="easy"):

    difficulties = ["easy", "medium", "hard"]

    difficulty = difficulty.strip().lower()

    if not difficulty in difficulties:
        embed = Embed(
            title=":x: STATUS CODE: Error",
            description=f"The difficulty parameter got an invalid argument. \nSupported arguments: {difficulties}",
            color=discord.Color.red(),
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    else:
        title, link = get_problem(problems[difficulty])
        embed = Embed(title=title)
        embed.add_field(name="Difficulty", value=difficulty.capitalize())
        embed.add_field(name="URL", value=link)
        await ctx.send(content=ctx.author.mention, embed=embed)


@client.command()
async def stacksearch(ctx, *args):
    query = " ".join(args)
    embed = getstacksearchresults(query)
    await ctx.send(content=ctx.author.mention, embed=embed)


@client.command()
async def barplot(ctx, *args):
    try:
        dt = {}
        for arg in args:
            val = arg.split("=")
            dt[val[0]] = int(val[1])
        df = pd.DataFrame(dt, index=[0])
        sns.barplot(x=df.columns.tolist(), y=df.iloc[0])
        plt.ylabel("")
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.clf()
        buf.seek(0)
        image_file = discord.File(fp=buf, filename="barplot.png")
        embed = Embed(
            title=":white_check_mark: STATUS CODE: Successful",
            color=discord.Color.green(),
        )
        await ctx.send(content=ctx.author.mention, embed=embed, file=image_file)
    
    except Exception as e:
        print(e)
        embed = Embed(
            title=":x: STATUS CODE: Error",
            description="Is the data you entered valid?",
            color=discord.Color.red(),
        )
        await ctx.send(content=ctx.author.mention, embed=embed)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        pass


@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=">help")
    )


client.run(os.environ["TOKEN"])
