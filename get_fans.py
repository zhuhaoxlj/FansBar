import time
import os
import csv
import datetime

# 导入CSDN数据获取模块
from csdn import extract_csdn_stats
# 导入今日头条数据获取模块
from toutiao import parse_toutiao_user_stats

toutiao_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAYd06xjdpZljEG3tiHeqEreoftdwWiWgqy-8K5cur014/?source=tuwen_detail&entrance_gid=7517216151676568116&log_from=dc1886426211a8_1750259763904"
csdn_url = "https://blog.csdn.net/qq_34598061"


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
    monitor_platforms(interval=5)
