import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import feedparser
from datetime import datetime, time
import logging
import asyncio

logger = logging.getLogger(__name__)

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

        # 뉴스 소스 (RSS 피드)
        self.news_sources = {
            "네이버_뉴스_헤드라인": "https://news.google.com/rss/search?q=when:24h+allinurl:naver.com&hl=ko&gl=KR&ceid=KR:ko",
            "구글_뉴스_한국": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
            "IT_뉴스": "https://news.google.com/rss/search?q=IT+기술+when:24h&hl=ko&gl=KR&ceid=KR:ko",
            "경제_뉴스": "https://news.google.com/rss/search?q=경제+when:24h&hl=ko&gl=KR&ceid=KR:ko",
        }

        self.news_task.start()

    def cog_unload(self):
        self.news_task.cancel()

    @tasks.loop(minutes=1)
    async def news_task(self):
        """매 분마다 실행되어 스케줄 확인"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 모든 길드의 뉴스 스케줄 확인
        news_schedules = self.config.get('news_schedules', default={})

        for guild_id_str, schedule_info in news_schedules.items():
            if not schedule_info.get('enabled', False):
                continue

            scheduled_time = schedule_info.get('time', '09:00')
            channel_id = schedule_info.get('channel_id')
            news_type = schedule_info.get('news_type', '구글_뉴스_한국')

            if current_time == scheduled_time and channel_id:
                guild = self.bot.get_guild(int(guild_id_str))
                if guild:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        try:
                            await self.send_news_summary(channel, news_type)
                            logger.info(f'뉴스를 {guild.name}의 {channel.name}에 전송했습니다.')
                        except Exception as e:
                            logger.error(f'뉴스 전송 오류: {e}')

    @news_task.before_loop
    async def before_news_task(self):
        await self.bot.wait_until_ready()

    async def fetch_news(self, news_type: str, limit: int = 5):
        """RSS 피드에서 뉴스 가져오기"""
        rss_url = self.news_sources.get(news_type)
        if not rss_url:
            return None

        try:
            # feedparser는 동기 함수이므로 executor에서 실행
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, rss_url)

            if not feed.entries:
                return None

            news_items = []
            for entry in feed.entries[:limit]:
                news_items.append({
                    'title': entry.get('title', '제목 없음'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200] if entry.get('summary') else ''
                })

            return news_items

        except Exception as e:
            logger.error(f'뉴스 가져오기 오류: {e}')
            return None

    async def send_news_summary(self, channel: discord.TextChannel, news_type: str):
        """뉴스 요약을 채널에 전송"""
        news_items = await self.fetch_news(news_type, limit=5)

        if not news_items:
            await channel.send('⚠️ 뉴스를 가져올 수 없습니다.')
            return

        embed = discord.Embed(
            title=f"📰 오늘의 주요 뉴스 - {news_type.replace('_', ' ')}",
            description=f"{datetime.now().strftime('%Y년 %m월 %d일')}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        for idx, item in enumerate(news_items, 1):
            title = item['title']
            link = item['link']

            # 제목이 너무 길면 자르기
            if len(title) > 100:
                title = title[:97] + "..."

            embed.add_field(
                name=f"{idx}. {title}",
                value=f"[기사 보기]({link})",
                inline=False
            )

        embed.set_footer(text="뉴스 자동 전송")

        await channel.send(embed=embed)

    @app_commands.command(name="news", description="최신 뉴스를 확인합니다")
    @app_commands.describe(
        news_type="뉴스 종류",
        count="가져올 뉴스 개수 (1-10)"
    )
    @app_commands.choices(news_type=[
        app_commands.Choice(name="구글 뉴스 한국", value="구글_뉴스_한국"),
        app_commands.Choice(name="네이버 뉴스 헤드라인", value="네이버_뉴스_헤드라인"),
        app_commands.Choice(name="IT 뉴스", value="IT_뉴스"),
        app_commands.Choice(name="경제 뉴스", value="경제_뉴스"),
    ])
    async def news(
        self,
        interaction: discord.Interaction,
        news_type: app_commands.Choice[str] = None,
        count: int = 5
    ):
        """뉴스 조회"""
        if count < 1 or count > 10:
            await interaction.response.send_message('❌ 뉴스 개수는 1~10개 사이여야 합니다.', ephemeral=True)
            return

        await interaction.response.defer()

        selected_type = news_type.value if news_type else "구글_뉴스_한국"
        news_items = await self.fetch_news(selected_type, limit=count)

        if not news_items:
            await interaction.followup.send('⚠️ 뉴스를 가져올 수 없습니다.')
            return

        embed = discord.Embed(
            title=f"📰 최신 뉴스 - {selected_type.replace('_', ' ')}",
            description=f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        for idx, item in enumerate(news_items, 1):
            title = item['title']
            link = item['link']

            if len(title) > 100:
                title = title[:97] + "..."

            embed.add_field(
                name=f"{idx}. {title}",
                value=f"[기사 보기]({link})",
                inline=False
            )

        embed.set_footer(text=f"요청자: {interaction.user.name}")

        await interaction.followup.send(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 뉴스 조회: {selected_type}')

    @app_commands.command(name="schedulenews", description="특정 시간에 자동으로 뉴스를 전송하도록 설정합니다")
    @app_commands.describe(
        channel="뉴스를 전송할 채널",
        time="전송 시간 (HH:MM 형식, 예: 09:00)",
        news_type="뉴스 종류"
    )
    @app_commands.choices(news_type=[
        app_commands.Choice(name="구글 뉴스 한국", value="구글_뉴스_한국"),
        app_commands.Choice(name="네이버 뉴스 헤드라인", value="네이버_뉴스_헤드라인"),
        app_commands.Choice(name="IT 뉴스", value="IT_뉴스"),
        app_commands.Choice(name="경제 뉴스", value="경제_뉴스"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def schedulenews(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        time: str,
        news_type: app_commands.Choice[str]
    ):
        """뉴스 자동 전송 스케줄 설정"""
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

        # 설정 저장
        guild_id = str(interaction.guild.id)
        if 'news_schedules' not in self.config.config:
            self.config.config['news_schedules'] = {}

        self.config.config['news_schedules'][guild_id] = {
            'enabled': True,
            'channel_id': channel.id,
            'time': time,
            'news_type': news_type.value
        }
        self.config._save_config(self.config.config)

        embed = discord.Embed(
            title="✅ 뉴스 자동 전송 설정",
            description="뉴스가 자동으로 전송됩니다.",
            color=discord.Color.green()
        )
        embed.add_field(name="채널", value=channel.mention, inline=True)
        embed.add_field(name="시간", value=time, inline=True)
        embed.add_field(name="뉴스 종류", value=news_type.name, inline=True)
        embed.set_footer(text=f"설정한 관리자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 뉴스 스케줄 설정: {time} in {channel.name}')

    @app_commands.command(name="stopnews", description="자동 뉴스 전송을 중지합니다")
    @app_commands.default_permissions(administrator=True)
    async def stopnews(self, interaction: discord.Interaction):
        """뉴스 자동 전송 중지"""
        guild_id = str(interaction.guild.id)

        if 'news_schedules' not in self.config.config or guild_id not in self.config.config['news_schedules']:
            await interaction.response.send_message('❌ 설정된 뉴스 스케줄이 없습니다.', ephemeral=True)
            return

        self.config.config['news_schedules'][guild_id]['enabled'] = False
        self.config._save_config(self.config.config)

        embed = discord.Embed(
            title="✅ 뉴스 자동 전송 중지",
            description="뉴스 자동 전송이 중지되었습니다.",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"중지한 관리자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 뉴스 자동 전송 중지')

    @app_commands.command(name="newsstatus", description="뉴스 자동 전송 설정을 확인합니다")
    @app_commands.default_permissions(administrator=True)
    async def newsstatus(self, interaction: discord.Interaction):
        """뉴스 스케줄 상태 확인"""
        guild_id = str(interaction.guild.id)

        news_schedules = self.config.get('news_schedules', default={})
        schedule_info = news_schedules.get(guild_id)

        if not schedule_info:
            await interaction.response.send_message('📰 설정된 뉴스 스케줄이 없습니다.', ephemeral=True)
            return

        enabled = schedule_info.get('enabled', False)
        channel_id = schedule_info.get('channel_id')
        scheduled_time = schedule_info.get('time', '미설정')
        news_type = schedule_info.get('news_type', '미설정')

        channel = interaction.guild.get_channel(channel_id) if channel_id else None

        embed = discord.Embed(
            title="📰 뉴스 자동 전송 설정 상태",
            color=discord.Color.green() if enabled else discord.Color.red()
        )

        embed.add_field(name="상태", value="✅ 활성화" if enabled else "❌ 비활성화", inline=True)
        embed.add_field(name="전송 시간", value=scheduled_time, inline=True)
        embed.add_field(name="뉴스 종류", value=news_type.replace('_', ' '), inline=True)

        if channel:
            embed.add_field(name="전송 채널", value=channel.mention, inline=False)
        else:
            embed.add_field(name="전송 채널", value="⚠️ 채널을 찾을 수 없음", inline=False)

        embed.set_footer(text=f"요청자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(News(bot))
