#管理関係
#-------------------------
#コマンド一覧
#/help : com_help
#/commandlist : com_commandlist
#/list : com_list
#/read : com_read
#/key_gen : com_key_gen
#/key_remove : com_key_remove
#/check_license : com_check_license
#/list_licenses : com_list_licenses
#/test : com_test
#/license_backup : com_license_backup
#/license_up : com_license_up
#/mention : com_mention
#/gench : com_gench
#/dm : com_dm
#btest : com_btest
#-------------------------

import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord import Embed
import os
from datetime import datetime, timedelta, timezone
import random
import string
import pytz
import json
import time
import platform


BLUE = "\033[34m"
RESET = "\033[0m"
ZONE ="     "
INFO = BLUE+" INFO"+RESET
#-----------------
TOKEN = "********"
GUILD_ID = 1310161717803876372
ALLOWED_USER_ID = 1154120232638627970
LOG_CHANNEL_ID = 1313738109577592883
version = "不明"
LICENSE_CATEGORY_NAME = "?license"
LICENSE_FILE = "licenses.json"
ICONIMG = "https://raw.githubusercontent.com/kazecom/N_answer_file/refs/heads/main/zen.png"
HELPIMG ="https://raw.githubusercontent.com/kazecom/N_answer_file/refs/heads/main/howtouse.png"
start_time = time.time()

os.system('clear')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_licenses():
    if os.path.exists(LICENSE_FILE) and os.path.getsize(LICENSE_FILE) > 0:
        with open(LICENSE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_licenses(licenses):
    with open(LICENSE_FILE, 'w') as file:
        json.dump(licenses, file, indent=4)

licenses = load_licenses()

@bot.event
async def on_ready():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now}{INFO}{ZONE}Bot {bot.user} が起動しました！")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"{now}{INFO}{ZONE}指定されたギルド: {guild.name} ({guild.id})")
    else:
        print(f"{now} WARN     指定されたギルドが見つかりませんでした。")
    await update_version()
    update_status.start()
    await bot.tree.sync()
    print(f"{now}{INFO}{ZONE}スラッシュコマンドが同期されました。")
    await send_log(f"{now}Botが正常に起動しました。バージョン: {version}")
    print(f"{now}{INFO}{ZONE}Botが正常に起動しました。バージョン: {version}")
    print("--------------------------------------------------------------------------")

async def get_license_channel(user_id: int):
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return None
    license_category = discord.utils.get(guild.categories, name=LICENSE_CATEGORY_NAME)
    if not license_category:
        return None

    license_channel_name = f"license-{user_id}"
    return discord.utils.get(license_category.text_channels, name=license_channel_name)

@tasks.loop(seconds=30) 
async def update_status():
    total_reports = await count_reports() 
    await bot.change_presence(activity=discord.Game(f"{total_reports} 個のレポに対応 v.{version}"))

async def count_reports():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return 0

    total_reports = 0

    for category in guild.categories:
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel): 
                if channel.name.endswith("確認") or channel.name.endswith("最終"):
                    total_reports += 1

    return total_reports

async def send_log(message: str):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("指定されたギルドが見つかりませんでした。")
        return

    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if not log_channel or not isinstance(log_channel, discord.TextChannel):
        print("指定されたログチャンネルが見つかりませんでした。")
        return

    await log_channel.send(message)

async def update_version():
    global version
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("指定されたギルドが見つかりません。")
        return

    config_category = discord.utils.get(guild.categories, name="?config")
    if not config_category:
        print("`?config` カテゴリーが見つかりません。")
        return

    ver_channel = discord.utils.get(config_category.channels, name="ver")
    if not ver_channel or not isinstance(ver_channel, discord.TextChannel):
        print("`ver` チャンネルが見つかりません。")
        return

    try:
        # 最新メッセージを取得
        async for message in ver_channel.history(limit=1):
            version = message.content.strip()  # 内容を格納
            print(f"{now}{INFO}{ZONE}バージョン情報を更新しました: {version}")
            return
    except Exception as e:
        print(f"`ver` チャンネルからの情報取得中にエラーが発生しました: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        await message.channel.send("こんにちは！メンションされました。")

    await bot.process_commands(message)

    


#com_help
@bot.tree.command(name="help", description="Botの使い方を説明します")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed()

    embed.set_author(name="help",
                 icon_url="https://raw.githubusercontent.com/kazecom/N_answer_file/refs/heads/main/zen.png")

    embed.add_field(name="ライセンスを所持していません。と表示される",
                value="ライセンスがあなたのアカウントに付与されていない状態です\n/dmを使用して管理者までお問い合わせをお願います",
                inline=False)
    embed.add_field(name="-----------------------",
                value="",
                inline=False)
    embed.add_field(name="このコマンドを実行する権限がありません。と表示される",
                value="実行しようとしているコマンドが管理者用コマンドの場合に表示されます\n一般ユーザーが使用することはできません",
                inline=False)
    
    embed.set_footer(text=f"質問があれば/dmへ  ver.{version}")

    await interaction.response.send_message(embed=embed)


#com_commandlist
@bot.tree.command(name="commandlist", description="コマンド一覧を表示します")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed()

    embed.set_author(name="command.list",
                     icon_url=f"{ICONIMG}")

    embed.add_field(name="コマンド一覧",
                    value="",
                    inline=False)
    embed.add_field(name="/help",
                    value="Botの使い方など、様々な情報を表示します。",
                    inline=False)
    embed.add_field(name="/commandlist",
                    value="一般ユーザーが使用できるコマンドのリストを表示します。",
                    inline=False)
    embed.add_field(name="-----------------------",
                    value="",
                    inline=False)
    embed.add_field(name="/list",
                    value="利用可能な教科と回数の一覧を表示します。\n教科名を指定すると指定した教科のみ見ることができます。\n例 : `/list 教科名:数学`",
                    inline=False)
    embed.add_field(name="/read",
                    value="指定した教科・回数・レポートタイプに対応するテキストを表示します。\n例: `/read 教科名:数学 第何回:1 レポートタイプ:最終`",
                    inline=False)
    embed.add_field(name="-----------------------",
                    value="",
                    inline=False)
    embed.add_field(name="/check_license",
                    value="自身のアカウントに付与されている\nライセンスの有効期限を表示することができます\n(ライセンスがない場合などは有効期限は表示されません)",
                    inline=False)
    embed.add_field(name="-----------------------",
                    value="",
                    inline=False)
    embed.add_field(name="/mention",
                    value="相手と回数を指定することで自動でメンションを行います\n別でチャンネルが作られるため実行したチャンネルに害はありません\n例 : `/mention users:@k0_e  time:20`",
                    inline=False)
    embed.add_field(name="/dm",
                    value="BOT管理者に直接DMを送ることができます\nエラーなどの際に使用していただけると\n対応が早くなる可能性があります",
                    inline=False)

    embed.set_image(url=f"{HELPIMG}")

    embed.set_footer(text=f"質問があれば/dmへ  ver.{version}")

    await interaction.response.send_message(embed=embed)

#com_list
@bot.tree.command(name="list", description="利用可能なグループと番号の一覧を送信します")
async def list_groups(interaction: discord.Interaction):
    is_valid = await check_license(interaction, interaction.user.id)
    if is_valid:
        guild = bot.get_guild(GUILD_ID)
        if guild is None:
            await interaction.response.send_message("指定されたギルドが見つかりませんでした。")
            return

        groups = {}
        for category in guild.categories:
            if category.name.startswith("!"):
                continue  # カテゴリー名が「!」で始まる場合はスキップ

            for channel in category.channels:
                if isinstance(channel, discord.TextChannel) and (channel.name.endswith("確認") or channel.name.endswith("最終")):
                    group_name = category.name
                    number = channel.name  # チャンネル名をそのまま使用

                    # チャンネル名の形式を整える
                    if "最終" in number:
                        formatted_number = f"第{number.split('_')[0]}・最終"
                    else:
                        # 回数を初期化
                        回数 = number.split('_')[1] if '_' in number else "不明"
                        formatted_number = f"第{number.split('_')[0]}・{回数}"

                    if group_name not in groups:
                        groups[group_name] = []
                    groups[group_name].append(formatted_number)

        embed = discord.Embed(
            title="利用可能な教科・番号",
            color=0x3498db
        )

        if not groups:
            embed.description = "利用可能なグループは見つかりませんでした。"
        else:
            for group, numbers in groups.items():
                embed.add_field(name=f"**{group}**", value=', '.join(numbers), inline=False)
        try:
            await interaction.response.send_message(embed=embed)
        except discord.HTTPException as e:
            print(f"エラーメッセージの送信中にエラーが発生しました: {e}")
    else:
        return

#com_read
@bot.tree.command(name="read", description="指定したレポートを送信します")
@app_commands.describe(
    教科名="教科名を選択してください",
    第何回="第何回かを指定してください",
    レポートタイプ="確認か最終を選択してください",
    何回="確認の回数を指定してください（任意）"
)
@app_commands.choices(
    教科名=[
        app_commands.Choice(name="家庭総合", value="家庭総合"),
        app_commands.Choice(name="数学A", value="数学A"),
        app_commands.Choice(name="生物基礎", value="生物基礎"),
        app_commands.Choice(name="総合的な探求の時間2", value="総合的な探求の時間2"),
        app_commands.Choice(name="体育2", value="体育2"),
        app_commands.Choice(name="特別活動2", value="特別活動2"),
        app_commands.Choice(name="日本史探求", value="日本史探求"),
        app_commands.Choice(name="美術1", value="美術1"),
        app_commands.Choice(name="保健", value="保健"),
        app_commands.Choice(name="論理表現1", value="論理表現1"),
        app_commands.Choice(name="論理国語", value="論理国語"),
    ],
    レポートタイプ=[
        app_commands.Choice(name="確認", value="確認"),
        app_commands.Choice(name="最終", value="最終"),
    ]
)
async def read(
    interaction: discord.Interaction,
    教科名: app_commands.Choice[str],
    第何回: int,
    レポートタイプ: app_commands.Choice[str],
    何回: int = None,
):
    is_valid = await check_license(interaction, interaction.user.id)
    if is_valid:
        guild = bot.get_guild(GUILD_ID)
        if guild is None:
            await interaction.response.send_message("指定されたギルドが見つかりませんでした。")
            return

        category = discord.utils.get(guild.categories, name=教科名.value)
        if not category:
            await interaction.response.send_message(f"教科「{教科名.value}」のカテゴリーが見つかりませんでした。")
            return

        channel_name = f"{第何回}_{何回}_{レポートタイプ.value}" if レポートタイプ.value == "確認" and 何回 is not None else f"{第何回}_{レポートタイプ.value}"
        if レポートタイプ.value == "最終":
            channel_name = f"{第何回}_{レポートタイプ.value}"

        channel = discord.utils.get(category.text_channels, name=channel_name)
        if not channel:
            await interaction.response.send_message(f"指定された教科と条件に一致するチャンネル「{channel_name}」が見つかりませんでした。")
            return

        if channel:
            messages = []
            async for message in channel.history(limit=10):
                messages.append(message.content)

            content = "\n".join(messages)

            embed = discord.Embed(
                title=f"第{第何回}回・{レポートタイプ.value}",
                description=content,
                color=0x1abc9c,
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("指定されたチャンネルが見つかりませんでした。")
    else:
        return

async def remove_license(user_id: int):
    global licenses
    if str(user_id) in licenses:
        del licenses[str(user_id)]
        save_licenses(licenses)
        return f"ユーザー {user_id} からライセンスを削除しました。"
    else:
        return "指定されたユーザーにはライセンスが付与されていません。"

#com_key_gen
@bot.tree.command(name="key_gen", description="ライセンスキーを生成してユーザーに付与します")
@app_commands.describe(user_id="ライセンスを付与するユーザーのID", expiration_datetime="ライセンスの有効期限（YYYYMMDDHHMMSS形式）")
async def key_gen(interaction: discord.Interaction, user_id: str, expiration_datetime: str):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
        return

    if not user_id.isdigit():
        await interaction.response.send_message("無効なユーザーIDです。整数で入力してください。", ephemeral=True)
        return

    user_id = int(user_id)
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        await interaction.response.send_message("指定されたギルドが見つかりませんでした。", ephemeral=True)
        return

    try:
        user = await guild.fetch_member(user_id)
    except discord.NotFound:
        user = None 
    except discord.Forbidden:
        await interaction.response.send_message("Botにユーザー情報を取得する権限がありません。", ephemeral=True)
        return
    except discord.HTTPException:
        await interaction.response.send_message("ユーザー情報の取得中にエラーが発生しました。", ephemeral=True)
        return

    try:
        expiration_date = datetime.strptime(expiration_datetime, '%Y%m%d%H%M%S')
    except ValueError:
        await interaction.response.send_message("無効な日付形式です。", ephemeral=True)
        return

    def generate_license_key():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    license_key = generate_license_key()
    licenses[str(user_id)] = {
        "license_key": license_key,
        "expiration_date": expiration_date.strftime('%Y-%m-%d %H:%M:%S')
    }
    save_licenses(licenses)

    dm_message = f"ライセンスキーが発行されました\nライセンスキー: {license_key}\n有効期限: {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}"
    if user is not None:
        try:
            await user.send(dm_message)
        except discord.Forbidden:
            dm_message = "ユーザーにDMを送信できませんでした。ユーザーのDM設定を確認してください。"

    await interaction.response.send_message(f"ユーザー {user_id} にライセンスを付与しました。ライセンスキーは `{license_key}` で、期限は {expiration_date.strftime('%Y-%m-%d %H:%M:%S')} です。\n{dm_message}", ephemeral=True)

#com_key_remove
@bot.tree.command(name="key_remove", description="ユーザーからライセンスを削除します")
@app_commands.describe(user_id="ライセンスを削除するユーザーのID")
async def key_remove(interaction: discord.Interaction, user_id: str):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
        return

    if not user_id.isdigit():
        await interaction.response.send_message("無効なユーザーIDです。整数で入力してください。", ephemeral=True)
        return

    user_id = int(user_id)
    message = await remove_license(user_id)
    await interaction.response.send_message(message, ephemeral=True)

#com_check_license
@bot.tree.command(name="check_license", description="自分のライセンス情報を確認します")
async def check_license_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    license_info = licenses.get(str(user_id))

    if not license_info:
        await interaction.response.send_message("ライセンスを所持していません。", ephemeral=True)
        return

    expiration_date_str = license_info["expiration_date"]

    try:
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        current_time = datetime.now(tokyo_tz)
        expiration_date = tokyo_tz.localize(datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S'))
    except ValueError:
        await interaction.response.send_message("ライセンスの有効期限が無効です。", ephemeral=True)
        return

    if expiration_date < current_time:
        await interaction.response.send_message("ライセンスの有効期限が切れています。", ephemeral=True)
        return

    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    await interaction.response.send_message(f"現在の時間: {current_time_str}\nライセンスは有効です。有効期限: {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}", ephemeral=True)

#com_list_licenses
@bot.tree.command(name="list_licenses", description="全てのライセンス情報をリストで表示します")
async def list_licenses(interaction: discord.Interaction):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
        return

    if not licenses:
        await interaction.response.send_message("現在、ライセンスを持っているユーザーは一人もいません。", ephemeral=True)
        return

    license_list = []
    for user_id, info in licenses.items():
        license_list.append(f"ユーザー {user_id}: 有効期限 {info['expiration_date']}")

    await interaction.response.send_message("\n".join(license_list), ephemeral=True)

#com_test
@bot.tree.command(name="test", description="ライセンスを用いたコマンド実行のテスト用です")
async def test_command(interaction: discord.Interaction):
    is_valid = await check_license(interaction, interaction.user.id)
    if is_valid:
        await interaction.response.send_message("ライセンスが有効です。", ephemeral=True)
    else:
        return

async def check_license(interaction: discord.Interaction, user_id: int):
    license_info = licenses.get(str(user_id))

    if not license_info:
        await interaction.response.send_message("ライセンスを所持していません。", ephemeral=True)
        return False

    expiration_date_str = license_info["expiration_date"]

    try:
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        current_time = datetime.now(tokyo_tz)
        expiration_date = tokyo_tz.localize(datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S'))
    except ValueError:
        await interaction.response.send_message("ライセンスの有効期限が無効です。", ephemeral=True)
        return False

    if expiration_date < current_time:
        await interaction.response.send_message("ライセンスの有効期限が切れています。", ephemeral=True)
        return False

    return True 

#com_license_backup
@bot.tree.command(name="license_backup", description="ライセンス情報をバックアップしてDMで送信します")
async def license_backup(interaction: discord.Interaction):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
        return

    if os.path.exists(LICENSE_FILE) and os.path.getsize(LICENSE_FILE) > 0:
        with open(LICENSE_FILE, 'r') as file:
            licenses_content = file.read()
    else:
        await interaction.response.send_message("ライセンス情報が見つかりませんでした。", ephemeral=True)
        return

    try:
        await interaction.user.send(f"ライセンス情報のバックアップ:\n```json\n{licenses_content}\n```")
        await interaction.response.send_message("ライセンス情報のバックアップをDMで送信しました。", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("ユーザーにDMを送信できませんでした。ユーザーのDM設定を確認してください。", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"エラーが発生しました: {e}", ephemeral=True)

#com_license_up
@bot.tree.command(name="license_up", description="ライセンス情報をアップロードして上書きします")
@app_commands.describe(file="アップロードするファイル")
async def license_up(interaction: discord.Interaction, file: discord.Attachment):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
        return

    if not file.filename.endswith(".json"):
        await interaction.response.send_message("無効なファイル形式です。JSONファイルをアップロードしてください。", ephemeral=True)
        return

    try:
        file_content = await file.read()
    except Exception as e:
        await interaction.response.send_message(f"ファイルのダウンロード中にエラーが発生しました: {e}", ephemeral=True)
        return
    
    try:
        with open(LICENSE_FILE, 'wb') as f:
            f.write(file_content)
        await interaction.response.send_message("ライセンス情報を正常にアップロードしました。", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"ファイルの保存中にエラーが発生しました: {e}", ephemeral=True)

#com_mention
@bot.tree.command(name='mention', description='指定したユーザーをメンションします。')
@app_commands.describe(
    users='メンションする相手を指定します（@ユーザー形式で複数指定可）。',
    time='メンションする回数を指定します (1-100)。',
    message='メンション以外に送るメッセージを指定します。'
)
async def mention(interaction: discord.Interaction, users: str, time: int, message: str = None):
    # 時間のバリデーション
    if not isinstance(time, int) or not (1 <= time <= 100):
        await interaction.response.send_message("メンション回数は1から100の間の数字で指定してください。", ephemeral=True)
        return

    # 一時的な応答
    await interaction.response.defer(ephemeral=True)

    # ユーザーをメンション形式で取得
    user_mentions = users.split()

    # チャンネル名の生成
    now = datetime.now()
    channel_name = f"{now.strftime('%Y-%m-%d_%H-%M')}-{interaction.user.name}"
    
    # チャンネルの作成
    guild = interaction.guild
    new_channel = await guild.create_text_channel(name=channel_name)
    await new_channel.send(f'新しいチャンネルが作成されました: {new_channel.mention}')

    # 進捗表示のためのメッセージをコマンドを実行したチャンネルに送信
    progress_message = await interaction.followup.send("実行します", ephemeral=False)

    # メンションの実行
    for i in range(time):
        # メンションを送信
        mentions = ' '.join(user_mentions)  # メンション形式でそのまま使用
        await new_channel.send(f'{mentions} {message if message else ""}')
        
        # 進捗の更新
        completed = (i + 1) * 100 // time  # 完了した進捗を計算
        progress_squares = completed // 5  # 完了した進捗に応じて絵文字数を計算
        progress = ":green_square:" * progress_squares + ":black_large_square:" * (20 - progress_squares)
        
        progress_display = f"{progress} {completed}%/{100}%"
        
        # 進捗メッセージを編集
        await progress_message.edit(content=progress_display)

    # メンション完了のメッセージを全員に送信
    await interaction.channel.send(f'{interaction.user.display_name} がメンションを実行しました。新しく作成されたチャンネル: {new_channel.mention}')

    # チャンネル削除ボタンの作成
    button = discord.ui.Button(label="チャンネルを削除", style=discord.ButtonStyle.danger)
    
    async def button_callback(button_interaction: discord.Interaction):
        # チャンネルが存在するか確認
        if new_channel:
            try:
                await new_channel.delete()
                await button_interaction.response.send_message("チャンネルが削除されました。", ephemeral=True)
            except discord.NotFound:
                await button_interaction.response.send_message("チャンネルは既に削除されています。", ephemeral=True)
        else:
            await button_interaction.response.send_message("チャンネルは既に削除されています。", ephemeral=True)

    button.callback = button_callback

    # ボタンを含むメッセージをコマンドを実行したチャンネルに送信
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    await new_channel.send("以下のボタンでチャンネルを削除できます。", view=view)

#com_gench
@bot.tree.command(name='gench', description='管理用チャンネルを作成する')
@app_commands.describe(
    subject='教科名',
    number='第何回',
    report_type='レポートタイプ',
    report_number='何番'
)
@app_commands.choices(
    report_type=[
        app_commands.Choice(name="確認", value="確認"),
        app_commands.Choice(name="最終", value="最終"),
    ]
)
async def gench(
    interaction: discord.Interaction, 
    subject: str, 
    number: int, 
    report_type: app_commands.Choice[str],  # 選択肢式に変更
    report_number: int = None
):
    # ユーザーの権限を確認
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("あなたにはこのコマンドを使用する権限がありません。", ephemeral=True)
        return
    
    # オプションの検証
    valid_subjects = [
        "家庭総合", "論理国語", "日本史探求", "数学A", "保健",
        "論理表現1", "美術1", "生物基礎", "体育2", 
        "総合的な探求の時間2", "特別活動2"
    ]
    
    if subject not in valid_subjects:
        await interaction.response.send_message("無効な教科名です。", ephemeral=True)
        return
    
    if not (1 <= number <= 99):
        await interaction.response.send_message("第何回は1桁から2桁の整数で指定してください。", ephemeral=True)
        return

    # report_type の値を確認
    if report_type.name not in ["確認", "最終"]:
        await interaction.response.send_message("無効なレポートタイプです。確認または最終を選択してください。", ephemeral=True)
        return

    if report_type.name == "確認" and report_number is None:
        await interaction.response.send_message("レポートタイプが確認の場合、何番を指定してください。", ephemeral=True)
        return

    # カテゴリーを検索
    guild = bot.get_guild(GUILD_ID)
    category = discord.utils.get(guild.categories, name=subject)

    if category is None:
        await interaction.response.send_message(f"{subject}のカテゴリーは存在しません。", ephemeral=True)
        return

    # チャンネル名を設定
    if report_type.name == "確認":
        channel_name = f"{number}_{report_number}_確認"
    else:
        channel_name = f"{number}_最終"

    # チャンネルを作成
    await guild.create_text_channel(channel_name, category=category)
    await interaction.response.send_message(f"チャンネル '{channel_name}' が '{subject}' カテゴリーに作成されました。", ephemeral=True)

#com_dm
@bot.tree.command(name='dm', description='管理人にDMを送信します')
async def dm(interaction: discord.Interaction, message: str):
    # DMを送信するユーザーを取得
    user = await bot.fetch_user(ALLOWED_USER_ID)

    # 招待URLを作成（権限が必要）
    invite = None
    for channel in interaction.guild.text_channels:
        if channel.permissions_for(interaction.guild.me).create_instant_invite:
            invite = await channel.create_invite(max_age=0,max_uses=1)  # 無期限の招待と1回の使用期限
            break

    # 埋め込みメッセージを作成
    embed = discord.Embed(title="新しいメッセージ", color=discord.Color.blue())
    embed.add_field(name="送信者", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)

    # アバターが存在する場合のみサムネイルを設定
    if interaction.user.avatar:
        embed.set_thumbnail(url=interaction.user.avatar.url)

    embed.add_field(name="送信時間", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)

    # サーバー名と招待URLを追加
    server_name = interaction.guild.name
    if invite:
        embed.add_field(name=f"送信サーバー: {server_name}", value=f"[招待リンク]({invite})", inline=False)
    else:
        embed.add_field(name="送信サーバー", value=server_name, inline=False)

    # サーバーアイコンが存在する場合のみ追加
    if interaction.guild.icon:
        embed.set_footer(text="サーバーアイコン", icon_url=interaction.guild.icon.url)  # フッターにサーバーアイコンを追加

    embed.add_field(name="メッセージ内容", value=message, inline=False)

    # エラー回避
    await interaction.response.defer(ephemeral=True)

    total_steps = 1

    await user.send(embed=embed)

    completed = 100
    progress_squares = completed // 5  
    progress = ":green_square:" * progress_squares + ":black_large_square:" * (20 - progress_squares)

    progress_display = f"{progress} {completed}%/{100}%"

    progress_message = await interaction.followup.send(content=f"{progress} {completed}%/{100}%", ephemeral=True)

    await progress_message.edit(content=progress_display)

    await progress_message.edit(content="メッセージの送信が完了しました。")

#com_btest
@bot.tree.command(name='btest', description='Ping値、起動からの経過時間を表示します')
async def dtest(interaction: discord.Interaction):
    #Ping値を取得
    ping = round(bot.latency * 1000)
    #経過時間を計算
    elapsed_time = time.time() - start_time
    elapsed_time_str = f"{int(elapsed_time // 3600)}時間 {int((elapsed_time % 3600) // 60)}分 {int(elapsed_time % 60)}秒"

    embed = discord.Embed(title="Botのステータス", color=0x00ff00)
    embed.add_field(name="Ping", value=f"{ping} ms", inline=False)
    embed.add_field(name="起動からの経過時間", value=elapsed_time_str, inline=False)

    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)