from typing import TYPE_CHECKING

from ballsdex.packages.events.cog import Events

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    await bot.add_cog(Events(bot))
