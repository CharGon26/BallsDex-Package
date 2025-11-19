import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, Set

# Import for DB access (to validate balls and check ownership)
from ballsdex.core.models import Ball, BallInstance
from ballsdex.core.utils.transformers import BallEnabledTransform

class Wishlist(commands.GroupCog):
    """
    Manage your wishlist of countryballs you want to collect.
    """

    def __init__(self, bot):
        self.bot = bot
        # In-memory storage: {user_id: set of ball_country_names}
        self.wishlists: Dict[int, Set[str]] = {}

    @app_commands.command()
    async def view(self, interaction: discord.Interaction):
        """
        View your current wishlist and see which cards you already own.
        """
        await interaction.response.defer(ephemeral=False)
        
        user_id = interaction.user.id
        wishlist = self.wishlists.get(user_id, set())
        
        if not wishlist:
            await interaction.followup.send("Your wishlist is empty!", ephemeral=False)
            return
        
        embed = discord.Embed(
            title=f"{interaction.user.name}'s Wishlist",
            description=f"Your wishlist has {len(wishlist)} item/s.",
            color=discord.Color.blue()
        )
        
        # Query DB for ownership
        owned_counts = {}
        for ball_name in wishlist:
            ball = await Ball.filter(country__iexact=ball_name).first()
            if ball:
                count = await BallInstance.filter(player__discord_id=user_id, ball=ball).count()
                owned_counts[ball_name] = count
        
        wishlist_text = []
        for ball_name in sorted(wishlist):
            owned = owned_counts.get(ball_name, 0)
            status = f"✅ Owned ({owned})" if owned > 0 else "❌ Not owned"
            emoji = self.bot.get_emoji((await Ball.filter(country__iexact=ball_name).first()).emoji_id) if await Ball.filter(country__iexact=ball_name).first() else ""
            wishlist_text.append(f"{emoji} {ball_name} - {status}")
        
        # Handle long lists by splitting into fields
        current_field = ""
        field_count = 1
        for line in wishlist_text:
            if len(current_field) + len(line) + 1 > 1024:
                embed.add_field(
                    name=f"Wishlist (Part {field_count})" if field_count > 1 else "Wishlist",
                    value=current_field,
                    inline=False
                )
                current_field = line + "\n"
                field_count += 1
            else:
                current_field += line + "\n"
        
        if current_field:
            embed.add_field(
                name=f"Wishlist (Part {field_count})" if field_count > 1 else "Wishlist",
                value=current_field,
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command()
    async def add(
        self,
        interaction: discord.Interaction,
        countryball: BallEnabledTransform
    ):
        """
        Add a countryball to your wishlist.

        Parameters
        ----------
        countryball: Ball
            The countryball you want to add to your wishlist
        """
        if not countryball:
            await interaction.response.send_message("That countryball doesn't exist.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.user.id
        ball_name = countryball.country
        
        if user_id not in self.wishlists:
            self.wishlists[user_id] = set()
        
        if ball_name in self.wishlists[user_id]:
            await interaction.followup.send(f"{ball_name} is already in your wishlist.", ephemeral=True)
            return
        
        self.wishlists[user_id].add(ball_name)
        emoji = self.bot.get_emoji(countryball.emoji_id)
        await interaction.followup.send(f"{emoji} {ball_name} has been added to your wishlist!", ephemeral=True)

    @app_commands.command()
    async def remove(
        self,
        interaction: discord.Interaction,
        countryball: BallEnabledTransform
    ):
        """
        Remove a countryball from your wishlist.

        Parameters
        ----------
        countryball: Ball
            The countryball you want to remove from your wishlist
        """
        if not countryball:
            await interaction.response.send_message("That countryball doesn't exist.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.user.id
        ball_name = countryball.country
        
        if user_id not in self.wishlists or ball_name not in self.wishlists[user_id]:
            await interaction.followup.send(f"{ball_name} is not in your wishlist.", ephemeral=True)
            return
        
        self.wishlists[user_id].remove(ball_name)
        emoji = self.bot.get_emoji(countryball.emoji_id)
        await interaction.followup.send(f"{emoji} {ball_name} has been removed from your wishlist!", ephemeral=True)

    @app_commands.command()
    async def purge(self, interaction: discord.Interaction):
        """
        Clear your entire wishlist.
        """
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.user.id
        if user_id not in self.wishlists:
            await interaction.followup.send("Your wishlist is already empty.", ephemeral=True)
            return
        
        count = len(self.wishlists[user_id])
        self.wishlists[user_id].clear()
        await interaction.followup.send(f"Cleared {count} items from your wishlist!", ephemeral=True)