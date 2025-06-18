#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据分析模块 - 读取 CSV 文件并生成包含 echarts 图表的 HTML 页面
"""

import os
import csv
import json
import webbrowser
from datetime import datetime, timedelta

def read_csv_data(file_path):
    """读取CSV数据文件"""
    if not os.path.exists(file_path):
        return [], []
        
    timestamps = []
    values = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 跳过标题行
            next(reader)
            
            for row in reader:
                if len(row) > 0:
                    # 将时间戳和数值添加到列表中
                    timestamps.append(row[0])  # 时间戳在第一列
                    # 根据文件类型读取对应的数据列
                    if 'csdn' in file_path.lower():
                        values.append(row[3])  # CSDN 粉丝数在第四列
                    elif 'toutiao' in file_path.lower():
                        values.append(row[2])  # 头条粉丝数在第三列
    except Exception as e:
        print(f"读取 {file_path} 时出错: {e}")
        
    return timestamps, values

def generate_html(csdn_data, toutiao_data):
    """生成包含 echarts 图表的 HTML 页面"""
    
    # 提取数据
    csdn_timestamps, csdn_values = csdn_data
    toutiao_timestamps, toutiao_values = toutiao_data
    
    # 为了保持图表数据的完整性，找到两个数据集的最早和最晚的时间戳
    all_timestamps = csdn_timestamps + toutiao_timestamps
    
    # 如果没有数据，返回错误提示页面
    if not all_timestamps:
        return generate_error_html("没有找到数据，请确保已经收集了足够的数据点。")
    
    # 预处理数据，确保数字格式正确，并转换时间戳为日期对象
    csdn_data_pairs = []
    for i, ts in enumerate(csdn_timestamps):
        try:
            # 解析时间戳
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            value = int(csdn_values[i]) if csdn_values[i].isdigit() else 0
            csdn_data_pairs.append([dt.strftime("%Y-%m-%d %H:%M:%S"), value])
        except (ValueError, IndexError):
            continue
            
    toutiao_data_pairs = []
    for i, ts in enumerate(toutiao_timestamps):
        try:
            # 解析时间戳
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            value = int(toutiao_values[i]) if toutiao_values[i].isdigit() else 0
            toutiao_data_pairs.append([dt.strftime("%Y-%m-%d %H:%M:%S"), value])
        except (ValueError, IndexError):
            continue
    
    # 计算百分比变化（基于所有数据）
    csdn_values_int = [pair[1] for pair in csdn_data_pairs]
    toutiao_values_int = [pair[1] for pair in toutiao_data_pairs]
    
    csdn_change = calculate_change(csdn_values_int)
    toutiao_change = calculate_change(toutiao_values_int)
    
    # 准备 echarts 数据
    csdn_data_json = json.dumps(csdn_data_pairs)
    toutiao_data_json = json.dumps(toutiao_data_pairs)
    
    # 生成 HTML
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>粉丝数据分析</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{
            font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f7f9fc;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 20px 0;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.9;
            font-size: 16px;
        }}
        .card {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            padding: 20px;
        }}
        .charts-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .chart-card {{
            flex: 1;
            min-width: calc(50% - 10px);
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 15px;
        }}
        .chart {{
            width: 100%;
            height: 400px;
        }}
        .stats-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            flex: 1;
            min-width: calc(25% - 15px);
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 15px;
            text-align: center;
        }}
        .stat-title {{
            font-size: 16px;
            color: #666;
            margin-bottom: 10px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .stat-change {{
            margin-top: 5px;
            font-size: 14px;
        }}
        .positive {{
            color: #4caf50;
        }}
        .negative {{
            color: #f44336;
        }}
        .combined-chart {{
            width: 100%;
            height: 500px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px 0;
            color: #666;
            font-size: 14px;
        }}
        .time-filter {{
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .time-btn {{
            padding: 8px 16px;
            background-color: #f0f0f0;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
            color: #333;
        }}
        .time-btn:hover {{
            background-color: #e0e0e0;
        }}
        .time-btn.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        @media (max-width: 768px) {{
            .chart-card, .stat-card {{
                min-width: 100%;
            }}
            .time-btn {{
                padding: 6px 12px;
                font-size: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>粉丝数据分析报告</h1>
            <p>数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-title">CSDN 当前粉丝数</div>
                <div class="stat-value">{csdn_values_int[-1] if csdn_values_int else 'N/A'}</div>
                <div class="stat-change {get_change_class(csdn_change)}">
                    {format_change(csdn_change)}
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-title">头条 当前粉丝数</div>
                <div class="stat-value">{toutiao_values_int[-1] if toutiao_values_int else 'N/A'}</div>
                <div class="stat-change {get_change_class(toutiao_change)}">
                    {format_change(toutiao_change)}
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-title">CSDN 数据点</div>
                <div class="stat-value">{len(csdn_values_int)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">头条 数据点</div>
                <div class="stat-value">{len(toutiao_values_int)}</div>
            </div>
        </div>
        
        <div class="card">
            <div class="time-filter" id="combinedTimeFilter">
                <button class="time-btn active" data-range="all">所有数据</button>
                <button class="time-btn" data-range="month">近一月</button>
                <button class="time-btn" data-range="week">近一周</button>
                <button class="time-btn" data-range="3days">近三天</button>
                <button class="time-btn" data-range="today">今日</button>
            </div>
            <div class="combined-chart" id="combinedChart"></div>
        </div>
        
        <div class="charts-container">
            <div class="chart-card">
                <div class="time-filter" id="csdnTimeFilter">
                    <button class="time-btn active" data-range="all">所有数据</button>
                    <button class="time-btn" data-range="month">近一月</button>
                    <button class="time-btn" data-range="week">近一周</button>
                    <button class="time-btn" data-range="3days">近三天</button>
                    <button class="time-btn" data-range="today">今日</button>
                </div>
                <div class="chart" id="csdnChart"></div>
            </div>
            <div class="chart-card">
                <div class="time-filter" id="toutiaoTimeFilter">
                    <button class="time-btn active" data-range="all">所有数据</button>
                    <button class="time-btn" data-range="month">近一月</button>
                    <button class="time-btn" data-range="week">近一周</button>
                    <button class="time-btn" data-range="3days">近三天</button>
                    <button class="time-btn" data-range="today">今日</button>
                </div>
                <div class="chart" id="toutiaoChart"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>© {datetime.now().year} 粉丝数据分析工具 - 自动生成</p>
        </div>
    </div>

    <script>
        // 所有原始数据
        var csdnData = {csdn_data_json};
        var toutiaoData = {toutiao_data_json};
        
        // 初始化图表
        var csdnChart = echarts.init(document.getElementById('csdnChart'));
        var toutiaoChart = echarts.init(document.getElementById('toutiaoChart'));
        var combinedChart = echarts.init(document.getElementById('combinedChart'));
        
        // 根据时间范围筛选数据
        function filterDataByRange(data, range) {{
            if (range === 'all') {{
                return data;
            }}
            
            var now = new Date();
            var cutoffDate = new Date();
            
            switch(range) {{
                case 'today':
                    cutoffDate.setHours(0, 0, 0, 0);
                    break;
                case '3days':
                    cutoffDate.setDate(now.getDate() - 3);
                    break;
                case 'week':
                    cutoffDate.setDate(now.getDate() - 7);
                    break;
                case 'month':
                    cutoffDate.setMonth(now.getMonth() - 1);
                    break;
            }}
            
            return data.filter(function(item) {{
                var itemDate = new Date(item[0]);
                return itemDate >= cutoffDate;
            }});
        }}
        
        // 绘制CSDN图表
        function drawCSDNChart(range) {{
            var filteredData = filterDataByRange(csdnData, range);
            
            if (filteredData.length === 0) {{
                // 如果筛选后没有数据，显示提示信息
                csdnChart.setOption({{
                    title: {{
                        text: 'CSDN 粉丝趋势 - 选定时间段无数据',
                        left: 'center'
                    }},
                    graphic: [
                        {{
                            type: 'text',
                            left: 'center',
                            top: 'middle',
                            style: {{
                                text: '选定的时间段内没有数据',
                                fontSize: 20,
                                fill: '#999'
                            }}
                        }}
                    ]
                }});
                return;
            }}
            
            var csdnOption = {{
                title: {{
                    text: 'CSDN 粉丝趋势',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'axis',
                    formatter: function(params) {{
                        var date = new Date(params[0].value[0]);
                        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString() + '<br/>' +
                               params[0].marker + ' 粉丝数: ' + params[0].value[1];
                    }}
                }},
                xAxis: {{
                    type: 'time',
                    axisLabel: {{
                        formatter: function(value) {{
                            var date = new Date(value);
                            return date.getMonth() + 1 + '/' + date.getDate();
                        }}
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '粉丝数',
                    nameTextStyle: {{
                        padding: [0, 0, 0, 40]
                    }}
                }},
                series: [
                    {{
                        name: 'CSDN 粉丝',
                        type: 'line',
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 6,
                        lineStyle: {{
                            color: '#5470C6',
                            width: 3
                        }},
                        itemStyle: {{
                            color: '#5470C6'
                        }},
                        areaStyle: {{
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {{
                                    offset: 0,
                                    color: 'rgba(84, 112, 198, 0.5)'
                                }},
                                {{
                                    offset: 1,
                                    color: 'rgba(84, 112, 198, 0.1)'
                                }}
                            ])
                        }},
                        data: filteredData.map(function(item) {{ return [item[0], item[1]]; }})
                    }}
                ],
                toolbox: {{
                    feature: {{
                        saveAsImage: {{}}
                    }}
                }}
            }};
            
            csdnChart.setOption(csdnOption, true);
        }}
        
        // 绘制头条图表
        function drawToutiaoChart(range) {{
            var filteredData = filterDataByRange(toutiaoData, range);
            
            if (filteredData.length === 0) {{
                // 如果筛选后没有数据，显示提示信息
                toutiaoChart.setOption({{
                    title: {{
                        text: '头条 粉丝趋势 - 选定时间段无数据',
                        left: 'center'
                    }},
                    graphic: [
                        {{
                            type: 'text',
                            left: 'center',
                            top: 'middle',
                            style: {{
                                text: '选定的时间段内没有数据',
                                fontSize: 20,
                                fill: '#999'
                            }}
                        }}
                    ]
                }});
                return;
            }}
            
            var toutiaoOption = {{
                title: {{
                    text: '头条 粉丝趋势',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'axis',
                    formatter: function(params) {{
                        var date = new Date(params[0].value[0]);
                        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString() + '<br/>' +
                               params[0].marker + ' 粉丝数: ' + params[0].value[1];
                    }}
                }},
                xAxis: {{
                    type: 'time',
                    axisLabel: {{
                        formatter: function(value) {{
                            var date = new Date(value);
                            return date.getMonth() + 1 + '/' + date.getDate();
                        }}
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '粉丝数',
                    nameTextStyle: {{
                        padding: [0, 0, 0, 40]
                    }}
                }},
                series: [
                    {{
                        name: '头条 粉丝',
                        type: 'line',
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 6,
                        lineStyle: {{
                            color: '#FF9F43',
                            width: 3
                        }},
                        itemStyle: {{
                            color: '#FF9F43'
                        }},
                        areaStyle: {{
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {{
                                    offset: 0,
                                    color: 'rgba(255, 159, 67, 0.5)'
                                }},
                                {{
                                    offset: 1,
                                    color: 'rgba(255, 159, 67, 0.1)'
                                }}
                            ])
                        }},
                        data: filteredData.map(function(item) {{ return [item[0], item[1]]; }})
                    }}
                ],
                toolbox: {{
                    feature: {{
                        saveAsImage: {{}}
                    }}
                }}
            }};
            
            toutiaoChart.setOption(toutiaoOption, true);
        }}
        
        // 绘制组合图表
        function drawCombinedChart(range) {{
            var filteredCSDNData = filterDataByRange(csdnData, range);
            var filteredToutiaoData = filterDataByRange(toutiaoData, range);
            
            if (filteredCSDNData.length === 0 && filteredToutiaoData.length === 0) {{
                // 如果筛选后没有数据，显示提示信息
                combinedChart.setOption({{
                    title: {{
                        text: 'CSDN vs 头条 粉丝数对比 - 选定时间段无数据',
                        left: 'center'
                    }},
                    graphic: [
                        {{
                            type: 'text',
                            left: 'center',
                            top: 'middle',
                            style: {{
                                text: '选定的时间段内没有数据',
                                fontSize: 20,
                                fill: '#999'
                            }}
                        }}
                    ]
                }});
                return;
            }}
            
            var combinedOption = {{
                title: {{
                    text: 'CSDN vs 头条 粉丝数对比',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'axis',
                    formatter: function(params) {{
                        if (params.length === 0) return '';
                        
                        var date = new Date(params[0].value[0]);
                        var result = date.toLocaleDateString() + ' ' + date.toLocaleTimeString() + '<br/>';
                        
                        params.forEach(function(param) {{
                            if (param.value) {{
                                result += param.marker + ' ' + param.seriesName + ': ' + param.value[1] + '<br/>';
                            }}
                        }});
                        
                        return result;
                    }}
                }},
                legend: {{
                    data: ['CSDN 粉丝', '头条 粉丝'],
                    top: 30
                }},
                grid: {{
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                }},
                toolbox: {{
                    feature: {{
                        saveAsImage: {{}}
                    }}
                }},
                xAxis: {{
                    type: 'time',
                    axisLabel: {{
                        formatter: function(value) {{
                            var date = new Date(value);
                            return date.getMonth() + 1 + '/' + date.getDate();
                        }}
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '粉丝数'
                }},
                series: [
                    {{
                        name: 'CSDN 粉丝',
                        type: 'line',
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 8,
                        lineStyle: {{
                            width: 3,
                            color: '#5470C6'
                        }},
                        data: filteredCSDNData.map(function(item) {{ return [item[0], item[1]]; }})
                    }},
                    {{
                        name: '头条 粉丝',
                        type: 'line',
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 8,
                        lineStyle: {{
                            width: 3,
                            color: '#FF9F43'
                        }},
                        data: filteredToutiaoData.map(function(item) {{ return [item[0], item[1]]; }})
                    }}
                ]
            }};
            
            combinedChart.setOption(combinedOption, true);
        }}
        
        // 为时间筛选按钮添加点击事件
        function setupTimeFilters() {{
            // CSDN图表的时间筛选
            var csdnFilterButtons = document.querySelectorAll('#csdnTimeFilter .time-btn');
            csdnFilterButtons.forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    // 移除所有按钮的active类
                    csdnFilterButtons.forEach(function(b) {{ b.classList.remove('active'); }});
                    // 给当前点击的按钮添加active类
                    this.classList.add('active');
                    // 根据选择的时间范围重新绘制图表
                    drawCSDNChart(this.getAttribute('data-range'));
                }});
            }});
            
            // 头条图表的时间筛选
            var toutiaoFilterButtons = document.querySelectorAll('#toutiaoTimeFilter .time-btn');
            toutiaoFilterButtons.forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    // 移除所有按钮的active类
                    toutiaoFilterButtons.forEach(function(b) {{ b.classList.remove('active'); }});
                    // 给当前点击的按钮添加active类
                    this.classList.add('active');
                    // 根据选择的时间范围重新绘制图表
                    drawToutiaoChart(this.getAttribute('data-range'));
                }});
            }});
            
            // 组合图表的时间筛选
            var combinedFilterButtons = document.querySelectorAll('#combinedTimeFilter .time-btn');
            combinedFilterButtons.forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    // 移除所有按钮的active类
                    combinedFilterButtons.forEach(function(b) {{ b.classList.remove('active'); }});
                    // 给当前点击的按钮添加active类
                    this.classList.add('active');
                    // 根据选择的时间范围重新绘制图表
                    drawCombinedChart(this.getAttribute('data-range'));
                }});
            }});
        }}
        
        // 初始化所有图表
        function initCharts() {{
            drawCSDNChart('all');
            drawToutiaoChart('all');
            drawCombinedChart('all');
            setupTimeFilters();
        }}
        
        // 响应窗口大小变化
        window.addEventListener('resize', function() {{
            csdnChart.resize();
            toutiaoChart.resize();
            combinedChart.resize();
        }});
        
        // 页面加载完成后初始化图表
        document.addEventListener('DOMContentLoaded', initCharts);
        
        // 如果DOMContentLoaded已经触发，手动初始化图表
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initCharts);
        }} else {{
            initCharts();
        }}
    </script>
</body>
</html>
    """
    
    return html

def generate_error_html(error_message):
    """生成错误提示页面"""
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析错误</title>
    <style>
        body {{
            font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f7f9fc;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .error-card {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            padding: 30px;
            text-align: center;
            max-width: 500px;
            width: 90%;
        }}
        .error-icon {{
            font-size: 60px;
            color: #f44336;
            margin-bottom: 20px;
        }}
        h1 {{
            margin: 0 0 20px 0;
            color: #333;
        }}
        p {{
            margin: 20px 0;
            line-height: 1.6;
            color: #666;
        }}
        .button {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #5470C6;
            color: white;
            border-radius: 5px;
            text-decoration: none;
            transition: background-color 0.3s;
        }}
        .button:hover {{
            background-color: #4560b0;
        }}
    </style>
</head>
<body>
    <div class="error-card">
        <div class="error-icon">⚠️</div>
        <h1>无法生成数据分析</h1>
        <p>{error_message}</p>
        <a href="javascript:window.history.back();" class="button">返回</a>
    </div>
</body>
</html>
    """
    return html

def calculate_change(values):
    """计算数据的百分比变化"""
    if not values or len(values) < 2:
        return 0
    
    first_value = values[0]
    last_value = values[-1]
    
    if first_value == 0:
        return 0
        
    change = (last_value - first_value) / first_value * 100
    return change

def format_change(change):
    """格式化变化百分比显示"""
    if change == 0:
        return "无变化"
    
    if change > 0:
        return f"+{change:.2f}%"
    else:
        return f"{change:.2f}%"
    
def get_change_class(change):
    """获取变化的CSS类"""
    if change > 0:
        return "positive"
    elif change < 0:
        return "negative"
    else:
        return ""

def generate_analysis_page():
    """生成分析页面并打开"""
    # 读取数据
    csdn_data = read_csv_data('csdn_stats.csv')
    toutiao_data = read_csv_data('toutiao_stats.csv')
    
    # 生成HTML
    html_content = generate_html(csdn_data, toutiao_data)
    
    # 保存HTML文件
    output_file = 'fans_data_analysis.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 打开浏览器显示
    webbrowser.open('file://' + os.path.abspath(output_file))
    return output_file

if __name__ == "__main__":
    # 测试函数
    output_file = generate_analysis_page()
    print(f"分析页面已生成: {output_file}") 