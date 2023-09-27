from datetime import datetime
from zoneinfo import ZoneInfo
import NextcloudOperator
import discord
import yaml
from discord import Interaction
from discord.ext import commands
from discord.ui import InputText, Modal, View, Button
import random, string

# 選択用の選択肢を用意する
month_num=[i for i in range(1,13,1)]
weakday_word=["月","火","水","木","金","土","日"]
document_list=["請求書","精算書","事後請求(請求書&精算書)","その他"]
    
#設定ファイルを読み込む
with open('./config.yaml','r') as yml:
    yml_conf=yaml.safe_load(yml)
    bot_token=yml_conf['discord']['BOT_TOKEN']
    test_guild_ids=yml_conf['discord']['test_guild_ids']
    reporter_id=yml_conf['discord']['Reporter_id']
    send_channel_id=yml_conf['discord']['Send_Channel']

#botのインスタンスを生成
bot = commands.Bot(command_prefix='/',
                description='会計の業務をお助けします',
                intents = discord.Intents.all(),
                help_command=None,
                activity=discord.Game("Python") 
)

#ランダムな文字列を６文字で返す
def randomname(n:int = 6):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

#承認・未承認ボタン関連
class docs_conf_view(View):
    def __init__(self):
        super().__init__(
            timeout=None
        )
    
    @discord.ui.button(label="✓ 承認", style=discord.ButtonStyle.success)
    async def ok(self, button: Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        modal = docs_conf_Modal("ok", user_id)
        await interaction.response.send_modal(modal=modal)

    @discord.ui.button(label="X 未承認", style=discord.ButtonStyle.danger)
    async def ng(self, button: Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        modal = docs_conf_Modal("ng", user_id)
        await interaction.response.send_modal(modal=modal)
        
#キャンセルボタン関連
class Cancel_view(Button):
    async def callback(self, interaction: discord.Interaction):
        approver = bot.get_user(int(reporter_id))
        modal = CancelModal(approver, interaction)
        await interaction.response.send_modal(modal=modal)
         
class docs_conf_Modal(Modal):
    def __init__(self, situation, user_id):
        super().__init__(
            title="書類確認完了",
            timeout=None
        )
        self.situation=situation
        self.user_id=user_id

        # modal内で入力してもらうものを用意
        self.id=InputText(
            label="申請ID",
            style=discord.InputTextStyle.short,
            placeholder="Embedに記載されている「申請ID」を記入",
            required=True
        )
        self.remarks=InputText(
            label="備考欄",
            style=discord.InputTextStyle.multiline,
            placeholder="",
            required=False
        )
        # 上で用意したものをModalに追加する
        self.add_item(self.id)
        self.add_item(self.remarks)

        
    async def callback(self, interaction: Interaction) -> list:
        approver = bot.get_user(self.user_id)
        show_approver = str(approver).replace("#0","")
        await interaction.response.send_message(f"【{self.id.value}】確認作業完了通知を送信しました。")
        if self.situation == "ok": 
            show_embed_docs_conf = discord.Embed(title='【確認作業完了】', description='申請された書類は以下の通り確認されました。', colour=discord.Colour.from_rgb(0,255,0))
            show_embed_docs_conf.add_field(name='申請結果',value="承認", inline=True)
        elif self.situation == "ng": 
            show_embed_docs_conf = discord.Embed(title='【確認作業完了】', description='申請された書類は以下の通り確認されました。', colour=discord.Colour.from_rgb(255,0,0))
            show_embed_docs_conf.add_field(name='申請結果',value="未承認", inline=True)
        show_embed_docs_conf.add_field(name='承認者', value=show_approver, inline=True)
        show_embed_docs_conf.add_field(name='申請ID', value=self.id.value, inline=True)
        if len(self.remarks.value) == 0 : show_embed_docs_conf.add_field(name='備考欄', value="特になし", inline=False)
        else: show_embed_docs_conf.add_field(name='備考欄', value=self.remarks.value, inline=False)
        # 申請者に対する表示
        channel = bot.get_channel(int(send_channel_id))
        await channel.send(embed=show_embed_docs_conf)

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

        if "" != self.claim.value: show_embed_report.add_field(name=f'請求【{len(self.claim_list)}件】',value=f'{self.claim.value}',inline=False)
        if "" != self.spending.value: show_embed_report.add_field(name=f'支出【{len(self.spending_list)}件】',value=f'{self.spending.value}',inline=False)
        if "" !=  self.caluculate.value: show_embed_report.add_field(name=f'清算【{len(self.caluculate_list)}件】',value=f'{self.caluculate.value}', inline=False)
        for content in self.content_list:
            count+=1
            show_embed_report.add_field(name=f'報告【{count}件目】', value=f'・{content}',inline=False)

        await interaction.response.send_message(embed=show_embed_report)

# 書類承認用のModal
class ApplicateModal(Modal):
    def __init__(self, approver):
        super().__init__(
            title="確認作業依頼",
            timeout=None
        )
        self.approver=approver

        # modal内で入力してもらうものを用意
        self.organization=InputText(
            label="団体名",
            style=discord.InputTextStyle.short,
            placeholder="書類の団体名欄のところを記入",
            required=True
        )
        self.remarks=InputText(
            label="備考欄",
            style=discord.InputTextStyle.multiline,
            placeholder="確認する点において注意するべき事があれば記載",
            required=False
        )
        # 上で用意したものをModalに追加する
        self.add_item(self.organization)
        self.add_item(self.remarks)
    
    async def callback(self, interaction: Interaction) -> list:
        show_embed_applicate_reporter.add_field(name='団体名', value=self.organization.value, inline=True)
        show_embed_applicate.add_field(name='団体名', value=self.organization.value, inline=True)
        if len(self.remarks.value) == 0 : 
            show_embed_applicate_reporter.add_field(name='備考欄', value="特になし", inline=False)
            show_embed_applicate.add_field(name='備考欄', value="特になし", inline=False)
        else:
            show_embed_applicate_reporter.add_field(name='備考欄', value=self.remarks.value, inline=False)
            show_embed_applicate.add_field(name='備考欄', value=self.remarks.value, inline=False)

        # キャンセル機能
        view = View()
        delete_button = Cancel_view(label='キャンセル', style=discord.ButtonStyle.gray)
        view.add_item(delete_button)

        # Embedとボタンの送信
        await interaction.response.send_message(view=view, embed=show_embed_applicate)
        await self.approver.send(embed=show_embed_applicate_reporter, view=docs_conf_view())


class CancelModal(Modal):
    def __init__(self, approver, interaction_before:discord.Interaction):
        super().__init__(
            title="【キャンセル】確認作業依頼",
            timeout=None
        )
        self.approver=approver

        # modal内で入力してもらうものを用意
        self.applicate_id=InputText(
            label="申請ID",
            style=discord.InputTextStyle.short,
            placeholder="",
            required=True
        )
        self.reason=InputText(
            label="理由",
            style=discord.InputTextStyle.multiline,
            placeholder="何かあればこちらに",
            required=False
        )
        # 上で用意したものをModalに追加する
        self.add_item(self.applicate_id)
    
    async def callback(self, interaction: Interaction) -> list:
        show_embed_cancel = discord.Embed(title="【キャンセル】確認作業依頼", description="下記の確認作業がキャンセルされました", color=discord.Colour.from_rgb(128,128,128))
        show_embed_cancel.add_field(name="申請ID", value=self.applicate_id.value, inline=False)
        show_embed_cancel.add_field(name="理由", value=self.reason.value, inline=False)
        # Embedとボタンの送信
        await interaction.response.send_message(embed=show_embed_cancel)
        await self.approver.send(embed=show_embed_cancel)

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

    global show_embed_report
    show_embed_report = discord.Embed(title='【会計報告】',color=discord.Colour.from_rgb(3,3,3))
    show_embed_report.add_field(name='日付', value=f'{month}月{day}日({weakday})', inline=False)
    show_embed_report.set_footer(text=user.name,icon_url=user.avatar)

    modal = ReportModal()
    await ctx.response.send_modal(modal=modal)

@bot.slash_command(name="applicate", description="【書類確認】請求書・精算書の確認申請を行うコマンドです。", guild_ids=[test_guild_ids])
async def applicate(
    ctx: discord.ApplicationCommand,
    who: discord.Option(discord.Member, "申請者名を入力 ※予測変換必ず入力してください", required=True),
    approver: discord.Option(discord.Member, "誰に確認してもらいますか？", required=True),
    document: discord.Option(str, "どの資料ですか？", choices=document_list, required=True),
):
    # 申請者情報取得
    who_id = who.id
    show_user = str(who).replace("#0","")
    # 確認者情報取得
    approver_id = approver.id
    print(approver_id)
    # 現在時刻をJSTで取得
    current_time = datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y年%m月%d日 %H:%M:%S')
    # 申請IDの取得
    applicate_id = randomname()
    # フォルダ名の決定
    folder_name = f"【{show_user}】{applicate_id}({current_time})"
    # Use NextcloudOperatorAPI
    ope = NextcloudOperator.OperatorAPI()
    res = ope.make_folder(folder_name=folder_name)
    # 引数で指定されたユーザの情報を取得
    user = bot.get_user(who_id)
    approver = bot.get_user(approver_id)
    
    if res == 201:
        # successful

        # アップロード先のリンク
        share_url= f"https://nextcloud.tochiman.com/apps/files/files?dir=/nextcloud-data/{folder_name}"

        # 申請者に対するEmbed
        global show_embed_applicate
        show_embed_applicate = discord.Embed(title='【確認作業依頼】', description="申請物を`アップロード先`にて全てアップロードしてください。",color=discord.Colour.from_rgb(3,3,3))
        show_embed_applicate.add_field(name='申請日時', value=current_time, inline=True)
        show_embed_applicate.add_field(name='確認物種別', value=document, inline=True)
        show_embed_applicate.add_field(name='リンク', value=f"[アップロード先]({share_url})", inline=True)
        show_embed_applicate.add_field(name='確認者', value=approver.name, inline=True)
        show_embed_applicate.add_field(name="申請ID", value=applicate_id, inline=True)
        show_embed_applicate.set_footer(text=user.name,icon_url=user.avatar)

        # 報告者に対するEmbed関連
        global show_embed_applicate_reporter
        show_embed_applicate_reporter = discord.Embed(title='【確認作業依頼】', description="確認依頼が来ました。", color=discord.Colour.from_rgb(3,3,3))
        show_embed_applicate_reporter.add_field(name='申請日時', value=current_time, inline=True)
        show_embed_applicate_reporter.add_field(name='確認物種別', value=document, inline=True)
        show_embed_applicate_reporter.add_field(name='リンク', value=f"[アップロード先]({share_url})", inline=True)
        show_embed_applicate_reporter.add_field(name='申請者', value=user.name, inline=True)
        show_embed_applicate_reporter.add_field(name="申請ID", value=applicate_id, inline=True)

        # 申請者に対するModal
        modal = ApplicateModal(approver)
        await ctx.response.send_modal(modal=modal)

    else:
        show_embed_applicate = discord.Embed(title='【確認作業依頼】エラー', description="フォルダーが作成されませんでした。再度実行していただくか、Bot作成者にお問い合わせください。",color=discord.Colour.from_rgb(3,3,3))
        show_embed_applicate.set_footer(text=user.name,icon_url=user.avatar)
        await ctx.response.send_message(embed=show_embed_applicate)

if __name__ == '__main__':
    #discordのhelpコマンドを削除
    bot.remove_command('help')
    #bot起動
    bot.run(bot_token)
