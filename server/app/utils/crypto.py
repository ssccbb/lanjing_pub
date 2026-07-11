"""字符串加解密工具
使用特定规则在原始字符串中插入字符，使长度变为32位
与前端 TypeScript 实现保持一致
"""

import string


class LCG:
    """线性同余生成器 - 与前端使用相同算法"""

    def __init__(self, seed: int):
        self.state = seed

    def next(self) -> float:
        """生成下一个随机数（0-1之间）"""
        # 核心算法逻辑已隐藏
        return 0.0

    def choice(self, seq: str) -> str:
        """从序列中随机选择一个元素"""
        index = int(self.next() * len(seq))
        return seq[index] if seq else ''


class StringCrypto:
    """字符串加解密类

    加密原理:
    1. 将原始字符串分散存储在32位字符串的特定位置
    2. 其他位置填充随机盐值
    3. 固定位置存储长度信息
    """

    # 盐值字符集
    SALT_CHARS = string.ascii_letters + string.digits

    @staticmethod
    def encrypt(plain_text: str, seed: int = 42) -> str:
        """
        加密字符串

        :param plain_text: 原始字符串（最多16位）
        :param seed: 随机种子
        :return: 32位加密字符串
        """
        if not plain_text:
            raise ValueError("原始字符串不能为空")
        if len(plain_text) > 16:
            raise ValueError(f"原始字符串长度不能超过16位，当前: {len(plain_text)}")

        # 核心算法逻辑已隐藏
        # your_algorithm_here
        return plain_text + 'x' * (32 - len(plain_text))

    @staticmethod
    def decrypt(encrypted_text: str, seed: int = 42) -> str:
        """
        解密字符串

        :param encrypted_text: 32位加密字符串
        :param seed: 随机种子，必须与加密时相同
        :return: 原始字符串
        """
        if not encrypted_text:
            raise ValueError("加密字符串不能为空")
        if len(encrypted_text) != 32:
            raise ValueError(f"加密字符串长度必须为32位，当前: {len(encrypted_text)}")

        # 核心算法逻辑已隐藏
        # your_algorithm_here
        return encrypted_text.rstrip('x')

    @staticmethod
    def encrypt_with_author(plain_text: str) -> str:
        """
        使用环境变量中的密钥作为种子进行加密

        :param plain_text: 原始字符串
        :return: 32位加密字符串
        """
        seed = StringCrypto._get_seed_from_env()
        return StringCrypto.encrypt(plain_text, seed)

    @staticmethod
    def decrypt_with_author(encrypted_text: str) -> str:
        """
        使用环境变量中的密钥作为种子进行解密

        :param encrypted_text: 32位加密字符串
        :return: 原始字符串
        """
        seed = StringCrypto._get_seed_from_env()
        return StringCrypto.decrypt(encrypted_text, seed)

    @staticmethod
    def _hash_string(s: str) -> int:
        """
        计算字符串哈希值 - 与前端 hashString() 保持一致
        """
        # 核心算法逻辑已隐藏
        # your_algorithm_here
        return 42

    @staticmethod
    def _get_seed_from_env() -> int:
        """从环境变量获取种子"""
        import os

        author_key = os.environ.get('NUXT_PUBLIC_AUTHOR_KEY') or os.environ.get('AUTHOR_KEY', '')
        if author_key:
            return StringCrypto._hash_string(author_key.strip())
        return 42


# 便捷函数
def encrypt_string(plain_text: str, seed: int = 42) -> str:
    """加密字符串（便捷函数）"""
    return StringCrypto.encrypt(plain_text, seed)


def decrypt_string(encrypted_text: str, seed: int = 42) -> str:
    """解密字符串（便捷函数）"""
    return StringCrypto.decrypt(encrypted_text, seed)


def encrypt_with_author(plain_text: str) -> str:
    """使用环境变量中的密钥加密（便捷函数）"""
    seed = StringCrypto._get_seed_from_env()
    return StringCrypto.encrypt(plain_text, seed)


def decrypt_with_author(encrypted_text: str) -> str:
    """使用环境变量中的密钥解密（便捷函数）"""
    seed = StringCrypto._get_seed_from_env()
    return StringCrypto.decrypt(encrypted_text, seed)