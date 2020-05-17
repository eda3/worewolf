import random
import sys
from typing import List

from cogs.utils.const import GameStatusConst, join_channel_const
from cogs.utils.roles import simple
from cogs.utils.werewolf_bot import WerewolfBot
from discord import utils
from discord.ext.commands import Bot, Cog, command, context
from setup_logger import setup_logger

logger = setup_logger(__name__)


class GameStatusCog(Cog):
    def __init__(self, bot: WerewolfBot):
        logger.debug("GameStatusCogのinit")
        self.bot: WerewolfBot = bot

    @command(aliases=["cre"])
    async def create(self, ctx: context) -> None:
        """人狼ゲーム作成(エイリアス[cre])"""
        if self.bot.game.status == GameStatusConst.PLAYING.value:
            await ctx.send("現在ゲーム中です。createコマンドは使えません")
            return
        if self.bot.game.status == GameStatusConst.WAITING.value:
            await ctx.send("現在参加者募集中です")
            return

        self.bot.game.status = GameStatusConst.WAITING.value
        await ctx.send("参加者の募集を開始しました。")

    @command()
    async def start(self, ctx: context) -> None:
        """人狼ゲーム開始"""
        # メソッド名取得
        method: str = sys._getframe().f_code.co_name

        if self.bot.game.status == GameStatusConst.NOTHING.value:
            await ctx.send(f"まだ募集されておりません。{method}コマンドは使えません")
            return

        self.bot.game.status = GameStatusConst.PLAYING.value
        await ctx.send(f"ゲームのステータスを{self.bot.game.status}に変更しました")

        # 役職配布
        n = len(self.bot.game.player_list)
        role = simple[n]
        role_list = random.sample(role, n)

        for i, player in enumerate(self.bot.game.player_list):
            name = player.name
            role = role_list[i]

            # 送信先チャンネル取得
            channel = ctx.guild.get_channel(join_channel_const[i])
            await channel.send(f"{name}の役職は{role}です")

        await self.set_game_roll(ctx)

    async def set_game_roll(self, ctx: context) -> None:
        player_list = self.bot.game.player_list
        n = len(player_list)
        if 0 == n:
            await ctx.send("参加者は0人です")
            return

        for i, player in enumerate(player_list):
            d_roll_name = "join0" + str(i)
            d_roll = utils.get(ctx.guild.roles, name=d_roll_name)

            await player.d_member.add_roles(d_roll)
            s = f"{player.name}さんは鍵チャンネル{d_roll_name}にアクセス出来るようになりました"
            await ctx.send(s)

    @command(aliases=["sgs"])
    async def show_game_status(self, ctx: context) -> None:
        """コマンド:現在のゲームステータスを表示

        :param ctx:
        :return:
        """
        await ctx.send("show_game_statusコマンドが実行されました")
        status: str = self.bot.game.status
        await ctx.send(f"現在のゲームのステータスは{status}です")

    @command(aliases=["setgs"])
    async def set_game_status(self, ctx: context, status: str = "") -> None:
        """コマンド：ゲームステータスを引数statusに設定

        :param ctx:
        :param status:ゲームのステータス。GameStatusConst参照
        :return:
        """
        status_list: List[str] = [x.value for x in GameStatusConst]

        if status == "":
            await ctx.send(f"引数がありません。引数は以下からえらんでください。 {status_list}")
            return

        if status not in status_list:
            await ctx.send(f"引数が間違っています。引数は以下からえらんでください。{status_list}")
            return

        self.bot.game.status = status
        await ctx.send(f"ゲームのステータスを{status}にセットしました")


def setup(bot: Bot) -> None:
    bot.add_cog(GameStatusCog(bot))
