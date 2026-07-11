"""配置加载工具"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

# 缓存配置内容
_config_cache: Optional[Dict[str, Any]] = None
_config_mtime: Optional[float] = None


def load_algorithm_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """加载推荐算法配置

    支持缓存，但当文件修改时间变化时自动重新加载

    Args:
        config_path: 配置文件路径，默认使用项目config目录下的文件

    Returns:
        dict: 配置字典
    """
    global _config_cache, _config_mtime

    if config_path is None:
        # 默认路径：项目根目录/server/config/
        base_dir = Path(__file__).parent.parent.parent
        config_path = base_dir / "config" / "home_page_algorithm.yaml"
    else:
        config_path = Path(config_path)

    # 检查文件是否需要重新加载
    try:
        current_mtime = config_path.stat().st_mtime
        if _config_cache is not None and _config_mtime == current_mtime:
            return _config_cache
        _config_mtime = current_mtime
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    # 读取并解析YAML
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    _config_cache = config
    return config


def get_section_config(config: Dict[str, Any], section_name: str) -> Dict[str, Any]:
    """获取特定区块的配置"""
    sections = config.get("sections", {})
    return sections.get(section_name, {})


def reload_config() -> Dict[str, Any]:
    """强制重新加载配置"""
    global _config_cache, _config_mtime
    _config_cache = None
    _config_mtime = None
    return load_algorithm_config()
