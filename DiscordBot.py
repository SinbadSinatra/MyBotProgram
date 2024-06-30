import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import asyncio

TOKEN = 'insert-token'
API_KEY = 'insert-api-key'
CHANNEL_ID = 'channel'

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix='$', intents=intents)

player_scores = {}  # Dictionary to store player scores

class ConfirmationView(View):
    def __init__(self, ctx, score):
        super().__init__()
        self.ctx = ctx
        self.score = score

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        global dreidel_spinning
        dreidel_spinning = False
        # Saving data to persistent storage could be implemented here if needed
        await interaction.response.send_message("Data and scores successfully saved!", ephemeral=True)

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        global dreidel_spinning
        dreidel_spinning = False
        await interaction.response.send_message("Data not saved.", ephemeral=True)

    @discord.ui.button(label='Continue', style=discord.ButtonStyle.gray)
    async def continue_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        global dreidel_spinning
        dreidel_spinning = True  # Set dreidel_spinning back to True to resume
        await interaction.response.send_message("Game resumed!", ephemeral=True)
        # Restart the dreidel game
        await start_dreidel_game(self.ctx)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == '$hello':
        await message.channel.send(f'Hello, {message.author.mention}!')

    elif message.content.lower().startswith('$roll d20'):
        d20 = random.randint(1, 20)
        await message.channel.send(f'{message.author.mention} rolled a {d20}.')

    elif message.content.lower().startswith('$roll d6'):
        d6 = random.randint(1, 6)
        await message.channel.send(f'{message.author.mention} rolled a {d6}.')

    await bot.process_commands(message)

@bot.command()
async def myhelp(ctx):
    embed = discord.Embed(title="My Bot Commands", description="List of commands that the bot can perform.")
    embed.add_field(name="$rollD6", value="Rolls a D6.")
    embed.add_field(name="$rollD20", value="Rolls a D20.")
    embed.add_field(name="$dreidel", value="Spins a dreidel.")
    embed.add_field(name="$dreidel-status", value="Checks the stats of a player in the dreidel game.")
    embed.add_field(name="$8ball [question]", value="Generates answers for 8Ball.")
    embed.add_field(name="$stop", value="Ceases the dreidel game.")
    await ctx.send(embed=embed)

@bot.command(name="rollD6")
async def roll_d6(ctx):
    d6 = random.randint(1, 6)
    await ctx.send(f"You rolled a {d6}.")

@bot.command(name="rollD20")
async def roll_d20(ctx):
    d20 = random.randint(1, 20)
    await ctx.send(f"You rolled a {d20}.")

dreidel_spinning = False

async def start_dreidel_game(ctx):
    global dreidel_spinning
    pot = 1000
    await ctx.send(f"The initial value of the amount of coins in the pot is {pot}")

    global player_scores  # Access the global player_scores dictionary

    end_time = asyncio.get_running_loop().time() + 300
    while asyncio.get_running_loop().time() < end_time and dreidel_spinning:
        spins = ["נ (Nun)", "ג (Gimmel)", "ה (Hay)", "ש (Shin)"]
        spin = random.choice(spins)
        await ctx.send(f"You spun a {spin}.")

        if spin == "נ (Nun)":
            await ctx.send("Nothing.")
        elif spin == "ג (Gimmel)":
            await ctx.send(f"(1000 COINS) Take the whole pot. Total coins: {player_scores.get(ctx.author.name, 0) + 1000}")
            player_scores[ctx.author.name] = player_scores.get(ctx.author.name, 0) + 1000
            pot -= 1000
        elif spin == "ה (Hay)":
            await ctx.send(f"+1/2 nominal sum of coins (500 coins). Total coins: {player_scores.get(ctx.author.name, 0) + 500}")
            player_scores[ctx.author.name] = player_scores.get(ctx.author.name, 0) + 500
            pot -= 500
        else:
            await ctx.send(f"The odds are ever in favour of your misfortune, {ctx.author.name}.")
            await ctx.send(f"Total coins: {player_scores.get(ctx.author.name, 0) - 5}")
            player_scores[ctx.author.name] = player_scores.get(ctx.author.name, 0) - 5
            pot += 5

        await asyncio.sleep(2)

    if dreidel_spinning:
        winner = max(player_scores, key=player_scores.get)
        await ctx.send(f"The game has ended. The winner is {winner} with {player_scores[winner]} coins.")
    else:
        await ctx.send("The dreidel game has been stopped.")

    dreidel_spinning = False

@bot.command()
async def dreidel(ctx):
    global dreidel_spinning
    if dreidel_spinning:
        await ctx.send("A dreidel game is already in progress!")
        return

    dreidel_spinning = True
    await start_dreidel_game(ctx)

@bot.command(name="stop")
async def stop(ctx):
    global dreidel_spinning
    if dreidel_spinning:
        dreidel_spinning = False  # Stop the game
        score = player_scores.get(ctx.author.name, 0)
        view = ConfirmationView(ctx, score)
        await ctx.send(f"Do you want to save your score of {score} points?", view=view)
    else:
        await ctx.send("There is no dreidel game in progress to stop.")

@bot.command(name="dreidel-status")
async def dreidel_status(ctx):
    await ctx.send("Mention the user (@username) whose stats you want to check.")
    try:
        message = await bot.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.mentions) > 0)
        player = message.mentions[0]
        await ctx.send(f"Fetching data of {player.display_name}...")
        await asyncio.sleep(2)
        await ctx.send(f"Inspectee User: **{player.display_name}**\nScore since last played: **{player_scores.get(player.name, 0)} pts**")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond.")
    except IndexError:
        await ctx.send("No user mentioned. Please mention a user to check the stats.")

@bot.command(name="8ball")
async def eightball(ctx, *, question: str):
    responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
                 "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
                 "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
                 "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
                 "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
                 "Very doubtful."]
    response = random.choice(responses)
    await ctx.send(f"Question: {question}\nAnswer: {response}")

@bot.event
async def on_ready():
    print(f"Bot has been successfully established! Shard ID: {bot.shard_id}")
    chat = bot.get_channel(1069983788236550154)
    if chat is not None:
        await chat.send("Bot has been successfully launched!")
    else:
        print("Channel not found or bot does not have access to the channel.")
        for guild in bot.guilds:
            print(f"Guild: {guild.name} (ID: {guild.id})")
            for channel in guild.channels:
                print(f"Channel: {channel.name} (ID: {channel.id}) Type: {channel.type}")

bot.run(TOKEN)
