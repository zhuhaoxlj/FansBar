#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
掘金用户数据爬取脚本
使用requests和BeautifulSoup获取掘金用户页面数据，提取文章点赞、阅读、关注者和关注数量
"""

import requests
import re
import datetime
import os
from bs4 import BeautifulSoup
import json
import time

def fetch_page(url, headers=None):
    """通过requests获取页面内容"""
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Referer': 'https://juejin.cn/'
        }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"获取页面时出错: {e}")
        return None

def extract_juejin_stats(url):
    """提取掘金用户页面上的统计数据：文章点赞、阅读、关注和被关注数"""
    try:
        html_content = fetch_page(url)
        if not html_content:
            raise ValueError("没有要解析的HTML内容")

        soup = BeautifulSoup(html_content, 'lxml')
        
        # 初始化变量
        likes = "0"
        reads = "0"
        following = "0"
        followers = "0"
        
        # 尝试从HTML中提取数据
        # 文章点赞数
        likes_elem = soup.find('div', string=re.compile(r'文章被点赞'))
        if likes_elem and likes_elem.find_next('div'):
            likes = likes_elem.find_next('div').text.strip()
            
        # 文章阅读数
        reads_elem = soup.find('div', string=re.compile(r'文章被阅读'))
        if reads_elem and reads_elem.find_next('div'):
            reads = reads_elem.find_next('div').text.strip()
            
        # 关注了
        following_elem = soup.find('div', string=re.compile(r'关注了'))
        if following_elem and following_elem.find_next('div'):
            following = following_elem.find_next('div').text.strip()
            
        # 关注者
        followers_elem = soup.find('div', string=re.compile(r'关注者'))
        if followers_elem and followers_elem.find_next('div'):
            followers = followers_elem.find_next('div').text.strip()
        
        # 尝试正则表达式获取数据，作为备选方案
        if likes == "0":
            text = soup.get_text()
            likes_match = re.search(r'文章被点赞\s*(\d+)', text)
            if likes_match:
                likes = likes_match.group(1)
        
        if reads == "0":
            text = soup.get_text()
            reads_match = re.search(r'文章被阅读\s*([,\d]+)', text)
            if reads_match:
                reads = reads_match.group(1)
        
        if following == "0":
            text = soup.get_text()
            following_match = re.search(r'关注了\s*(\d+)', text)
            if following_match:
                following = following_match.group(1)
        
        if followers == "0":
            text = soup.get_text()
            followers_match = re.search(r'关注者\s*(\d+)', text)
            if followers_match:
                followers = followers_match.group(1)
                
        # 尝试提取结构化数据
        if likes == "0" or reads == "0" or following == "0" or followers == "0":
            json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    # 处理获取到的JSON数据
                    # 具体字段需要根据掘金网站的JSON结构进行调整
                except:
                    pass
                
        # 清理数据 - 移除逗号和非数字字符
        likes = re.sub(r'[^\d]', '', likes) if likes else "0"
        reads = re.sub(r'[^\d]', '', reads) if reads else "0"
        following = re.sub(r'[^\d]', '', following) if following else "0"
        followers = re.sub(r'[^\d]', '', followers) if followers else "0"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 验证数据是否完整（所有数据非零）
        data_complete = all(
            int(x) > 0 for x in [likes, reads, following, followers]
        )
        
        if data_complete:
            # 确保data目录存在
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # 构建CSV文件路径
            csv_file = os.path.join(data_dir, 'juejin_stats.csv')
            
            # 检查文件是否存在，决定是否写入标题行
            file_exists = os.path.isfile(csv_file)
            
            # 保存数据到CSV文件
            with open(csv_file, 'a', encoding='utf-8') as f:
                if not file_exists:
                    f.write("更新时间,文章点赞,文章阅读,关注了,关注者\n")
                f.write(
                    f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{likes},{reads},{following},{followers}\n")

            print(f"\n数据已保存到 {os.path.abspath(csv_file)}")
        else:
            print("\n掘金数据不完整或有数据项为0，未保存到CSV文件。所有数据项必须大于0才能保存。")
            
        return {
            "timestamp": timestamp,
            "likes": likes,
            "reads": reads,
            "following": following,
            "followers": followers,
            "site": "掘金",
            "data_complete": data_complete
        }
    except Exception as e:
        print(f"提取掘金数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likes": "Error",
            "reads": "Error",
            "following": "Error",
            "followers": "Error",
            "site": "掘金",
            "data_complete": False
        }

if __name__ == "__main__":
    # 测试函数
    juejin_url = "https://juejin.cn/user/3799544245529837/posts"
    data = extract_juejin_stats(juejin_url)
    print(f"[{data['timestamp']}]")
    print(f"文章被点赞: {data['likes']}")
    print(f"文章被阅读: {data['reads']}")
    print(f"关注了: {data['following']}")
    print(f"关注者: {data['followers']}")
    print(f"数据完整: {data['data_complete']}") 