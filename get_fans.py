import time
import os
import csv
import datetime

# 导入CSDN数据获取模块
from csdn import extract_csdn_stats
# 导入今日头条数据获取模块
from toutiao import parse_toutiao_user_stats

def load_config():
    """从配置文件加载URL"""
    config = {
        "CSDN_URL": "https://blog.csdn.net/qq_34598061",  # 默认URL
        "TOUTIAO_URL": "https://www.toutiao.com/c/user/token/MS4wLjABAAAA-vxeZNtd-323uOaHVG-qQJnP0kL3_QSOTO85-9GJPXo/"  # 默认URL
    }
    
    # 尝试读取配置文件
    try:
        config_file = 'config.env'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
            print(f"已从{config_file}加载配置")
    except Exception as e:
        print(f"无法加载配置文件: {e}")
    
    return config

def monitor_platforms(interval=5, duration=None):
    print(f"开始监控多平台数据")
    print(f"数据采集频率：每 {interval} 秒一次")
    print("按 Ctrl+C 停止...")

    # Initialize start time if duration is specified
    start_time = time.time() if duration else None

    try:
        while True:
            data = extract_csdn_stats(csdn_url)
            print(data)

            data = parse_toutiao_user_stats(toutiao_url)
            print(data)

            # 检查是否超过指定的运行时间
            if duration and (time.time() - start_time) > duration:
                print(f"监控完成。已运行 {duration} 秒。")
                break

            print(f"\n等待 {interval} 秒后继续...")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n监控被用户停止。")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    # 加载配置
    config = load_config()
    
    # CSDN 博客统计
    csdn_url = config.get("CSDN_URL")
    csdn_data = extract_csdn_stats(csdn_url)
    print(f"\n[{csdn_data['site']} - {csdn_data['timestamp']}]")
    print(f"总访问量: {csdn_data['visitors']}")
    print(f"原创: {csdn_data['originals']}")
    print(f"粉丝: {csdn_data['followers']}")
    print(f"关注: {csdn_data['following']}")
    
    # 暂停 3 秒
    time.sleep(3)
    
    # 头条统计
    toutiao_url = config.get("TOUTIAO_URL")
    toutiao_data = parse_toutiao_user_stats(toutiao_url)
    if toutiao_data:
        print(f"\n[头条 - {toutiao_data['timestamp']}]")
        print(f"获赞数: {toutiao_data['likes']}")
        print(f"粉丝数: {toutiao_data['fans']}")
        print(f"关注数: {toutiao_data['follows']}")
    else:
        print("\n头条数据获取失败")
    
    print("\n数据统计完成!")
