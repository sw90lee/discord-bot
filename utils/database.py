import sqlite3
import aiosqlite
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='data/bot.db'):
        self.db_path = db_path

    async def setup(self):
        """데이터베이스 초기화 및 테이블 생성"""
        async with aiosqlite.connect(self.db_path) as db:
            # 레벨링 테이블
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_levels (
                    guild_id INTEGER,
                    user_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    last_message_time TIMESTAMP,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')

            # 경고 테이블
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 자동 역할 테이블
            await db.execute('''
                CREATE TABLE IF NOT EXISTS auto_roles (
                    guild_id INTEGER PRIMARY KEY,
                    role_id INTEGER
                )
            ''')

            # 반응 역할 테이블
            await db.execute('''
                CREATE TABLE IF NOT EXISTS reaction_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    message_id INTEGER,
                    emoji TEXT,
                    role_id INTEGER,
                    UNIQUE(message_id, emoji)
                )
            ''')

            # 주식 감시 목록 테이블
            await db.execute('''
                CREATE TABLE IF NOT EXISTS stock_watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    ticker TEXT,
                    name TEXT,
                    last_price REAL DEFAULT 0,
                    last_change_percent REAL DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, ticker)
                )
            ''')

            await db.commit()
            logger.info('데이터베이스 초기화 완료')

    # ===== 레벨링 시스템 =====
    async def add_xp(self, guild_id: int, user_id: int, xp_amount: int = 10):
        """XP 추가 및 레벨업 확인"""
        async with aiosqlite.connect(self.db_path) as db:
            # 현재 XP와 레벨 가져오기
            async with db.execute(
                'SELECT xp, level FROM user_levels WHERE guild_id = ? AND user_id = ?',
                (guild_id, user_id)
            ) as cursor:
                result = await cursor.fetchone()

            if result:
                current_xp, current_level = result
                new_xp = current_xp + xp_amount
                new_level = self._calculate_level(new_xp)

                await db.execute('''
                    UPDATE user_levels
                    SET xp = ?, level = ?, total_messages = total_messages + 1, last_message_time = ?
                    WHERE guild_id = ? AND user_id = ?
                ''', (new_xp, new_level, datetime.now(), guild_id, user_id))

                leveled_up = new_level > current_level
            else:
                # 새 사용자
                new_xp = xp_amount
                new_level = self._calculate_level(new_xp)
                await db.execute('''
                    INSERT INTO user_levels (guild_id, user_id, xp, level, total_messages, last_message_time)
                    VALUES (?, ?, ?, ?, 1, ?)
                ''', (guild_id, user_id, new_xp, new_level, datetime.now()))

                leveled_up = new_level > 0

            await db.commit()
            return new_level if leveled_up else None

    def _calculate_level(self, xp: int) -> int:
        """XP로부터 레벨 계산 (필요 XP: 5 * (level ^ 2) + 50 * level + 100)"""
        level = 0
        while xp >= self._xp_for_level(level + 1):
            level += 1
        return level

    def _xp_for_level(self, level: int) -> int:
        """특정 레벨에 도달하기 위한 총 XP"""
        return 5 * (level ** 2) + 50 * level + 100

    async def get_user_level(self, guild_id: int, user_id: int):
        """사용자 레벨 정보 가져오기"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT xp, level, total_messages
                FROM user_levels
                WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id)) as cursor:
                return await cursor.fetchone()

    async def get_leaderboard(self, guild_id: int, limit: int = 10):
        """서버 레벨 순위표"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT user_id, xp, level, total_messages
                FROM user_levels
                WHERE guild_id = ?
                ORDER BY xp DESC
                LIMIT ?
            ''', (guild_id, limit)) as cursor:
                return await cursor.fetchall()

    async def get_user_rank(self, guild_id: int, user_id: int):
        """사용자의 서버 내 순위"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT COUNT(*) + 1
                FROM user_levels
                WHERE guild_id = ? AND xp > (
                    SELECT xp FROM user_levels WHERE guild_id = ? AND user_id = ?
                )
            ''', (guild_id, guild_id, user_id)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

    # ===== 경고 시스템 =====
    async def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str):
        """경고 추가"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, user_id, moderator_id, reason))
            await db.commit()

    async def get_warnings(self, guild_id: int, user_id: int):
        """사용자의 경고 목록"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT id, moderator_id, reason, timestamp
                FROM warnings
                WHERE guild_id = ? AND user_id = ?
                ORDER BY timestamp DESC
            ''', (guild_id, user_id)) as cursor:
                return await cursor.fetchall()

    async def clear_warnings(self, guild_id: int, user_id: int):
        """사용자의 모든 경고 삭제"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM warnings WHERE guild_id = ? AND user_id = ?',
                (guild_id, user_id)
            )
            await db.commit()

    # ===== 자동 역할 =====
    async def set_auto_role(self, guild_id: int, role_id: int):
        """자동 역할 설정"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO auto_roles (guild_id, role_id)
                VALUES (?, ?)
            ''', (guild_id, role_id))
            await db.commit()

    async def get_auto_role(self, guild_id: int):
        """자동 역할 가져오기"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT role_id FROM auto_roles WHERE guild_id = ?',
                (guild_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

    async def remove_auto_role(self, guild_id: int):
        """자동 역할 제거"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM auto_roles WHERE guild_id = ?', (guild_id,))
            await db.commit()

    # ===== 반응 역할 =====
    async def add_reaction_role(self, guild_id: int, message_id: int, emoji: str, role_id: int):
        """반응 역할 추가"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute('''
                    INSERT INTO reaction_roles (guild_id, message_id, emoji, role_id)
                    VALUES (?, ?, ?, ?)
                ''', (guild_id, message_id, emoji, role_id))
                await db.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    async def get_reaction_role(self, message_id: int, emoji: str):
        """반응 역할 가져오기"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT role_id FROM reaction_roles
                WHERE message_id = ? AND emoji = ?
            ''', (message_id, emoji)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

    async def get_message_reaction_roles(self, message_id: int):
        """특정 메시지의 모든 반응 역할"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT emoji, role_id FROM reaction_roles
                WHERE message_id = ?
            ''', (message_id,)) as cursor:
                return await cursor.fetchall()

    async def remove_reaction_role(self, message_id: int, emoji: str):
        """반응 역할 제거"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM reaction_roles WHERE message_id = ? AND emoji = ?',
                (message_id, emoji)
            )
            await db.commit()

    # ===== 주식 감시 목록 =====
    async def add_stock_to_watchlist(self, guild_id: int, ticker: str, name: str):
        """주식 감시 목록에 추가"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute('''
                    INSERT INTO stock_watchlist (guild_id, ticker, name)
                    VALUES (?, ?, ?)
                ''', (guild_id, ticker, name))
                await db.commit()
                return True
            except:
                return False

    async def remove_stock_from_watchlist(self, guild_id: int, ticker: str):
        """주식 감시 목록에서 제거"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM stock_watchlist WHERE guild_id = ? AND ticker = ?',
                (guild_id, ticker)
            )
            await db.commit()

    async def get_watchlist(self, guild_id: int):
        """서버의 주식 감시 목록 가져오기"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT ticker, name, last_price, last_change_percent
                FROM stock_watchlist
                WHERE guild_id = ?
                ORDER BY added_at
            ''', (guild_id,)) as cursor:
                return await cursor.fetchall()

    async def get_watchlist_count(self, guild_id: int):
        """서버의 주식 감시 목록 개수"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT COUNT(*) FROM stock_watchlist WHERE guild_id = ?',
                (guild_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

    async def update_stock_price(self, guild_id: int, ticker: str, price: float, change_percent: float):
        """주식 가격 업데이트"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE stock_watchlist
                SET last_price = ?, last_change_percent = ?
                WHERE guild_id = ? AND ticker = ?
            ''', (price, change_percent, guild_id, ticker))
            await db.commit()
