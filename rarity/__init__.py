from .cog import Rarity

async def setup(bot):
    await bot.add_cog(Rarity(bot))