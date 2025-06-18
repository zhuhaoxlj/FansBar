import time
import os
import csv
import datetime

# 导入CSDN数据获取模块
from csdn import extract_csdn_stats
# 导入今日头条数据获取模块
from toutiao import parse_toutiao_user_stats
# 导入掘金数据获取模块
from juejin import extract_juejin_stats
# 导入知乎数据获取模块
from zhihu import extract_zhihu_stats

def load_config():
    """从配置文件加载URL"""
    config = {
        "CSDN_URL": "https://blog.csdn.net/qq_34598061",  # 默认URL
        "TOUTIAO_URL": "https://www.toutiao.com/c/user/token/MS4wLjABAAAA-vxeZNtd-323uOaHVG-qQJnP0kL3_QSOTO85-9GJPXo/",  # 默认URL
        "JUEJIN_URL": "https://juejin.cn/user/3799544245529837/posts",  # 默认URL
        "ZHIHU_URL": "https://www.zhihu.com/people/bu-yi-jue-63"  # 默认URL
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
            
            data = extract_juejin_stats(juejin_url)
            print(data)
            
            data = extract_zhihu_stats(zhihu_url)
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
    
    # 暂停 3 秒
    time.sleep(3)
    
    # 掘金统计
    juejin_url = config.get("JUEJIN_URL")
    juejin_data = extract_juejin_stats(juejin_url)
    if juejin_data:
        print(f"\n[掘金 - {juejin_data['timestamp']}]")
        print(f"点赞数: {juejin_data['likes']}")
        print(f"阅读量: {juejin_data['reads']}")
        print(f"关注者: {juejin_data['followers']}")
        print(f"关注了: {juejin_data['following']}")
    else:
        print("\n掘金数据获取失败")
    
    # 暂停 3 秒
    time.sleep(3)
    
    # 知乎统计
    zhihu_url = config.get("ZHIHU_URL")
    zhihu_data = extract_zhihu_stats(zhihu_url)
    if zhihu_data and zhihu_data['data_complete']:
        print(f"\n[知乎 - {zhihu_data['timestamp']}]")
        print(f"用户名: {zhihu_data['username']}")
        print(f"简介: {zhihu_data['tagline']}")
        print(f"回答: {zhihu_data['answers']}")
        print(f"文章: {zhihu_data['articles']}")
        print(f"专栏: {zhihu_data['columns']}")
        print(f"收藏: {zhihu_data['collections']}")
        print(f"赞同: {zhihu_data['upvotes']}")
        print(f"感谢: {zhihu_data['thanks']}")
        print(f"浏览: {zhihu_data['views']}")
        print(f"关注了: {zhihu_data['following']}")
        print(f"关注者: {zhihu_data['followers']}")
        if zhihu_data['recent_activity']:
            print("最近活动:")
            for activity in zhihu_data['recent_activity'][:3]:
                print(f"  - {activity['type']}: {activity['title']}")
    else:
        print("\n知乎数据获取失败")
    
    print("\n数据统计完成!")
