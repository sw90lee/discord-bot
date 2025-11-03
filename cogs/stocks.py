import discord
from discord.ext import commands, tasks
from discord import app_commands
import yfinance as yf
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.db = bot.db

        # 주요 지표 티커 심볼
        self.indices = {
            "코스피": "^KS11",
            "코스닥": "^KQ11",
            "나스닥": "^IXIC",
            "S&P_500": "^GSPC",
            "다우존스": "^DJI",
            "비트코인": "BTC-USD",
            "이더리움": "ETH-USD",
            "원달러": "KRW=X"
        }

        self.stocks_task.start()
        self.watchlist_monitor_task.start()

    def cog_unload(self):
        self.stocks_task.cancel()
        self.watchlist_monitor_task.cancel()

    @tasks.loop(minutes=1)
    async def stocks_task(self):
        """매 분마다 실행되어 스케줄 확인"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 모든 길드의 주식 스케줄 확인
        stocks_schedules = self.config.get('stocks_schedules', default={})

        for guild_id_str, schedule_info in stocks_schedules.items():
            if not schedule_info.get('enabled', False):
                continue

            scheduled_time = schedule_info.get('time', '09:00')
            channel_id = schedule_info.get('channel_id')
            indices = schedule_info.get('indices', ['코스피', '코스닥', '나스닥'])

            if current_time == scheduled_time and channel_id:
                guild = self.bot.get_guild(int(guild_id_str))
                if guild:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        try:
                            await self.send_stocks_summary(channel, indices)
                            logger.info(f'주식 정보를 {guild.name}의 {channel.name}에 전송했습니다.')
                        except Exception as e:
                            logger.error(f'주식 정보 전송 오류: {e}')

    @stocks_task.before_loop
    async def before_stocks_task(self):
        await self.bot.wait_until_ready()

    def get_stock_data(self, ticker: str):
        """주식 데이터 가져오기"""
        try:
            stock = yf.Ticker(ticker)

            # 최신 데이터 가져오기
            hist = stock.history(period="2d")

            if hist.empty or len(hist) < 1:
                return None

            current_price = hist['Close'].iloc[-1]

            # 전일 종가와 비교
            if len(hist) >= 2:
                previous_price = hist['Close'].iloc[-2]
                change = current_price - previous_price
                change_percent = (change / previous_price) * 100
            else:
                change = 0
                change_percent = 0

            return {
                'price': current_price,
                'change': change,
                'change_percent': change_percent
            }

        except Exception as e:
            logger.error(f'주식 데이터 가져오기 오류 ({ticker}): {e}')
            return None

    def format_price(self, price: float, ticker: str) -> str:
        """가격 포맷팅"""
        if ticker == "KRW=X":  # 원/달러 환율
            return f"{price:.2f}원"
        elif "BTC" in ticker or "ETH" in ticker:  # 암호화폐
            return f"${price:,.2f}"
        elif ticker.startswith("^KS") or ticker.startswith("^KQ"):  # 한국 지수
            return f"{price:,.2f}"
        else:  # 미국 지수
            return f"{price:,.2f}"

    async def send_stocks_summary(self, channel: discord.TextChannel, indices: list):
        """주식 정보 요약을 채널에 전송"""
        embed = discord.Embed(
            title="📈 주식 시장 현황",
            description=f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        for index_name in indices:
            ticker = self.indices.get(index_name)
            if not ticker:
                continue

            data = self.get_stock_data(ticker)
            if not data:
                embed.add_field(
                    name=f"📊 {index_name}",
                    value="⚠️ 데이터를 가져올 수 없습니다",
                    inline=False
                )
                continue

            # 상승/하락 이모지
            if data['change'] > 0:
                emoji = "📈"
                color_indicator = "🟢"
                change_text = f"+{data['change']:.2f} (+{data['change_percent']:.2f}%)"
            elif data['change'] < 0:
                emoji = "📉"
                color_indicator = "🔴"
                change_text = f"{data['change']:.2f} ({data['change_percent']:.2f}%)"
            else:
                emoji = "➖"
                color_indicator = "⚪"
                change_text = "0.00 (0.00%)"

            price_text = self.format_price(data['price'], ticker)

            embed.add_field(
                name=f"{emoji} {index_name}",
                value=f"{color_indicator} **{price_text}**\n{change_text}",
                inline=True
            )

        embed.set_footer(text="주식 자동 전송 • 데이터 제공: Yahoo Finance")

        await channel.send(embed=embed)

    @app_commands.command(name="stocks", description="주식 시장 현황을 확인합니다")
    @app_commands.describe(
        index1="첫 번째 지표",
        index2="두 번째 지표 (선택사항)",
        index3="세 번째 지표 (선택사항)",
        index4="네 번째 지표 (선택사항)"
    )
    @app_commands.choices(
        index1=[
            app_commands.Choice(name="코스피", value="코스피"),
            app_commands.Choice(name="코스닥", value="코스닥"),
            app_commands.Choice(name="나스닥", value="나스닥"),
            app_commands.Choice(name="S&P 500", value="S&P_500"),
            app_commands.Choice(name="다우존스", value="다우존스"),
            app_commands.Choice(name="비트코인", value="비트코인"),
            app_commands.Choice(name="이더리움", value="이더리움"),
            app_commands.Choice(name="원/달러", value="원달러"),
        ],
        index2=[
            app_commands.Choice(name="코스피", value="코스피"),
            app_commands.Choice(name="코스닥", value="코스닥"),
            app_commands.Choice(name="나스닥", value="나스닥"),
            app_commands.Choice(name="S&P 500", value="S&P_500"),
            app_commands.Choice(name="다우존스", value="다우존스"),
            app_commands.Choice(name="비트코인", value="비트코인"),
            app_commands.Choice(name="이더리움", value="이더리움"),
            app_commands.Choice(name="원/달러", value="원달러"),
        ],
        index3=[
            app_commands.Choice(name="코스피", value="코스피"),
            app_commands.Choice(name="코스닥", value="코스닥"),
            app_commands.Choice(name="나스닥", value="나스닥"),
            app_commands.Choice(name="S&P 500", value="S&P_500"),
            app_commands.Choice(name="다우존스", value="다우존스"),
            app_commands.Choice(name="비트코인", value="비트코인"),
            app_commands.Choice(name="이더리움", value="이더리움"),
            app_commands.Choice(name="원/달러", value="원달러"),
        ],
        index4=[
            app_commands.Choice(name="코스피", value="코스피"),
            app_commands.Choice(name="코스닥", value="코스닥"),
            app_commands.Choice(name="나스닥", value="나스닥"),
            app_commands.Choice(name="S&P 500", value="S&P_500"),
            app_commands.Choice(name="다우존스", value="다우존스"),
            app_commands.Choice(name="비트코인", value="비트코인"),
            app_commands.Choice(name="이더리움", value="이더리움"),
            app_commands.Choice(name="원/달러", value="원달러"),
        ]
    )
    async def stocks(
        self,
        interaction: discord.Interaction,
        index1: app_commands.Choice[str],
        index2: app_commands.Choice[str] = None,
        index3: app_commands.Choice[str] = None,
        index4: app_commands.Choice[str] = None
    ):
        """주식 조회"""
        await interaction.response.defer()

        indices = [index1.value]
        if index2:
            indices.append(index2.value)
        if index3:
            indices.append(index3.value)
        if index4:
            indices.append(index4.value)

        embed = discord.Embed(
            title="📈 주식 시장 현황",
            description=f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        for index_name in indices:
            ticker = self.indices.get(index_name)
            if not ticker:
                continue

            data = self.get_stock_data(ticker)
            if not data:
                embed.add_field(
                    name=f"📊 {index_name}",
                    value="⚠️ 데이터를 가져올 수 없습니다",
                    inline=False
                )
                continue

            # 상승/하락 이모지
            if data['change'] > 0:
                emoji = "📈"
                color_indicator = "🟢"
                change_text = f"+{data['change']:.2f} (+{data['change_percent']:.2f}%)"
            elif data['change'] < 0:
                emoji = "📉"
                color_indicator = "🔴"
                change_text = f"{data['change']:.2f} ({data['change_percent']:.2f}%)"
            else:
                emoji = "➖"
                color_indicator = "⚪"
                change_text = "0.00 (0.00%)"

            price_text = self.format_price(data['price'], ticker)

            embed.add_field(
                name=f"{emoji} {index_name}",
                value=f"{color_indicator} **{price_text}**\n{change_text}",
                inline=True
            )

        embed.set_footer(text=f"요청자: {interaction.user.name} • 데이터 제공: Yahoo Finance")

        await interaction.followup.send(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 주식 조회: {", ".join(indices)}')

    @app_commands.command(name="schedulestocks", description="특정 시간에 자동으로 주식 정보를 전송하도록 설정합니다")
    @app_commands.describe(
        channel="주식 정보를 전송할 채널",
        time="전송 시간 (HH:MM 형식, 예: 09:00)",
        indices="표시할 지표들 (쉼표로 구분, 예: 코스피,나스닥,비트코인)"
    )
    @app_commands.default_permissions(administrator=True)
    async def schedulestocks(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        time: str,
        indices: str = "코스피,코스닥,나스닥"
    ):
        """주식 자동 전송 스케줄 설정"""
        # 시간 형식 검증
        try:
            hour, minute = map(int, time.split(':'))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError
        except:
            await interaction.response.send_message(
                '❌ 올바른 시간 형식을 입력해주세요. (예: 09:00, 18:30)',
                ephemeral=True
            )
            return

        # 지표 검증
        indices_list = [idx.strip() for idx in indices.split(',')]
        valid_indices = []
        for idx in indices_list:
            if idx in self.indices:
                valid_indices.append(idx)

        if not valid_indices:
            await interaction.response.send_message(
                f'❌ 올바른 지표를 입력해주세요.\n사용 가능: {", ".join(self.indices.keys())}',
                ephemeral=True
            )
            return

        # 설정 저장
        guild_id = str(interaction.guild.id)
        if 'stocks_schedules' not in self.config.config:
            self.config.config['stocks_schedules'] = {}

        self.config.config['stocks_schedules'][guild_id] = {
            'enabled': True,
            'channel_id': channel.id,
            'time': time,
            'indices': valid_indices
        }
        self.config._save_config(self.config.config)

        embed = discord.Embed(
            title="✅ 주식 자동 전송 설정",
            description="주식 정보가 자동으로 전송됩니다.",
            color=discord.Color.green()
        )
        embed.add_field(name="채널", value=channel.mention, inline=True)
        embed.add_field(name="시간", value=time, inline=True)
        embed.add_field(name="지표", value=", ".join(valid_indices), inline=False)
        embed.set_footer(text=f"설정한 관리자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 주식 스케줄 설정: {time} in {channel.name}')

    @app_commands.command(name="stopstocks", description="자동 주식 정보 전송을 중지합니다")
    @app_commands.default_permissions(administrator=True)
    async def stopstocks(self, interaction: discord.Interaction):
        """주식 자동 전송 중지"""
        guild_id = str(interaction.guild.id)

        if 'stocks_schedules' not in self.config.config or guild_id not in self.config.config['stocks_schedules']:
            await interaction.response.send_message('❌ 설정된 주식 스케줄이 없습니다.', ephemeral=True)
            return

        self.config.config['stocks_schedules'][guild_id]['enabled'] = False
        self.config._save_config(self.config.config)

        embed = discord.Embed(
            title="✅ 주식 자동 전송 중지",
            description="주식 자동 전송이 중지되었습니다.",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"중지한 관리자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 주식 자동 전송 중지')

    @app_commands.command(name="stocksstatus", description="주식 자동 전송 설정을 확인합니다")
    @app_commands.default_permissions(administrator=True)
    async def stocksstatus(self, interaction: discord.Interaction):
        """주식 스케줄 상태 확인"""
        guild_id = str(interaction.guild.id)

        stocks_schedules = self.config.get('stocks_schedules', default={})
        schedule_info = stocks_schedules.get(guild_id)

        if not schedule_info:
            await interaction.response.send_message('📈 설정된 주식 스케줄이 없습니다.', ephemeral=True)
            return

        enabled = schedule_info.get('enabled', False)
        channel_id = schedule_info.get('channel_id')
        scheduled_time = schedule_info.get('time', '미설정')
        indices = schedule_info.get('indices', [])

        channel = interaction.guild.get_channel(channel_id) if channel_id else None

        embed = discord.Embed(
            title="📈 주식 자동 전송 설정 상태",
            color=discord.Color.green() if enabled else discord.Color.red()
        )

        embed.add_field(name="상태", value="✅ 활성화" if enabled else "❌ 비활성화", inline=True)
        embed.add_field(name="전송 시간", value=scheduled_time, inline=True)
        embed.add_field(name="지표", value=", ".join(indices) if indices else "없음", inline=False)

        if channel:
            embed.add_field(name="전송 채널", value=channel.mention, inline=False)
        else:
            embed.add_field(name="전송 채널", value="⚠️ 채널을 찾을 수 없음", inline=False)

        embed.set_footer(text=f"요청자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ===== 주식 감시 목록 기능 =====

    @tasks.loop(minutes=5)
    async def watchlist_monitor_task(self):
        """5분마다 감시 목록의 주식들을 체크"""
        for guild in self.bot.guilds:
            try:
                # 알림 설정 확인
                alert_config = self.config.get('stock_alerts', str(guild.id), default=None)
                if not alert_config or not alert_config.get('enabled', False):
                    continue

                channel_id = alert_config.get('channel_id')
                threshold = alert_config.get('threshold', 5.0)  # 기본 5%

                if not channel_id:
                    continue

                channel = guild.get_channel(channel_id)
                if not channel:
                    continue

                # 감시 목록 가져오기
                watchlist = await self.db.get_watchlist(guild.id)

                for ticker, name, last_price, last_change_percent in watchlist:
                    data = self.get_stock_data(ticker)
                    if not data:
                        continue

                    current_price = data['price']
                    change_percent = data['change_percent']

                    # 변동률이 임계값을 초과하는지 확인
                    if abs(change_percent) >= threshold:
                        # 이전에 알림을 보낸 적이 있는지 확인 (같은 변동률이면 중복 알림 방지)
                        if abs(change_percent - last_change_percent) < 0.1:
                            continue

                        # 알림 전송
                        await self.send_alert(channel, ticker, name, data, threshold)

                    # 가격 업데이트
                    await self.db.update_stock_price(guild.id, ticker, current_price, change_percent)

            except Exception as e:
                logger.error(f'감시 목록 모니터링 오류 ({guild.name}): {e}')

    @watchlist_monitor_task.before_loop
    async def before_watchlist_monitor_task(self):
        await self.bot.wait_until_ready()

    async def send_alert(self, channel: discord.TextChannel, ticker: str, name: str, data: dict, threshold: float):
        """주식 변동 알림 전송"""
        change_percent = data['change_percent']

        if change_percent > 0:
            emoji = "🚀"
            color = discord.Color.green()
            title = f"📈 주식 급등 알림!"
        else:
            emoji = "⚠️"
            color = discord.Color.red()
            title = f"📉 주식 급락 알림!"

        embed = discord.Embed(
            title=title,
            description=f"{emoji} **{name} ({ticker})**",
            color=color,
            timestamp=discord.utils.utcnow()
        )

        price_text = self.format_price(data['price'], ticker)
        change_text = f"{'+' if change_percent > 0 else ''}{change_percent:.2f}%"

        embed.add_field(name="현재가", value=price_text, inline=True)
        embed.add_field(name="변동률", value=change_text, inline=True)
        embed.add_field(name="임계값", value=f"{threshold}%", inline=True)

        embed.set_footer(text=f"주식 알림 • {datetime.now().strftime('%H:%M')}")

        await channel.send(f"<@&알림>", embed=embed)  # 역할 멘션은 설정에 따라 조정 가능
        logger.info(f'{channel.guild.name}에 {ticker} 알림 전송: {change_percent:.2f}%')

    @app_commands.command(name="addstock", description="감시 목록에 주식을 추가합니다 (최대 10개)")
    @app_commands.describe(
        ticker="주식 티커 (예: AAPL, 005930.KS, BTC-USD)",
        name="주식 이름 (선택사항)"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def addstock(self, interaction: discord.Interaction, ticker: str, name: str = None):
        """주식 감시 목록에 추가"""
        # 대문자로 변환
        ticker = ticker.upper()

        # 개수 확인 (최대 10개)
        count = await self.db.get_watchlist_count(interaction.guild.id)
        if count >= 10:
            await interaction.response.send_message(
                '❌ 감시 목록은 최대 10개까지만 추가할 수 있습니다.\n`/removestock`으로 기존 주식을 제거한 후 추가해주세요.',
                ephemeral=True
            )
            return

        await interaction.response.defer()

        # 주식 정보 확인
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # 이름이 제공되지 않으면 자동으로 가져오기
            if not name:
                name = info.get('longName') or info.get('shortName') or ticker

            # 감시 목록에 추가
            success = await self.db.add_stock_to_watchlist(interaction.guild.id, ticker, name)

            if not success:
                await interaction.followup.send(f'❌ {ticker}는 이미 감시 목록에 있습니다.', ephemeral=True)
                return

            # 현재 가격 가져오기
            data = self.get_stock_data(ticker)
            if data:
                await self.db.update_stock_price(interaction.guild.id, ticker, data['price'], data['change_percent'])

            embed = discord.Embed(
                title="✅ 주식 감시 목록 추가",
                description=f"**{name} ({ticker})**가 감시 목록에 추가되었습니다.",
                color=discord.Color.green()
            )

            if data:
                price_text = self.format_price(data['price'], ticker)
                change_text = f"{'+' if data['change'] > 0 else ''}{data['change_percent']:.2f}%"
                embed.add_field(name="현재가", value=price_text, inline=True)
                embed.add_field(name="변동률", value=change_text, inline=True)

            embed.add_field(name="감시 목록", value=f"{count + 1}/10개", inline=False)
            embed.set_footer(text=f"추가한 관리자: {interaction.user.name}")
            embed.timestamp = discord.utils.utcnow()

            await interaction.followup.send(embed=embed)
            logger.info(f'{interaction.user.name}이(가) {ticker} 감시 목록에 추가')

        except Exception as e:
            await interaction.followup.send(f'❌ 주식 정보를 가져올 수 없습니다: {ticker}\n올바른 티커 심볼인지 확인해주세요.', ephemeral=True)
            logger.error(f'주식 추가 오류 ({ticker}): {e}')

    @app_commands.command(name="removestock", description="감시 목록에서 주식을 제거합니다")
    @app_commands.describe(ticker="제거할 주식 티커")
    @app_commands.default_permissions(manage_guild=True)
    async def removestock(self, interaction: discord.Interaction, ticker: str):
        """주식 감시 목록에서 제거"""
        ticker = ticker.upper()

        await self.db.remove_stock_from_watchlist(interaction.guild.id, ticker)

        embed = discord.Embed(
            title="✅ 주식 감시 목록 제거",
            description=f"**{ticker}**가 감시 목록에서 제거되었습니다.",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"제거한 관리자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)
        logger.info(f'{interaction.user.name}이(가) {ticker} 감시 목록에서 제거')

    @app_commands.command(name="watchlist", description="현재 감시 중인 주식 목록을 확인합니다")
    async def watchlist(self, interaction: discord.Interaction):
        """감시 목록 확인"""
        watchlist = await self.db.get_watchlist(interaction.guild.id)

        if not watchlist:
            await interaction.response.send_message('📊 감시 목록이 비어있습니다.\n`/addstock` 명령어로 주식을 추가해보세요!', ephemeral=True)
            return

        await interaction.response.defer()

        embed = discord.Embed(
            title="📊 주식 감시 목록",
            description=f"총 {len(watchlist)}/10개",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        for ticker, name, last_price, last_change_percent in watchlist:
            # 현재 가격 가져오기
            data = self.get_stock_data(ticker)

            if data:
                price_text = self.format_price(data['price'], ticker)
                change_text = f"{'+' if data['change'] > 0 else ''}{data['change_percent']:.2f}%"

                if data['change'] > 0:
                    indicator = "🟢"
                elif data['change'] < 0:
                    indicator = "🔴"
                else:
                    indicator = "⚪"

                value = f"{indicator} **{price_text}** ({change_text})"
            else:
                value = "⚠️ 데이터를 가져올 수 없습니다"

            embed.add_field(
                name=f"{name} ({ticker})",
                value=value,
                inline=False
            )

        embed.set_footer(text=f"요청자: {interaction.user.name} • 5분마다 자동 모니터링")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="setalert", description="주식 변동 알림을 설정합니다")
    @app_commands.describe(
        channel="알림을 받을 채널",
        threshold="알림 임계값 (%, 예: 5 = 5% 이상 변동 시 알림)"
    )
    @app_commands.default_permissions(administrator=True)
    async def setalert(self, interaction: discord.Interaction, channel: discord.TextChannel, threshold: float = 5.0):
        """주식 알림 설정"""
        if threshold < 1 or threshold > 50:
            await interaction.response.send_message('❌ 임계값은 1%에서 50% 사이여야 합니다.', ephemeral=True)
            return

        # 설정 저장
        guild_id = str(interaction.guild.id)
        if 'stock_alerts' not in self.config.config:
            self.config.config['stock_alerts'] = {}

        self.config.config['stock_alerts'][guild_id] = {
            'enabled': True,
            'channel_id': channel.id,
            'threshold': threshold
        }
        self.config._save_config(self.config.config)

        embed = discord.Embed(
            title="✅ 주식 알림 설정",
            description="주식 변동 알림이 활성화되었습니다.",
            color=discord.Color.green()
        )
        embed.add_field(name="알림 채널", value=channel.mention, inline=True)
        embed.add_field(name="임계값", value=f"{threshold}%", inline=True)
        embed.add_field(name="확인 주기", value="5분마다", inline=True)
        embed.set_footer(text=f"설정한 관리자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 주식 알림 설정: {threshold}% in {channel.name}')

    @app_commands.command(name="stopalert", description="주식 변동 알림을 중지합니다")
    @app_commands.default_permissions(administrator=True)
    async def stopalert(self, interaction: discord.Interaction):
        """주식 알림 중지"""
        guild_id = str(interaction.guild.id)

        if 'stock_alerts' not in self.config.config or guild_id not in self.config.config['stock_alerts']:
            await interaction.response.send_message('❌ 설정된 주식 알림이 없습니다.', ephemeral=True)
            return

        self.config.config['stock_alerts'][guild_id]['enabled'] = False
        self.config._save_config(self.config.config)

        embed = discord.Embed(
            title="✅ 주식 알림 중지",
            description="주식 변동 알림이 중지되었습니다.",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"중지한 관리자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 주식 알림 중지')

async def setup(bot):
    await bot.add_cog(Stocks(bot))
