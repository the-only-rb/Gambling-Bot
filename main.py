import discord
from discord import app_commands
from discord.ext import commands
import random
import datetime

# Initiates the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Keeps user balances and stock in memory
user_balances = {}
last_earn_time = {}
stock = 10000  # Initial stock of points available to win

# Admin role ID
ADMIN_ROLE_ID = 1320128307987087381  # Replace with your actual admin role ID

# Helper function: Add points
def add_points(user_id, amount):
    if user_id not in user_balances:
        user_balances[user_id] = 0
    user_balances[user_id] += amount

# Helper function: Subtract points
def subtract_points(user_id, amount):
    if user_id not in user_balances:
        user_balances[user_id] = 0
    user_balances[user_id] -= amount

# Helper function: Get user balance
def get_balance(user_id):
    return user_balances.get(user_id, 0)

# Helper function: Adjust stock
def adjust_stock(amount):
    global stock
    stock += amount

# Check if user is admin
def is_admin(user):
    return any(role.id == ADMIN_ROLE_ID for role in user.roles)

# Slash command: Check balance
@bot.tree.command(name="balance", description="Check your balance")
async def balance(interaction: discord.Interaction):
    user = interaction.user
    balance = get_balance(user.id)
    await interaction.response.send_message(f"💰 {user.mention} has {balance} points!", ephemeral=True)

# Slash command: Earn points (once per day)
@bot.tree.command(name="earn", description="Earn points (once per day)")
async def earn(interaction: discord.Interaction):
    user = interaction.user
    now = datetime.datetime.now()

    if user.id in last_earn_time:
        last_used = last_earn_time[user.id]
        time_difference = now - last_used
        if time_difference.total_seconds() < 86400:  # 24 hours in seconds
            remaining_time = 86400 - time_difference.total_seconds()
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            await interaction.response.send_message(
                f"❌ You can use `/earn` again in {hours} hour(s) and {minutes} minute(s).",
                ephemeral=True
            )
            return

    points = random.randint(20, 150)
    adjust_stock(-points)  # Deduct points from stock
    add_points(user.id, points)
    last_earn_time[user.id] = now
    await interaction.response.send_message(
        f"🎉 Congratulations {user.mention}, you earned {points} points! You can earn more tomorrow.",
        ephemeral=True
    )

# Slash command: Coin flip game
@bot.tree.command(name="coinflip", description="Gamble your points on a coinflip!")
@app_commands.describe(bet="How many points to bet?", choice="heads or tails?")
async def coinflip(interaction: discord.Interaction, bet: int, choice: str):
    user = interaction.user
    balance = get_balance(user.id)

    if bet <= 0 or balance < bet or choice.lower() not in ["heads", "tails"]:
        await interaction.response.send_message("❌ Invalid bet or choice!", ephemeral=True)
        return

    result = random.choice(["heads", "tails"])
    if result == choice.lower():
        winnings = int(bet * 1.5)
        add_points(user.id, winnings - bet)
        adjust_stock(-winnings)
        await interaction.response.send_message(
            f"🎉 It's {result}! {user.mention} won {winnings} points! Your new balance is {get_balance(user.id)} points!",
            ephemeral=True
        )
    else:
        add_points(user.id, -bet)
        adjust_stock(bet)
        await interaction.response.send_message(
            f"😔 It's {result}. {user.mention} lost {bet} points. Your new balance is {get_balance(user.id)} points.",
            ephemeral=True
        )

# Slash command: Dice roll
@bot.tree.command(name="diceroll", description="Gamble your points with dice roll!")
@app_commands.describe(bet="Points to bet", guess="Your guess (1-6)")
async def diceroll(interaction: discord.Interaction, bet: int, guess: int):
    user = interaction.user
    balance = get_balance(user.id)

    if bet <= 0 or balance < bet or guess < 1 or guess > 6:
        await interaction.response.send_message("❌ Invalid bet or guess!", ephemeral=True)
        return

    result = random.randint(1, 6)
    if result == guess:
        winnings = bet * 6
        add_points(user.id, winnings - bet)
        adjust_stock(-winnings)
        await interaction.response.send_message(
            f"🎲 The dice rolled {result}! {user.mention} won {winnings} points! Your new balance is {get_balance(user.id)} points!",
            ephemeral=True
        )
    else:
        add_points(user.id, -bet)
        adjust_stock(bet)
        await interaction.response.send_message(
            f"🎲 The dice rolled {result}. {user.mention} lost {bet} points. Your new balance is {get_balance(user.id)} points.",
            ephemeral=True
        )

# Slash command: Colour game
@bot.tree.command(name="colourgame", description="Guess a colour, win points!")
@app_commands.describe(bet="Points to bet", guess="Your guess (red, green, blue, pink)")
async def colourgame(interaction: discord.Interaction, bet: int, guess: str):
    user = interaction.user
    balance = get_balance(user.id)

    if bet <= 0 or balance < bet or guess.lower() not in ["red", "green", "blue", "pink"]:
        await interaction.response.send_message("❌ Invalid bet or guess!", ephemeral=True)
        return

    result = random.choice(["red", "green", "blue", "pink"])
    if result == guess.lower():
        winnings = bet * 4
        add_points(user.id, winnings - bet)
        adjust_stock(-winnings)
        await interaction.response.send_message(
            f"🎨 The colour was {result}! {user.mention} won {winnings} points! Your new balance is {get_balance(user.id)} points!",
            ephemeral=True
        )
    else:
        add_points(user.id, -bet)
        adjust_stock(bet)
        await interaction.response.send_message(
            f"🎨 The colour was {result}. {user.mention} lost {bet} points. Your new balance is {get_balance(user.id)} points.",
            ephemeral=True
        )

# Slash command: Check stock
@bot.tree.command(name="check_stock", description="Points in stock")
async def check_stock(interaction: discord.Interaction):
    await interaction.response.send_message(f"📊 Current points in stock: {stock}", ephemeral=True)

# Slash command: Restock (Admin only)
@bot.tree.command(name="restock", description="[Admin only!] Restock points")
async def restock(interaction: discord.Interaction, points: int):
    if not is_admin(interaction.user) or points <= 0:
        await interaction.response.send_message("❌ You are not authorized to restock!", ephemeral=True)
        return
    adjust_stock(points)
    await interaction.response.send_message(f"✅ Restocked {points} points. Current stock: {stock}", ephemeral=True)

# Slash command: Add points (Admin only)
@bot.tree.command(name="addpoints", description="Add points to a user (Admin only)")
async def add_points_command(interaction: discord.Interaction, user: discord.User, points: int):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    add_points(user.id, points)
    await interaction.response.send_message(f"✅ Added {points} points to {user.mention}'s balance.", ephemeral=True)

# Slash command: Subtract points (Admin only)
@bot.tree.command(name="subtract", description="Subtract points from a user (Admin only)")
async def subtract_command(interaction: discord.Interaction, user: discord.User, points: int):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    subtract_points(user.id, points)
    await interaction.response.send_message(f"✅ Subtracted {points} points from {user.mention}'s balance.", ephemeral=True)

# Slash command: Exchange points (Placeholder)
@bot.tree.command(name="exchange", description="Exchange points for rewards!")
@app_commands.describe(points="Points to exchange", item="The reward you want to claim")
async def exchange(interaction: discord.Interaction, points: int, item: str):
    user = interaction.user
    balance = get_balance(user.id)

    # Define rewards and their point costs
    rewards = {
        "1K V-Bucks": 500,
        "2K V-Bucks": 1500,
        "NFA S3 Account": 5000,
        "NFA S2 Account": 10000,
        "NFA Black Knight Account": 30000,
        "NFA Ikonik Account": 50000,
    }

    # Check if the reward exists and points are sufficient
    if item not in rewards or points != rewards[item]:
        reward_list = "\n".join([f"• {cost} Points = {reward}" for reward, cost in rewards.items()])
        await interaction.response.send_message(
            f"❌ Invalid reward or point amount!\n\n__**Rewards**__\n{reward_list}",
            ephemeral=True
        )
        return

    if balance < points:
        await interaction.response.send_message(f"❌ You don't have enough points to claim `{item}`!", ephemeral=True)
        return

    # Deduct points and create a ticket
    subtract_points(user.id, points)
    await interaction.response.send_message(
        f"🎁 {user.mention}, you have exchanged {points} points for `{item}`! A ticket has been created for this request.",
        ephemeral=True
    )

    # Create ticket channel
    guild = interaction.guild
    ticket_channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        overwrites={
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
        },
        reason="Exchange request ticket"
    )

    # Notify admin and user in ticket
    admin_mention = "1320128307987087381"  # Replace with your admin's actual mention or role ID
    await ticket_channel.send(
        f"{admin_mention}, {user.mention} wants to exchange `{points}` points for `{item}`. Please assist them!"
    )

#slash command. exchange info
@bot.tree.command(name="exchange_info", description="View prices and rewards for exchanging points!")
async def exchange_info(interaction: discord.Interaction):
    prices = """
    __**Prices**__
    • 100 Points = $3
    • 500 Points = $4
    • 1000 Points = $6
    • 5000 Points = $9
    • 10000 Points = $12
    """
    rewards = """
    __**Rewards**__
    • 500 Points = 1K V-Bucks
    • 1500 Points = 2K V-Bucks
    • 5000 Points = NFA S3 Account
    • 10000 Points = NFA S2 Account
    • 30000 Points = NFA Black Knight Account
    • 50000 Points = NFA Ikonik Account
    """
    how_to_get_points = """
    __**How do I get points?**__
    You get points by using the `/earn` button once a day. You can then use those points by gambling them on games. 
    Another way is that you can win giveaways or buy them with money!
    """
    await interaction.response.send_message(f"__**Exchange <@1320376099821064273> Points for Rewards!**__\n\n{how_to_get_points}\n{prices}\n{rewards}", ephemeral=True)
# slash command. horse
@bot.tree.command(name="horse_racing", description="Bet on a horse and win!")
@app_commands.describe(bet="Amount of points to bet", horse="Horse number (1-16)")
async def horse_racing(interaction: discord.Interaction, bet: int, horse: int):
    user = interaction.user
    balance = get_balance(user.id)

    # Validate input
    if bet <= 0 or balance < bet or horse < 1 or horse > 16:
        await interaction.response.send_message("❌ Invalid bet or horse number!", ephemeral=True)
        return

    result = random.randint(1, 16)
    if result == horse:
        winnings = bet * 16
        add_points(user.id, winnings - bet)
        adjust_stock(-winnings)
        await interaction.response.send_message(
            f"🐎 It's horse {result}! You won {winnings} points! Your new balance is {get_balance(user.id)} points!",
            ephemeral=True
        )
    else:
        add_points(user.id, -bet)
        adjust_stock(bet)
        await interaction.response.send_message(
            f"🐎 It's horse {result}. You lost {bet} points. Your new balance is {get_balance(user.id)} points.",
            ephemeral=True
        )

# On ready event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Run the bot
bot.run('ENTER BOT TOKEN')  # Replace with your actual bot token
