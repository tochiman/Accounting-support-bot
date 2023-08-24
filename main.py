import datetime

import discord
import yaml
from discord import Interaction
from discord.ext import commands
from discord.ui import InputText, Modal

# 会計報告用のModal
class ReportModal(Modal):
    def __init__(self):
        super().__init__(
            title="会計報告",
            timeout=None
        )
        # modal内で入力してもらうものを用意
        self.claim=InputText(
            label="請求【「、」区切り】",
            style=discord.InputTextStyle.short,
            placeholder="「委員会名(支出番号)、…」という形で指定",
            required=False
        )
        self.spending=InputText(
            label="支出【「、」区切り】",
            style=discord.InputTextStyle.short,
            placeholder="「委員会名(支出番号)、…」という形で指定",
            required=False
        )
        self.caluculate=InputText(
            label="精算【「、」区切り】",
            style=discord.InputTextStyle.short,
            placeholder="「委員会名(支出番号)、…」という形で指定",
            required=False
        )
        self.content=InputText(
            label="報告内容",
            style=discord.InputTextStyle.paragraph,
            placeholder="報告が複数の場合は「！(全角)」で区切る",
            required=True
        )
        # 上で用意したものをModalに追加する
        self.add_item(self.claim)
        self.add_item(self.spending)
        self.add_item(self.caluculate)
        self.add_item(self.content)
    
    async def callback(self, interaction: Interaction) -> list:
        count = 0
        #区切tったものを取り出してリストで保管
        self.claim_list=list(str(self.claim.value).split("、"))
        self.spending_list=list(str(self.spending.value).split("、"))
        self.caluculate_list=list(str(self.caluculate.value).split("、"))
        self.content_list=list(str(self.content.value).split("！"))

        if "" != self.claim.value: show_embed.add_field(name=f'請求【{len(self.claim_list)}件】',value=f'{self.claim.value}',inline=False)
        if "" != self.spending.value: show_embed.add_field(name=f'支出【{len(self.spending_list)}件】',value=f'{self.spending.value}',inline=False)
        if "" !=  self.caluculate.value: show_embed.add_field(name=f'清算【{len(self.caluculate_list)}件】',value=f'{self.caluculate.value}', inline=False)
        for content in self.content_list:
            count+=1
            show_embed.add_field(name=f'報告【{count}件目】', value=f'・{content}',inline=False)

        await interaction.response.send_message(embed=show_embed)

# 選択用の選択肢を用意する
month_num=[i for i in range(1,13,1)]
weakday_word=["月","火","水","木","金","土","日"]
    
#設定ファイルを読み込む
with open('./config.yaml','r') as yml:
    yml_config=yaml.safe_load(yml)
    bot_token=yml_config['discord']['BOT_TOKEN']
    test_guild_ids=yml_config['discord']['test_guild_ids']

#botのインスタンスを生成
bot = commands.Bot(command_prefix='/',
                description='会計の業務をお助けします',
                intents = discord.Intents.all(),
                help_command=None,
                activity=discord.Game("Python") 
)

# 起動時に実行する処理       
@bot.event
async def on_ready():
    print(f'{bot.user} Ready!!')

@bot.slash_command(name="report",description="【確認用】会計報告用のコマンドです。※全体には送信しません。", guild_ids=[test_guild_ids])
async def report(
    ctx: discord.ApplicationCommand,
    who: discord.Option(discord.Member, "報告者名を入力", required=True),
    month: discord.Option(int, "何月ですか？",choices=month_num, required=True),
    day: discord.Option(int, "何日ですか？(半角数字でお願いします)", required=True),
    weakday: discord.Option(str, "何曜日ですか？", choices=weakday_word, required=True)
):

    # 引数で指定されたユーザの情報を取得
    who_id = who.id
    user = bot.get_user(who_id)

    global show_embed
    show_embed = discord.Embed(title='【会計報告】',color=discord.Colour.from_rgb(3,3,3))
    show_embed.add_field(name='日付', value=f'{month}月{day}日({weakday})', inline=False)
    show_embed.set_footer(text=user.name,icon_url=user.avatar)

    modal = ReportModal()
    await ctx.response.send_modal(modal=modal)
    


#discordのhelpコマンドを削除
bot.remove_command('help')
#bot起動
bot.run(bot_token)