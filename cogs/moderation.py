import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="kick", description="멤버를 서버에서 추방합니다")
    @app_commands.describe(
        member="추방할 멤버",
        reason="추방 사유"
    )
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "사유 없음"):
        """멤버 킥"""
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message('❌ 자신보다 높거나 같은 역할을 가진 멤버는 추방할 수 없습니다.', ephemeral=True)
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message('❌ 자기 자신을 추방할 수 없습니다.', ephemeral=True)
            return

        try:
            await member.kick(reason=f'{interaction.user.name}: {reason}')

            embed = discord.Embed(
                title="👢 멤버 추방",
                description=f'{member.mention} 님이 서버에서 추방되었습니다.',
                color=discord.Color.orange()
            )
            embed.add_field(name="사유", value=reason, inline=False)
            embed.add_field(name="담당 모더레이터", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) {member.name}를 추방함: {reason}')

        except discord.Forbidden:
            await interaction.response.send_message('❌ 해당 멤버를 추방할 권한이 없습니다.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'킥 명령어 오류: {e}')

    @app_commands.command(name="ban", description="멤버를 서버에서 차단합니다")
    @app_commands.describe(
        member="차단할 멤버",
        reason="차단 사유",
        delete_messages="삭제할 메시지 기간 (일)"
    )
    @app_commands.default_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "사유 없음",
        delete_messages: int = 0
    ):
        """멤버 밴"""
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message('❌ 자신보다 높거나 같은 역할을 가진 멤버는 차단할 수 없습니다.', ephemeral=True)
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message('❌ 자기 자신을 차단할 수 없습니다.', ephemeral=True)
            return

        try:
            await member.ban(
                reason=f'{interaction.user.name}: {reason}',
                delete_message_days=min(delete_messages, 7)
            )

            embed = discord.Embed(
                title="🔨 멤버 차단",
                description=f'{member.mention} 님이 서버에서 차단되었습니다.',
                color=discord.Color.red()
            )
            embed.add_field(name="사유", value=reason, inline=False)
            embed.add_field(name="담당 모더레이터", value=interaction.user.mention, inline=False)
            if delete_messages > 0:
                embed.add_field(name="삭제된 메시지", value=f'최근 {delete_messages}일', inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) {member.name}를 차단함: {reason}')

        except discord.Forbidden:
            await interaction.response.send_message('❌ 해당 멤버를 차단할 권한이 없습니다.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'밴 명령어 오류: {e}')

    @app_commands.command(name="unban", description="차단된 사용자의 차단을 해제합니다")
    @app_commands.describe(user_id="차단 해제할 사용자 ID")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        """언밴"""
        try:
            user_id_int = int(user_id)
            user = await self.bot.fetch_user(user_id_int)

            await interaction.guild.unban(user, reason=f'{interaction.user.name}에 의한 차단 해제')

            embed = discord.Embed(
                title="✅ 차단 해제",
                description=f'{user.mention} ({user.name})님의 차단이 해제되었습니다.',
                color=discord.Color.green()
            )
            embed.add_field(name="담당 모더레이터", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) {user.name}의 차단을 해제함')

        except ValueError:
            await interaction.response.send_message('❌ 올바른 사용자 ID를 입력해주세요.', ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message('❌ 해당 사용자를 찾을 수 없거나 차단되지 않았습니다.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'언밴 명령어 오류: {e}')

    @app_commands.command(name="timeout", description="멤버를 일시적으로 타임아웃합니다")
    @app_commands.describe(
        member="타임아웃할 멤버",
        minutes="타임아웃 시간 (분)",
        reason="타임아웃 사유"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: int,
        reason: str = "사유 없음"
    ):
        """타임아웃"""
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message('❌ 자신보다 높거나 같은 역할을 가진 멤버는 타임아웃할 수 없습니다.', ephemeral=True)
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message('❌ 자기 자신을 타임아웃할 수 없습니다.', ephemeral=True)
            return

        if minutes < 1 or minutes > 40320:  # 최대 28일
            await interaction.response.send_message('❌ 타임아웃 시간은 1분에서 40320분(28일) 사이여야 합니다.', ephemeral=True)
            return

        try:
            duration = timedelta(minutes=minutes)
            await member.timeout(duration, reason=f'{interaction.user.name}: {reason}')

            embed = discord.Embed(
                title="⏰ 타임아웃",
                description=f'{member.mention} 님이 타임아웃되었습니다.',
                color=discord.Color.orange()
            )
            embed.add_field(name="기간", value=f'{minutes}분', inline=True)
            embed.add_field(name="사유", value=reason, inline=False)
            embed.add_field(name="담당 모더레이터", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) {member.name}를 {minutes}분 타임아웃함: {reason}')

        except discord.Forbidden:
            await interaction.response.send_message('❌ 해당 멤버를 타임아웃할 권한이 없습니다.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'타임아웃 명령어 오류: {e}')

    @app_commands.command(name="untimeout", description="멤버의 타임아웃을 해제합니다")
    @app_commands.describe(member="타임아웃 해제할 멤버")
    @app_commands.default_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member):
        """타임아웃 해제"""
        try:
            await member.timeout(None, reason=f'{interaction.user.name}에 의한 타임아웃 해제')

            embed = discord.Embed(
                title="✅ 타임아웃 해제",
                description=f'{member.mention} 님의 타임아웃이 해제되었습니다.',
                color=discord.Color.green()
            )
            embed.add_field(name="담당 모더레이터", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) {member.name}의 타임아웃을 해제함')

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'타임아웃 해제 명령어 오류: {e}')

    @app_commands.command(name="clear", description="메시지를 대량 삭제합니다")
    @app_commands.describe(amount="삭제할 메시지 수 (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        """메시지 대량 삭제"""
        if amount < 1 or amount > 100:
            await interaction.response.send_message('❌ 1개에서 100개 사이의 메시지만 삭제할 수 있습니다.', ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
            deleted = await interaction.channel.purge(limit=amount)

            embed = discord.Embed(
                title="🗑️ 메시지 삭제",
                description=f'{len(deleted)}개의 메시지가 삭제되었습니다.',
                color=discord.Color.blue()
            )
            embed.add_field(name="담당 모더레이터", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f'{interaction.user.name}이(가) {len(deleted)}개의 메시지 삭제')

        except discord.Forbidden:
            await interaction.followup.send('❌ 메시지를 삭제할 권한이 없습니다.', ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'메시지 삭제 오류: {e}')

    @app_commands.command(name="warn", description="멤버에게 경고를 부여합니다")
    @app_commands.describe(
        member="경고할 멤버",
        reason="경고 사유"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """경고 부여"""
        if member.id == interaction.user.id:
            await interaction.response.send_message('❌ 자기 자신에게 경고를 줄 수 없습니다.', ephemeral=True)
            return

        try:
            await self.db.add_warning(interaction.guild.id, member.id, interaction.user.id, reason)
            warnings = await self.db.get_warnings(interaction.guild.id, member.id)
            warning_count = len(warnings)

            embed = discord.Embed(
                title="⚠️ 경고",
                description=f'{member.mention} 님에게 경고가 부여되었습니다.',
                color=discord.Color.yellow()
            )
            embed.add_field(name="사유", value=reason, inline=False)
            embed.add_field(name="총 경고 수", value=f'{warning_count}회', inline=True)
            embed.add_field(name="담당 모더레이터", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)

            # DM으로도 알림
            try:
                dm_embed = discord.Embed(
                    title="⚠️ 경고 알림",
                    description=f'{interaction.guild.name} 서버에서 경고를 받았습니다.',
                    color=discord.Color.yellow()
                )
                dm_embed.add_field(name="사유", value=reason, inline=False)
                dm_embed.add_field(name="총 경고 수", value=f'{warning_count}회', inline=True)
                await member.send(embed=dm_embed)
            except:
                pass  # DM 실패해도 무시

            logger.info(f'{interaction.user.name}이(가) {member.name}에게 경고 부여: {reason}')

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'경고 명령어 오류: {e}')

    @app_commands.command(name="warnings", description="멤버의 경고 목록을 확인합니다")
    @app_commands.describe(member="확인할 멤버")
    @app_commands.default_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        """경고 목록 확인"""
        try:
            warnings = await self.db.get_warnings(interaction.guild.id, member.id)

            if not warnings:
                await interaction.response.send_message(f'{member.mention} 님은 경고가 없습니다.', ephemeral=True)
                return

            embed = discord.Embed(
                title=f"⚠️ {member.name}의 경고 목록",
                description=f"총 {len(warnings)}개의 경고",
                color=discord.Color.yellow()
            )

            for idx, (warn_id, mod_id, reason, timestamp) in enumerate(warnings[:10], 1):
                moderator = interaction.guild.get_member(mod_id)
                mod_name = moderator.name if moderator else f"ID: {mod_id}"
                embed.add_field(
                    name=f"경고 #{warn_id}",
                    value=f"사유: {reason}\n모더레이터: {mod_name}\n시간: {timestamp}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'경고 목록 조회 오류: {e}')

    @app_commands.command(name="clearwarnings", description="멤버의 모든 경고를 삭제합니다")
    @app_commands.describe(member="경고를 삭제할 멤버")
    @app_commands.default_permissions(administrator=True)
    async def clearwarnings(self, interaction: discord.Interaction, member: discord.Member):
        """경고 삭제"""
        try:
            await self.db.clear_warnings(interaction.guild.id, member.id)

            embed = discord.Embed(
                title="✅ 경고 삭제",
                description=f'{member.mention} 님의 모든 경고가 삭제되었습니다.',
                color=discord.Color.green()
            )
            embed.add_field(name="담당 관리자", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) {member.name}의 경고를 모두 삭제함')

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'경고 삭제 오류: {e}')

async def setup(bot):
    await bot.add_cog(Moderation(bot))
