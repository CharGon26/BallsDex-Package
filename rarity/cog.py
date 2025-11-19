import discord
from discord import app_commands
from discord.ext import commands
from ballsdex.settings import settings
from collections import defaultdict
from ballsdex.core.models import Ball
from ballsdex.core.utils.paginator import FieldPageSource, Pages, TextPageSource

# Rarity command made by wascertified.
# This command generates a list of countryballs ranked by rarity with percentages.

class Rarity(commands.Cog):
    """
    Custom commands for the bot.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def rarity(
        self,
        interaction: discord.Interaction,
        chunked: bool = True,
        include_disabled: bool = False,
    ):
        """
        Generate a list of countryballs ranked by rarity.

        Parameters
        ----------
        chunked: bool
            Group together countryballs with the same rarity.
        include_disabled: bool
            Include the countryballs that are disabled or with a rarity of 0.
        """
        await interaction.response.defer(ephemeral=False)
        
        balls_queryset = Ball.all().order_by("rarity")
        if not include_disabled:
            balls_queryset = balls_queryset.filter(rarity__gt=0, enabled=True)
        sorted_balls = await balls_queryset

        entries = []
        if chunked:
            indexes: dict[float, list[Ball]] = defaultdict(list)
            for ball in sorted_balls:
                indexes[ball.rarity].append(ball)
            i = 1
            for chunk in indexes.values():
                for ball in chunk:
                    percentage = ball.rarity * 100
                    emoji = self.bot.get_emoji(int(ball.emoji_id)) or ""
                    entries.append((f"{i}. {emoji} {ball.country}", f"{percentage:.2f}%"))
                i += len(chunk)
        else:
            for i, ball in enumerate(sorted_balls, start=1):
                percentage = ball.rarity * 100
                emoji = self.bot.get_emoji(int(ball.emoji_id)) or ""
                entries.append((f"{i}. {emoji} {ball.country}", f"{percentage:.2f}%"))

        source = FieldPageSource(entries, per_page=10, inline=False)
        source.embed.title = "🚀 DW Dex Rarity List ☄️"
        source.embed.color = discord.Color.blue()
        source.embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        pages = Pages(source=source, interaction=interaction)
        await pages.start(ephemeral=False)