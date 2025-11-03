import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config
        self.last_message_times = {}  # 쿨다운 관리

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """메시지 수신 시 XP 부여"""
        # 봇 메시지나 DM 무시
        if message.author.bot or not message.guild:
            return

        # 레벨링 시스템이 비활성화되어 있으면 무시
        if not self.config.get('leveling', 'enabled', default=True):
            return

        # 쿨다운 확인
        user_key = (message.guild.id, message.author.id)
        cooldown = self.config.get('leveling', 'xp_cooldown', default=60)

        if user_key in self.last_message_times:
            time_diff = (datetime.now() - self.last_message_times[user_key]).total_seconds()
            if time_diff < cooldown:
                return

        # XP 부여
        xp_amount = self.config.get('leveling', 'xp_per_message', default=10)
        new_level = await self.db.add_xp(message.guild.id, message.author.id, xp_amount)

        # 마지막 메시지 시간 업데이트
        self.last_message_times[user_key] = datetime.now()

        # 레벨업 알림
        if new_level is not None:
            if self.config.get('leveling', 'announce_level_up', default=True):
                level_up_msg = self.config.get(
                    'leveling',
                    'level_up_message',
                    default='🎊 {mention}님이 레벨 {level}에 도달했습니다!'
                )
                level_up_msg = level_up_msg.format(
                    mention=message.author.mention,
                    name=message.author.name,
                    level=new_level
                )

                try:
                    await message.channel.send(level_up_msg, delete_after=10)
                    logger.info(f'{message.author.name}이(가) 레벨 {new_level}에 도달')
                except Exception as e:
                    logger.error(f'레벨업 메시지 전송 오류: {e}')

    @app_commands.command(name="rank", description="자신 또는 다른 사용자의 레벨을 확인합니다")
    @app_commands.describe(member="레벨을 확인할 멤버 (선택사항)")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        """레벨 확인"""
        if member is None:
            member = interaction.user

        try:
            user_data = await self.db.get_user_level(interaction.guild.id, member.id)

            if not user_data:
                await interaction.response.send_message(
                    f'{member.mention} 님은 아직 레벨 데이터가 없습니다. 메시지를 보내서 XP를 획득하세요!',
                    ephemeral=True
                )
                return

            xp, level, total_messages = user_data
            rank = await self.db.get_user_rank(interaction.guild.id, member.id)

            # 다음 레벨까지 필요한 XP
            next_level_xp = self._xp_for_level(level + 1)
            current_level_xp = self._xp_for_level(level)
            xp_progress = xp - current_level_xp
            xp_needed = next_level_xp - current_level_xp

            # 진행률 바
            progress = int((xp_progress / xp_needed) * 20)
            progress_bar = f"[{'█' * progress}{'░' * (20 - progress)}]"

            embed = discord.Embed(
                title=f"📊 {member.name}의 레벨",
                color=member.color
            )

            embed.set_thumbnail(url=member.display_avatar.url)

            embed.add_field(name="레벨", value=f"**{level}**", inline=True)
            embed.add_field(name="순위", value=f"**#{rank}**", inline=True)
            embed.add_field(name="총 XP", value=f"**{xp:,}**", inline=True)

            embed.add_field(
                name="다음 레벨까지",
                value=f"{progress_bar}\n{xp_progress:,} / {xp_needed:,} XP",
                inline=False
            )

            embed.add_field(name="총 메시지 수", value=f"{total_messages:,}개", inline=True)

            embed.set_footer(text=f"요청자: {interaction.user.name}")
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'레벨 조회 오류: {e}')

    def _xp_for_level(self, level: int) -> int:
        """특정 레벨에 도달하기 위한 총 XP"""
        return 5 * (level ** 2) + 50 * level + 100

    @app_commands.command(name="leaderboard", description="서버 레벨 순위표를 확인합니다")
    @app_commands.describe(page="페이지 번호 (1페이지당 10명)")
    async def leaderboard(self, interaction: discord.Interaction, page: int = 1):
        """순위표"""
        if page < 1:
            await interaction.response.send_message('❌ 페이지 번호는 1 이상이어야 합니다.', ephemeral=True)
            return

        try:
            limit = 10
            offset = (page - 1) * limit

            # 전체 데이터를 가져와서 오프셋 적용
            all_data = await self.db.get_leaderboard(interaction.guild.id, limit=1000)

            if not all_data:
                await interaction.response.send_message('아직 레벨 데이터가 없습니다.', ephemeral=True)
                return

            # 페이지네이션
            page_data = all_data[offset:offset + limit]

            if not page_data:
                await interaction.response.send_message('❌ 해당 페이지에 데이터가 없습니다.', ephemeral=True)
                return

            embed = discord.Embed(
                title=f"🏆 {interaction.guild.name} 레벨 순위표",
                description=f"페이지 {page}",
                color=discord.Color.gold()
            )

            leaderboard_text = ""
            for idx, (user_id, xp, level, total_messages) in enumerate(page_data, start=offset + 1):
                member = interaction.guild.get_member(user_id)
                if member:
                    # 메달 이모지
                    medal = ""
                    if idx == 1:
                        medal = "🥇"
                    elif idx == 2:
                        medal = "🥈"
                    elif idx == 3:
                        medal = "🥉"
                    else:
                        medal = f"**{idx}.**"

                    leaderboard_text += f"{medal} {member.name} - 레벨 **{level}** (XP: {xp:,})\n"

            embed.description = leaderboard_text if leaderboard_text else "데이터가 없습니다."

            total_pages = (len(all_data) + limit - 1) // limit
            embed.set_footer(text=f"페이지 {page}/{total_pages} • 요청자: {interaction.user.name}")
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'순위표 조회 오류: {e}')

    @app_commands.command(name="setlevel", description="사용자의 레벨을 설정합니다 (관리자 전용)")
    @app_commands.describe(
        member="레벨을 설정할 멤버",
        level="설정할 레벨"
    )
    @app_commands.default_permissions(administrator=True)
    async def setlevel(self, interaction: discord.Interaction, member: discord.Member, level: int):
        """레벨 설정 (관리자)"""
        if level < 0:
            await interaction.response.send_message('❌ 레벨은 0 이상이어야 합니다.', ephemeral=True)
            return

        try:
            # 해당 레벨에 필요한 XP 계산
            required_xp = self._xp_for_level(level)

            # 데이터베이스 직접 업데이트
            await self.db.add_xp(member.guild.id, member.id, 0)  # 초기화
            # XP 설정을 위해 직접 SQL 실행
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as db:
                await db.execute('''
                    UPDATE user_levels
                    SET xp = ?, level = ?
                    WHERE guild_id = ? AND user_id = ?
                ''', (required_xp, level, interaction.guild.id, member.id))
                await db.commit()

            embed = discord.Embed(
                title="✅ 레벨 설정",
                description=f'{member.mention} 님의 레벨이 **{level}**로 설정되었습니다.',
                color=discord.Color.green()
            )
            embed.add_field(name="설정한 관리자", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) {member.name}의 레벨을 {level}로 설정')

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'레벨 설정 오류: {e}')

async def setup(bot):
    await bot.add_cog(Leveling(bot))
