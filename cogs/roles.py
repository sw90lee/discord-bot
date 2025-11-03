import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="autorole", description="신규 멤버에게 자동으로 부여할 역할을 설정합니다")
    @app_commands.describe(role="자동으로 부여할 역할")
    @app_commands.default_permissions(manage_roles=True)
    async def autorole(self, interaction: discord.Interaction, role: discord.Role):
        """자동 역할 설정"""
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message('❌ 봇보다 높거나 같은 역할은 자동 역할로 설정할 수 없습니다.', ephemeral=True)
            return

        try:
            await self.db.set_auto_role(interaction.guild.id, role.id)

            embed = discord.Embed(
                title="✅ 자동 역할 설정",
                description=f'신규 멤버에게 {role.mention} 역할이 자동으로 부여됩니다.',
                color=discord.Color.green()
            )
            embed.add_field(name="설정한 관리자", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) 자동 역할 설정: {role.name}')

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'자동 역할 설정 오류: {e}')

    @app_commands.command(name="removeautorole", description="자동 역할 설정을 제거합니다")
    @app_commands.default_permissions(manage_roles=True)
    async def removeautorole(self, interaction: discord.Interaction):
        """자동 역할 제거"""
        try:
            await self.db.remove_auto_role(interaction.guild.id)

            embed = discord.Embed(
                title="✅ 자동 역할 제거",
                description='자동 역할 설정이 제거되었습니다.',
                color=discord.Color.green()
            )
            embed.add_field(name="제거한 관리자", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) 자동 역할 제거')

        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'자동 역할 제거 오류: {e}')

    @app_commands.command(name="role", description="멤버에게 역할을 부여하거나 제거합니다")
    @app_commands.describe(
        member="대상 멤버",
        role="역할",
        action="부여 또는 제거"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="부여 (add)", value="add"),
        app_commands.Choice(name="제거 (remove)", value="remove")
    ])
    @app_commands.default_permissions(manage_roles=True)
    async def role(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
        action: app_commands.Choice[str]
    ):
        """역할 부여/제거"""
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message('❌ 봇보다 높거나 같은 역할은 관리할 수 없습니다.', ephemeral=True)
            return

        if role.position >= interaction.user.top_role.position and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message('❌ 자신보다 높거나 같은 역할은 관리할 수 없습니다.', ephemeral=True)
            return

        try:
            if action.value == "add":
                if role in member.roles:
                    await interaction.response.send_message(f'❌ {member.mention} 님은 이미 {role.mention} 역할을 가지고 있습니다.', ephemeral=True)
                    return

                await member.add_roles(role, reason=f'{interaction.user.name}에 의한 역할 부여')

                embed = discord.Embed(
                    title="✅ 역할 부여",
                    description=f'{member.mention} 님에게 {role.mention} 역할이 부여되었습니다.',
                    color=discord.Color.green()
                )
                logger.info(f'{interaction.user.name}이(가) {member.name}에게 {role.name} 역할 부여')

            else:  # remove
                if role not in member.roles:
                    await interaction.response.send_message(f'❌ {member.mention} 님은 {role.mention} 역할을 가지고 있지 않습니다.', ephemeral=True)
                    return

                await member.remove_roles(role, reason=f'{interaction.user.name}에 의한 역할 제거')

                embed = discord.Embed(
                    title="✅ 역할 제거",
                    description=f'{member.mention} 님의 {role.mention} 역할이 제거되었습니다.',
                    color=discord.Color.orange()
                )
                logger.info(f'{interaction.user.name}이(가) {member.name}의 {role.name} 역할 제거')

            embed.add_field(name="담당 관리자", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message('❌ 역할을 관리할 권한이 없습니다.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'역할 관리 오류: {e}')

    @app_commands.command(name="reactionrole", description="반응 역할을 설정합니다")
    @app_commands.describe(
        message_id="역할을 부여할 메시지 ID",
        emoji="반응할 이모지",
        role="부여할 역할"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def reactionrole(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        role: discord.Role
    ):
        """반응 역할 설정"""
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message('❌ 봇보다 높거나 같은 역할은 설정할 수 없습니다.', ephemeral=True)
            return

        try:
            msg_id = int(message_id)
            message = await interaction.channel.fetch_message(msg_id)

            # 데이터베이스에 저장
            success = await self.db.add_reaction_role(interaction.guild.id, msg_id, emoji, role.id)

            if not success:
                await interaction.response.send_message('❌ 해당 메시지와 이모지 조합은 이미 설정되어 있습니다.', ephemeral=True)
                return

            # 메시지에 이모지 추가
            await message.add_reaction(emoji)

            embed = discord.Embed(
                title="✅ 반응 역할 설정",
                description=f'메시지에 {emoji} 반응을 추가하면 {role.mention} 역할이 부여됩니다.',
                color=discord.Color.green()
            )
            embed.add_field(name="메시지 ID", value=message_id, inline=True)
            embed.add_field(name="이모지", value=emoji, inline=True)
            embed.add_field(name="역할", value=role.mention, inline=True)
            embed.add_field(name="설정한 관리자", value=interaction.user.mention, inline=False)
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user.name}이(가) 반응 역할 설정: {emoji} -> {role.name}')

        except ValueError:
            await interaction.response.send_message('❌ 올바른 메시지 ID를 입력해주세요.', ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message('❌ 해당 메시지를 찾을 수 없습니다.', ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message('❌ 이모지를 추가할 수 없습니다. 올바른 이모지인지 확인해주세요.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'❌ 오류 발생: {e}', ephemeral=True)
            logger.error(f'반응 역할 설정 오류: {e}')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """반응 추가 시 역할 부여"""
        if payload.user_id == self.bot.user.id:
            return

        # 반응 역할 확인
        emoji_str = str(payload.emoji)
        role_id = await self.db.get_reaction_role(payload.message_id, emoji_str)

        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)

        if not role or not member:
            return

        try:
            if role not in member.roles:
                await member.add_roles(role, reason="반응 역할")
                logger.info(f'{member.name}에게 반응 역할 {role.name} 부여')
        except Exception as e:
            logger.error(f'반응 역할 부여 오류: {e}')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """반응 제거 시 역할 제거"""
        if payload.user_id == self.bot.user.id:
            return

        # 반응 역할 확인
        emoji_str = str(payload.emoji)
        role_id = await self.db.get_reaction_role(payload.message_id, emoji_str)

        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)

        if not role or not member:
            return

        try:
            if role in member.roles:
                await member.remove_roles(role, reason="반응 역할 제거")
                logger.info(f'{member.name}의 반응 역할 {role.name} 제거')
        except Exception as e:
            logger.error(f'반응 역할 제거 오류: {e}')

async def setup(bot):
    await bot.add_cog(Roles(bot))
