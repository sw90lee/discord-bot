import discord
from discord.ext import commands
import os
import logging
import asyncio
from utils.database import Database
from utils.config import Config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 봇 설정
intents = discord.Intents.default()
intents.members = True  # 멤버 관련 이벤트를 받기 위해 필요
intents.message_content = True
intents.guilds = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None  # 기본 help 명령어 비활성화
        )
        self.db = Database()
        self.config = Config()

    async def setup_hook(self):
        """봇 시작 시 초기화"""
        logger.info('데이터베이스 초기화 중...')
        await self.db.setup()

        logger.info('Cogs 로딩 중...')
        cogs = [
            'cogs.welcome',
            'cogs.moderation',
            'cogs.roles',
            'cogs.utility',
            'cogs.leveling'
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f'{cog} 로드 완료')
            except Exception as e:
                logger.error(f'{cog} 로드 실패: {e}')

        # 슬래시 명령어 동기화
        try:
            logger.info('슬래시 명령어 동기화 중...')
            synced = await self.tree.sync()
            logger.info(f'{len(synced)}개의 슬래시 명령어가 동기화되었습니다.')
        except Exception as e:
            logger.error(f'슬래시 명령어 동기화 실패: {e}')

    async def on_ready(self):
        """봇이 준비되었을 때"""
        logger.info(f'{self.user.name} (ID: {self.user.id})로 로그인했습니다.')
        logger.info(f'디스코드 버전: {discord.__version__}')
        logger.info(f'{len(self.guilds)}개의 서버에 연결되었습니다.')

        # 봇 상태 설정
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)}개 서버 | /help"
        )
        await self.change_presence(activity=activity)

        logger.info('봇이 정상적으로 시작되었습니다.')

    async def on_command_error(self, ctx, error):
        """명령어 오류 처리"""
        if isinstance(error, commands.CommandNotFound):
            return  # 명령어를 찾을 수 없는 경우 무시
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('❌ 이 명령어를 실행할 권한이 없습니다.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'❌ 필수 인자가 누락되었습니다: {error.param.name}')
        else:
            logger.error(f'명령어 오류: {error}')
            await ctx.send('❌ 명령어 실행 중 오류가 발생했습니다.')

# 환경 변수에서 토큰 로드
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN 환경 변수가 설정되지 않았습니다.")

# ConfigMap에서 환영 채널 ID 로드 (Kubernetes 환경)
WELCOME_CHANNEL_ID = os.getenv('WELCOME_CHANNEL_ID')

if __name__ == '__main__':
    try:
        logger.info('봇을 시작합니다...')
        bot = DiscordBot()

        # ConfigMap에서 로드한 환영 채널 ID를 config에 저장
        if WELCOME_CHANNEL_ID:
            bot.config.config['welcome_channel_id'] = WELCOME_CHANNEL_ID
            logger.info(f'환영 채널 ID 설정: {WELCOME_CHANNEL_ID}')

        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info('봇을 종료합니다...')
    except Exception as e:
        logger.error(f'봇 실행 중 오류 발생: {e}')
