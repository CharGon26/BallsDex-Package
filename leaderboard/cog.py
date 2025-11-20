import discord
from discord import app_commands
from discord.ext import commands
from ballsdex.settings import settings
from tortoise.functions import Count
from ballsdex.core.models import Ball, BallInstance, Player, balls, Special
from ballsdex.core.utils.paginator import FieldPageSource, Pages, TextPageSource

# This command sends the top 20 players with the most balls in ephemeral.

class Leaderboard(commands.Cog):
    """
    leaderboard command for the bot.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def leaderboard(self, interaction: discord.Interaction, server_only: bool = False):
        """
        Show the leaderboard of users with the most caught countryballs.

        Parameters
        ----------
        server_only: bool
            Show only players from this server (based on guild membership).
        """
        await interaction.response.defer(ephemeral=False, thinking=True)
        
        if server_only and interaction.guild:
            # Get Discord IDs of guild members
            guild_member_ids = {member.id for member in interaction.guild.members}
            # Filter players to those in the guild
            players = await Player.annotate(ball_count=Count("balls")).filter(discord_id__in=guild_member_ids).order_by("-ball_count").limit(20)
            embed_title = "🏆 Top 20 Server Players 🏆"
        else:
            # Global leaderboard
            players = await Player.annotate(ball_count=Count("balls")).order_by("-ball_count").limit(20)
            embed_title = "🏆 Top 20 Doctor Who Dex Players 🏆"
        
        if not players:
            await interaction.followup.send("No players found.", ephemeral=False)
            return

        entries = []
        for i, player in enumerate(players):
            user = self.bot.get_user(player.discord_id)
            if user is None:
                user = await self.bot.fetch_user(player.discord_id)

            # Add medal for top three
            if i == 0:
                medal = "🥇"
            elif i == 1:
                medal = "🥈"
            elif i == 2:
                medal = "🥉"
            else:
                medal = ""
            
            entries.append((f"{i + 1}. {medal} {user.name}", f"Whos: {player.ball_count}"))

        source = FieldPageSource(entries, per_page=10, inline=False)
        source.embed.title = embed_title
        source.embed.color = discord.Color.gold()
        source.embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        pages = Pages(source=source, interaction=interaction)
        await pages.start(ephemeral=False)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
