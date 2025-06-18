import requests
import re
import datetime
from bs4 import BeautifulSoup
import os

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
                    follower_count = element.find(
                        class_='user-profile-statistics-num').text.strip()
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
        visitor_count = re.sub(
            r'[^\d]', '', visitor_count) if visitor_count else "0"
        original_count = re.sub(
            r'[^\d]', '', original_count) if original_count else "0"
        follower_count = re.sub(
            r'[^\d]', '', follower_count) if follower_count else "0"
        following_count = re.sub(
            r'[^\d]', '', following_count) if following_count else "0"

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 验证数据是否有效（非零值）
        data_complete = all(
            int(x) > 0 for x in [visitor_count, original_count, follower_count, following_count]
        )
        
        if data_complete:
            # 检查文件是否存在，决定是否写入标题行
            file_exists = os.path.isfile('csdn_stats.csv')
            
            # 将数据保存到CSV文件
            with open('csdn_stats.csv', 'a', encoding='utf-8') as f:
                if not file_exists:
                    f.write("更新时间,总访问量,原创,粉丝数,关注数\n")
                f.write(
                    f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{visitor_count},{original_count},{follower_count},{following_count}\n")

            print(f"\n数据已保存到 {os.path.abspath('csdn_stats.csv')}")
        else:
            print("\nCSND数据不完整或有数据项为0，未保存到CSV文件")
            
        return {
            "timestamp": timestamp,
            "visitors": visitor_count,
            "originals": original_count,
            "followers": follower_count,
            "following": following_count,
            "site": "CSDN",
            "data_complete": data_complete
        }
    except Exception as e:
        print(f"Error extracting CSDN data: {e}")
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "visitors": "Error",
            "originals": "Error",
            "followers": "Error",
            "following": "Error",
            "site": "CSDN",
            "data_complete": False
        }


if __name__ == "__main__":
    # 测试函数
    csdn_url = "https://blog.csdn.net/qq_34598061"
    data = extract_csdn_stats(csdn_url)
    print(f"[{data['timestamp']}]")
    print(f"总访问量: {data['visitors']}")
    print(f"原创: {data['originals']}")
    print(f"粉丝: {data['followers']}")
    print(f"关注: {data['following']}")
    print(f"数据完整: {data['data_complete']}")
