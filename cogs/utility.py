import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="봇의 응답 속도를 확인합니다")
    async def ping(self, interaction: discord.Interaction):
        """핑 확인"""
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f'지연시간: {latency}ms',
            color=discord.Color.blue()
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="서버 정보를 확인합니다")
    async def serverinfo(self, interaction: discord.Interaction):
        """서버 정보"""
        guild = interaction.guild

        embed = discord.Embed(
            title=f"📊 {guild.name} 정보",
            color=discord.Color.blue()
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # 기본 정보
        embed.add_field(name="서버 ID", value=guild.id, inline=True)
        embed.add_field(name="소유자", value=guild.owner.mention if guild.owner else "알 수 없음", inline=True)
        embed.add_field(name="생성일", value=guild.created_at.strftime('%Y-%m-%d'), inline=True)

        # 멤버 정보
        total_members = guild.member_count
        bot_count = len([m for m in guild.members if m.bot])
        human_count = total_members - bot_count

        embed.add_field(name="전체 멤버", value=total_members, inline=True)
        embed.add_field(name="사람", value=human_count, inline=True)
        embed.add_field(name="봇", value=bot_count, inline=True)

        # 채널 정보
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)

        embed.add_field(name="텍스트 채널", value=text_channels, inline=True)
        embed.add_field(name="음성 채널", value=voice_channels, inline=True)
        embed.add_field(name="카테고리", value=categories, inline=True)

        # 기타 정보
        embed.add_field(name="역할 수", value=len(guild.roles), inline=True)
        embed.add_field(name="이모지 수", value=len(guild.emojis), inline=True)
        embed.add_field(name="부스트 레벨", value=guild.premium_tier, inline=True)

        embed.set_footer(text=f"요청자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="사용자 정보를 확인합니다")
    @app_commands.describe(member="정보를 확인할 멤버 (선택사항)")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        """사용자 정보"""
        if member is None:
            member = interaction.user

        embed = discord.Embed(
            title=f"👤 {member.name}의 정보",
            color=member.color
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        # 기본 정보
        embed.add_field(name="사용자 ID", value=member.id, inline=True)
        embed.add_field(name="닉네임", value=member.display_name, inline=True)
        embed.add_field(name="봇 여부", value="예" if member.bot else "아니오", inline=True)

        # 날짜 정보
        embed.add_field(name="계정 생성일", value=member.created_at.strftime('%Y-%m-%d %H:%M'), inline=True)
        embed.add_field(name="서버 참가일", value=member.joined_at.strftime('%Y-%m-%d %H:%M') if member.joined_at else "알 수 없음", inline=True)

        # 역할 정보
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        if roles:
            embed.add_field(name=f"역할 ({len(roles)}개)", value=" ".join(roles[:10]), inline=False)
        else:
            embed.add_field(name="역할", value="없음", inline=False)

        # 상태
        status_emoji = {
            discord.Status.online: "🟢 온라인",
            discord.Status.idle: "🟡 자리 비움",
            discord.Status.dnd: "🔴 다른 용무 중",
            discord.Status.offline: "⚫ 오프라인"
        }
        embed.add_field(name="상태", value=status_emoji.get(member.status, "알 수 없음"), inline=True)

        embed.set_footer(text=f"요청자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll", description="투표를 생성합니다")
    @app_commands.describe(
        question="투표 질문",
        option1="선택지 1",
        option2="선택지 2",
        option3="선택지 3 (선택사항)",
        option4="선택지 4 (선택사항)",
        option5="선택지 5 (선택사항)"
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: str = None,
        option4: str = None,
        option5: str = None
    ):
        """투표 생성"""
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        if option5:
            options.append(option5)

        # 이모지 번호
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

        embed = discord.Embed(
            title="📊 " + question,
            color=discord.Color.blue()
        )

        description = "\n".join([f"{emojis[i]} {opt}" for i, opt in enumerate(options)])
        embed.description = description

        embed.set_footer(text=f"투표 생성자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

        # 반응 추가
        message = await interaction.original_response()
        for i in range(len(options)):
            await message.add_reaction(emojis[i])

        logger.info(f'{interaction.user.name}이(가) 투표 생성: {question}')

    @app_commands.command(name="announce", description="공지사항을 생성합니다")
    @app_commands.describe(
        title="공지 제목",
        description="공지 내용",
        color="색상 (red, green, blue, yellow, purple, orange)"
    )
    @app_commands.choices(color=[
        app_commands.Choice(name="빨강 (red)", value="red"),
        app_commands.Choice(name="초록 (green)", value="green"),
        app_commands.Choice(name="파랑 (blue)", value="blue"),
        app_commands.Choice(name="노랑 (yellow)", value="yellow"),
        app_commands.Choice(name="보라 (purple)", value="purple"),
        app_commands.Choice(name="주황 (orange)", value="orange")
    ])
    @app_commands.default_permissions(manage_messages=True)
    async def announce(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: app_commands.Choice[str] = None
    ):
        """공지 생성"""
        color_map = {
            "red": discord.Color.red(),
            "green": discord.Color.green(),
            "blue": discord.Color.blue(),
            "yellow": discord.Color.yellow(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange()
        }

        embed_color = color_map.get(color.value if color else "blue", discord.Color.blue())

        embed = discord.Embed(
            title="📢 " + title,
            description=description,
            color=embed_color
        )

        embed.set_footer(text=f"작성자: {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)
        logger.info(f'{interaction.user.name}이(가) 공지 생성: {title}')

    @app_commands.command(name="avatar", description="사용자의 아바타를 확인합니다")
    @app_commands.describe(member="아바타를 확인할 멤버 (선택사항)")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        """아바타 확인"""
        if member is None:
            member = interaction.user

        embed = discord.Embed(
            title=f"{member.name}의 아바타",
            color=member.color
        )

        embed.set_image(url=member.display_avatar.url)

        embed.add_field(
            name="다운로드",
            value=f"[클릭하여 다운로드]({member.display_avatar.url})",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
