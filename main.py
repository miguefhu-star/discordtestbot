
import discord
from discord.ext import commands
import requests
import os  # Biblioteca necessária para ler as Secrets

# --- CONFIGURAÇÕES SEGURAS ---
# O os.getenv vai buscar o valor que guardaste nas Secrets do GitHub
TOKEN = os.getenv('DISCORD_TOKEN')
HYPIXEL_API_KEY = os.getenv('HYPIXEL_KEY')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_uuid(username):
    """Converte o nick do Minecraft em UUID via API da Mojang"""
    try:
        url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        response = requests.get(url).json()
        return response.get('id')
    except:
        return None

@bot.command()
async def stats(ctx, username):
    uuid = get_uuid(username)
    if not uuid:
        return await ctx.send("❌ Jogador não encontrado.")

    url = f"https://api.hypixel.net/v2/skyblock/profiles?key={HYPIXEL_API_KEY}&uuid={uuid}"
    data = requests.get(url).json()

    if not data.get('profiles'):
        return await ctx.send("Este jogador não tem perfis de Skyblock.")

    for perfil in data['profiles']:
        nome_perfil = perfil.get('cute_name', 'Desconhecido')
        dados_jogador = perfil.get('members', {}).get(uuid, {})
        
        # --- Stats  ---
        lvl = dados_jogador.get('leveling', {}).get('experience', 0) / 100
        purse = dados_jogador.get('currencies', {}).get('coin_purse', 0)

        # --- Skills  ---
        skills_data = dados_jogador.get('player_data', {}).get('experience', {})
        
        def get_skill_lvl(name):
            exp = skills_data.get(f'SKILL_{name}', 0)
            if exp >= 1000000: return f"{exp/1000000:.1f}M"
            if exp >= 1000: return f"{exp/1000:.1f}k"
            return f"{exp:.0f}"

        combat = get_skill_lvl('COMBAT')
        mining = get_skill_lvl('MINING')
        farming = get_skill_lvl('FARMING')
        foraging = get_skill_lvl('FORAGING')
        fishing = get_skill_lvl('FISHING')

        # --- Construção do Embed ---
        embed = discord.Embed(
            title=f"📊 {username} @ {nome_perfil}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="⭐ SB Level", value=f"{lvl:.0f}", inline=True)
        embed.add_field(name="💰 Purse", value=f"{purse:,.0f}", inline=True)
        
        # Campo de Skills formatado
        skills_text = (
            f"⚔️ **Combat:** {combat}\n"
            f"⛏️ **Mining:** {mining}\n"
            f"🌾 **Farming:** {farming}\n"
            f"🌳 **Foraging:** {foraging}\n"
            f"🎣 **Fishing:** {fishing}"
        )
        embed.add_field(name="📜 Skills (EXP)", value=skills_text, inline=False)
        
        await ctx.send(embed=embed)

@bot.command()
async def todos(ctx, username):
    """Lista todos os perfis do jogador"""
    uuid = get_uuid(username)
    if not uuid:
        return await ctx.send("❌ Jogador não encontrado.")

    url = f"https://api.hypixel.net/v2/skyblock/profiles?key={HYPIXEL_API_KEY}&uuid={uuid}"
    data = requests.get(url).json()

    if not data.get('profiles'):
        return await ctx.send("Nenhum perfil encontrado.")

    embed = discord.Embed(title=f"🗂️ Todos os perfis de {username}", color=discord.Color.blue())

    for p in data['profiles']:
        nome = p.get('cute_name')
        p_stats = p['members'][uuid]
        lvl = p_stats.get('leveling', {}).get('experience', 0) / 100
        
        embed.add_field(
            name=f"🔹 {nome}", 
            value=f"Level: {lvl:.0f}", 
            inline=True
        )

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'✅ Bot online como {bot.user}')

bot.run(TOKEN)
