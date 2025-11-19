import discord
from discord import app_commands
from discord.ext import commands
from ballsdex.settings import settings
from collections import defaultdict
from ballsdex.core.models import Ball, BallInstance
from ballsdex.core.utils.paginator import FieldPageSource, Pages, TextPageSource

# Rarity command made by wascertified.
# This command generates a list of countryballs ranked by rarity with percentages and emojis.

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
        owned_only: bool = False,
    ):
        """
        Generate a list of countryballs ranked by rarity.

        Parameters
        ----------
        chunked: bool
            Group together countryballs with the same rarity.
        include_disabled: bool
            Include the countryballs that are disabled or with a rarity of 0.
        owned_only: bool
            Show only the countryballs you own.
        """
        await interaction.response.defer(ephemeral=False)
        
        balls_queryset = Ball.all()
        if not include_disabled:
            balls_queryset = balls_queryset.filter(rarity__gt=0, enabled=True)
        
        if owned_only:
            # Get ball IDs owned by the user
            owned_ball_ids = await BallInstance.filter(player__discord_id=interaction.user.id).distinct().values_list("ball_id", flat=True)
            balls_queryset = balls_queryset.filter(id__in=owned_ball_ids)
        
        sorted_balls = await balls_queryset.order_by("rarity")

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

        source = FieldPageSource(entries, per_page=5, inline=False)
        if owned_only:
            source.embed.title = "☄️Cards owned rarity list "
        else:
            source.embed.title = "☄️ DW Dex Rarity List"
        source.embed.color = discord.Color.blue()
        source.embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        pages = Pages(source=source, interaction=interaction)
        await pages.start(ephemeral=False)


async def setup(bot):
    await bot.add_cog(Rarity(bot))
