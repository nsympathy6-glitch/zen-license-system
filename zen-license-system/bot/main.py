import discord
from discord import app_commands
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LICENSE_SERVER_URL = os.getenv("LICENSE_SERVER_URL", "http://localhost:8000")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        print(f"Synced commands to guild {GUILD_ID}")
    else:
        await tree.sync()
        print("Synced commands globally")
    print(f"Bot logged in as {client.user}")

@tree.command(name="redeem", description="Redeem your license key using the challenge code from your Zen")
@app_commands.describe(
    zen_serial="Your Zen serial number",
    discord_id="Your Discord user ID",
    challenge_code="The challenge code shown on your Zen"
)
async def redeem(interaction: discord.Interaction, zen_serial: str, discord_id: str, challenge_code: str):
    await interaction.response.defer()

    async with httpx.AsyncClient() as client_http:
        try:
            # Get challenge from server to validate
            challenge_resp = await client_http.post(
                f"{LICENSE_SERVER_URL}/api/challenge",
                json={"zen_serial": zen_serial, "discord_id": discord_id},
                timeout=10.0
            )

            if challenge_resp.status_code != 200:
                error_data = challenge_resp.json()
                await interaction.followup.send(f"**Error:** {error_data.get('detail', 'Could not verify order')}")
                return

            challenge_data = challenge_resp.json()
            order_id = challenge_data["order_id"]
            expected_challenge = challenge_data["challenge"]

            # Verify challenge
            try:
                if int(challenge_code) != expected_challenge:
                    await interaction.followup.send("**Challenge mismatch!** Make sure you entered the correct code from your Zen.")
                    return
            except ValueError:
                await interaction.followup.send("**Invalid challenge code.** Must be a number.")
                return

            # Generate key
            key_resp = await client_http.post(
                f"{LICENSE_SERVER_URL}/api/generate_key",
                json={
                    "order_id": order_id,
                    "zen_serial": zen_serial,
                    "challenge": expected_challenge
                },
                timeout=10.0
            )

            if key_resp.status_code == 200:
                data = key_resp.json()
                embed = discord.Embed(
                    title="License Key Issued",
                    description="Your key has been generated successfully!",
                    color=discord.Color.green()
                )
                embed.add_field(name="Key", value=f"`{data['key']}`", inline=False)
                embed.set_footer(text="Enter this key in your Zen script to unlock it.")
                await interaction.followup.send(embed=embed)

            elif key_resp.status_code == 403:
                error_data = key_resp.json()
                await interaction.followup.send(f"**Access Denied:** {error_data.get('detail')}")

            elif key_resp.status_code == 429:
                await interaction.followup.send("**Rate Limited:** Too many requests. Please wait and try again.")

            else:
                error_data = key_resp.json()
                await interaction.followup.send(f"**Error:** {error_data.get('detail')}")

        except httpx.RequestError:
            await interaction.followup.send("**Connection Error:** Could not reach the license server.")

@tree.command(name="check", description="Check your order status")
@app_commands.describe(order_id="Your order ID")
async def check(interaction: discord.Interaction, order_id: str):
    await interaction.response.defer()

    async with httpx.AsyncClient() as client_http:
        try:
            response = await client_http.get(
                f"{LICENSE_SERVER_URL}/api/orders/{order_id}",
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                embed = discord.Embed(title="Order Details", color=discord.Color.blue())
                embed.add_field(name="Order ID", value=data['order_id'], inline=True)
                embed.add_field(name="Status", value=data['status'], inline=True)
                embed.add_field(name="Tier", value=data['tier'], inline=True)
                embed.add_field(name="Product", value=data['product'], inline=True)
                embed.add_field(name="Expires", value=data.get('expires_at', 'N/A'), inline=True)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("**Order not found.**")

        except httpx.RequestError:
            await interaction.followup.send("**Connection Error:** Could not reach the license server.")

@tree.command(name="help_license", description="How to use the license system")
async def help_license(interaction: discord.Interaction):
    embed = discord.Embed(
        title="License System",
        description="How to unlock your Zen script",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="Steps",
        value="1. Open the launcher and log in with Discord\n"
              "2. Click EXPORT on a purchased script\n"
              "3. Save the .gpc file and compile to your Zen\n"
              "4. Run the script - you'll see a challenge code\n"
              "5. Use `/redeem` with your serial, Discord ID, and challenge\n"
              "6. Enter the key into your Zen script",
        inline=False
    )
    embed.add_field(
        name="Commands",
        value="`/redeem` - Get your license key\n"
              "`/check` - Check order status",
        inline=False
    )
    await interaction.followup.send(embed=embed)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in .env")
    else:
        client.run(DISCORD_TOKEN)
