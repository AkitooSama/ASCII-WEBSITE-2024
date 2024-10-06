import discord
from discord.ext import commands
from static_classes.responses import FunctionResponses

class MarketplaceBot(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.responses = FunctionResponses()
        self.client.loop.create_task(self.responses.load_all_data())

    @discord.app_commands.command(
            name="set_paypal_link",
            description="Sets or updates the PayPal link for buyers."
    )
    @discord.app_commands.describe(
            link="The PayPal payments link to be set or updated."
    )
    @discord.app_commands.default_permissions()
    async def set_paypal_link(self, interaction: discord.Interaction, link: str) -> None:
        await interaction.response.defer()
        await self.responses.set_paypal_link(interaction=interaction, link=link)

    @discord.app_commands.command(
            name="set_ping_role",
            description="Sets or updates the role to ping staff for assistance."
    )
    @discord.app_commands.describe(
            role="The staff role to be pinged."
    )
    @discord.app_commands.default_permissions()
    async def set_ping_role(self, interaction: discord.Interaction, role: discord.Role) -> None:
        await interaction.response.defer()
        await self.responses.set_ping_role(interaction=interaction, role=role)

    @discord.app_commands.command(
            name="stop",
            description="Stops bot from sending further messages in this channel."
    )
    @discord.app_commands.default_permissions()
    async def stop(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await self.responses.stop_interaction(interaction=interaction)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or str(message.channel.id) in self.responses.ignored_channels:
            return
        if "ticket" in message.channel.name.lower():
            await self.responses.handle_command(client=self.client, message=message)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        if isinstance(channel, discord.TextChannel) and "ticket" in channel.name.lower():
            await self.responses.handle_new_ticket_channel(channel)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        if isinstance(channel, discord.TextChannel):
            if str(channel.id) in self.responses.ignored_channels:
                self.responses.ignored_channels.remove(str(channel.id))
                await self.responses.save_all_data()

        if str(channel.id) in self.responses.command_limits.keys():
            del self.responses.command_limits[str(channel.id)]
            await self.responses.save_all_data()

async def setup(client: commands.Bot):
    await client.add_cog(MarketplaceBot(client))
