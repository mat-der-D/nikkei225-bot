import discord
from discord.ext import commands
import yfinance as yf
from datetime import date
import os

def fetch_nikkei225_latest_close() -> tuple[date, float]:
    """
    Yahoo Financeから日経225の最新の終値と日付を取得する関数
    
    Returns:
        tuple[date, float]: 日付と終値のタプル
    """
    try:
        # 日経225のティッカーシンボル
        ticker = "^N225"
        # データ取得
        nikkei_data = yf.Ticker(ticker)
        # 株価履歴を取得（直近の取引日）
        hist = nikkei_data.history(period="1d")
        
        if hist.empty:
            raise ValueError("データを取得できませんでした")
        
        # 最新の日付と終値を取得
        latest_date = hist.index[-1].date()
        latest_close = float(hist['Close'].iloc[-1])
        
        return (latest_date, latest_close)
    except Exception as e:
        raise RuntimeError(f"日経225データの取得中にエラーが発生しました: {str(e)}")


# 特権インテントを有効にする
intents = discord.Intents.default()
intents.message_content = True
# 必要に応じて他の特権インテントも有効にする
# intents.members = True
# intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def latest_nikkei225(ctx):
    try:
        latest_date, latest_close = fetch_nikkei225_latest_close()
        await ctx.send(f"日経225の最新の終値は{latest_close}円です。({latest_date:%Y/%m/%d})")
    except Exception as e:
        await ctx.send(f"エラーが発生しました: {str(e)}")

# 注意: トークンは公開しないでください。環境変数などで管理することをお勧めします。
# Discordデベロッパーポータルで特権インテントを有効にする必要があります。
# https://discord.com/developers/applications にアクセスし、
# あなたのアプリケーションを選択 → Bot → Privileged Gateway Intents で
# 「Message Content Intent」を有効にしてください。
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
