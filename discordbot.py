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
inmemberlist = {}
mute_dict = {}
JST = timezone(timedelta(hours=+9), 'JST')

token = os.environ['DISCORD_BOT_TOKEN']

# Botログイン処理
@client.event
async def on_ready():
    print('起動完了しました！')
    print(client.user.name)
    print(client.user.id)
    print('------')
    channel = client.get_channel(682141572317446167)
    await channel.send('今から活動開始します！')
    await Resetvclist()
    await channel.send('再起動に伴い総接続時間をリセットしました')
    await Resetinlist()
    await channel.send('再起動に伴いIn率をリセットしました')
    
    activity = discord.Game(name='おしごと🍎')
    await client.change_presence(activity=activity)

# 指定時間に総接続時間をリセットする処理
async def Resetvclist():
    global memberlist
    membername = [member.name for member in client.get_all_members() if not member.bot] # Bot以外のユーザー名を辞書のkeyに入れる処理
    zero = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # 辞書の値に全員分０を代入
    memberlist = dict(zip(membername, zero)) # リストを使用して辞書に格納

    channel = client.get_channel(682141572317446167)
    await channel.send('総接続時間をリセットしたよ！')

async def Resetinlist():
    global inmemberlist
    inmembername = [member.name for member in client.get_all_members() if not member.bot] # Bot以外のユーザー名を辞書に入れる処理
    inmemberzero = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    inmemberlist = dict(zip(inmembername, inmemberzero)) # In率処理の辞書作成

    channel = client.get_channel(682141572317446167)
    await channel.send('In率をリセットしたよ！')

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
            inmemberlist[memberkey0] = inmemberlist[memberkey0] + 1
        else:
            return
    print(inmemberlist)
    await channel.send('昨日の0時0分より今までにInした人を記録したよ！')

# ６０秒に一回ループさせる処理
@tasks.loop(seconds=60)
async def weekloop():
    checktime = datetime.now(JST).strftime('%a-%H:%M')
    channel = client.get_channel(682141572317446167)
    if checktime == 'Mon-00:00':
        await channel.send('月曜日の０時０分になったから総接続時間を出力してデータをクリアするね！')
        await Sendvclist()
        await Resetvclist()
        await Sendinlist()
        await Resetinlist()

@tasks.loop(seconds=60)
async def dayloop():
    checkday = datetime.now(JST).strftime('%H:%M')
    if checkday == '01:00':
        channel = client.get_channel(682141572317446167)
        await channel.send('前日、Inしたかどうかを検知して記録するね！')
        await Incheck()

# ここからボイスチャンネルの入退出を検知する処理
@client.event
async def on_voice_state_update(member, before, after): 
    global pretime_dict # 入退出時刻を記録する辞書
    global memberlist # VCの１週間の記録用の辞書
    global mute_dict # Mute時間を記録する辞書
    global mutehours
    global muteminutes
    global muteseconds
    channel = client.get_channel(682141572317446167)
    oneroom = [681867519379767322, 681867557627756613, 681867619246145550, 681867705329909765, 681867763505037321, 681867861937225729, 681867973127962792, 681868176501506079]

    if member.guild.id == 681853809789501440 and (before.channel != after.channel): # 特定のサーバーだけ処理が行われるように

        if not member.bot: # Botだった場合弾く処理
            print('ボイスチャンネルに変化があったよ！')
            now = datetime.now(JST)

            # Mute状態になった時の処理
            if before.self_mute is None:
                mute_dict[member.name] = time.time()
                msg = f'{now:%m/%d-%H:%M} に {member.name} さんが ミュートにしたよ！'
                await channel.send(msg)
                print(msg)
                print(f'ミュート状態の変更を検知したため辞書を更新したよ！ {mute_dict}')

            # Mute状態が解除された時の処理
            elif after.self_mute is None:
                mutetime = time.time() - mute_dict[member.name] # ミュート状態の時間を計算
                rounding_mute = round((mutetime / 1), 1) # 経過時間の小数点一桁で四捨五入

                # mutetimeを時、分、秒に変換する処理
                mutehours = 0
                muteminutes = 0
                muteseconds = rounding_mute

                # 1分以上1時間未満の通話時間の処理
                if 3600 > rounding_mute >= 60:
                    muteminutes = rounding_mute /60
                    muteseconds = rounding_mute % 60

                # 1時間以上の通話時間の処理
                elif rounding_mute >= 3600:
                    mutehours = rounding_mute / 3600
                    interimendmuteminutes = rounding_mute % 3600
                    muteminutes = interimendmuteminutes /60
                    muteseconds = interimendmuteminutes % 60
                msg = f'{now:%m/%d-%H:%M} に {member.name} さんが ミュート状態を解除したよ！ ミュート時間は {int(mutehours)} 時間 {int(muteminutes)} 分 {int(muteseconds)} 秒だったよ！'
                print(msg)
                print(f'ミュート状態の変更を検知したため辞書を更新したよ！ {mute_dict}')

            elif before.channel is None:  # ここから入室時の処理
                if not after.channel.id in oneroom:
                    pretime_dict[member.name] = time.time() 
                    msg = f'{now:%m/%d-%H:%M} に {member.name} さんが {after.channel.name} に参加したよ！' # 入室時メッセージ
                    await channel.send(msg)
                    print(msg)
                    print(f'入室を検知したため辞書を更新したよ！{pretime_dict}')

                # 直接個通部屋に入った時の処理
                elif after.channel.id in oneroom:
                    pretime_dict[member.name] = time.time()
                    msg = f'{now:%m/%d-%H:%M} に {member.name} さんが 個通部屋 {after.channel.name} に入室したよ！' # 入室メッセージ
                    await channel.send(msg)
                    print(msg)
                    print(f'入室を検知したため辞書を更新したよ！{pretime_dict}')

            elif after.channel is None: # 退出時の処理
                duration_time = time.time() - pretime_dict[member.name] # 入室時からの経過時間を計算
                roundingtime = round((duration_time / 1), 1) # 経過時間の小数点一桁で四捨五入

                # ここから原始的な方法でduration_timeを時間、分、秒に変換
                endhours = 0
                endminutes = 0
                endseconds = roundingtime

                # 1分以上1時間未満の通話時間の場合の処理
                if 3600 > roundingtime >= 60:
                    endminutes = roundingtime / 60
                    endseconds = roundingtime % 60

                # 1時間以上の通話時間の場合の処理
                elif roundingtime >= 3600:
                    endhours = roundingtime / 3600
                    interimendminutes = roundingtime % 3600
                    endminutes = interimendminutes / 60
                    endseconds = interimendminutes % 60

                # 退出時のメッセージ
                msg = f'{now:%m/%d-%H:%M} に {member.name} さんが {before.channel.name} から退出したよ！ 通話時間は {int(endhours)} 時間 {int(endminutes)} 分 {int(endseconds)} 秒で \n ミュート時間は {int(mutehours)} 時間 {int(muteminutes)} 分 {int(muteseconds)} 秒だったよ！' 
                await channel.send(msg)
                print(msg)
                print(f'退室を検知したため辞書を更新したよ！{pretime_dict}')

                # ここから通話時間を記録していく処理
                memberlist[member.name] = memberlist[member.name] + int(roundingtime)
                await channel.send('総接続時間を更新したよ！')
            
            # 個通部屋入室を検知
            elif after.channel.id in oneroom:
                msg = f'{now:%m/%d-%H:%M} に {member.name} さんが 個通部屋 {after.channel.name} に入室したよ！'
                await channel.send(msg)
                print(msg)

            # ここから部屋移動を通知する処理
            elif before.channel != after.channel:
                msg = f'{now:%m/%d-%H:%M} に {member.name} さんが {before.channel.name} から {after.channel.name} に移動したよ!'
                await channel.send(msg)
                print(msg)

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
    "過去の恋愛の失敗談とか...ある？",
    "学生時代にやってた部活とかある？",
    "子供のころどんな性格だった？",
    "小学生の時どんな遊びが流行ったー？",
    "好きだった給食ってなに！？",
    "駄菓子何が好きだった？",
    "卒業文集何書いた？",
    "移動教室で一番テンション上がったとこどこ！？",
    "好きな食べ物なに？",
    "出身地どこ？",
    "出身地の観光スポット教えてよ！",
    "方言で喋ってみよ！",
    "休日何してるー？",
    "今なら笑える失敗談とか話してみる？",
    "生で見たことある有名人いる？",
    "もし宝くじで一億円当たったらどう使う？",
    "もしも、１日だけ性別が変わったら何をしてみたい？",
    "飼うなら猫？犬？どっち！",
    "ハンバーガーならマクド派？モス派？",
    "目玉焼きに何かける？",
    "朝ごはん、パン派？ごはん派？",
    "学生時代、部活とかやってた？",
    "学生の頃の、これはうちの学校だけだろ！っていう校則とかあったｗ？",
    "名前の由来教えてよ！",
    "今日の夜ごはん何？",
    "最後に付き合ったのいつ？",
]

# ここからコマンド関連の処理
@client.event
async def on_message(message):
    global memberlist
    global inmemberlist
    if client.user != message.author:

        # ?helpでembedを表示させる処理
        if message.content == '?help':
            authorname = 'れんあいのくにの乙女🍎'
            authorurl = 'https://github.com/WinterProduce/discordpy-startup/blob/master/discordbot.py'
            authoricon = 'https://cdn.discordapp.com/attachments/508795281299603469/684325828112547850/image_-_2.jpg'
            embed = discord.Embed(title ='私の使い方だよ！', description = 'コマンドと使い方をお見せするね！', color=0X0000FF)
            embed.add_field(name = '?help', value = 'あなたが今見ているこれを表示するよ！', inline=False)
            embed.add_field(name = '?wadai', value = 'みんなに話題を提供するよ！', inline = False)
            embed.add_field(name = '?count', value = 'サーバーのメンバーカウントを表示するよ！', inline=False)
            embed.add_field(name = '?members', value = 'メンバー一覧を表示するよ！', inline = False)
            embed.add_field(name = '?vc', value = '全員のおしゃべりした時間を表示するよ！', inline=False)
            embed.add_field(name = '?in', value = '全員のIn率を表示するよ！', inline = False)
            embed.add_field(name = '?resetvclist', value = '総接続時間をリセットするよ！', inline=False)
            embed.add_field(name = '?resetinlist', value = 'In率リストをリセットするよ！', inline = False)
            embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/508795281299603469/684324816525983775/ERn70g_UUAAUx-1.png')
            embed.set_author(name = authorname, url = authorurl, icon_url = authoricon)
            await message.channel.send(embed=embed)

        # 話題リストにある話題をランダムに出力する処理
        if message.content == '?wadai':
            choice = random.choice(wadai)
            await message.channel.send(choice)

        # メンバー、ユーザー、Bot数をそれぞれ出力する処理
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

        # メンバーの名前をすべて出力する処理
        if message.content == '?members':
            for memberkey, in memberlist.keys():
                await message.channel.send(f'メンバー一覧 : {memberkey}')

        # 総接続時間の辞書の値すべてに0を代入する処理
        if message.content == '?resetvclist':
            if message.author.guild_permissions.administrator: # 管理者しか実行できないようにする
                membername = [member.name for member in client.get_all_members() if not member.bot] # Bot以外のユーザー名を辞書のkeyに入れる処理
                zero = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # 辞書の値に全員分０を代入
                memberlist = dict(zip(membername, zero)) # リストを使用して辞書に格納
                await message.channel.send('総接続時間をリセットしたよ！')

            else:
                await message.channel.send('君の権限だと実行できないよ！')

        # In率辞書の値すべてに0を代入する処理
        if message.content == '?resetinlist':
            if message.author.guild_permissions.administrator:
                inmembername = [member.name for member in client.get_all_members() if not member.bot] # Bot以外のユーザー名を辞書に入れる処理
                inmemberzero = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                inmemberlist = dict(zip(inmembername, inmemberzero)) # In率処理の辞書作成
                await message.channel.send('In率リストをリセットしたよ！')

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

        # 全員のIn率と4日以上Inしている人を出力
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

# ループ処理実行
weekloop.start()
dayloop.start()

# Botスタート
client.run(token)
