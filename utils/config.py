import json
import os
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path='data/config.json'):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """설정 파일 로드"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f'설정 파일 로드 완료: {self.config_path}')
                    return config
            except Exception as e:
                logger.error(f'설정 파일 로드 실패: {e}')
                return self._default_config()
        else:
            logger.info('설정 파일이 없습니다. 기본 설정을 사용합니다.')
            config = self._default_config()
            self._save_config(config)
            return config

    def _default_config(self) -> dict:
        """기본 설정"""
        return {
            'welcome': {
                'enabled': True,
                'title': '🎉 새로운 멤버가 도착했습니다!',
                'description': '{mention}님, 환영합니다!',
                'color': 0x00ff00,  # 녹색
                'footer': '즐거운 시간 되세요!',
                'show_member_count': True,
                'show_avatar': True
            },
            'leveling': {
                'enabled': True,
                'xp_per_message': 10,
                'xp_cooldown': 60,  # 초 단위 (1분에 한 번만 XP 획득)
                'level_up_message': '🎊 {mention}님이 레벨 {level}에 도달했습니다!',
                'announce_level_up': True
            },
            'moderation': {
                'log_channel_id': None,  # 로그 채널 ID (설정 시)
                'max_warnings': 3  # 최대 경고 횟수
            }
        }

    def _save_config(self, config: dict):
        """설정 파일 저장"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f'설정 파일 저장 완료: {self.config_path}')
        except Exception as e:
            logger.error(f'설정 파일 저장 실패: {e}')

    def get(self, *keys, default=None) -> Any:
        """설정 값 가져오기 (중첩된 키 지원)"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, *keys, value: Any):
        """설정 값 변경"""
        if not keys:
            return

        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self._save_config(self.config)
        logger.info(f'설정 변경: {".".join(keys)} = {value}')

    def get_welcome_config(self, guild_id: Optional[int] = None) -> dict:
        """환영 메시지 설정 가져오기 (서버별 설정 지원)"""
        if guild_id:
            guild_welcome = self.get('guilds', str(guild_id), 'welcome')
            if guild_welcome:
                return guild_welcome
        return self.get('welcome', default={})

    def set_welcome_config(self, guild_id: int, **kwargs):
        """서버별 환영 메시지 설정"""
        guild_str = str(guild_id)
        if 'guilds' not in self.config:
            self.config['guilds'] = {}
        if guild_str not in self.config['guilds']:
            self.config['guilds'][guild_str] = {}
        if 'welcome' not in self.config['guilds'][guild_str]:
            self.config['guilds'][guild_str]['welcome'] = {}

        # 기존 설정 유지하면서 업데이트
        self.config['guilds'][guild_str]['welcome'].update(kwargs)
        self._save_config(self.config)
        logger.info(f'서버 {guild_id}의 환영 메시지 설정 변경')

    def reload(self):
        """설정 파일 다시 로드"""
        self.config = self._load_config()
        logger.info('설정 파일 다시 로드됨')
