#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
头条用户数据爬取脚本
使用DrissionPage库获取今日头条用户页面数据，提取获赞、粉丝和关注数量
"""

from DrissionPage import ChromiumOptions, ChromiumPage, errors
import time
import os
import sys
import re
import platform
import random
from bs4 import BeautifulSoup
import datetime

def init_browser():
    """
    初始化并返回浏览器实例
    """
    # 第一部分：配置浏览器选项
    co = ChromiumOptions()

    # 关闭无头模式，头条网站会检测无头浏览器
    co.headless(True)  # 改为非无头模式，减少被检测概率

    # 设置常见的用户代理
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ]
    co.set_user_agent(random.choice(user_agents))

    # 禁用自动化特性检测
    co.set_pref("excludeSwitches", ["enable-automation"])
    co.set_pref("useAutomationExtension", False)
    co.set_argument("--disable-blink-features=AutomationControlled")

    # 系统特定配置
    if platform.system() == "Darwin":  # macOS
        co.set_argument("--no-sandbox")
        co.set_argument("--disable-gpu")

    # 添加一些真实浏览器的特性
    co.set_argument("--disable-notifications")
    co.set_argument("--disable-popup-blocking")
    co.set_pref("credentials_enable_service", False)
    co.set_pref("profile.password_manager_enabled", False)
    co.auto_port(True)

    try:
        print("正在启动浏览器...")
        page = ChromiumPage(co)
        return page
    except Exception as e:
        print(f"启动浏览器时出错: {e}")
        import traceback
        print(traceback.format_exc())
        return None

def parse_toutiao_user_stats(url: str, page=None):
    """
    使用DrissionPage获取头条用户页面并解析用户数据
    
    参数:
        url: 头条用户页面URL
        page: 已初始化的ChromiumPage实例，如果为None则创建新实例
        
    返回:
        dict: 包含用户数据的字典
    """
    browser_created_here = False
    
    try:
        # 如果没有传入浏览器实例，创建新实例
        if page is None:
            page = init_browser()
            browser_created_here = True
            if page is None:
                return None

        print("正在访问头条用户页面...")
        # 访问页面
        page.get(url)

        # 增强等待机制
        print("等待页面加载完成...")
        page.wait.doc_loaded()

        # 检查页面是否已加载成功
        try:
            # 等待页面上某个可能的固定元素出现
            page.wait.ele_displayed('body', timeout=10)
        except errors.TimeoutError:
            print("页面加载超时，正在重试...")
            page.refresh()
            time.sleep(3)
            page.wait.doc_loaded()

        # 执行一些随机滚动，模拟真实用户行为
        print("模拟页面交互...")
        try:
            for _ in range(3):
                # 使用try-except来确保页面交互稳定
                try:
                    # 随机滚动页面
                    scroll_amount = random.randint(100, 300)
                    page.run_js(f"window.scrollBy(0, {scroll_amount});")
                    # 添加随机等待，避免操作过快
                    time.sleep(random.uniform(0.3, 0.8))
                except errors.ContextLostError:
                    print("页面刷新中，等待页面重新加载...")
                    time.sleep(0.2)
                    page.wait.doc_loaded()
                    time.sleep(0.1)
                except Exception as e:
                    print(f"滚动操作失败: {e}")
                    time.sleep(0.1)
        except Exception as e:
            print(f"滚动页面时出错: {e}")
            # 继续执行，不中断流程

        # 获取页面源码
        html_source = page.html

        # 将源码保存到文件（可选）
        with open('toutiao_page_source.html', 'w', encoding='utf-8') as f:
            f.write(html_source)

        print(f"页面源码已保存到 {os.path.abspath('toutiao_page_source.html')}")

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_source, 'lxml')

        # 方法1: 直接尝试从页面元素中获取数据
        # 尝试找到包含数据的容器元素
        text = soup.get_text()

        # 使用正则表达式提取数字
        likes_match = re.search(r'(\d+)\s*获赞', text)
        fans_match = re.search(r'(\d+)\s*粉丝', text)
        follows_match = re.search(r'(\d+)\s*关注', text)

        # 提取数字
        likes = likes_match.group(1) if likes_match else "未找到"
        fans = fans_match.group(1) if fans_match else "未找到"
        follows = follows_match.group(1) if follows_match else "未找到"

        # 输出结果
        print("\n用户数据:")
        print(f"获赞数: {likes}")
        print(f"粉丝数: {fans}")
        print(f"关注数: {follows}")

        # 检查是否所有数据都获取成功并且大于0
        data_complete = all(x != "未找到" for x in [likes, fans, follows]) and all(int(x) > 0 for x in [likes, fans, follows] if x.isdigit())
        
        if data_complete:
            # 确保data目录存在
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # 构建CSV文件路径
            csv_file = os.path.join(data_dir, 'toutiao_stats.csv')
            
            # 检查文件是否存在
            file_exists = os.path.isfile(csv_file)
            
            # 将数据保存到CSV文件
            with open(csv_file, 'a', encoding='utf-8') as f:
                if not file_exists:
                    f.write("更新时间,获赞数,粉丝数,关注数\n")
                f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{likes},{fans},{follows}\n")

            print(f"\n数据已保存到 {os.path.abspath(csv_file)}")
        else:
            print("\n数据不完整或有数据项为0，未保存到CSV文件。所有数据项必须大于0才能保存。")

        # 尝试直接提取JavaScript变量中的数据的方法 (如果上面的方法失败)
        if not data_complete:
            print("\n尝试从JavaScript变量中提取数据...")

            try:
                # 使用页面的JavaScript获取数据，添加错误处理
                js_user_data = page.run_js("""
                try {
                    // 尝试获取全局变量中的用户数据
                    let userData = {};
                    
                    // 搜索可能包含用户数据的变量
                    if (typeof window.__HYDRATE__INFO !== 'undefined') {
                        return JSON.stringify(window.__HYDRATE__INFO);
                    }
                    
                    // 获取页面上的所有数据
                    const dataElements = document.querySelectorAll('[data-log-click]');
                    let results = [];
                    for (let el of dataElements) {
                        results.push({
                            text: el.innerText,
                            data: el.getAttribute('data-log-click')
                        });
                    }
                    
                    // 如果直接找不到，则返回页面文本以便进行正则提取
                    return JSON.stringify({
                        bodyText: document.body.innerText,
                        dataElements: results
                    });
                } catch(e) {
                    return "JS错误: " + e.toString();
                }
                """)

                if js_user_data and not js_user_data.startswith("JS错误"):
                    print("从JS中提取的数据:")
                    likes_js = re.search(
                        r'"like_count"\s*:\s*(\d+)', js_user_data)
                    fans_js = re.search(
                        r'"fans_count"\s*:\s*(\d+)', js_user_data)
                    follows_js = re.search(
                        r'"follow_count"\s*:\s*(\d+)', js_user_data)

                    js_likes = likes_js.group(1) if likes_js else None
                    js_fans = fans_js.group(1) if fans_js else None
                    js_follows = follows_js.group(1) if follows_js else None

                    if all(x is not None for x in [js_likes, js_fans, js_follows]):
                        # 如果JS方法获取到了所有数据，则更新并保存到CSV
                        likes = js_likes
                        fans = js_fans
                        follows = js_follows
                        
                        # 检查数据项是否都大于0
                        all_greater_than_zero = all(int(x) > 0 for x in [likes, fans, follows])
                        
                        if all_greater_than_zero:
                            # 确保data目录存在
                            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
                            os.makedirs(data_dir, exist_ok=True)
                            
                            # 构建CSV文件路径
                            csv_file = os.path.join(data_dir, 'toutiao_stats.csv')
                            
                            # 检查文件是否存在
                            file_exists = os.path.isfile(csv_file)
                            
                            # 将数据保存到CSV文件
                            with open(csv_file, 'a', encoding='utf-8') as f:
                                if not file_exists:
                                    f.write("更新时间,获赞数,粉丝数,关注数\n")
                                f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{likes},{fans},{follows}\n")
                            
                            print(f"\n数据已通过JS方法获取并保存到 {os.path.abspath(csv_file)}")
                            
                            # 标记数据为完整
                            data_complete = True
                        else:
                            print("\n通过JS获取的数据中有项为0，未保存到CSV文件。所有数据项必须大于0才能保存。")
                    else:
                        if js_likes:
                            print(f"获赞数: {js_likes}")
                        else:
                            print("未找到获赞数")
                            
                        if js_fans:
                            print(f"粉丝数: {js_fans}")
                        else:
                            print("未找到粉丝数")
                            
                        if js_follows:
                            print(f"关注数: {js_follows}")
                        else:
                            print("未找到关注数")
                            
                        print("\n无法从JS中获取完整的数据")
                else:
                    print(f"JS执行错误或未返回有效数据: {js_user_data}")

            except Exception as e:
                print(f"从JS提取数据时出错: {e}")
                import traceback
                print(traceback.format_exc())

        # 返回数据字典
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likes": likes if likes != "未找到" else "0",
            "fans": fans if fans != "未找到" else "0",
            "follows": follows if follows != "未找到" else "0",
            "site": "今日头条",
            "data_complete": data_complete
        }
    except Exception as e:
        print(f"解析头条用户数据时出错: {e}")
        import traceback
        print(traceback.format_exc())
        
        # 清理资源
        if browser_created_here and page:
            try:
                page.quit()
                print("已关闭浏览器实例")
            except:
                pass
                
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likes": "0",
            "fans": "0",
            "follows": "0",
            "site": "今日头条",
            "data_complete": False
        }
    finally:
        # 清理资源
        if browser_created_here and page:
            try:
                page.quit()
                print("已关闭浏览器实例")
            except:
                pass


if __name__ == "__main__":
    # 测试函数
    toutiao_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAaezOXkHVr0_hGmL4GwLKscbUPJUTiWw7zZZIImy3PGc/"
    data = parse_toutiao_user_stats(toutiao_url)
    print(f"\n[{data['timestamp']}]")
    print(f"获赞数: {data['likes']}")
    print(f"粉丝数: {data['fans']}")
    print(f"关注数: {data['follows']}")
    print(f"数据完整: {data['data_complete']}")
