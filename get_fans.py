import time
import os
import csv
import datetime
import requests
import re
from bs4 import BeautifulSoup

def fetch_page(url, headers=None):
    """Fetch the page content using requests library"""
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Referer': 'https://blog.csdn.net/'
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

def extract_csdn_stats(url):
    """Extract visitor, original, follower and following counts from CSDN HTML content"""
    try:
        html_content = fetch_page(url)
        if not html_content:
            raise ValueError("No HTML content to parse")
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Initialize variables
        visitor_count = "0"
        original_count = "0"
        follower_count = "0"
        following_count = "0"
        
        # First approach: Find statistics in CSDN's profile statistics section
        stats_elements = soup.select('.user-profile-statistics-num')
        if len(stats_elements) >= 4:
            visitor_count = stats_elements[0].text.strip()
            original_count = stats_elements[1].text.strip()
            follower_count = stats_elements[2].text.strip()
            following_count = stats_elements[3].text.strip()
        
        # Second approach: Find by looking at the structure with text labels
        if follower_count == "0":
            # Find elements that have "粉丝" text in their parent or sibling elements
            for element in soup.find_all(['div', 'li']):
                if element.find(text=re.compile('粉丝')) and element.find(class_='user-profile-statistics-num'):
                    follower_count = element.find(class_='user-profile-statistics-num').text.strip()
                    break
        
        # Third approach: Use regex to find numbers near "粉丝" text
        if follower_count == "0":
            for element in soup.find_all(text=re.compile('粉丝')):
                parent = element.parent
                # Look for parent elements within 3 levels up
                for _ in range(3):
                    if parent and parent.name:
                        numbers = re.findall(r'\d+', parent.text)
                        if numbers:
                            follower_count = numbers[0]
                            break
                        parent = parent.parent
        
        # Clean the numbers - remove commas and non-numeric characters
        visitor_count = re.sub(r'[^\d]', '', visitor_count) if visitor_count else "0"
        original_count = re.sub(r'[^\d]', '', original_count) if original_count else "0" 
        follower_count = re.sub(r'[^\d]', '', follower_count) if follower_count else "0"
        following_count = re.sub(r'[^\d]', '', following_count) if following_count else "0"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "timestamp": timestamp,
            "site": "CSDN",
            "visitors": visitor_count,
            "originals": original_count,
            "followers": follower_count,
            "following": following_count
        }
    except Exception as e:
        print(f"Error extracting CSDN data: {e}")
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "site": "CSDN",
            "visitors": "Error",
            "originals": "Error",
            "followers": "Error",
            "following": "Error"
        }

def save_to_csv(data, filename="fan_data.csv"):
    """Save the extracted data to a CSV file"""
    file_exists = os.path.isfile(filename)
    
    # CSV字段：时间戳、网站、访问量、原创、粉丝数、关注数
    fieldnames = ["timestamp", "site", "visitors", "originals", "followers", "following"]
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)

def monitor_csdn_stats(url, interval=5, duration=None):
    """
    Monitor CSDN statistics at specified intervals
    """
    print(f"开始监控CSDN数据")
    print(f"数据采集频率：每 {interval} 秒一次")
    print("按 Ctrl+C 停止...")
    
    # Initialize start time if duration is specified
    start_time = time.time() if duration else None
    
    try:
        while True:
            print(f"\n正在获取 CSDN 数据...")
            
            data = extract_csdn_stats(url)
            print(f"[{data['site']} - {data['timestamp']}]")
            print(f"总访问量: {data['visitors']}")
            print(f"原创: {data['originals']}")
            print(f"粉丝: {data['followers']}")
            print(f"关注: {data['following']}")
            
            # Save data to CSV
            save_to_csv(data)
            
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
    # CSDN URL to monitor
    csdn_url = "https://blog.csdn.net/qq_34598061"
    
    # Start monitoring CSDN statistics
    monitor_csdn_stats(csdn_url, interval=5) 