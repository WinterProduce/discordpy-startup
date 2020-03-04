import discord
import datetime as dt
from datetime import datetime, timedelta, timezone
import time
from discord.ext import tasks, commands
import random
import os



client = discord.Client()
pretime_dict = {}
memberlist = {}
JST = timezone(timedelta(hours=+9), 'JST')

token = os.environ['DISCORD_BOT_TOKEN']

# Botログイン処理
@client.event
async def on_ready():
    global memberlist
    global inmemberlist
    print('起動完了しました！')
    print(client.user.name)
    print(client.user.id)
    print('------')
    channel = client.get_channel(682141572317446167)
    await channel.send('今から活動開始します！')
    # ここから総接続時間辞書のリセット処理
    membername = [member.name for member in client.get_all_members() if not member.bot] # Bot以外のユーザー名を辞書のkeyに入れる処理
    zero = []
    memberlist = dict(zip(membername, zero)) # リストを使用して辞書に格納
    for memberlistkey in memberlist.keys(): # 総接続時間辞書の値すべてに0を代入
        memberlist[memberlistkey] = 0
        print(memberlist)
    await channel.send('再起動に伴い総接続時間辞書の値すべてに０を代入しました！')

    inmembername = [member.name for member in client.get_all_members() if not member.bot] # Bot以外のユーザー名を辞書に入れる処理
    inmemberzero = []
    inmemberlist = dict(zip(inmembername, inmemberzero)) # In率処理の辞書作成

    for inmemberlistkey in inmemberlist.keys(): # 辞書の値すべてに0を代入
        inmemberlist[inmemberlistkey] = 0
        print(inmemberlist)
    await channel.send('再起動に伴いIn率処理の辞書の値すべてに0を代入しました！')

    activity = discord.Game(name='🍎')
    await client.change_presence(activity=activity)

# 指定時間に総接続時間をリセットする処理
async def Resetvclist():
    global memberlist
    membername = [member.name for member in client.get_all_members() if not member.bot] # 全員分のNAMEを辞書のkeyに入れる処理
    zero = []
    memberlist = dict(zip(membername, zero)) # リストを使用して辞書に格納

    for memberlistkey in memberlist.keys(): # 総接続時間辞書の値すべてに0を代入
        memberlist[memberlistkey] = 0
    print(memberlist)

    channel = client.get_channel(682141572317446167)
    await channel.send('総接続時間をリセットしました')

async def Resetinlist():
    global inmemberlist
    inmembername = [member.name for member in client.get_all_members() if not member.bot] # Bot以外のユーザー名を辞書に入れる処理
    inmemberzero = []
    inmemberlist = dict(zip(inmembername, inmemberzero)) # In率処理の辞書作成

    for inmemberlistkey in inmemberlist.keys(): # 辞書の値すべてに0を代入
        inmemberlist[inmemberlistkey] = 0
        print(inmemberlist)

    channel = client.get_channel(682141572317446167)
    await channel.send('In率をリセットしました')

# １週間の総接続時間を出力する処理
async def Sendvclist():
    channel = client.get_channel(682141572317446167)

    for memberkey, membervalue in memberlist.items():
        await channel.send(f'ユーザー名: {memberkey}  通話時間: {membervalue} 秒')

    for memberkey60, membervalue60 in memberlist.items():
        if membervalue60 >= 3600:
            vc60 = {memberkey60}
            await channel.send(f'総接続時間が60分以上のユーザー: {vc60}')
        elif membervalue60 < 3600:
            vc0 = {memberkey60}
            await channel.send(f'総接続時間が60分未満のユーザー: {vc0}')

async def Sendinlist():
    channel = client.get_channel(682141572317446167)

    for inkey, invalue in inmemberlist.items():
        await channel.send(f'ユーザー名: {inkey}  In率: {invalue} 日')
    
    for inkey4, invalue4 in inmemberlist.items():
        if invalue4 >= 4:
            in4 = {inkey4}
            await channel.send(f'In率が4日以上のユーザー: {in4}')
        elif invalue4 < 4:
            in0 = {inkey4}
            await channel.send(f'In率が4日未満のユーザー: {in0}')

# １週間のIn率を検知、出力する処理
async def Incheck():
    global inmemberlist
    channel = client.get_channel(682141572317446167)
    for memberkey0, membervalue0 in memberlist.items(): # 1秒以上通話した人の名前を検知
        if membervalue0 > 0:
            for name0 in memberkey0:
                inmemberlist[name0] = inmemberlist[name0] + 1
            print(inmemberlist)
            await channel.send('昨日の0時0分より今までにInした人を記録したよ！')
        else:
            return

# ６０秒に一回ループさせる処理
@tasks.loop(seconds=60)
async def weekloop():
    checktime = datetime.now(JST).strftime('%a-%H:%M')
    channel = client.get_channel(682141572317446167)
    if checktime == 'Wed-11:47':
        await channel.send('月曜日の０時０分になったため総接続時間を出力しデータをクリアします')
        await Sendvclist()
        await Resetvclist()
        await Sendinlist()
        await Resetinlist()

@tasks.loop(seconds=60)
async def dayloop():
    checkday = datetime.now(JST).strftime('%H:%M')
    if checkday == '11:47':
        channel = client.get_channel(682141572317446167)
        await channel.send('前日、Inしたかどうかを検知します')
        await Incheck()
    
# ループ処理実行
weekloop.start()
dayloop.start()

# ここからボイスチャンネルの入退出を検知する処理
@client.event
async def on_voice_state_update(member, before, after): 
    global pretime_dict # 辞書型で入室時間をユーザーごとに記録することで入室時間の再代入による不具合を回避
    global memberlist # VCの１週間の記録用の辞書
    channel = client.get_channel(682141572317446167)
    if member.guild.id == 681853809789501440 and (before.channel != after.channel): # 特定のサーバーだけ処理が行われるように
        if not member.bot:
            print('ボイスチャンネルに変化があったよ！')
            now = datetime.now(JST)

            if before.channel is None:  # ここから入室時の処理
                pretime_dict[member.name] = time.time() 
                msg = f'{now:%m/%d-%H:%M} に {member.name} が {after.channel.name} に参加しました。' # 入室ログ
                await channel.send(msg)
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
                await channel.send(msg)

                # ここから通話時間を記録していく処理
                memberlist[member.name] = memberlist[member.name] + int(roundingtime)
                await channel.send('総接続時間を更新したよ！')

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

# ここからコマンド関連の処理
@client.event
async def on_message(message):
    global memberlist
    if client.user != message.author:

        if message.content == '?help':
            authorname = 'れんあいのくにの乙女🍎'
            authorurl = 'https://github.com/WinterProduce/discordpy-startup/blob/master/discordbot.py'
            authoricon = 'https://cdn.discordapp.com/attachments/508795281299603469/684325828112547850/image_-_2.jpg'
            embed = discord.Embed(title ='私の使い方だよ！', description = 'コマンドと使い方をお見せするね！', color=0X0000FF)
            embed.add_field(name = '?help', value = 'あなたが今見ているこれを表示するよ！', inline=False)
            embed.add_field(name = '?count', value = 'サーバーのメンバーカウントを表示するよ！', inline=False)
            embed.add_field(name = '?vc', value = '全員のおしゃべりした時間を表示するよ！', inline=False)
            embed.add_field(name = '?resetvclist', value = '総接続時間をリセットするよ！', inline=False)
            embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/508795281299603469/684324816525983775/ERn70g_UUAAUx-1.png')
            embed.set_author(name = authorname, url = authorurl, icon_url = authoricon)
            await message.channel.send(embed=embed)

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
            for memberkey, in memberlist.keys():
                await message.channel.send(f'メンバー一覧 : {memberkey}')
    
        if message.content == '?resetvclist':
            if message.author.guild_permissions.administrator: # 管理者しか実行できないようにする
                membername = [member.name for member in client.get_all_members() if not member.bot] # Bot以外のユーザー名を辞書のkeyに入れる処理
                zero = [0,0,0,0,0,0,0,0,0,0,0,0,0,0] # 辞書の値に全員分０を代入
                memberlist = dict(zip(membername, zero)) # リストを使用して辞書に格納
                await message.channel.send('総接続時間をリセットしました！')
            else:
                await message.channel.send('君の権限だと実行できないよ！')
        # 全員の総接続時間と60分以上Inしている人を出力
        if message.content == '?vc':
            channel = client.get_channel(682141572317446167)
            for memberkey, membervalue in memberlist.items():
                await channel.send(f'ユーザー名: {memberkey}  通話時間: {membervalue} 秒')
            for memberkey60, membervalue60 in memberlist.items():
                if membervalue60 >= 3600:
                    vc60 = {memberkey60}
                    await channel.send(f'総接続時間が60分以上のユーザー: {vc60}')
                elif membervalue60 < 3600:
                    vc0 = {memberkey60}
                    await channel.send(f'総接続時間が60分未満のユーザー: {vc0}')
        if message.content == '?in':
            channel = client.get_channel(682141572317446167)

            for inkey, invalue in inmemberlist.items():
                await channel.send(f'ユーザー名: {inkey}  In率: {invalue} 日')
    
            for inkey4, invalue4 in inmemberlist.items():
                if invalue4 >= 4:
                    in4 = {inkey4}
                    await channel.send(f'In率が4日以上のユーザー: {in4}')
                elif invalue4 < 4:
                    in0 = {inkey4}
                    await channel.send(f'In率が4日未満のユーザー: {in0}')

client.run(token)
