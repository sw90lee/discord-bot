import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.db = bot.db

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """새 멤버가 서버에 참가했을 때"""
        logger.info(f'새 멤버 참가: {member.name} (ID: {member.id}) in {member.guild.name}')

        welcome_config = self.config.get_welcome_config(member.guild.id)

        if not welcome_config.get('enabled', True):
            logger.info('환영 메시지가 비활성화되어 있습니다.')
            return

        # 환영 채널 결정
        channel = None
        welcome_channel_id = self.config.get('welcome_channel_id') or \
                           self.config.get('guilds', str(member.guild.id), 'welcome_channel_id')

        if welcome_channel_id:
            channel = self.bot.get_channel(int(welcome_channel_id))

        if not channel:
            channel = member.guild.system_channel

        if not channel:
            logger.warning(f'환영 메시지를 보낼 채널을 찾을 수 없습니다: {member.guild.name}')
            return

        try:
            # 환영 메시지 생성
            title = welcome_config.get('title', '🎉 새로운 멤버가 도착했습니다!')
            description = welcome_config.get('description', '{mention}님, 환영합니다!')
            description = description.format(
                mention=member.mention,
                name=member.name,
                server=member.guild.name,
                member_count=member.guild.member_count
            )

            color = welcome_config.get('color', 0x00ff00)
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color(color)
            )

            if welcome_config.get('show_avatar', True):
                embed.set_thumbnail(url=member.display_avatar.url)

            if welcome_config.get('show_member_count', True):
                embed.add_field(
                    name="서버 정보",
                    value=f"현재 멤버 수: {member.guild.member_count}명",
                    inline=False
                )

            footer_text = welcome_config.get('footer', '즐거운 시간 되세요!')
            embed.set_footer(text=footer_text)
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)
            logger.info(f'환영 메시지 전송 완료: {member.name}')

            # 자동 역할 부여
            auto_role_id = await self.db.get_auto_role(member.guild.id)
            if auto_role_id:
                role = member.guild.get_role(auto_role_id)
                if role:
                    try:
                        await member.add_roles(role, reason="자동 역할 부여")
                        logger.info(f'{member.name}에게 자동 역할 {role.name} 부여')
                    except Exception as e:
                        logger.error(f'자동 역할 부여 실패: {e}')

        except Exception as e:
            logger.error(f'환영 메시지 전송 중 오류: {e}')

    @app_commands.command(name="setwelcome", description="환영 메시지 설정")
    @app_commands.describe(
        title="환영 메시지 제목",
        description="환영 메시지 내용 ({mention}, {name}, {server}, {member_count} 사용 가능)",
        color="색상 (hex 코드, 예: #00ff00)",
        footer="하단 텍스트"
    )
    @app_commands.default_permissions(administrator=True)
    async def setwelcome(
        self,
        interaction: discord.Interaction,
        title: str = None,
        description: str = None,
        color: str = None,
        footer: str = None
    ):
        """환영 메시지 사용자 정의"""
        updates = {}

        if title:
            updates['title'] = title
        if description:
            updates['description'] = description
        if footer:
            updates['footer'] = footer
        if color:
            try:
                # hex 색상 코드를 정수로 변환
                color_int = int(color.replace('#', ''), 16)
                updates['color'] = color_int
            except ValueError:
                await interaction.response.send_message('❌ 올바른 색상 코드를 입력해주세요 (예: #00ff00)', ephemeral=True)
                return

        if not updates:
            await interaction.response.send_message('❌ 변경할 설정을 하나 이상 입력해주세요.', ephemeral=True)
            return

        self.config.set_welcome_config(interaction.guild.id, **updates)

        embed = discord.Embed(
            title="✅ 환영 메시지 설정 완료",
            description="환영 메시지가 업데이트되었습니다.",
            color=discord.Color.green()
        )

        for key, value in updates.items():
            embed.add_field(name=key, value=str(value), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f'{interaction.user.name}이(가) 환영 메시지 설정 변경: {updates}')

    @app_commands.command(name="welcometest", description="환영 메시지 테스트")
    @app_commands.default_permissions(administrator=True)
    async def welcometest(self, interaction: discord.Interaction):
        """현재 환영 메시지 설정 테스트"""
        welcome_config = self.config.get_welcome_config(interaction.guild.id)

        title = welcome_config.get('title', '🎉 새로운 멤버가 도착했습니다!')
        description = welcome_config.get('description', '{mention}님, 환영합니다!')
        description = description.format(
            mention=interaction.user.mention,
            name=interaction.user.name,
            server=interaction.guild.name,
            member_count=interaction.guild.member_count
        )

        color = welcome_config.get('color', 0x00ff00)
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color(color)
        )

        if welcome_config.get('show_avatar', True):
            embed.set_thumbnail(url=interaction.user.display_avatar.url)

        if welcome_config.get('show_member_count', True):
            embed.add_field(
                name="서버 정보",
                value=f"현재 멤버 수: {interaction.guild.member_count}명",
                inline=False
            )

        footer_text = welcome_config.get('footer', '즐거운 시간 되세요!')
        embed.set_footer(text=footer_text)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message("환영 메시지 미리보기:", embed=embed, ephemeral=True)

    @app_commands.command(name="welcomechannel", description="환영 메시지를 보낼 채널 설정")
    @app_commands.describe(channel="환영 메시지를 보낼 채널")
    @app_commands.default_permissions(administrator=True)
    async def welcomechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """환영 메시지 채널 설정"""
        guild_str = str(interaction.guild.id)
        if 'guilds' not in self.config.config:
            self.config.config['guilds'] = {}
        if guild_str not in self.config.config['guilds']:
            self.config.config['guilds'][guild_str] = {}

        self.config.config['guilds'][guild_str]['welcome_channel_id'] = channel.id
        self.config._save_config(self.config.config)

        await interaction.response.send_message(
            f'✅ 환영 메시지 채널이 {channel.mention}로 설정되었습니다.',
            ephemeral=True
        )
        logger.info(f'환영 채널 설정: {channel.name} in {interaction.guild.name}')

async def setup(bot):
    await bot.add_cog(Welcome(bot))
