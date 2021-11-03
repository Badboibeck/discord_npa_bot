import re

DIXXCORD_GUILD_ID = 3

# region channels
"""STATS_MEMBER_COUNT_CHANNEL_ID = 7"""
STATS_MEMBER_COUNT_CHANNEL_ID = 7

PATREON_CHAT_CHANNEL_ID = 6

GENERAL_CHAT_CHANNEL_ID = 5

REDS_SOFTWARE_TEST_CHANNEL_ID = 6

HLL_ADMIN_SUPPORT_REPORT_CHANNEL_ID = 6

SQD_ADMIN_SUPPORT_REPORT_CHANNEL_ID = 8

ADMIN_SUPPORT_AUTO_REPORTS_CHANNEL_ID = 7

POWER_PLAYERS_TRYHARDS_CHANNEL_ID = 6

SQUAD_SQUAD_SERVER_STATUS_CHANNEL_ID = 7

COMMUNITY_COMING_GOING_CHANNEL_ID = 3

REDS_MOD_SOFTWARE_BOT_ERRORS_CHANNEL_ID = 7

POWER_PLAYERS_TRYHARD_ASSISTANT_CHANNEL_ID = 7

NPA_MOD_LOG_CHANNEL_ID = 8

RUST_ADMIN_SUPPORT_REPORT_CHANNEL_ID = 8

HELP_DESK_CHANNEL_ID = 8

HELP_DESK_LOG_CHANNEL_ID = 8

# endregion

# region roles
DIXX_DEVS_ROLE_ID = 6

GOAT_ROLE_ID = 6

PATRONS_ROLE_ID = 6

PATREON_BOSS_ROLE_ID = 6

BOOSTERS_ROLE_ID = 5

NPA_MINI_MOD_ROLE_ID = 8

TRYHARDS_ROLE_ID = 6

REDS_ROLE_ID = 6

OPERATORS_ROLE_ID = 7

NPA_MOD_ROLE_ID = 8

REGS_ROLE_ID = 3

JUMPER_ROLE_ID = 3

GAME_LEADER_HLL_ROLE_ID = 6

ADMIN_HLL_LEAD_ROLE_ID = 6

ADMIN_HLL_SR_ROLE_ID = 6

ADMIN_HLL_ROLE_ID = 6

HLL_EVENT_STAFF_ROLE_ID = 8

GAME_LEADER_SQD_ROLE_ID = 6

ADMIN_SQD_LEAD_ROLE_ID = 6

ADMIN_SQD_SR_ROLE_ID = 6

ADMIN_SQD_ROLE_ID = 6

GAME_LEADER_EFT_ROLE_ID = 6

ADMIN_EFT_ROLE_ID = 7

GAME_LEADER_HUNT_ROLE_ID = 7

ADMIN_HUNT_ROLE_ID = 7

GAME_LEADER_GB_ROLE_ID = 7

ADMIN_GB_ROLE_ID = 7

ADMIN_RUST_ROLE_ID = 8

ONE_AD_ROLE_ID = 7

BADGERS_ROLE_ID = 7

BHB_ROLE_ID = 7

EASY_ROLE_ID = 7

MVG_ROLE_ID = 7

STG_ROLE_ID = 7

EGC_ROLE_ID = 8

OS_ROLE_ID = 8

THE_LINE_ROLE_ID = 7

OSS_LEAD_ROLE_ID = 8

OSS_SECTION_ROLE_ID = 8

OSS_ROLE_ID = 7

SOC_ROLE_ID = 8

DB_ROLE_ID = 8

ARTIFICIAL_INTELLIGENCE_ROLE_ID = 3

# endregion


# region emote utf-8
EMOTE_CHECK_MARK_BUTTON = u"\U00002705"
EMOTE_WHITE_CHECK_MARK = EMOTE_CHECK_MARK_BUTTON
EMOTE_CHART_WITH_UPWARDS_TREND = u"\U0001F4C8"
EMOTE_CHART_WITH_DOWNWARDS_TREND = u"\U0001F4C9"
EMOTE_BOOM = u"\U0001F4A5"
EMOTE_SKULL = u"\U0001F480"
EMOTE_HAMMER = u"\U0001f528"
EMOTE_HEART = u"\U00002764\U0000fe0f"
EMOTE_BROKEN_HEART = u"\U0001F494"
EMOTE_X = u"\U0000274c"
# endregion


# region nick name variants
NICK_NAME_VARIANTS = ["NPA"]
NICK_NAME_VARIANTS_RE = [re.compile(r"\[NPA\]", re.IGNORECASE)]
OLD_NICK_NAME_VARIANTS_RE = [re.compile(r"\[(DIXX|DIXXIE)\]", re.IGNORECASE)]
# endregion


# region Embed DIXX Colors
EMBED_DIXX_GOLD = 15580211
EMBED_DIXX_PURPLE = 7950792
EMBED_DARK_BLUE = 1447458
EMBED_DIXX_WITE = 16777215
# endregion


# region Source Servers
SQUAD_COLO_SERVER = {
    "offline_name": "NEVER PLAY ALONE :: DISCORD.GG/NPA :: SQD",
    "address": "",
    "query_port": 27165,
    "discord_guild": 3,
    "discord_channel": 7,
    "discord_msg": 7,
    "embed_thumbnail": "https://joinsquad.com/wp-content/themes/squad/img/logo.png",
}
GB_NYC_PVE_SERVER = {
    "offline_name": "NEVER PLAY ALONE :: PVP COOP :: US NY :: DISCORD.GG/NPA",
    "address": "",
    "query_port": 31503,
    "discord_guild": 3,
    "discord_channel": 8,
    "discord_msg": 8,
    "embed_thumbnail": "https://cdn.discordapp.com/attachments/670683769241337877/822252504104304690/GB_Project192x192.png",
}
GB_NYC_PVP_SERVER = {
    "offline_name": "NEVER PLAY ALONE :: PVE :: US NEW YORK :: DISCORD.GG/NPA",
    "address": "",
    "query_port": 3,
    "discord_guild": 3,
    "discord_channel": 8,
    "discord_msg": 8,
    "embed_thumbnail": "https://cdn.discordapp.com/attachments/670683769241337877/822252504104304690/GB_Project192x192.png",
}
RUST_COLO_SERVER = {
    "offline_name": "NEVER PLAY ALONE :: NPA.GG ::VANILLA",
    "address": "",
    "query_port": 28015,
    "discord_guild": 3,
    "discord_channel": 8,
    "discord_msg": 8,
    "embed_thumbnail": "https://cdn.discordapp.com/attachments/670683769241337877/845830459245068288/4be30338d1a685ea1d5212a935acbfb7.png",
}
SOURCE_SERVERS = [SQUAD_COLO_SERVER, GB_NYC_PVE_SERVER, GB_NYC_PVP_SERVER, RUST_COLO_SERVER]
# endregion