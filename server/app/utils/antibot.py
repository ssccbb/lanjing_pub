"""反爬虫工具 - User-Agent 检查"""
import re
from typing import Optional, Set
from fastapi import Request, HTTPException, status

# 已知的爬虫/机器人 User-Agent 黑名单（正则模式）
CRAWLER_PATTERNS = [
    # 常见爬虫框架
    r"python-requests",
    r"urllib",
    r"scrapy",
    r"curl",
    r"wget",
    r"httpclient",
    r"java",
    r"okhttp",
    r"httpclient",
    r"phantomjs",
    r"selenium",
    r"puppeteer",
    r"playwright",
    r"headlesschrome",
    r"headless",
    # 扫描工具
    r"nikto",
    r"nmap",
    r"sqlmap",
    r"masscan",
    r"zgrab",
    r"gobuster",
    r"dirbuster",
    r"burp",
    r"metasploit",
    r"nessus",
    r"openvas",
    r"acunetix",
    r"awvs",
    r"wpscan",
    # 搜索引擎爬虫（可选，根据需要开启）
    # r"baiduspider",
    # r"googlebot",
    # r"bingbot",
    # r"yandexbot",
    # r"sogou",
    # r"360spider",
    # 其他可疑客户端
    r"spider",
    r"crawler",
    r"bot[^a-z]",
    r"scanner",
    r"apachebench",
    r"jmeter",
    r"loader",
    r"harvest",
]

# 编译正则以提高性能
CRAWLER_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in CRAWLER_PATTERNS]

# 白名单（允许的爬虫，如果黑名单误伤可以在这里放行）
ALLOWED_BOTS: Set[str] = {
    # 搜索引擎爬虫（允许收录）
    "baiduspider",      # 百度
    "googlebot",        # Google
    "bingbot",          # 必应
    "yandexbot",        # Yandex
    "sogou",            # 搜狗
    "360spider",        # 360
    "shenmaspider",     # 神马
    "bytespider",       # 字节跳动(今日头条)
    "duckduckbot",      # DuckDuckGo
    "slurp",            # Yahoo
    "facebookexternalhit",  # Facebook
    "twitterbot",       # Twitter
    "linkedinbot",      # LinkedIn
    "applebot",         # Apple
}


def is_crawler(user_agent: Optional[str]) -> bool:
    """
    检查 User-Agent 是否为爬虫/机器人
    :param user_agent: User-Agent 字符串
    :return: True 如果是爬虫，False 如果是正常浏览器
    """
    if not user_agent:
        # 空 User-Agent 视为爬虫
        return True

    ua_lower = user_agent.lower()

    # 检查是否在白名单
    for allowed in ALLOWED_BOTS:
        if allowed.lower() in ua_lower:
            return False

    # 检查是否匹配黑名单模式
    for pattern in CRAWLER_REGEX:
        if pattern.search(user_agent):
            return True

    # 检查是否是浏览器（简单判断）
    # 正常浏览器通常包含: Mozilla, Chrome, Safari, Firefox, Edge, Opera 等
    browser_keywords = ["mozilla", "chrome", "safari", "firefox", "edge", "opera"]
    has_browser_keyword = any(kw in ua_lower for kw in browser_keywords)

    # 如果不包含任何浏览器关键词，可能也是爬虫
    if not has_browser_keyword:
        # 但可能是移动端 App 或其他合法客户端，这里保守处理
        # 只拦截明显非浏览器的
        suspicious = ["libwww", "lwp-", "pecl", "modules", "package"]
        for s in suspicious:
            if s in ua_lower:
                return True

    return False


def check_user_agent(request: Request) -> bool:
    """
    FastAPI 依赖函数：检查 User-Agent
    如果是爬虫则抛出 403 异常
    :param request: FastAPI Request 对象
    :return: True 如果是正常请求
    :raises: HTTPException 403 如果是爬虫
    """
    user_agent = request.headers.get("user-agent", "")
    client_ip = _get_client_ip(request)

    if is_crawler(user_agent):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return True


def check_user_agent_soft(request: Request) -> bool:
    """
    软检查：只记录日志，不拦截
    用于观察阶段，先不阻断
    :param request: FastAPI Request 对象
    :return: True 如果是爬虫，False 正常
    """
    user_agent = request.headers.get("user-agent", "")
    return is_crawler(user_agent)


def _get_client_ip(request: Request) -> str:
    """获取客户端IP"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_crawler_info(user_agent: Optional[str]) -> Optional[str]:
    """
    获取匹配的爬虫类型信息（用于日志记录）
    :param user_agent: User-Agent 字符串
    :return: 匹配的爬虫类型，如果不是爬虫返回 None
    """
    if not user_agent:
        return "empty_ua"

    for pattern in CRAWLER_REGEX:
        match = pattern.search(user_agent)
        if match:
            return match.group(0)

    return None
