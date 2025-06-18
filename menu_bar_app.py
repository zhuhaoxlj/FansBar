#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
macOS Menu Bar Application for displaying CSDN and Toutiao statistics
"""

import rumps
import threading
import time
import os
import csv
from datetime import datetime
from csdn import extract_csdn_stats
from toutiao import parse_toutiao_user_stats, init_browser

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

class StatisticsMenuBarApp(rumps.App):
    def __init__(self):
        super(StatisticsMenuBarApp, self).__init__("Stats")
        
        # 加载配置
        self.config = load_config()
        
        # Initialize data
        self.csdn_data = None
        self.toutiao_data = None
        self.current_display = "csdn"  # Start with CSDN
        self.rotation_interval = 5  # Seconds to display each platform
        
        # 专注模式标志
        self.focus_mode_enabled = False  
        
        # Initialize detailed menu items
        self.csdn_details_menu = rumps.MenuItem("CSDN详细数据")
        self.csdn_visitors_item = rumps.MenuItem("访问量: 加载中...")
        self.csdn_originals_item = rumps.MenuItem("原创: 加载中...")
        self.csdn_followers_item = rumps.MenuItem("粉丝: 加载中...")
        self.csdn_following_item = rumps.MenuItem("关注: 加载中...")
        
        self.toutiao_details_menu = rumps.MenuItem("头条详细数据")
        self.toutiao_likes_item = rumps.MenuItem("获赞: 加载中...")
        self.toutiao_fans_item = rumps.MenuItem("粉丝: 加载中...")
        self.toutiao_follows_item = rumps.MenuItem("关注: 加载中...")
        
        # 专注模式菜单
        self.focus_mode_item = rumps.MenuItem("专注模式", callback=self.toggle_focus_mode)
        
        # Add items to submenus
        self.csdn_details_menu.add(self.csdn_visitors_item)
        self.csdn_details_menu.add(self.csdn_originals_item)
        self.csdn_details_menu.add(self.csdn_followers_item)
        self.csdn_details_menu.add(self.csdn_following_item)
        
        self.toutiao_details_menu.add(self.toutiao_likes_item)
        self.toutiao_details_menu.add(self.toutiao_fans_item)
        self.toutiao_details_menu.add(self.toutiao_follows_item)
        
        # Configure menu - 完全清除默认菜单并使用我们自己的菜单项
        self.menu.clear()  # 清除默认菜单
        self.menu.add(self.csdn_details_menu)
        self.menu.add(self.toutiao_details_menu)
        self.menu.add(None)  # 分隔符
        self.menu.add(self.focus_mode_item)
        self.menu.add("更新数据")
        # 不添加退出选项，因为rumps已经默认添加了一个
        
        # 初始化浏览器实例
        self.browser = None
        self.init_browser()
        
        # Start data collection thread
        self.data_thread = threading.Thread(target=self.collect_data_periodically)
        self.data_thread.daemon = True
        self.data_thread.start()
        
        # Start display rotation thread
        self.display_thread = threading.Thread(target=self.rotate_display)
        self.display_thread.daemon = True
        self.display_thread.start()
    
    def init_browser(self):
        """初始化浏览器实例"""
        try:
            self.browser = init_browser()
            if self.browser:
                print("浏览器初始化成功")
            else:
                print("浏览器初始化失败")
        except Exception as e:
            print(f"初始化浏览器时出错: {e}")
            self.browser = None
    
    def toggle_focus_mode(self, sender):
        """切换专注模式"""
        sender.state = not sender.state
        self.focus_mode_enabled = sender.state
        if sender.state:
            try:
                rumps.notification("专注模式", "已启用", "菜单栏数据将暂停更新")
            except:
                pass
        else:
            try:
                rumps.notification("专注模式", "已关闭", "菜单栏数据将继续更新")
            except:
                pass
    
    def rotate_display(self):
        """Rotate between CSDN and Toutiao data in the menu bar"""
        while True:
            if not self.focus_mode_enabled:  # 只在非专注模式下更新
                if self.current_display == "csdn" and self.csdn_data and self.csdn_data.get("data_complete", False):
                    self.title = f"CSDN: {self.csdn_data['followers']}"
                    self.current_display = "toutiao"
                elif self.current_display == "toutiao" and self.toutiao_data and self.toutiao_data.get("data_complete", False):
                    self.title = f"头条: {self.toutiao_data['fans']}"
                    self.current_display = "csdn"
            time.sleep(self.rotation_interval)
    
    def update_menu_items(self):
        """Update the menu items with current data"""
        if self.csdn_data:
            self.csdn_visitors_item.title = f"访问量: {self.csdn_data['visitors']}"
            self.csdn_originals_item.title = f"原创: {self.csdn_data['originals']}"
            self.csdn_followers_item.title = f"粉丝: {self.csdn_data['followers']}"
            self.csdn_following_item.title = f"关注: {self.csdn_data['following']}"
            
        if self.toutiao_data:
            self.toutiao_likes_item.title = f"获赞: {self.toutiao_data['likes']}"
            self.toutiao_fans_item.title = f"粉丝: {self.toutiao_data['fans']}"
            self.toutiao_follows_item.title = f"关注: {self.toutiao_data['follows']}"
    
    def collect_data(self):
        """Collect data from both platforms"""
        try:
            # CSDN data
            csdn_url = self.config.get("CSDN_URL")
            self.csdn_data = extract_csdn_stats(csdn_url)
            
            if self.csdn_data and self.csdn_data.get("data_complete", False):
                print(f"[CSDN] 粉丝数: {self.csdn_data['followers']} (数据完整)")
            else:
                print("[CSDN] 数据不完整，未保存")
            
            # Toutiao data
            toutiao_url = self.config.get("TOUTIAO_URL")
            
            # 检查浏览器实例是否可用，如果不可用则重新初始化
            if self.browser is None:
                self.init_browser()
                
            # 使用持久化的浏览器实例获取头条数据
            self.toutiao_data = parse_toutiao_user_stats(toutiao_url, self.browser)
            
            if self.toutiao_data and self.toutiao_data.get("data_complete", False):
                print(f"[头条] 粉丝数: {self.toutiao_data['fans']} (数据完整)")
            elif self.toutiao_data:
                print(f"[头条] 数据不完整，未保存")
            else:
                print("获取头条数据失败，尝试重新初始化浏览器")
                # 如果获取数据失败，尝试重新初始化浏览器
                if self.browser:
                    try:
                        self.browser.quit()
                    except:
                        pass
                self.init_browser()
                if self.browser:
                    # 再次尝试获取数据
                    self.toutiao_data = parse_toutiao_user_stats(toutiao_url, self.browser)
                    if self.toutiao_data and self.toutiao_data.get("data_complete", False):
                        print(f"[头条] 粉丝数: {self.toutiao_data['fans']} (数据完整)")
                    elif self.toutiao_data:
                        print(f"[头条] 数据不完整，未保存")
            
            # Update menu items with new data
            self.update_menu_items()
            
            # Update title immediately after collection
            if not self.focus_mode_enabled:  # 只在非专注模式下更新标题
                if self.current_display == "csdn" and self.csdn_data and self.csdn_data.get("data_complete", False):
                    self.title = f"CSDN: {self.csdn_data['followers']}"
                elif self.current_display == "toutiao" and self.toutiao_data and self.toutiao_data.get("data_complete", False):
                    self.title = f"头条: {self.toutiao_data['fans']}"
            
            # 只有当两个平台的数据都完整时，才显示通知
            csdn_data_complete = self.csdn_data and self.csdn_data.get("data_complete", False)
            toutiao_data_complete = self.toutiao_data and self.toutiao_data.get("data_complete", False)
            
            # Try to show notification when data is updated
            if not self.focus_mode_enabled and (csdn_data_complete or toutiao_data_complete):  # 只在非专注模式下显示通知
                try:
                    csdn_fans = self.csdn_data['followers'] if csdn_data_complete else "未获取"
                    toutiao_fans = self.toutiao_data['fans'] if toutiao_data_complete else "未获取"
                    
                    rumps.notification(
                        title="数据已更新", 
                        subtitle="粉丝统计", 
                        message=f"CSDN: {csdn_fans} 粉丝, 头条: {toutiao_fans} 粉丝"
                    )
                except Exception as e:
                    print(f"无法显示通知: {e}")
                    # 通知失败不影响主要功能
            
        except Exception as e:
            print(f"Error collecting data: {e}")
            import traceback
            print(traceback.format_exc())
    
    def collect_data_periodically(self):
        """Collect data periodically"""
        while True:
            self.collect_data()
            # Wait for 30 minutes before collecting again
            time.sleep(30 * 60)
    
    @rumps.clicked("更新数据")
    def update_data(self, _):
        """Manually update data"""
        thread = threading.Thread(target=self.collect_data)
        thread.daemon = True
        thread.start()
        try:
            rumps.notification("数据更新", "统计数据", "正在更新数据，请稍等...")
        except Exception as e:
            print(f"无法显示通知: {e}")
    
    def run(self):
        """运行应用，并处理退出清理"""
        try:
            super(StatisticsMenuBarApp, self).run()
        finally:
            # 应用退出时关闭浏览器
            if self.browser:
                try:
                    print("应用退出，关闭浏览器...")
                    self.browser.quit()
                except Exception as e:
                    print(f"关闭浏览器时出错: {e}")

if __name__ == "__main__":
    StatisticsMenuBarApp().run()