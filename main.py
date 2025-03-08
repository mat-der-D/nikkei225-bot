import discord
from discord.ext import commands
import yfinance as yf
from datetime import date
import sys
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
        hist = nikkei_data.history(period="14d")
        
        if hist.empty:
            raise ValueError("データを取得できませんでした")
        
        # 最新の日付と終値を取得
        latest_date = hist.index[-1].date()
        latest_close = float(hist['Close'].iloc[-1])
        
        return (latest_date, latest_close)
    except Exception as e:
        raise RuntimeError(f"日経225データの取得中にエラーが発生しました: {str(e)}")


async def send_nikkei_data_to_channels(bot: commands.Bot, latest_date: date, latest_close: float, target_channel_ids: list[str]) -> None:
    """
    日経225のデータを設定されたチャンネルに送信する関数
    
    Args:
        bot (commands.Bot): ボットオブジェクト
        latest_date (date): 日経225の最新データの日付
        latest_close (float): 日経225の最新の終値
        target_channel_ids (list): 送信先チャンネルIDのリスト
    """
    if target_channel_ids:
        # 特定のチャンネルIDが設定されている場合
        await send_to_specific_channels(bot, target_channel_ids, latest_date, latest_close)
    else:
        # 環境変数が設定されていない場合
        print("環境変数 DISCORD_TARGET_CHANNEL_IDS が設定されていません。最初のチャンネルに送信します。")


async def send_to_specific_channels(bot: commands.Bot, channel_ids: list[str], latest_date: date, latest_close: float) -> None:
    """
    指定されたチャンネルIDリストに日経225のデータを送信する関数
    
    Args:
        bot (commands.Bot): ボットオブジェクト
        channel_ids (list): 送信先チャンネルIDのリスト
        latest_date (date): 日経225の最新データの日付
        latest_close (float): 日経225の最新の終値
    """
    message_sent = False
    for channel_id in channel_ids:
        try:
            channel = bot.get_channel(int(channel_id))
            if channel:
                await channel.send(f"日経225の最新の終値は{latest_close}円です。({latest_date:%Y/%m/%d})")
                print(f"メッセージをチャンネル '{channel.name}' (ID: {channel_id}) に送信しました")
                message_sent = True
            else:
                print(f"指定されたチャンネルID {channel_id} が見つかりませんでした")
        except Exception as e:
            print(f"チャンネルID {channel_id} への送信中にエラーが発生しました: {str(e)}")
    
    if not message_sent:
        print("設定されたチャンネルIDにはどれも送信できませんでした")

# 特権インテントを有効にする
async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    # 必要に応じて他の特権インテントも有効にする
    # intents.members = True
    # intents.presences = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user.name}')
        try:
            # 環境変数からチャンネルIDのリストを取得（カンマ区切りで複数指定可能）
            target_channel_ids_str = os.environ.get('DISCORD_TARGET_CHANNEL_IDS', '')
            target_channel_ids = [id.strip() for id in target_channel_ids_str.split(',') if id.strip()]
            
            # ボット起動時に日経225の情報を取得
            latest_date, latest_close = fetch_nikkei225_latest_close()
            await send_nikkei_data_to_channels(bot, latest_date, latest_close, target_channel_ids)
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")
        finally:
            # on_readyの処理が終わったらプログラムを終了する
            await bot.close()
            sys.exit(0)

    # 注意: トークンは公開しないでください。環境変数などで管理することをお勧めします。
    # Discordデベロッパーポータルで特権インテントを有効にする必要があります。
    # https://discord.com/developers/applications にアクセスし、
    # あなたのアプリケーションを選択 → Bot → Privileged Gateway Intents で
    # 「Message Content Intent」を有効にしてください。
    token = os.environ.get('DISCORD_TOKEN')
    await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

