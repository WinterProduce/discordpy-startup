import discord
import datetime as dt
from datetime import datetime, timedelta
import time
from discord.ext import tasks
import random
import os


client = discord.Client()
pretime_dict = {}
memberlist = {}

token = os.environ['DISCORD_BOT_TOKEN']

# Botログイン処理
@client.event
async def on_ready():
    print('起動完了しました！')
    print(client.user.name)
    print(client.user.id)
    print('------')
    startup_channel = client.get_channel(682141572317446167)
    await startup_channel.send('今から活動開始します！')
# ここからボイスチャンネルの入退出を検知する処理
@client.event
async def on_voice_state_update(member, before, after): 
    global pretime_dict # 辞書型で入室時間をユーザーごとに記録することで入室時間の再代入による不具合を回避
    global memberlist # VCの１週間の記録用の辞書
    if member.guild.id == 681853809789501440 and (before.channel != after.channel): # 特定のサーバーだけ処理が行われるように
        print('ボイスチャンネルに変化があったよ！')
        now = datetime.now()
        alert_channel = client.get_channel(682141572317446167) # 入退室ログを出力するチャンネルを指定

        if before.channel is None:  # ここから入室時の処理
            pretime_dict[member.name] = time.time() 
            msg = f'{now:%m/%d-%H:%M} に {member.name} が {after.channel.name} に参加しました。' # 入室ログ
            await alert_channel.send(msg)
            print(pretime_dict)

        elif after.channel is None: # 退出時の処理
            print(pretime_dict)
            duration_time = time.time() - pretime_dict[member.name] # 入室時からの経過時間を計算
            roundingtime = round((duration_time / 1), 1) # 経過時間の小数点一桁で四捨五入
            # ここから原始的な方法でduration_timeを時間、分、秒に変換
            endhours = 0
            endminutes = 0
            endseconds = roundingtime

            if 3600 > roundingtime >= 60:
                endminutes = roundingtime / 60
                endseconds = roundingtime % 60

            elif roundingtime >= 3600:
                endhours = roundingtime / 3600
                interimendminutes = roundingtime % 3600
                endminutes = interimendminutes / 60
                endseconds = interimendminutes % 60

            msg = f'{now:%m/%d-%H:%M} に {member.name} が {before.channel.name} から退出しました。 通話時間は {int(endhours)} 時間 {int(endminutes)} 分 {int(endseconds)} 秒でした。' # 退出ログ
            await alert_channel.send(msg)

            # ここから通話時間を記録していく処理
            memberlist[member.name] = memberlist[member.name] + int(roundingtime)
            await alert_channel.send('総接続時間を更新したよ！')

# ランダムに話題を出すプログラム
wadai = [ # 話題リスト
    "修学旅行みたいに恋バナ...とかどう？",
    "趣味の話とかしようよ！",
    "自己紹介に書いてない自分のこととかあったりしない？",
    "フォルダのネタ画像出してみて笑！",
    "推しの子とかの話はどうかな？",
    "最近欲しいものってなんかあるー？",
    "明日の予定教えて！",
    "今週末の予定は！？",
    "将来の夢の話しよう！",
    "お悩み相談室開いて...みる？",
    "縛りありのしりとりとかしてみようよ！",
    "わざわざ言うほどでもないけど自慢できることある？",
    "心理テストとかやってみない？",
    "なにかゲームしようよ！ そうだなぁ、英語禁止ゲームとかどう？",
    "私はゲームがしたいなぁーー 濁音禁止ゲームやりたいな！",
    "過去の恋愛について話そうよ！",
    "学生時代にやってた部活とかある？",
    ""
]

@client.event
async def on_message(message):
    global memberlist
    if client.user != message.author:
        if message.content == '?help':
            await message.channel.send('?wadaiで私が話題を提供してあげるよ！')

        if message.content == '?wadai':
            choice = random.choice(wadai)
            await message.channel.send(choice)

        if message.content == '?count':
            guild = message.guild
            # ユーザとBOTを区別しない場合
            member_count = guild.member_count
            await message.channel.send(f'メンバー数：{member_count}')

            # ユーザのみ
            user_count = sum(1 for member in guild.members if not member.bot)
            await message.channel.send(f'ユーザ数：{user_count}')

            # BOTのみ
            bot_count = sum(1 for member in guild.members if member.bot)
            await message.channel.send(f'BOT数：{bot_count}')

        if message.content == '?members':
            allmember = [member.name for member in client.get_all_members() if not member.bot]
            await message.channel.send(f'メンバー一覧 : {allmember}')
            
        if message.content == '?reset':
            membername = [member.name for member in client.get_all_members()　if not member.bot] # 全員分のNAMEを辞書のkeyに入れる処理
            zero = [0,0,0,0,0,0,0,0,0,0,0,0,0,0] # 辞書の値に全員分０を代入
            memberlist = dict(zip(membername, zero)) # リストを使用して辞書に格納
            await message.channel.send('総接続時間記録の値、すべてに０を代入しました')
        if message.content == '?vc':
            await message.channel.send('以前のresetからの総接続時間はこちらです！'memberlist)



client.run(token)
