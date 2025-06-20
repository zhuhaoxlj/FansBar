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
                    elif 'juejin' in file_path.lower():
                        values.append(row[4])  # 掘金粉丝数在第五列
                    elif 'zhihu' in file_path.lower():
                        values.append(row[5])  # 知乎粉丝数在第六列
    except Exception as e:
        print(f"读取 {file_path} 时出错: {e}")
        
    return timestamps, values

def generate_html(csdn_data, toutiao_data, juejin_data, zhihu_data):
    """生成包含 echarts 图表的 HTML 页面"""
    
    # 提取数据
    csdn_timestamps, csdn_values = csdn_data
    toutiao_timestamps, toutiao_values = toutiao_data
    juejin_timestamps, juejin_values = juejin_data
    zhihu_timestamps, zhihu_values = zhihu_data
    
    # 为了保持图表数据的完整性，找到所有数据集的时间戳
    all_timestamps = csdn_timestamps + toutiao_timestamps + juejin_timestamps + zhihu_timestamps
    
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
    
    juejin_data_pairs = []
    for i, ts in enumerate(juejin_timestamps):
        try:
            # 解析时间戳
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            value = int(juejin_values[i]) if juejin_values[i].isdigit() else 0
            juejin_data_pairs.append([dt.strftime("%Y-%m-%d %H:%M:%S"), value])
        except (ValueError, IndexError):
            continue
            
    zhihu_data_pairs = []
    for i, ts in enumerate(zhihu_timestamps):
        try:
            # 解析时间戳
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            value = int(zhihu_values[i]) if zhihu_values[i].isdigit() else 0
            zhihu_data_pairs.append([dt.strftime("%Y-%m-%d %H:%M:%S"), value])
        except (ValueError, IndexError):
            continue
    
    # 计算百分比变化（基于所有数据）
    csdn_values_int = [pair[1] for pair in csdn_data_pairs]
    toutiao_values_int = [pair[1] for pair in toutiao_data_pairs]
    juejin_values_int = [pair[1] for pair in juejin_data_pairs]
    zhihu_values_int = [pair[1] for pair in zhihu_data_pairs]
    
    csdn_change = calculate_change(csdn_values_int)
    toutiao_change = calculate_change(toutiao_values_int)
    juejin_change = calculate_change(juejin_values_int)
    zhihu_change = calculate_change(zhihu_values_int)
    
    # 准备 echarts 数据
    csdn_data_json = json.dumps(csdn_data_pairs)
    toutiao_data_json = json.dumps(toutiao_data_pairs)
    juejin_data_json = json.dumps(juejin_data_pairs)
    zhihu_data_json = json.dumps(zhihu_data_pairs)
    
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
            <h1>平台粉丝数据分析</h1>
            <p>数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-title">CSDN 粉丝</div>
                <div class="stat-value">{csdn_values_int[-1] if csdn_values_int else 'N/A'}</div>
                <div class="stat-change {get_change_class(csdn_change)}">{format_change(csdn_change)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">头条粉丝</div>
                <div class="stat-value">{toutiao_values_int[-1] if toutiao_values_int else 'N/A'}</div>
                <div class="stat-change {get_change_class(toutiao_change)}">{format_change(toutiao_change)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">掘金粉丝</div>
                <div class="stat-value">{juejin_values_int[-1] if juejin_values_int else 'N/A'}</div>
                <div class="stat-change {get_change_class(juejin_change)}">{format_change(juejin_change)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">知乎粉丝</div>
                <div class="stat-value">{zhihu_values_int[-1] if zhihu_values_int else 'N/A'}</div>
                <div class="stat-change {get_change_class(zhihu_change)}">{format_change(zhihu_change)}</div>
            </div>
        </div>

        <div class="card">
            <div class="time-filter">
                <button class="time-btn active" data-days="7">7天</button>
                <button class="time-btn" data-days="30">30天</button>
                <button class="time-btn" data-days="90">90天</button>
                <button class="time-btn" data-days="180">180天</button>
                <button class="time-btn" data-days="365">1年</button>
                <button class="time-btn" data-days="0">全部</button>
            </div>
            <div id="combined-chart" class="combined-chart"></div>
        </div>
        
        <div class="charts-container">
            <div class="chart-card">
                <h3>CSDN粉丝趋势</h3>
                <div id="csdn-chart" class="chart"></div>
            </div>
            <div class="chart-card">
                <h3>头条粉丝趋势</h3>
                <div id="toutiao-chart" class="chart"></div>
            </div>
            <div class="chart-card">
                <h3>掘金粉丝趋势</h3>
                <div id="juejin-chart" class="chart"></div>
            </div>
            <div class="chart-card">
                <h3>知乎粉丝趋势</h3>
                <div id="zhihu-chart" class="chart"></div>
            </div>
        </div>

        <div class="footer">
            <p>© {datetime.now().year} 粉丝数据分析工具 | 由 Python 与 ECharts 强力驱动</p>
        </div>
    </div>

    <script>
        // 解析数据
        const csdnData = {csdn_data_json};
        const toutiaoData = {toutiao_data_json};
        const juejinData = {juejin_data_json};
        const zhihuData = {zhihu_data_json};
        
        // 初始化图表
        const csdnChart = echarts.init(document.getElementById('csdn-chart'));
        const toutiaoChart = echarts.init(document.getElementById('toutiao-chart'));
        const juejinChart = echarts.init(document.getElementById('juejin-chart'));
        const zhihuChart = echarts.init(document.getElementById('zhihu-chart'));
        const combinedChart = echarts.init(document.getElementById('combined-chart'));
        
        // 设置CSDN图表
        csdnChart.setOption({{
            title: {{
                text: 'CSDN粉丝数趋势',
                left: 'center',
                textStyle: {{
                    fontSize: 16
                }}
            }},
            tooltip: {{
                trigger: 'axis',
                formatter: function(params) {{
                    const date = new Date(params[0].value[0]);
                    const formattedDate = `${{date.getFullYear()}}-${{(date.getMonth()+1).toString().padStart(2, '0')}}-${{date.getDate().toString().padStart(2, '0')}} ${{date.getHours().toString().padStart(2, '0')}}:${{date.getMinutes().toString().padStart(2, '0')}}`;
                    return `${{formattedDate}}<br/>粉丝数: ${{params[0].value[1]}}`;
                }}
            }},
            xAxis: {{
                type: 'time',
                splitLine: {{
                    show: false
                }}
            }},
            yAxis: {{
                type: 'value',
                nameLocation: 'end',
                splitLine: {{
                    show: true,
                    lineStyle: {{
                        type: 'dashed',
                        color: '#DDD'
                    }}
                }}
            }},
            series: [
                {{
                    name: 'CSDN粉丝',
                    type: 'line',
                    data: csdnData,
                    showSymbol: false,
                    smooth: true,
                    lineStyle: {{
                        width: 3,
                        color: '#4e79a7'
                    }},
                    areaStyle: {{
                        color: {{
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                {{
                                    offset: 0,
                                    color: 'rgba(78, 121, 167, 0.5)'
                                }},
                                {{
                                    offset: 1,
                                    color: 'rgba(78, 121, 167, 0.1)'
                                }}
                            ]
                        }}
                    }}
                }}
            ],
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }}
        }});
        
        // 设置今日头条图表
        toutiaoChart.setOption({{
            title: {{
                text: '头条粉丝数趋势',
                left: 'center',
                textStyle: {{
                    fontSize: 16
                }}
            }},
            tooltip: {{
                trigger: 'axis',
                formatter: function(params) {{
                    const date = new Date(params[0].value[0]);
                    const formattedDate = `${{date.getFullYear()}}-${{(date.getMonth()+1).toString().padStart(2, '0')}}-${{date.getDate().toString().padStart(2, '0')}} ${{date.getHours().toString().padStart(2, '0')}}:${{date.getMinutes().toString().padStart(2, '0')}}`;
                    return `${{formattedDate}}<br/>粉丝数: ${{params[0].value[1]}}`;
                }}
            }},
            xAxis: {{
                type: 'time',
                splitLine: {{
                    show: false
                }}
            }},
            yAxis: {{
                type: 'value',
                nameLocation: 'end',
                splitLine: {{
                    show: true,
                    lineStyle: {{
                        type: 'dashed',
                        color: '#DDD'
                    }}
                }}
            }},
            series: [
                {{
                    name: '头条粉丝',
                    type: 'line',
                    data: toutiaoData,
                    showSymbol: false,
                    smooth: true,
                    lineStyle: {{
                        width: 3,
                        color: '#f28e2b'
                    }},
                    areaStyle: {{
                        color: {{
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                {{
                                    offset: 0,
                                    color: 'rgba(242, 142, 43, 0.5)'
                                }},
                                {{
                                    offset: 1,
                                    color: 'rgba(242, 142, 43, 0.1)'
                                }}
                            ]
                        }}
                    }}
                }}
            ],
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }}
        }});
        
        // 设置掘金图表
        juejinChart.setOption({{
            title: {{
                text: '掘金粉丝数趋势',
                left: 'center',
                textStyle: {{
                    fontSize: 16
                }}
            }},
            tooltip: {{
                trigger: 'axis',
                formatter: function(params) {{
                    const date = new Date(params[0].value[0]);
                    const formattedDate = `${{date.getFullYear()}}-${{(date.getMonth()+1).toString().padStart(2, '0')}}-${{date.getDate().toString().padStart(2, '0')}} ${{date.getHours().toString().padStart(2, '0')}}:${{date.getMinutes().toString().padStart(2, '0')}}`;
                    return `${{formattedDate}}<br/>粉丝数: ${{params[0].value[1]}}`;
                }}
            }},
            xAxis: {{
                type: 'time',
                splitLine: {{
                    show: false
                }}
            }},
            yAxis: {{
                type: 'value',
                nameLocation: 'end',
                splitLine: {{
                    show: true,
                    lineStyle: {{
                        type: 'dashed',
                        color: '#DDD'
                    }}
                }}
            }},
            series: [
                {{
                    name: '掘金粉丝',
                    type: 'line',
                    data: juejinData,
                    showSymbol: false,
                    smooth: true,
                    lineStyle: {{
                        width: 3,
                        color: '#59a14f'
                    }},
                    areaStyle: {{
                        color: {{
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                {{
                                    offset: 0,
                                    color: 'rgba(89, 161, 79, 0.5)'
                                }},
                                {{
                                    offset: 1,
                                    color: 'rgba(89, 161, 79, 0.1)'
                                }}
                            ]
                        }}
                    }}
                }}
            ],
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }}
        }});
        
        // 设置知乎图表
        zhihuChart.setOption({{
            title: {{
                text: '知乎粉丝数趋势',
                left: 'center',
                textStyle: {{
                    fontSize: 16
                }}
            }},
            tooltip: {{
                trigger: 'axis',
                formatter: function(params) {{
                    const date = new Date(params[0].value[0]);
                    const formattedDate = `${{date.getFullYear()}}-${{(date.getMonth()+1).toString().padStart(2, '0')}}-${{date.getDate().toString().padStart(2, '0')}} ${{date.getHours().toString().padStart(2, '0')}}:${{date.getMinutes().toString().padStart(2, '0')}}`;
                    return `${{formattedDate}}<br/>粉丝数: ${{params[0].value[1]}}`;
                }}
            }},
            xAxis: {{
                type: 'time',
                splitLine: {{
                    show: false
                }}
            }},
            yAxis: {{
                type: 'value',
                nameLocation: 'end',
                splitLine: {{
                    show: true,
                    lineStyle: {{
                        type: 'dashed',
                        color: '#DDD'
                    }}
                }}
            }},
            series: [
                {{
                    name: '知乎粉丝',
                    type: 'line',
                    data: zhihuData,
                    showSymbol: false,
                    smooth: true,
                    lineStyle: {{
                        width: 3,
                        color: '#8E44AD'
                    }},
                    areaStyle: {{
                        color: {{
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                {{
                                    offset: 0,
                                    color: 'rgba(142, 68, 173, 0.5)'
                                }},
                                {{
                                    offset: 1,
                                    color: 'rgba(142, 68, 173, 0.1)'
                                }}
                            ]
                        }}
                    }}
                }}
            ],
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }}
        }});
        
        // 设置合并图表选项
        function updateCombinedChart(days) {{
            let filteredCsdnData = csdnData;
            let filteredToutiaoData = toutiaoData;
            let filteredJuejinData = juejinData;
            let filteredZhihuData = zhihuData;
            
            if (days > 0) {{
                const cutoffDate = new Date();
                cutoffDate.setDate(cutoffDate.getDate() - days);
                
                filteredCsdnData = csdnData.filter(item => new Date(item[0]) >= cutoffDate);
                filteredToutiaoData = toutiaoData.filter(item => new Date(item[0]) >= cutoffDate);
                filteredJuejinData = juejinData.filter(item => new Date(item[0]) >= cutoffDate);
                filteredZhihuData = zhihuData.filter(item => new Date(item[0]) >= cutoffDate);
            }}
            
            combinedChart.setOption({{
                title: {{
                    text: '平台粉丝数对比',
                    left: 'center',
                    textStyle: {{
                        fontSize: 18,
                        fontWeight: 'bold'
                    }}
                }},
                tooltip: {{
                    trigger: 'axis',
                    axisPointer: {{
                        type: 'shadow'
                    }}
                }},
                legend: {{
                    data: ['CSDN', '头条', '掘金', '知乎'],
                    top: '30px'
                }},
                xAxis: {{
                    type: 'time',
                    splitLine: {{
                        show: false
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '粉丝数',
                    nameLocation: 'end',
                    splitLine: {{
                        show: true,
                        lineStyle: {{
                            type: 'dashed',
                            color: '#DDD'
                        }}
                    }}
                }},
                series: [
                    {{
                        name: 'CSDN',
                        type: 'line',
                        data: filteredCsdnData,
                        showSymbol: false,
                        smooth: true,
                        lineStyle: {{
                            width: 2.5,
                            color: '#4e79a7'
                        }}
                    }},
                    {{
                        name: '头条',
                        type: 'line',
                        data: filteredToutiaoData,
                        showSymbol: false,
                        smooth: true,
                        lineStyle: {{
                            width: 2.5,
                            color: '#f28e2b'
                        }}
                    }},
                    {{
                        name: '掘金',
                        type: 'line',
                        data: filteredJuejinData,
                        showSymbol: false,
                        smooth: true,
                        lineStyle: {{
                            width: 2.5,
                            color: '#59a14f'
                        }}
                    }},
                    {{
                        name: '知乎',
                        type: 'line',
                        data: filteredZhihuData,
                        showSymbol: false,
                        smooth: true,
                        lineStyle: {{
                            width: 2.5,
                            color: '#8E44AD'
                        }}
                    }}
                ],
                grid: {{
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                }}
            }});
        }}
        
        // 初始化合并图表 (默认显示7天)
        updateCombinedChart(7);
        
        // 添加时间过滤器按钮事件
        document.querySelectorAll('.time-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                // 取消所有按钮的活跃状态
                document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
                // 设置当前按钮为活跃状态
                this.classList.add('active');
                // 更新图表
                const days = parseInt(this.getAttribute('data-days'));
                updateCombinedChart(days);
            }});
        }});
        
        // 处理窗口大小变化
        window.addEventListener('resize', function() {{
            csdnChart.resize();
            toutiaoChart.resize();
            juejinChart.resize();
            zhihuChart.resize();
            combinedChart.resize();
        }});
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
        .error-container {{
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
            color: #e74c3c;
            margin-bottom: 20px;
        }}
        h1 {{
            margin: 0;
            margin-bottom: 20px;
            color: #e74c3c;
        }}
        p {{
            margin-bottom: 30px;
            line-height: 1.5;
            color: #555;
        }}
        .btn {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
        }}
        .btn:hover {{
            background-color: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <h1>数据分析错误</h1>
        <p>{error_message}</p>
        <a href="javascript:window.close();" class="btn">关闭页面</a>
    </div>
</body>
</html>
    """
    return html

def calculate_change(values):
    """计算数据变化百分比"""
    if not values or len(values) < 2:
        return None
    
    first_value = values[0]
    last_value = values[-1]
    
    if first_value == 0:
        return None
        
    change = ((last_value - first_value) / first_value) * 100
    return change

def format_change(change):
    """格式化变化百分比"""
    if change is None:
        return "数据不足"
        
    if change > 0:
        return f"+{change:.2f}%"
    else:
        return f"{change:.2f}%"

def get_change_class(change):
    """根据变化百分比获取样式类名"""
    if change is None:
        return ""
        
    if change > 0:
        return "positive"
    elif change < 0:
        return "negative"
    else:
        return ""

def generate_analysis_page():
    """生成粉丝数据分析页面"""
    try:
        # 获取数据文件路径
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        csdn_file = os.path.join(data_dir, 'csdn_stats.csv')
        toutiao_file = os.path.join(data_dir, 'toutiao_stats.csv')
        juejin_file = os.path.join(data_dir, 'juejin_stats.csv')
        zhihu_file = os.path.join(data_dir, 'zhihu_stats.csv')
        
        # 读取数据
        csdn_data = read_csv_data(csdn_file)
        toutiao_data = read_csv_data(toutiao_file)
        juejin_data = read_csv_data(juejin_file)
        zhihu_data = read_csv_data(zhihu_file)
        
        # 生成HTML
        html = generate_html(csdn_data, toutiao_data, juejin_data, zhihu_data)
        
        # 保存HTML文件
        output_file = os.path.join(data_dir, 'fans_analysis.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        # 在浏览器中打开
        webbrowser.open('file://' + os.path.abspath(output_file))
        
        return output_file
        
    except Exception as e:
        print(f"生成分析页面时出错: {e}")
        import traceback
        print(traceback.format_exc())
        
        # 生成错误页面
        error_html = generate_error_html(f"生成分析页面时出错: {str(e)}")
        error_file = os.path.join(data_dir, 'error.html')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_html)
            
        # 在浏览器中打开错误页面
        webbrowser.open('file://' + os.path.abspath(error_file))
        
        return None

if __name__ == "__main__":
    # 测试函数
    output_file = generate_analysis_page()
    print(f"分析页面已生成: {output_file}") 