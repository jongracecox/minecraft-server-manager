from enum import Enum


class ServerStatus(Enum):
    """Status of Minecraft Server."""
    STOPPED = "Stopped"
    RUNNING = "Running"
    UNKNOWN = "Unknown"


class GameRule(Enum):
    """Minecraft game rules."""
    KEEP_INVENTORY = "keepInventory"
    DO_WEATHER_CYCLE = "doWeatherCycle"
    COMMAND_BLOCK_OUTPUT = "commandBlockOutput"
    DISABLE_RAIDS = "disableRaids"
    DO_DAYLIGHT_CYCLE = "doDaylightCycle"
    DO_ENTITY_DROPS = "doEntityDrops"
    DO_INSOMNIA = "doInsomnia"
    DO_MOB_SPAWNING = "doMobSpawning"
    DO_WARDEN_SPAWNING = "doWardenSpawning"
    FALL_DAMAGE = "fallDamage"
    FIRE_DAMAGE = "fireDamage"
    MOB_GRIEFING = "mobGriefing"
    PVP = "pvp"
    SEND_COMMAND_FEEDBACK = "sendCommandFeedback"
    SHOW_COORDINATES = "showCoordinates"
    TNT_EXPLODES = "tntExplodes"
