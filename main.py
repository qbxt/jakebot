import discord
import json
from discord.ext import commands
import sys


try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("FATAL: config.json not found")
    sys.exit(0)

try:
    tmp = config["commandprefix"]
    tmp = config["servername"]
    tmp = config["founderroleid"]
    tmp = config["investorroleid"]
except KeyError:
    print("Invalid config.json. For help, see github.com/qbxt/jakebot")
    sys.exit(0)


bot = commands.Bot(command_prefix=commands.when_mentioned_or(config["commandprefix"]), case_insensitive=True)


@bot.event
async def on_ready():
    print("{} is fully logged in and ready".format(bot.user))


@bot.event
async def on_member_join(member):
    await when_member_joins(member)


@bot.command(name="join")
async def join(ctx):
    if ctx.guild is not None:
        try:
            await when_member_joins(ctx.message.mentions[0])
        except IndexError:
            await when_member_joins(ctx.author)
    else:
        await ctx.send("This can only be run in a guild")
        return


async def get_user_name(member):
    cont = False
    while not cont:  # get user name
        message = await member.send("What name do you go by? Enter your response below. For example: `Alex S.` or "
                                    "`Henry Wolfe`")

        def mcheck2(m):
            return m.author.id == member.id and m.guild is None

        msg = await bot.wait_for('message', check=mcheck2)
        username = msg.content

        message = await member.send("Good to meet you {}! Can I continue to call you {}?".format(username, username))
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check3(reaction, user):
            return user.id == member.id and str(reaction.emoji) in ["✅", "❌"] and reaction.message.guild is None

        reaction, user = await bot.wait_for('reaction_add', check=check3)

        if str(reaction.emoji) == "✅":
            cont = True
            continue
        elif str(reaction.emoji) == "❌":
            continue

    return username


async def get_company_name(member):
    cont = False
    while not cont:  # get company name
        await member.send("What company do you work for?")

        def mcheck(m):
            return m.author.id == member.id and m.guild is None

        msg = await bot.wait_for('message', check=mcheck)
        usercompany = msg.content

        message = await member.send("I got that you work for {}. Is that correct?".format(usercompany))
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check2(reaction, user):
            return user.id == member.id and str(reaction.emoji) in ["✅", "❌"] and reaction.message.guild is None

        reaction, user = await bot.wait_for('reaction_add', check=check2)

        if str(reaction.emoji) == "✅":
            cont = True
            continue
        elif str(reaction.emoji) == "❌":
            continue

    return usercompany


async def get_user_job(member):
    cont = False
    while not cont:  # get company name
        message = await member.send("Are you an investor 💵 or a founder 🛠?")
        await message.add_reaction("💵")
        await message.add_reaction("🛠")

        def check4(reaction, user):
            return user.id == member.id and str(reaction.emoji) in ["💵", "🛠"] and reaction.message.guild is None

        reaction, user = await bot.wait_for('reaction_add', check=check4)
        if str(reaction.emoji) == "💵":  # investor
            job = "Investor"
            message = await member.send("I'm going to put down that you're an investor. Is that correct?")
        elif str(reaction.emoji) == "🛠":  # founder
            job = "Founder"
            message = await member.send("I'm going to put down that you're a founder. Is that correct?")

        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check5(reaction, user):
            return user.id == member.id and str(reaction.emoji) in ["✅", "❌"] and reaction.message.guild is None

        reaction, user = await bot.wait_for('reaction_add', check=check5)

        if str(reaction.emoji) == "✅":
            cont = True
            continue
        elif str(reaction.emoji) == "❌":
            continue

    return job


async def when_member_joins(member):
    await member.send("Welcome to {}!".format(config["servername"]))
    message = await member.send("Please click the ✅ to begin the introduction process")
    await message.add_reaction("✅")

    def check(reaction, user):
        return user.id == member.id and str(reaction.emoji) == "✅"

    await bot.wait_for('reaction_add', check=check)

    username = await get_user_name(member)
    companyname = await get_company_name(member)
    job = await get_user_job(member)

    cont = False
    while not cont:
        message = await member.send(
            "🧑: {}\n🏭: {}\n💼: {}\n\nIf this is correct, please click the ✅. Otherwise, click an "
            "emoji below to edit the corresponding field.".format(username, companyname, job))
        await message.add_reaction("✅")
        await message.add_reaction("🧑")
        await message.add_reaction("🏭")
        await message.add_reaction("💼")

        def check6(reaction, user):
            return user.id == member.id and str(reaction.emoji) in ["✅", "🧑", "🏭", "💼"]

        reaction, user = await bot.wait_for('reaction_add', check=check6)

        if str(reaction.emoji) == "✅":
            cont = True
            continue
        elif str(reaction.emoji) == "🧑":
            username = await get_user_name(member)
            continue
        elif str(reaction.emoji) == "🏭":
            companyname = await get_company_name(member)
            continue
        elif str(reaction.emoji) == "💼":
            job = await get_user_job(member)
            continue

    if job.lower() == "founder":
        nickname = "{} [{}] [🛠]".format(username, companyname)
    elif job.lower() == "investor":
        nickname = "{} [{}] [💵]".format(username, companyname)

    if len(nickname) > 32:
        nickname = "{} [{}]".format(username, companyname)
        if len(nickname) > 32:
            await member.send("Error while changing nickname. Please message the server owner for help.")
            nickname = None

    if nickname is not None:
        await member.edit(nick=nickname)

    if job.lower() == "founder":
        await member.add_roles(member.guild.get_role(config["founderroleid"]), member.guild.get_role(config["onboardedroleid"]))
    elif job.lower() == "investor":
        await member.add_roles(member.guild.get_role(config["investorroleid"]), member.guild.get_role(config["onboardedroleid"]))

    await member.send("Onboarding complete! Welcome to {}".format(config["servername"]))


with open('token.json', 'r') as f:
    try:
        bot.run(json.load(f)["discord"])
    except KeyError:
        print("No token found in JSON. For help, visit github.com/qbxt/jakebot")
        sys.exit(0)
