#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置模块 - 保存和加载应用设置
"""

import os
import json

# 默认设置
DEFAULT_SETTINGS = {
    "update_interval": 30 * 60,  # 默认更新间隔（秒）
    "update_interval_name": "30分钟",  # 默认更新间隔名称
    "focus_mode": False,  # 专注模式是否启用
    "last_update": None,  # 最后更新时间
}

# 设置文件路径
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_settings.json')

def load_settings():
    """加载设置"""
    settings = DEFAULT_SETTINGS.copy()
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved_settings = json.load(f)
                # 更新默认设置
                settings.update(saved_settings)
    except Exception as e:
        print(f"加载设置时出错: {e}")
    
    return settings

def save_settings(settings):
    """保存设置"""
    try:
        print(f"正在保存设置: {json.dumps(settings, ensure_ascii=False)}")
        print(f"保存到文件: {SETTINGS_FILE}")
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        print("设置保存成功!")
        return True
    except Exception as e:
        print(f"保存设置时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_setting(key, value):
    """更新单个设置项"""
    settings = load_settings()
    old_value = settings.get(key)
    settings[key] = value
    print(f"更新设置 {key}: {old_value} -> {value}")
    return save_settings(settings)

if __name__ == "__main__":
    # 测试设置模块
    print("当前设置:", load_settings())
    update_setting("update_interval", 60)
    print("更新后设置:", load_settings()) 