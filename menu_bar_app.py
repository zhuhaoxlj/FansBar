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
from juejin import extract_juejin_stats
from zhihu import extract_zhihu_stats
from data_analysis import generate_analysis_page
import settings

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

class StatisticsMenuBarApp(rumps.App):
    def __init__(self):
        super(StatisticsMenuBarApp, self).__init__("Stats")
        
        # 加载配置
        self.config = load_config()
        
        # 加载设置
        self.app_settings = settings.load_settings()
        print(f"加载的应用设置: {self.app_settings}")
        
        # Initialize data
        self.csdn_data = None
        self.toutiao_data = None
        self.juejin_data = None
        self.zhihu_data = None
        self.current_display = "csdn"  # Start with CSDN
        self.rotation_interval = 5  # Seconds to display each platform
        
        # 更新频率（从设置加载）
        self.update_interval = self.app_settings.get("update_interval", 30 * 60)
        print(f"从设置加载的更新频率: {self.update_interval}秒")
        
        # 定时器和线程控制
        self.data_thread = None
        self.should_stop_thread = False
        
        # 专注模式标志
        self.focus_mode_enabled = self.app_settings.get("focus_mode", False)
        
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
        
        # 新增掘金菜单项
        self.juejin_details_menu = rumps.MenuItem("掘金详细数据")
        self.juejin_likes_item = rumps.MenuItem("点赞: 加载中...")
        self.juejin_reads_item = rumps.MenuItem("阅读: 加载中...")
        self.juejin_following_item = rumps.MenuItem("关注了: 加载中...")
        self.juejin_followers_item = rumps.MenuItem("关注者: 加载中...")
        
        # 新增知乎菜单项
        self.zhihu_details_menu = rumps.MenuItem("知乎详细数据")
        self.zhihu_upvotes_item = rumps.MenuItem("赞同: 加载中...")
        self.zhihu_likes_item = rumps.MenuItem("喜欢: 加载中...")
        self.zhihu_collections_item = rumps.MenuItem("收藏: 加载中...")
        self.zhihu_following_item = rumps.MenuItem("关注了: 加载中...")
        self.zhihu_followers_item = rumps.MenuItem("关注者: 加载中...")
        
        # 专注模式菜单
        self.focus_mode_item = rumps.MenuItem("专注模式", callback=self.toggle_focus_mode)
        self.focus_mode_item.state = self.focus_mode_enabled
        
        # 数据分析菜单项
        self.data_analysis_item = rumps.MenuItem("数据分析", callback=self.show_data_analysis)
        
        # 更新频率菜单
        self.update_interval_menu = rumps.MenuItem("更新频率")
        self.update_5s_item = rumps.MenuItem("5秒", callback=self.set_update_interval)
        self.update_30s_item = rumps.MenuItem("30秒", callback=self.set_update_interval)
        self.update_60s_item = rumps.MenuItem("60秒", callback=self.set_update_interval)
        self.update_5min_item = rumps.MenuItem("5分钟", callback=self.set_update_interval)
        self.update_30min_item = rumps.MenuItem("30分钟", callback=self.set_update_interval)
        self.update_1h_item = rumps.MenuItem("1小时", callback=self.set_update_interval)
        self.update_2h_item = rumps.MenuItem("2小时", callback=self.set_update_interval)
        
        # 设置默认选中的更新频率（从设置加载）
        interval_name = self.app_settings.get("update_interval_name", "30分钟")
        
        # 初始化所有菜单项为未选中状态
        self.update_5s_item.state = False
        self.update_30s_item.state = False
        self.update_60s_item.state = False
        self.update_5min_item.state = False
        self.update_30min_item.state = False
        self.update_1h_item.state = False
        self.update_2h_item.state = False
        
        # 根据保存的设置选中对应的菜单项
        if interval_name == "5秒":
            self.update_5s_item.state = True
        elif interval_name == "30秒":
            self.update_30s_item.state = True
        elif interval_name == "60秒":
            self.update_60s_item.state = True
        elif interval_name == "5分钟":
            self.update_5min_item.state = True
        elif interval_name == "30分钟" or "自定义" in interval_name:
            # 如果是自定义的也设为30分钟
            self.update_30min_item.state = True
            if "自定义" in interval_name:
                # 更新为标准间隔
                settings.update_setting("update_interval", 30 * 60)
                settings.update_setting("update_interval_name", "30分钟")
        elif interval_name == "1小时":
            self.update_1h_item.state = True
        elif interval_name == "2小时":
            self.update_2h_item.state = True
        else:
            # 默认为30分钟
            self.update_30min_item.state = True
        
        # 将更新频率选项添加到更新频率菜单
        self.update_interval_menu.add(self.update_5s_item)
        self.update_interval_menu.add(self.update_30s_item)
        self.update_interval_menu.add(self.update_60s_item)
        self.update_interval_menu.add(self.update_5min_item)
        self.update_interval_menu.add(self.update_30min_item)
        self.update_interval_menu.add(self.update_1h_item)
        self.update_interval_menu.add(self.update_2h_item)
        
        # Add items to submenus
        self.csdn_details_menu.add(self.csdn_visitors_item)
        self.csdn_details_menu.add(self.csdn_originals_item)
        self.csdn_details_menu.add(self.csdn_followers_item)
        self.csdn_details_menu.add(self.csdn_following_item)
        
        self.toutiao_details_menu.add(self.toutiao_likes_item)
        self.toutiao_details_menu.add(self.toutiao_fans_item)
        self.toutiao_details_menu.add(self.toutiao_follows_item)
        
        # 添加掘金子菜单项
        self.juejin_details_menu.add(self.juejin_likes_item)
        self.juejin_details_menu.add(self.juejin_reads_item)
        self.juejin_details_menu.add(self.juejin_following_item)
        self.juejin_details_menu.add(self.juejin_followers_item)
        
        # 添加知乎子菜单项
        self.zhihu_details_menu.add(self.zhihu_upvotes_item)
        self.zhihu_details_menu.add(self.zhihu_likes_item)
        self.zhihu_details_menu.add(self.zhihu_collections_item)
        self.zhihu_details_menu.add(self.zhihu_following_item)
        self.zhihu_details_menu.add(self.zhihu_followers_item)
        
        # Configure menu - 完全清除默认菜单并使用我们自己的菜单项
        self.menu.clear()  # 清除默认菜单
        self.menu.add(self.csdn_details_menu)
        self.menu.add(self.toutiao_details_menu)
        self.menu.add(self.juejin_details_menu)  # 添加掘金菜单
        self.menu.add(self.zhihu_details_menu)   # 添加知乎菜单
        self.menu.add(None)  # 分隔符
        self.menu.add(self.data_analysis_item)
        self.menu.add(None)  # 分隔符
        self.menu.add(self.update_interval_menu)
        self.menu.add("更新数据")
        self.menu.add(None)  # 分隔符
        self.menu.add(self.focus_mode_item)
        # 不添加退出选项，因为rumps已经默认添加了一个
        
        # 初始化浏览器实例
        self.browser = None
        self.init_browser()
        
        # Start data collection thread
        self.start_data_thread()
        
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
        
        # 保存设置
        settings.update_setting("focus_mode", self.focus_mode_enabled)
        
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
    
    def set_update_interval(self, sender):
        """设置更新频率"""
        # 取消所有选项的选中状态
        self.update_5s_item.state = False
        self.update_30s_item.state = False
        self.update_60s_item.state = False
        self.update_5min_item.state = False
        self.update_30min_item.state = False
        self.update_1h_item.state = False
        self.update_2h_item.state = False
        
        # 设置选中状态
        sender.state = True
        
        # 根据菜单项标题设置更新频率
        if sender.title == "5秒":
            self.update_interval = 5
            interval_text = "5秒"
        elif sender.title == "30秒":
            self.update_interval = 30
            interval_text = "30秒"
        elif sender.title == "60秒":
            self.update_interval = 60
            interval_text = "60秒"
        elif sender.title == "5分钟":
            self.update_interval = 5 * 60
            interval_text = "5分钟"
        elif sender.title == "30分钟":
            self.update_interval = 30 * 60
            interval_text = "30分钟"
        elif sender.title == "1小时":
            self.update_interval = 60 * 60
            interval_text = "1小时"
        elif sender.title == "2小时":
            self.update_interval = 2 * 60 * 60
            interval_text = "2小时"
        else:
            # 默认为30分钟
            self.update_interval = 30 * 60
            interval_text = "30分钟"
            self.update_30min_item.state = True
        
        print(f"test->{self.update_interval}")
        # 保存设置
        print(f"正在保存更新频率设置: {interval_text} ({self.update_interval}秒)")
        result1 = settings.update_setting("update_interval", self.update_interval)
        result2 = settings.update_setting("update_interval_name", interval_text)
        print(f"设置保存结果: update_interval={result1}, update_interval_name={result2}")
        
        # 更新当前设置中的值
        self.app_settings["update_interval"] = self.update_interval
        self.app_settings["update_interval_name"] = interval_text
        
        # 重新加载设置以确认它们被正确保存
        saved_settings = settings.load_settings()
        print(f"检查保存后的设置: update_interval={saved_settings.get('update_interval')}, update_interval_name={saved_settings.get('update_interval_name')}")
        
        # 重启数据收集线程
        self.restart_data_thread()
        
        # 显示通知
        try:
            rumps.notification(
                "更新频率已修改",
                f"每{interval_text}更新一次",
                "下次更新将在设定的时间间隔后进行"
            )
        except:
            pass
        
        # 输出日志，用于调试
        print(f"更新频率已修改为: {interval_text}，间隔秒数: {self.update_interval}")
    
    def restart_data_thread(self):
        """重启数据收集线程"""
        # 停止现有线程
        print(f"准备重启数据收集线程，当前更新频率: {self.update_interval}秒")
        self.should_stop_thread = True
        
        # 等待线程结束或超时
        if self.data_thread and self.data_thread.is_alive():
            try:
                print("等待现有线程结束...")
                self.data_thread.join(1)  # 等待1秒
                if self.data_thread.is_alive():
                    print("线程仍在运行，继续执行...")
            except Exception as e:
                print(f"等待线程结束时出错: {e}")
        
        # 启动新线程
        print("现有线程已停止，准备启动新线程")
        self.should_stop_thread = False
        self.data_thread = None  # 确保引用被清除
        self.start_data_thread()
        
        # 输出日志，用于调试
        print(f"数据收集线程已重启，更新间隔: {self.update_interval}秒")
    
    def start_data_thread(self):
        """启动数据收集线程"""
        self.data_thread = threading.Thread(target=self.collect_data_periodically)
        self.data_thread.daemon = True
        self.data_thread.start()
    
    def show_data_analysis(self, _):
        """显示数据分析页面"""
        try:
            # 在单独的线程中运行，避免阻塞主线程
            thread = threading.Thread(target=self._generate_analysis)
            thread.daemon = True
            thread.start()
            try:
                rumps.notification("数据分析", "生成中", "正在生成数据分析报告...")
            except:
                pass
        except Exception as e:
            print(f"显示数据分析时出错: {e}")
            try:
                rumps.notification("数据分析失败", "错误", str(e))
            except:
                pass
    
    def _generate_analysis(self):
        """在后台线程生成并显示分析页面"""
        try:
            output_file = generate_analysis_page()
            print(f"数据分析页面已生成: {output_file}")
        except Exception as e:
            print(f"生成数据分析时出错: {e}")
            import traceback
            print(traceback.format_exc())
    
    def rotate_display(self):
        """轮换显示不同平台的粉丝数"""
        while True:
            if not self.focus_mode_enabled:
                # 只显示CSDN的粉丝数
                self.current_display = "csdn"
                self.update_menu_items()
            time.sleep(self.rotation_interval)
    
    def update_menu_items(self):
        """根据当前数据更新菜单项显示"""
        if not self.focus_mode_enabled:
            if self.csdn_data:
                self.title = f"CSDN粉丝: {self.csdn_data['followers']}"
            else:
                self.title = "获取中..."
    
    def collect_data(self):
        """收集所有平台的数据"""
        # 获取CSDN数据
        try:
            print("\n正在获取CSDN数据...")
            self.csdn_data = extract_csdn_stats(self.config["CSDN_URL"])
            if self.csdn_data and self.csdn_data["data_complete"]:
                print(f"[CSDN] 粉丝数: {self.csdn_data['followers']} (数据完整)")
                
                # 更新CSDN菜单项
                self.csdn_visitors_item.title = f"访问量: {self.csdn_data['visitors']}"
                self.csdn_originals_item.title = f"原创: {self.csdn_data['originals']}"
                self.csdn_followers_item.title = f"粉丝: {self.csdn_data['followers']}"
                self.csdn_following_item.title = f"关注: {self.csdn_data['following']}"
            else:
                print("[CSDN] 数据不完整或获取失败")
                if not self.csdn_data:
                    self.csdn_data = {
                        "followers": "Error",
                        "data_complete": False
                    }
        except Exception as e:
            print(f"获取CSDN数据时出错: {e}")
            self.csdn_data = {
                "followers": "Error",
                "data_complete": False
            }
        
        # 更新最后更新时间
        settings.update_setting("last_update", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 更新显示
        self.update_menu_items()
    
    def collect_data_periodically(self):
        """Collect data periodically"""
        try:
            # 获取线程ID用于调试
            import threading
            thread_id = threading.get_ident()
            
            # 记录当前的更新间隔，用于检测是否发生变化
            current_interval = self.update_interval
            print(f"线程 {thread_id}: 启动数据收集线程，更新间隔: {current_interval}秒")
            
            # 先执行一次数据收集
            self.collect_data()
            
            # 记录上次收集数据的时间
            last_collection_time = time.time()
            
            # 然后定期执行
            while not self.should_stop_thread:
                # 每秒检查一次是否需要更新数据或者更新间隔是否变化
                time.sleep(1)
                
                if self.should_stop_thread:
                    print(f"线程 {thread_id}: 收到停止信号，退出循环")
                    break
                
                # 检查是否需要收集数据
                current_time = time.time()
                elapsed_time = current_time - last_collection_time
                
                # 如果更新间隔发生变化，重新计算下次更新时间
                if current_interval != self.update_interval:
                    print(f"线程 {thread_id}: 检测到更新间隔变化: {current_interval} -> {self.update_interval}秒")
                    # 如果新的间隔比已经等待的时间短，立即执行收集
                    if self.update_interval <= elapsed_time:
                        print(f"线程 {thread_id}: 新间隔小于已等待时间，立即执行数据收集")
                        self.collect_data()
                        last_collection_time = time.time()
                    current_interval = self.update_interval
                    print(f"线程 {thread_id}: 更新间隔已更新为: {current_interval}秒")
                
                # 如果已经等待了足够的时间，执行数据收集
                elif elapsed_time >= current_interval:
                    print(f"线程 {thread_id}: 已达到更新时间，执行数据收集 (经过: {elapsed_time:.1f}秒, 间隔: {current_interval}秒)")
                    self.collect_data()
                    last_collection_time = time.time()
                
                # 输出调试信息
                if int(elapsed_time) % 5 == 0:  # 每5秒输出一次状态
                    print(f"线程 {thread_id}: 等待更新, 已经等待: {elapsed_time:.1f}秒, 间隔设置: {current_interval}秒, 剩余: {max(0, current_interval-elapsed_time):.1f}秒")
                    
        except Exception as e:
            print(f"周期性数据收集出错: {e}")
            import traceback
            print(traceback.format_exc())
    
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
            # 标记线程应该停止
            self.should_stop_thread = True
            
            # 应用退出时关闭浏览器
            if self.browser:
                try:
                    print("应用退出，关闭浏览器...")
                    self.browser.quit()
                except Exception as e:
                    print(f"关闭浏览器时出错: {e}")

if __name__ == "__main__":
    StatisticsMenuBarApp().run()