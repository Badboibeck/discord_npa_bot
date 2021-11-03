from discord import Embed
import datetime
from dixxbot.statics import EMBED_DIXX_PURPLE, EMBED_DIXX_GOLD


def get_timestamp():
    return datetime.datetime.now()


def whois_user_info(member):
    date_format = "%a, %d %b %Y %I:%M %p"
    embed = Embed(color=EMBED_DIXX_PURPLE, description=member.mention)
    embed.set_author(name=str(member), icon_url=member.avatar_url)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Joined", value=member.joined_at.strftime(date_format))
    embed.add_field(name="Registered", value=member.created_at.strftime(date_format))

    if len(member.roles) > 1:
        member_reverse = sorted(member.roles, key=lambda x: x.position, reverse=True)
        role_string = " ".join([r.mention for r in member_reverse][:-1])
        embed.add_field(
            name="Roles [{}]".format(len(member.roles) - 1),
            value=role_string[0:1024],
            inline=False,
        )
    embed.set_footer(text="ID: " + str(member.id))

    embed.timestamp = get_timestamp()
    return embed


def mod_action_embed(member, author, reason, message, action):
    embed = Embed(title=f"{action} | {member}", color=EMBED_DIXX_GOLD,)
    embed.add_field(name="User", value=f"{member.mention}", inline=True)
    embed.add_field(name="Moderator", value=f"{author.mention}", inline=True)
    embed.add_field(name="Reason", value=f"{reason}", inline=False)
    embed.add_field(
        name="Message ID", value=f"[{message.id}]({message.jump_url})", inline=False
    )
    embed.set_footer(text="ID: " + str(member.id))

    embed.timestamp = get_timestamp()
    return embed

def help_desk_embed(message):
    embed = Embed(
        title=f"HELP DESK REPORT | {message.author}",
        color=0xEDBC05,
    )
    embed.add_field(name="User", value=f"{message.author.mention}", inline=False)
    embed.add_field(name="Message", value=f"{message.content}", inline=False)
    embed.set_footer(text="ID: " + str(message.author.id))
    embed.timestamp = get_timestamp()
    return embed


def author_help_desk_embed(message):
    embed = Embed(
        title=f"Thank you! The NPA Staff have received your request/report.",
        color=0xEDBC05,
    )
    embed.add_field(name="Message", value=f"{message.content}", inline=False)
    embed.set_footer(text="Please submit additional info via the Help Desk Channel.")
    embed.timestamp = get_timestamp()
    return embed

def help_command_embed():
    embed = Embed(title="MODERATION HELP", color=EMBED_DIXX_GOLD,)
    embed.add_field(
        name="WARN",
        value="'?mod warn <member> <reason> [other_reason]'\n*This command will send a discreet warning to the member.*",
        inline=False,
    )
    embed.add_field(
        name="KICK",
        value="'?mod kick <member> <reason> [other_reason]'\n*This command will send a discreet message and kick the member from the community.*",
        inline=False,
    )
    embed.add_field(
        name="SOFTBAN",
        value="'?mod softban <member> <reason> [other_reason]'\n*This command will send a discreet message, kick the member from the community, and delete the member's messages in the past 24hrs*",
        inline=False,
    )
    embed.add_field(
        name="BAN",
        value="'?mod ban <member> <reason> [other_reason]'\n*This command will send a discreet message, ban the member from the community, and delete the member's messages in the past 24hrs*",
        inline=False,
    )
    embed.add_field(
        name="UNBAN",
        value="'?mod unban <user> <reason> [other_reason]'\n*This command will unban the user.",
        inline=False,
    )
    embed.add_field(
        name="DOCUMENTATION",
        value="[Decision Tree](https://docs.google.com/presentation/d/1TimP8XK4XhP6C1IPP_Yq0nf8h3EEi8WNzaDhNKcoImY/edit?usp=sharing) | [Command Messages](https://docs.google.com/spreadsheets/d/1D6TW21CKMYnygR6z12boFAlfGGTVDG8uqJemtYYVJ_s/edit?usp=sharing)",
        inline=False,
    )
    embed.set_footer(text="Have a question? Ping a NPA DEV or MOD.")

    return embed
