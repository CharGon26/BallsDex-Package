from .cog import Wishlist

async def setup(bot):
    await bot.add_cog(Wishlist(bot))