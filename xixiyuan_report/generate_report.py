#!/usr/bin/env python3
"""
西溪源村旅游资源调查报告 - 完整PDF生成脚本
"""
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                 TableStyle, PageBreak, Image, KeepTogether, HRFlowable)
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from io import BytesIO
from datetime import datetime
import textwrap

# ============================================================
# 字体注册
# ============================================================
FONT_PATH = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
try:
    pdfmetrics.registerFont(TTFont('WQY', FONT_PATH))
    FONT_NAME = 'WQY'
except:
    try:
        pdfmetrics.registerFont(TTFont('SourceHan', '/home/knooe/.fonts/SourceHanSansSC.otf'))
        FONT_NAME = 'SourceHan'
    except:
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        FONT_NAME = 'STSong-Light'

# matplotlib 中文字体
try:
    font_prop = fm.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = 'sans-serif'
except:
    pass

# ============================================================
# 颜色方案
# ============================================================
MC_PRIMARY = HexColor('#1a5276')
MC_SECONDARY = HexColor('#2e86c1')
MC_ACCENT = HexColor('#27ae60')
MC_DARK_R = HexColor('#2c3e50')
C_LIGHT_BG = HexColor('#f0f4f8')
C_TABLE_HEADER = HexColor('#1a5276')
C_TABLE_ROW1 = HexColor('#eaf2f8')
C_TABLE_ROW2 = HexColor('#ffffff')
MC_DARK = HexColor('#2c3e50')
C_BORDER = HexColor('#bdc3c7')

OUTPUT_DIR = '/home/knooe/workspace/xixiyuan_report'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 样式定义
# ============================================================
def create_styles():
    styles = {}
    
    styles['cover_title'] = ParagraphStyle(
        'CoverTitle', fontName=FONT_NAME, fontSize=26, leading=36,
        alignment=TA_CENTER, textColor=white, spaceAfter=6*mm
    )
    styles['cover_subtitle'] = ParagraphStyle(
        'CoverSubtitle', fontName=FONT_NAME, fontSize=16, leading=24,
        alignment=TA_CENTER, textColor=HexColor('#d5e8f0'), spaceAfter=3*mm
    )
    styles['h1'] = ParagraphStyle(
        'H1', fontName=FONT_NAME, fontSize=18, leading=28, 
        alignment=TA_LEFT, textColor=MC_PRIMARY, spaceBefore=15*mm, spaceAfter=8*mm,
        borderWidth=0, borderPadding=0
    )
    styles['h2'] = ParagraphStyle(
        'H2', fontName=FONT_NAME, fontSize=14, leading=22,
        alignment=TA_LEFT, textColor=MC_SECONDARY, spaceBefore=10*mm, spaceAfter=5*mm
    )
    styles['h3'] = ParagraphStyle(
        'H3', fontName=FONT_NAME, fontSize=12, leading=18,
        alignment=TA_LEFT, textColor=MC_DARK, spaceBefore=6*mm, spaceAfter=3*mm
    )
    styles['body'] = ParagraphStyle(
        'Body', fontName=FONT_NAME, fontSize=10.5, leading=18,
        alignment=TA_JUSTIFY, textColor=MC_DARK, spaceBefore=2*mm, spaceAfter=2*mm,
        firstLineIndent=21
    )
    styles['body_no_indent'] = ParagraphStyle(
        'BodyNI', fontName=FONT_NAME, fontSize=10.5, leading=18,
        alignment=TA_JUSTIFY, textColor=MC_DARK, spaceBefore=2*mm, spaceAfter=2*mm
    )
    styles['toc'] = ParagraphStyle(
        'TOC', fontName=FONT_NAME, fontSize=11, leading=20,
        alignment=TA_LEFT, textColor=MC_DARK
    )
    styles['toc_h1'] = ParagraphStyle(
        'TOC_H1', fontName=FONT_NAME, fontSize=12, leading=22,
        alignment=TA_LEFT, textColor=MC_PRIMARY, spaceBefore=4*mm
    )
    styles['caption'] = ParagraphStyle(
        'Caption', fontName=FONT_NAME, fontSize=9, leading=14,
        alignment=TA_CENTER, textColor=grey, spaceBefore=2*mm, spaceAfter=4*mm
    )
    styles['cover_info'] = ParagraphStyle(
        'CoverInfo', fontName=FONT_NAME, fontSize=12, leading=20,
        alignment=TA_CENTER, textColor=white
    )
    return styles

# ============================================================
# 图表生成函数
# ============================================================
def setup_mpl_zh():
    """设置 matplotlib 中文支持"""
    try:
        import matplotlib.font_manager as fm
        # 使用文泉驿微米黑 .ttc
        fm.fontManager.addfont(FONT_PATH)
        # 重建字体缓存
        fm._load_fontmanager(try_read_cache=False)
        # 获取新注册的字体名称
        fp = fm.FontProperties(fname=FONT_PATH)
        font_name = fp.get_name()
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        # fallback: 直接用 FontProperties 指定每个文本
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        print(f"Warning: Chinese font setup failed: {e}")

def save_chart_to_buffer(fig, dpi=150):
    """将 matplotlib 图表保存到 BytesIO"""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return buf

def chart_resource_classification():
    """图2-1 西溪源村旅游资源分类树状图"""
    setup_mpl_zh()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    ax.text(5, 5.5, '西溪源村旅游资源', ha='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a5276', alpha=0.9), color='white')
    
    for x, y, label, clr in [(2, 4.2, '自然旅游资源', '#27ae60'), (5, 4.2, '人文旅游资源', '#e74c3c'), (8, 4.2, '社会旅游资源', '#f39c12')]:
        ax.text(x, y, label, ha='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor=clr, alpha=0.85), color='white')
        ax.plot([5, x], [5.2, y+0.2], 'gray', linewidth=1, alpha=0.5)
    
    items = [
        (0.6, 2.8, '午潮山\n林地资源\n灵项溪\n闲林水库', '#27ae60'),
        (1.9, 2.8, '跌水景观\n击浪现象\n棕榈树林\n丑橘树', '#27ae60'),
        (3.2, 2.8, '茶产业资源\n山地丘陵\n水域风光\n生物景观', '#27ae60'),
        (4.5, 2.8, '午潮亭\n登山步道\n海鱼干\n传统民居', '#e74c3c'),
        (5.8, 2.8, '庙宇遗址\n龙庆寺\n名人乡贤\n民俗节庆', '#e74c3c'),
        (7.1, 2.8, '清源广场\n乡村微脑平台\n老年活动中心\n文学创作基地', '#f39c12'),
        (8.4, 2.8, '茶产业园\n民宿经济\n共富基金\n数字治理', '#f39c12'),
    ]
    for x, y, text, clr in items:
        ax.text(x, y, text, ha='center', fontsize=8, va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=clr, alpha=0.9), color='#2c3e50')
    
    ax.set_title('图 2-1  西溪源村旅游资源分类', fontsize=13, fontweight='bold', color='#1a5276', pad=15)
    return save_chart_to_buffer(fig)

def chart_swot_matrix():
    """图3-1 SWOT分析矩阵"""
    setup_mpl_zh()
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(5, 9.5, 'SWOT 分析矩阵', ha='center', fontsize=16, fontweight='bold', color='#1a5276')
    
    quadrants = [
        (0, 5, 5, 10, 'S 优势 (Strengths)', '#27ae60', '\u2022 森林覆盖率超80%\n\u2022 西溪河源头区位优势\n\u2022 龙井茶产业基础好\n\u2022 全国乡村治理示范村\n\u2022 集体经济超1100万元'),
        (5, 5, 10, 10, 'W 劣势 (Weaknesses)', '#e74c3c', '\u2022 交通可达性不足\n\u2022 缺乏科学旅游规划\n\u2022 基础设施不完善\n\u2022 青壮年人口外流\n\u2022 旅游知名度低'),
        (0, 0, 5, 5, 'O 机会 (Opportunities)', '#2980b9', '\u2022 余杭区旅游发展政策\n\u2022 西溪湿地品牌拉动\n\u2022 城乡居民休闲需求增长\n\u2022 农文旅融合政策利好\n\u2022 千岛湖引水工程地标'),
        (5, 0, 10, 5, 'T 威胁 (Threats)', '#f39c12', '\u2022 周边景区竞争激烈\n\u2022 传统农业经济衰退\n\u2022 生态环境保护压力\n\u2022 盲目开发风险\n\u2022 同质化竞争加剧'),
    ]
    
    for x0, y0, x1, y1, title, clr, items in quadrants:
        rect = plt.Rectangle((x0, y0), x1-x0, y1-y0, facecolor=clr, alpha=0.08, edgecolor=clr, linewidth=2)
        ax.add_patch(rect)
        ax.text((x0+x1)/2, y1-0.5, title, ha='center', fontsize=12, fontweight='bold', color=clr)
        ax.text(x0+0.3, y1-1.1, items, fontsize=8.5, va='top', color='#2c3e50')
    
    return save_chart_to_buffer(fig)

def chart_market_analysis():
    """图4-1 客源市场分析饼图"""
    setup_mpl_zh()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    
    labels1 = ['杭州市区', '浙江省内其他', '长三角地区', '国内其他', '境外']
    sizes1 = [38, 28, 18, 12, 4]
    colors1 = ['#1a5276', '#2e86c1', '#5dade2', '#85c1e9', '#aed6f1']
    
    ax1.pie(sizes1, labels=labels1, colors=colors1, autopct='%1.0f%%', startangle=90, pctdistance=0.85)
    ax1.set_title('客源地域结构', fontsize=11, fontweight='bold', color='#1a5276')
    
    labels2 = ['休闲度假', '亲子研学', '生态观光', '文化体验', '其他']
    sizes2 = [35, 22, 20, 15, 8]
    colors2 = ['#27ae60', '#2ecc71', '#58d68d', '#82e0aa', '#a9dfbf']
    
    ax2.pie(sizes2, labels=labels2, colors=colors2, autopct='%1.0f%%', startangle=90, pctdistance=0.85)
    ax2.set_title('游客出行目的', fontsize=11, fontweight='bold', color='#1a5276')
    
    fig.suptitle('图 4-1  西溪源村客源市场分析', fontsize=13, fontweight='bold', color='#1a5276', y=1.02)
    fig.tight_layout()
    return save_chart_to_buffer(fig)

def chart_development_timeline():
    """图5-1 分期发展规划甘特图"""
    setup_mpl_zh()
    fig, ax = plt.subplots(figsize=(10, 4))
    
    phases = ['近期\n(2026-2028)', '中期\n(2029-2031)', '远期\n(2032-2035)']
    tasks = [
        ('基础设施建设', 0, 2.5, '#1a5276'),
        ('旅游服务中心', 0.5, 1.5, '#2e86c1'),
        ('茶园观光提升', 0, 3, '#27ae60'),
        ('午潮山步道完善', 0.5, 3, '#f39c12'),
        ('民宿集群建设', 1, 3, '#e74c3c'),
        ('龙庆寺文化修复', 1.5, 3, '#8e44ad'),
        ('清源广场打造', 0, 1, '#2980b9'),
        ('品牌与营销推广', 0.5, 3, '#16a085'),
        ('智慧旅游平台', 1, 3, '#d35400'),
        ('生态保护工程', 0, 3, '#2c3e50'),
    ]
    
    for i, (task, start, duration, clr) in enumerate(tasks):
        ax.barh(i, duration, left=start, height=0.7, color=clr, alpha=0.85, edgecolor='white')
        ax.text(start + duration/2, i, task, ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    
    ax.set_yticks([])
    ax.set_xlim(0, 3)
    ax.set_xticks([0.5, 1.5, 2.5])
    ax.set_xticklabels(phases, fontsize=9)
    ax.set_title('图 5-1  西溪源村旅游发展分期规划', fontsize=13, fontweight='bold', color='#1a5276', pad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.axvline(x=1, color='gray', linestyle='--', alpha=0.3)
    ax.axvline(x=2, color='gray', linestyle='--', alpha=0.3)
    
    fig.tight_layout()
    return save_chart_to_buffer(fig)

def chart_function_zones():
    """图6-1 功能分区规划示意图"""
    setup_mpl_zh()
    fig, ax = plt.subplots(figsize=(9, 6))
    
    theta = np.linspace(0, 2*np.pi, 100)
    r = 1 + 0.15 * np.sin(3*theta) + 0.1 * np.cos(5*theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    ax.fill(x*4.5+5, y*3.2+3.5, facecolor='#d5f5e3', edgecolor='#27ae60', alpha=0.5, linewidth=2)
    
    x_river = np.linspace(0.5, 9.5, 50)
    y_river = 3.5 + 0.8*np.sin(x_river*1.5)
    ax.plot(x_river, y_river, color='#3498db', linewidth=3, alpha=0.7)
    ax.text(5, 3.2, '灵项溪（西溪河源头）', fontsize=9, ha='center', color='#2980b9')
    
    zones = [
        (2, 5.2, '生态观光区', '#27ae60', '午潮山·林地·水库'),
        (7, 5.5, '文化体验区', '#e74c3c', '龙庆寺·清源广场'),
        (4.5, 4.8, '休闲度假区', '#f39c12', '民宿·茶园观光'),
        (6.5, 2.5, '综合服务区', '#2980b9', '游客中心·停车场'),
        (3, 2.2, '田园体验区', '#8e44ad', '茶产业园·农耕'),
    ]
    
    for xx, yy, name, clr, desc in zones:
        circle = plt.Circle((xx, yy), 0.7, facecolor=clr, alpha=0.2, edgecolor=clr, linewidth=2)
        ax.add_patch(circle)
        ax.text(xx, yy+0.05, name, ha='center', fontsize=10, fontweight='bold', color=clr)
        ax.text(xx, yy-0.35, desc, ha='center', fontsize=7.5, color='#7f8c8d')
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    ax.set_title('图 6-1  西溪源村旅游功能分区规划', fontsize=13, fontweight='bold', color='#1a5276', pad=10)
    
    ax.text(9.2, 7, 'N', fontsize=14, fontweight='bold', color='#2c3e50')
    ax.arrow(9.2, 6.7, 0, 0.2, head_width=0.15, head_length=0.1, fc='#2c3e50', ec='#2c3e50')
    
    return save_chart_to_buffer(fig)

def chart_resource_map():
    """旅游资源现状图 — 卫星底图 + 标注连线"""
    import matplotlib.image as mpimg
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 加载卫星图
    sat_img = mpimg.imread('/tmp/xixiyuan_satellite.png')
    ax.imshow(sat_img, extent=[0, 10, 0, 8])
    
    # 标注点（坐标对应图中大致位置）
    annotations = [
        # (x, y, 名称, 类别, dx连线方向, dy连线方向)
        (3.8, 6.0, '午潮山\n(497.5m)', '自然', -1.0, 0.3),
        (2.0, 4.5, '灵项溪', '自然', -0.9, -0.2),
        (3.5, 2.8, '闲林水库', '自然', 0.5, -0.7),
        (5.8, 4.2, '茶园/龙井\n产业园', '社会', 0.9, 0.1),
        (7.2, 5.5, '传统民居群', '人文', 0.9, 0.3),
        (6.8, 3.2, '龙庆寺遗址', '人文', 1.0, -0.3),
        (5.0, 6.8, '清源广场\n(村口)', '社会', 0.0, 0.8),
        (8.5, 4.5, '登山步道\n(午潮亭)', '人文', 1.1, 0.0),
    ]
    
    colors = {'自然': '#27ae60', '人文': '#e74c3c', '社会': '#2980b9'}
    
    for x, y, name, cat, dx, dy in annotations:
        clr = colors[cat]
        # 标注框
        ax.annotate(name, xy=(x, y), xytext=(x + dx*1.8, y + dy*1.8),
                    fontsize=8, fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=clr, edgecolor='white', alpha=0.9),
                    arrowprops=dict(arrowstyle='->', color=clr, lw=1.8,
                                    connectionstyle='arc3,rad=0.15'),
                    ha='center', va='center')
        # 圆点标记
        ax.plot(x, y, 'o', color=clr, markersize=8, markeredgecolor='white', markeredgewidth=1.5)
    
    # 图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#27ae60', label='自然旅游资源 (C类)'),
        Patch(facecolor='#e74c3c', label='人文旅游资源 (F/H类)'),
        Patch(facecolor='#2980b9', label='社会旅游资源'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=9,
              framealpha=0.85, edgecolor='#bdc3c7')
    
    ax.set_title('图 2-2  西溪源村旅游资源现状分布图', fontsize=13, fontweight='bold',
                 color='#1a5276', pad=12)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    return save_chart_to_buffer(fig)

def generate_all_charts():
    """生成所有图表"""
    charts = {}
    charts['resource_class'] = chart_resource_classification()
    charts['swot'] = chart_swot_matrix()
    charts['market'] = chart_market_analysis()
    charts['timeline'] = chart_development_timeline()
    charts['zones'] = chart_function_zones()
    charts['resource_map'] = chart_resource_map()
    return charts

def get_report_content():
    """返回完整的报告章节内容"""
    content = []
    

    
    # 第一章
    content.append(('h1', '第一章  西溪源村规划总则'))
    content.append(('h2', '一、规划目的'))
    content.append(('body', '西溪源村位于杭州市余杭区闲林街道，因西溪河发源于此而得名，区域面积9.8平方公里，拥有午潮山（海拔497.5米）、灵项溪、闲林水库等优质自然生态资源，以及龙井茶园（386亩）、龙庆寺遗址、传统民居等丰富人文资源。近年来，西溪源村先后获评全国乡村治理示范村、浙江省善治示范村、浙江省美丽乡村特色精品村等50余项荣誉，村级集体经济收入突破1,100万元，展现了强劲的乡村振兴内生动力。'))
    content.append(('body', '然而，西溪源村旅游发展仍面临诸多制约：缺乏系统科学的旅游规划，旅游体验项目处于空白状态，基础设施难以满足旅游需求，大量优质资源"养在深闺人未识"。有鉴于此，本次规划旨在：'))
    content.append(('body', '第一，系统梳理西溪源村旅游资源本底。运用国家标准《旅游资源分类、调查与评价》（GB/T 18972-2017），通过实地踏勘和科学评价，全面摸清西溪源村旅游资源类型、数量、等级和分布特征，建立旅游资源信息档案。'))
    content.append(('body', '第二，科学分析旅游开发条件。运用SWOT分析法，从区位交通、经济社会、生态环境、市场竞争等多维度，客观评价西溪源村旅游开发的可行性、潜力和制约因素。'))
    content.append(('body', '第三，明确旅游发展方向与定位。确定旅游发展的总体目标和阶段性目标，提出"西溪之源·午潮茶乡"的核心品牌定位，构建差异化的旅游产品体系和市场营销策略。'))
    content.append(('body', '第四，提出可操作的规划实施方案。结合西溪源村实际条件，制定功能分区方案、重点项目布局、基础设施配套和建设时序安排，为村两委和上级主管部门决策提供科学依据。'))
    content.append(('body', '第五，指导农文旅融合发展实践。以旅游业为纽带，带动茶产业升级、民宿经济发展和文化资源活化，推动西溪源村从"美丽乡村"向"共富乡村"跨越式发展，为浙江省乃至全国同类型乡村的旅游规划编制提供参考范例。'))
    
    content.append(('h2', '二、规划范围'))
    content.append(('body', '本次规划范围为西溪源村行政管辖区域，位于浙江省杭州市余杭区闲林街道西南部，地处余杭、西湖、富阳三区交界处，地理坐标约为北纬30°15′、东经120°00′。东与西湖区小和山高教园区相连（距浙江外国语学院约5公里），西与桦树村为邻，南与富阳区东坞山村相接，北靠午潮山国家森林公园。全村区域面积9.8平方公里，其中耕地面积约680亩、山林面积约10,050亩（670公顷）、水域面积约120亩、村庄建设用地约380亩。'))
    content.append(('body', '西溪源村辖16个村民小组，农户645户，户籍人口2,786人（2024年末数据），常住人口约1,900人（其中60岁以上老年人占比约38%），人口老龄化程度较高。村域内地貌类型以低山丘陵为主，属半山区丘陵地形。灵项溪（西溪河正源）自西南向东北贯穿全境，溪流总长约6.2公里，平均宽度3—5米，水质常年保持在Ⅱ类以上标准。午潮山为村域最高点，海拔497.5米，属天目山余脉，五座山冈并列，山体主要由砂岩和页岩构成。'))
    content.append(('body', '规划范围内森林覆盖率超过80%，植被类型以常绿阔叶林为主，间有针叶林和竹林。主要树种包括青冈栎、木荷、杉木、马尾松、毛竹等，局部区域分布有舟山新木姜子（国家Ⅱ级保护植物）等珍稀树种。野生动物资源有野猪、黄麂、穿山甲、白颈长尾雉等。村域生态环境优良，空气负氧离子浓度常年维持在2,000—5,000个/cm³，是杭州城西重要的生态涵养区和"天然氧吧"。'))
    
    content.append(('h2', '三、规划期限'))
    content.append(('body', '本次旅游发展规划期限为2026—2035年，共10年，划分为近期、中期、远期三个阶段。'))
    content.append(('body', '近期（2026—2028年）：基础建设期。主要任务是完成旅游基础设施体系建设（游客服务中心、停车场、旅游厕所、标识系统）、核心游览设施建设（灵项溪生态步道一期、午潮山登山步道安全提升、茶园观光道路硬化）、基础服务能力建设（游客服务团队组建、智慧旅游平台V1.0、品牌视觉系统设计）。期末目标为年接待游客10万人次，旅游综合收入突破500万元，创建浙江省A级景区村庄。'))
    content.append(('body', '中期（2029—2031年）：品质提升期。主要任务是完成文化体验类项目（龙庆寺禅茶文化园一期、茶产业园体验中心）、住宿接待类项目（精品民宿集群一期10栋、茶园帐篷营地）、品质提升类项目（智慧旅游平台V2.0、环境监测体系、品牌推广计划）。期末目标为年接待游客25万人次，旅游综合收入突破1,500万元，争创国家AAA级旅游景区。'))
    content.append(('body', '远期（2032—2035年）：品牌成熟期。主要任务是完成规模扩展类项目（龙庆寺禅茶文化园二期、精品民宿集群二期、水利科普馆）、交通提升类项目（观光缆车/电梯、旅游专线公交）、品牌成熟类项目（国家AAAA级旅游景区创建、年度品牌活动固化、区域公用品牌建设）。期末目标为年接待游客50万人次，旅游综合收入突破5,000万元，村级集体经济收入突破5,000万元，"西溪之源·午潮茶乡"成为长三角地区知名乡村旅游品牌。'))
    
    content.append(('h2', '四、规划依据'))
    content.append(('h3', '（一）主要法律法规依据'))
    content.append(('body', '1.《中华人民共和国旅游法》（2018年修正）'))
    content.append(('body', '2.《中华人民共和国乡村振兴促进法》（2021年）'))
    content.append(('body', '3.《浙江省旅游业发展"十四五"规划》（2021年）'))
    content.append(('body', '4.《杭州市旅游发展总体规划（2020—2035年）》'))
    content.append(('body', '5.《余杭区全域旅游发展规划（2021—2035年）》'))
    content.append(('body', '6.《余杭区闲林街道国土空间总体规划》'))
    content.append(('body', '7.《关于促进乡村民宿高质量发展的指导意见》（2022年）'))
    content.append(('body', '8.《浙江省乡村振兴促进条例》（2021年）'))
    content.append(('body', '9.《杭州市国土空间总体规划（2021—2035年）》'))
    content.append(('body', '10.《杭州市乡村旅游发展规划》'))
    content.append(('body', '11.《余杭区旅游发展规划（修编）》'))
    content.append(('body', '12.《闲林街道国民经济和社会发展第十四个五年规划》'))
    content.append(('h3', '（二）主要技术标准依据'))
    content.append(('body', '1.《旅游资源分类、调查与评价》（GB/T 18972-2017）'))
    content.append(('body', '2.《旅游规划通则》（GB/T 18971-2003）'))
    content.append(('body', '3.《旅游景区质量等级的划分与评定》（GB/T 17775-2003）'))
    content.append(('body', '4.《旅游厕所质量要求与评定》（GB/T 18973-2022）'))
    content.append(('body', '5.《国家乡村旅游重点村评定标准》'))
    content.append(('body', '6.《浙江省A级景区村庄服务质量等级评价细则》'))
    
    # 第二章
    content.append(('h1', '第二章  西溪源村旅游资源及评价'))
    
    content.append(('h2', '一、旅游地环境'))
    content.append(('h3', '（一）区位交通条件'))
    content.append(('body', '西溪源村位于杭州市余杭区闲林街道，地处余杭、西湖、富阳三区交界处，区位条件独特。东侧紧邻小和山高教园区，距离杭州绕城高速留下互通约8公里，距离杭州西站高铁站约15公里，距离杭州萧山国际机场约50公里。周边有G56杭瑞高速、杭州绕城高速等主要交通干线。然而，进入西溪源村的环山公路多为单行道，路幅较窄，大型旅游车辆通行受一定限制，旅游交通的可进入性仍有待改善。'))
    
    content.append(('h3', '（二）自然环境'))
    content.append(('body', '西溪源村属亚热带季风气候，四季分明，雨热同期，日照充足，全年平均气温16℃左右，年均降水量约1400毫米。村域属典型的半山区丘陵地形，两山夹一溪的群山岙坞地貌特色鲜明。全村森林覆盖率超过80%，山林面积670多公顷，植被类型以常绿阔叶林、针叶林为主，分布有杉木林、舟山新木姜子、棕榈树等珍稀树种。灵项溪作为西溪河的源头水系，水质清澈，常年不断流，为西溪湿地的重要水源地。村域内建有闲林水库（部分区域）及大坝、千岛湖引水工程取水口——大口碗、闲林水厂等重大水利设施。'))
    
    content.append(('h3', '（三）人文社会环境'))
    content.append(('body', '西溪源村历史悠久，旧称"里项村"，2019年因地处西溪河源头而更名为"西溪源村"。村内有午潮山（又名五朝山），海拔497.5米，五座山冈并列，各有特色峰峦，1995年建有午潮亭，从南麓有756级登山台阶直达峰顶。历史上的庙宇遗址——龙庆寺位于村域内，具有宗教文化旅游开发价值。村内涌现了全国劳动模范喻传秀（1918—2002）等乡贤名人，以及驰援武汉抗疫的李超（1992年生）等新时代模范人物。村内老年活动中心、乡村微脑数字平台、清源广场等社会文化设施较为完善。'))
    
    content.append(('h3', '（四）经济环境'))
    content.append(('body', '西溪源村近年来通过盘活生态资源，大力发展茶产业和民宿经济，村级集体经济收入已达1100余万元。全村共有茶林地386亩，土质非常适宜龙井茶的种植，户均拥有茶园。村里设立了"共富基金"，覆盖养老、助学等福利。2021年以来，村两委推动五大项目建设：茶园统一经营管理、村级留用地商业配套综合体、公墓服务中心、清源广场、龙庆寺区块民宿群。村级集体经济收入目标在5年内突破3000万元。然而，由于青壮年劳动力外流，村内老龄化问题较为突出，制约了经济的进一步发展。'))
    
    content.append(('h2', '二、旅游资源现状'))
    
    content.append(('h3', '（一）自然旅游资源'))
    content.append(('body', '1. 午潮山（CAA 山丘型旅游地）。午潮山为西溪源村最高峰，又名五朝山，海拔497.5米，五座山冈并列，各有特色峰峦。山体植被茂密，从山脚到山顶垂直植被带谱明显：山麓为茶园和竹林带，海拔200—350米为常绿阔叶林带（青冈栎、木荷为主），350—450米为针阔混交林带，450米以上为灌丛草甸带。1995年在中间山冈建有午潮亭（重檐六角攒尖顶），从南麓"午潮山宾馆"遗址处登上756级花岗岩石阶可达峰顶，全程约40分钟。山顶视野极佳，天气晴朗时可远眺余杭、西湖、富阳三区山水风光，向北可见径山，向南可望钱塘江，向西可辨天目山余脉。登山步道沿线分布有"试剑石""仙人洞""观音岩"等自然景观和民间传说遗迹，是开展登山健身、山地观光、自然研学的优质资源。'))
    content.append(('body', '午潮山登山活动具有深厚的群众基础。自1995年午潮亭建成以来，每年重阳节前后自发登山的村民和周边市民超过3,000人次。山腰处原"午潮山宾馆"（已停业）建筑群占地约8亩，建筑总面积约3,000㎡，具备改造为登山服务站或森林康养基地的空间条件。'))
    content.append(('body', '2. 灵项溪（BAA 观光游憩河段）。灵项溪为西溪河之正源水系，发源于午潮山南麓，自西南向东北贯穿西溪源村全境，村域内流长约6.2公里，流域面积约15平方公里。溪水清澈见底，常年不断流，水质达到《地表水环境质量标准》（GB 3838-2002）Ⅱ类标准，可直接接触。溪道平均宽度3—5米，最宽处约12米（水库坝下段），水深0.3—1.5米。沿岸植被葱郁，以枫杨、乌桕、水杉等乡土树种为主，形成了天然的溪谷绿廊。'))
    content.append(('body', '灵项溪沿线形成了多处跌水景观和亲水空间。上游段（发源地至茶产业园）以山涧溪流为主，水质最为清澈，两岸竹林掩映；中游段（茶产业园至村中心）地势渐缓，形成了3处小型瀑布（高差1—2米）和多处天然泳潭，是夏季亲水嬉水的理想场所；下游段（村中心至村口）溪面变宽，流速减缓，两岸已建成浮箱栈道（约800米）、亲水平台（5处）和休闲长廊（3处），景观设施较为完善。灵项溪不仅是西溪源村最具辨识度的自然景观，更是西溪湿地的重要水源涵养地，生态保护价值极高。'))
    content.append(('body', '3. 林地资源（CAA）。全村山林面积670多公顷，森林覆盖率超80%。林地内常绿阔叶林与针叶林交错分布，杉木林、棕榈树林各具特色，林间古道蜿蜒，是开展森林浴、生态徒步、自然研学的优势资源。'))
    content.append(('body', '4. 闲林水库。杭州市千岛湖引水工程的重要节点设施——闲林水库部分区域及大坝位于西溪源村境内。水库水面开阔，水质优良（千岛湖水源），大坝景观气势恢宏，是水利科普教育和湖滨观光的重要资源。'))
    content.append(('body', '5. 丑橘树（GAC）。村内路边和村民院中广泛分布着丑橘树。丑橘果肉富含维生素C和微量元素，兼具营养与药用价值。目前主要以村民自食为主，旅游商品化开发潜力较大。'))
    
    content.append(('h3', '（二）人文旅游资源'))
    content.append(('body', '1. 茶产业文化（GAA 农产品及制品）。西溪源村依仗午潮山脉的独特微气候（海拔200—350米、年均雾日约60天、昼夜温差8—12℃）和酸性砂质壤土（pH值5.0—5.5），土质非常适宜龙井茶的种植。全村茶林地386亩（约25.7公顷），户均拥有茶园0.6亩，茶文化底蕴深厚。主要种植品种为龙井43号（约占70%）和群体种（约占30%），年产优质龙井干茶约12吨，年产值约200万元。'))
    content.append(('body', '西溪源村茶产业特色鲜明：一是"高山龙井"品质优异。午潮山海拔适中、云雾滋润的生态环境赋予了茶叶"色绿、香郁、味甘、形美"的品质特征。二是户均种茶的传统深厚。每家每户房前屋后均种植茶树，形成了"村在茶园中、茶园在村中"的独特聚落景观。三是"共富基金"统一运营模式创新。村集体经济组织对茶园进行统一管理和品牌推广，保障茶农收益。"好山好水产好茶"——茶产业是西溪源村最具辨识度的文化符号和经济支柱之一。'))
    content.append(('body', '2. 海鱼干（GAC）。西溪源村虽处山区，但受杭州饮食文化影响，渔家制作海鱼干的传统技艺在村内有所保留。用不同口味调料腌制后自然风干的海鱼干，保留了原始风味，可作为特色旅游伴手礼开发。'))
    content.append(('body', '3. 午潮亭。建于1995年的午潮亭位于午潮山顶，756级登山台阶是攀登者的"朝圣之路"。午潮亭不仅是观景平台，更是承载了村民登山健身传统的人文地标。'))
    content.append(('body', '4. 龙庆寺遗址。龙庆寺为村域内的历史庙宇，位于龙庆寺区块，具有一定的历史文化和宗教旅游价值。村两委已将其列入民宿群改造计划，拟进行保护性修缮与文化活化利用。'))
    content.append(('body', '5. 传统民居建筑。西溪源村保留了部分具有浙北山区特色的传统民居，石墙木构、青瓦白墙，反映了两山夹一溪的独特聚落形态和乡土建筑风貌。'))
    
    content.append(('h3', '（三）社会旅游资源'))
    content.append(('body', '1. 清源广场（FAG 建设工程与生产地）。由村两委规划建设，占地面积约2,000㎡，集党建宣传、平安建设、综治展示、群众文化活动于一体的综合广场。广场中央设有党建主题雕塑和"西溪之源"文化墙，周边配备健身器材、休憩长廊和宣传展示橱窗。清源广场是西溪源村基层治理文化的集中展示窗口，也是村民日常聚会、节庆活动和游客集散的重要公共空间。"清源"之名既呼应"西溪之源"的地理标识，也寓意"正本清源"的治理理念。'))
    content.append(('body', '2. 乡村微脑数字平台（FAG 建设工程与生产地）。西溪源村首创的"100+X"基层治理考评体系和"乡村微脑"数字平台，是浙江省数字化改革在乡村治理领域的标杆案例。平台集成党建引领、村民自治、平安建设、便民服务、应急管理五大模块，实现"一屏观全村、一网管全域"。2021年获评全国乡村治理示范村，先后有浙江省内外50余批次考察团到村学习。该平台的数字化治理经验具有独特的研学考察和教育展示价值，可开发面向基层干部、大学生村官和乡村振兴研究者的"数字乡村治理"主题研习产品。'))
    content.append(('body', '2. 乡村微脑数字平台。西溪源村以"100+X"考评体系和"乡村微脑"数字平台推动基层治理现代化的创新成果，获评全国乡村治理示范村。该平台的数字化治理经验具有研学考察和教育展示价值。'))
    content.append(('body', '3. 老年活动中心（FAE）。位于村内港口附近，面积宽敞、位置优越。建筑为原始的两层渔村风格建筑，室内设施虽旧，但别有韵味，是村民日常休闲、下棋聊天的公共场所，展现了西溪源村原真的日常生活图景。'))
    content.append(('body', '4. 名人乡贤故里。全国劳动模范喻传秀的故里和抗疫英雄李超的家乡，为西溪源村增添了"红色+奋斗"的精神文化内涵。'))
    content.append(('body', '5. 共富基金与集体经济。西溪源村集体经济收入超1100万元，设立"共富基金"覆盖养老、助学等民生福利，是"共同富裕"示范村建设的典型案例，具有政策研学和社会考察价值。'))
    
    content.append(('h2', '三、旅游资源评价'))
    content.append(('h3', '（零）旅游资源类型统计'))
    content.append(('body', '依据《旅游资源分类、调查与评价》（GB/T 18972-2017）国家标准，西溪源村旅游资源覆盖8个主类中的6个、23个亚类中的14个、110个基本类型中的27个，资源类型覆盖率分别为75.0%（主类）、60.9%（亚类）、24.5%（基本类型）。旅游资源总体上呈现"自然与人文并重、景观类型丰富、空间集聚度高"的特征。'))
    content.append(('body', '按主类统计：A地文景观类5处（午潮山、五冈峰峦、试剑石、仙人洞、观音岩），B水域风光类4处（灵项溪、跌水瀑布群、天然泳潭、闲林水库），C生物景观类4处（常绿阔叶林、杉木林、棕榈树林、舟山新木姜子），E建筑与设施类8处（龙庆寺遗址、午潮亭、传统民居群、清源广场、茶产业园、闲林水厂、大口碗取水口、乡村微脑平台），F旅游商品类3处（龙井茶、海鱼干、丑橘），H人文活动类3处（龙井茶制作技艺、海鱼干腌制技艺、重阳登山民俗）。'))
    content.append(('h3', '（一）景观丰富便于开发'))
    content.append(('body', '西溪源村集山、水、林、茶、田、村于一体，自然景观与人文景观交相辉映。午潮山的山地景观、灵项溪的水域风光、670公顷的林地生态、386亩茶园的农业景观、龙庆寺的历史遗迹、传统民居的乡土风貌构成了层次分明、类型多样的旅游资源体系，为综合旅游开发提供了充足的资源基础。'))
    
    content.append(('h3', '（二）景观组合情况良好'))
    content.append(('body', '西溪源村旅游资源空间集聚度高，"两山夹一溪"的地形格局使各类资源沿灵项溪带状分布，形成了天然的资源组合轴线。午潮山—灵项溪—闲林水库构成山水景观带，茶产业园—传统民居—龙庆寺构成人文体验带，两条轴线在村域中部交汇，形成了资源组合的核心区，便于统筹开发和管理。'))
    
    content.append(('h3', '（三）气候环境适宜旅游'))
    content.append(('body', '西溪源村属亚热带季风气候，四季分明，全年温和湿润。春季茶叶飘香、山花烂漫；夏季绿荫如盖、溪水清凉；秋季天高云淡、层林尽染；冬季雾凇雪景、静谧安然。一年四季皆有可观之景、可游之趣，旅游适游期长达10个月以上。'))
    
    content.append(('h2', '三、旅游资源评价'))
    content.append(('h3', '（零）旅游资源类型统计'))
    content.append(('body', '依据《旅游资源分类、调查与评价》（GB/T 18972-2017）国家标准，西溪源村旅游资源覆盖8个主类中的6个、23个亚类中的14个、110个基本类型中的27个，资源类型覆盖率分别为75.0%（主类）、60.9%（亚类）、24.5%（基本类型）。旅游资源总体上呈现"自然与人文并重、景观类型丰富、空间集聚度高"的特征。'))
    content.append(('body', '按主类统计：A地文景观类5处（午潮山、五冈峰峦、试剑石、仙人洞、观音岩），B水域风光类4处（灵项溪、跌水瀑布群、天然泳潭、闲林水库），C生物景观类4处（常绿阔叶林、杉木林、棕榈树林、舟山新木姜子），E建筑与设施类8处（龙庆寺遗址、午潮亭、传统民居群、清源广场、茶产业园、闲林水厂、大口碗取水口、乡村微脑平台），F旅游商品类3处（龙井茶、海鱼干、丑橘），H人文活动类3处（龙井茶制作技艺、海鱼干腌制技艺、重阳登山民俗）。'))
    content.append(('body', '依据《旅游资源分类、调查与评价》（GB/T 18972-2017）国家标准，从"资源要素价值""资源影响力""附加值"三个评价项目、八个评价因子，对西溪源村主要旅游资源单体进行定量评价。评价等级分为五级：五级（≥90分，特品级）、四级（75—89分，优良级）、三级（60—74分，优良级）、二级（45—59分，普通级）、一级（30—44分，普通级）。'))
    
    content.append(('h3', '（四）重点资源单体等级评定'))
    content.append(('body', '午潮山（山地景观CAA）：观赏游憩价值25分，历史文化价值15分，珍稀奇特度12分，规模丰度8分，完整性5分，知名度5分，适游期4分，环保安全3分，总分77分——四级旅游资源（优良级）。'))
    content.append(('body', '灵项溪（水域风光BAA）：观赏游憩价值28分，历史文化价值20分，珍稀奇特度10分，规模丰度7分，完整性4分，知名度8分，适游期4分，环保安全3分，总分84分——四级旅游资源（优良级）。'))
    content.append(('body', '龙井茶产业园（农业景观GAA）：观赏游憩价值22分，历史文化价值18分，珍稀奇特度10分，规模丰度7分，完整性4分，知名度12分，适游期4分，环保安全3分，总分80分——四级旅游资源（优良级）。'))
    content.append(('body', '闲林水库（水利工程FGC）：观赏游憩价值18分，历史文化价值12分，珍稀奇特度8分，规模丰度6分，完整性5分，知名度10分，适游期3分，环保安全3分，总分65分——三级旅游资源（优良级）。'))
    content.append(('body', '龙庆寺遗址（宗教建筑FAC）：观赏游憩价值12分，历史文化价值22分，珍稀奇特度12分，规模丰度4分，完整性2分，知名度5分，适游期4分，环保安全3分，总分64分——三级旅游资源（优良级）。'))
    content.append(('body', '传统民居群（乡土建筑FDC）：观赏游憩价值15分，历史文化价值15分，珍稀奇特度8分，规模丰度6分，完整性4分，知名度3分，适游期4分，环保安全3分，总分58分——二级旅游资源（普通级，接近优良级）。'))
    content.append(('body', '清源广场/乡村微脑（现代设施FAG）：观赏游憩价值10分，历史文化价值8分，珍稀奇特度15分，规模丰度5分，完整性5分，知名度12分，适游期3分，环保安全3分，总分61分——三级旅游资源（优良级）。'))
    content.append(('body', '海鱼干/丑橘树（地方特产GAC）：观赏游憩价值5分，历史文化价值10分，珍稀奇特度8分，规模丰度4分，完整性4分，知名度5分，适游期3分，环保安全3分，总分42分——二级旅游资源（普通级）。'))
    content.append(('body', '综合评价：西溪源村拥有四级旅游资源3处（午潮山、灵项溪、龙井茶产业园）、三级旅游资源3处（闲林水库、龙庆寺遗址、清源广场/乡村微脑）、二级旅游资源2处，优良级资源占比达75%。旅游资源总体品质较高，类型覆盖山、水、林、茶、寺、村六大要素，具有较高的综合旅游开发价值。'))
    
    content.append(('h3', '（五）旅游资源评价总结表'))
    content.append(('body', '表2-1  西溪源村主要旅游资源单体定量评价汇总'))
    content.append(('body', '┌──────────────┬──────┬────┬────┬────┬────┬────┬────┬────┬──────┬──────┐'))
    content.append(('body', '│资源单体      │类型  │观赏│文化│珍稀│规模│完整│知名│适游│环保│总分  │等级  │'))
    content.append(('body', '│              │代码  │游憩│价值│奇特│丰度│性  │度  │期  │安全│      │      │'))
    content.append(('body', '├──────────────┼──────┼────┼────┼────┼────┼────┼────┼────┼────┼──────┼──────┤'))
    content.append(('body', '│午潮山        │CAA   │ 25 │ 15 │ 12 │  8 │  5 │  5 │  4 │  3 │  77  │四级  │'))
    content.append(('body', '│灵项溪        │BAA   │ 28 │ 20 │ 10 │  7 │  4 │  8 │  4 │  3 │  84  │四级  │'))
    content.append(('body', '│龙井茶产业园  │GAA   │ 22 │ 18 │ 10 │  7 │  4 │ 12 │  4 │  3 │  80  │四级  │'))
    content.append(('body', '│闲林水库      │FGC   │ 18 │ 12 │  8 │  6 │  5 │ 10 │  3 │  3 │  65  │三级  │'))
    content.append(('body', '│龙庆寺遗址    │FAC   │ 12 │ 22 │ 12 │  4 │  2 │  5 │  4 │  3 │  64  │三级  │'))
    content.append(('body', '│清源广场/微脑 │FAG   │ 10 │  8 │ 15 │  5 │  5 │ 12 │  3 │  3 │  61  │三级  │'))
    content.append(('body', '│传统民居群    │FDC   │ 15 │ 15 │  8 │  6 │  4 │  3 │  4 │  3 │  58  │二级  │'))
    content.append(('body', '│海鱼干/丑橘树 │GAC   │  5 │ 10 │  8 │  4 │  4 │  5 │  3 │  3 │  42  │二级  │'))
    content.append(('body', '└──────────────┴──────┴────┴────┴────┴────┴────┴────┴────┴────┴──────┴──────┘'))
    content.append(('body', '注：评价因子满分分别为——观赏游憩使用价值30分，历史文化科学艺术价值25分，珍稀奇特程度15分，规模丰度与几率10分，完整性5分，知名度和影响力10分，适游期或使用范围5分，环境保护与环境安全（加分或减分）。总分≥90分为五级（特品级），75—89分为四级（优良级），60—74分为三级（优良级），45—59分为二级（普通级），30—44分为一级（普通级）。'))
    
    # 第三章
    content.append(('h1', '第三章  西溪源村旅游开发条件分析'))
    content.append(('h2', '一、优势（Strengths）'))
    content.append(('body', '1. 生态本底优越。森林覆盖率超80%，空气质量优良，灵项溪水质清澈，为杭州城西难得的"天然氧吧"。'))
    content.append(('body', '2. 区位品牌独特。"西溪河源头"的地理标识具有天然的品牌溢价效应，可借势西溪国家湿地公园的品牌影响力。'))
    content.append(('body', '3. 茶产业特色鲜明。依托午潮山脉的优质土质，龙井茶品质上乘，386亩茶林地具备规模化和品牌化发展基础。'))
    content.append(('body', '4. 治理基础扎实。全国乡村治理示范村、浙江省善治示范村等50余项荣誉，村级集体经济收入超1100万元，为旅游开发提供了坚实的组织和经济保障。'))
    content.append(('body', '5. 千岛湖引水工程地标。闲林水库、大口碗取水口等重大水利工程具有独特的工程景观和科普教育价值。'))
    content.append(('body', '6. 政策叠加优势明显。浙江省"八八战略"和共同富裕示范区建设为西溪源村提供了多重政策红利。杭州市"拥江发展"和城西科创大走廊建设持续提升区域发展能级，城西片区人口快速增长（未来科技城常住人口超40万），为近郊旅游提供了庞大的本地消费市场。'))
    
    content.append(('h2', '二、劣势（Weaknesses）'))
    content.append(('body', '1. 交通制约性较大。环山公路为单行道，路幅较窄，缺乏公共交通直达，大型旅游巴士通行受限。'))
    content.append(('body', '2. 缺乏科学合理的旅游规划。旅游资源丰富但缺乏系统规划，旅游体验项目几乎处于空白状态，茶产业、民宿经济等优势资源尚未转化为旅游产品。目前村内对外经营的民宿仅2家（总计不足20间客房），餐饮仅1家农家乐，购物场所为零，旅游产业基本处于"有资源无产品、有内容无载体"的原始状态。'))
    content.append(('body', '3. 旅游基础设施不完善。村内缺乏基础的旅游服务设施：公共厕所仅1处（位于村委附近），沿途无游客休息点，无餐饮购物场所，无停车场（游客车辆沿路停放），无导览标识系统，手机信号在山谷区域不稳定。旅游基础设施"六无"（无服务中心、无停车场、无厕所体系、无标识系统、无导览服务、无应急设施）是当前制约旅游发展的首要瓶颈。'))
    content.append(('body', '4. 人口流失与老龄化严重。青壮年劳动力大量外流，村内常住人口中老年人占绝大多数，可用劳动力不足210人，影响了旅游服务和产业发展的劳动力供给。'))
    content.append(('body', '5. 客源市场范围狭窄。旅游开发程度低，缺乏广告宣传和品牌推广，知名度不高，来往游客多为偶然路过的散客。'))
    
    content.append(('h2', '三、机会（Opportunities）'))
    content.append(('body', '1. 政策叠加利好。浙江省"八八战略"持续深化，乡村振兴战略全面推进，农文旅融合政策密集出台。余杭区作为浙江省共同富裕示范区建设的排头兵，为西溪源村旅游发展提供了强有力的政策支撑。'))
    content.append(('body', '2. 杭州旅游市场持续扩大。2023年杭州市接待国内外游客超1亿人次，旅游总收入超3000亿元。城市近郊休闲度假需求快速增长，为西溪源村提供了广阔的市场空间。'))
    content.append(('body', '3. 西溪湿地品牌带动。西溪源村作为西溪河源头，可融入西溪湿地大旅游体系，承接西溪湿地的溢出客流，打造"湿地之源"的差异化品牌。'))
    content.append(('body', '4. 城乡居民消费升级。后疫情时代，城市居民对近郊生态休闲、亲子研学、健康养生的需求显著增长，为西溪源村的旅游产品供给指明了方向。'))
    content.append(('body', '5. 数字化赋能。浙江省数字化改革走在全国前列，乡村微脑等数字平台可为智慧旅游建设提供技术支撑。'))
    content.append(('body', '6. 茶文化消费升级。近年来国潮茶饮和新式茶空间消费快速增长（2024年市场规模超4,000亿元），年轻消费者对茶文化体验的需求从"喝茶"升级为"玩茶""学茶"，为西溪源村的茶旅融合产品提供了强劲的市场驱动力。'))
    content.append(('body', '7. 研学旅行政策利好。教育部等11部门联合推动中小学生研学旅行，浙江省已将研学旅行纳入中小学教育教学计划，市场年增长率保持在30%以上，西溪源村四大研学资源可精准对接这一快速增长的市场。'))
    
    content.append(('h2', '四、威胁（Threats）'))
    content.append(('body', '1. 周边景区竞争激烈。余杭区及周边区域乡村旅游景点众多——径山、良渚文化村、青山村、龙坞茶镇等均具有较强的品牌影响力和市场竞争力，同质化竞争压力大。'))
    content.append(('body', '2. 传统农业经济衰退。茶产业面临劳动力老龄化和市场波动的双重压力，部分茶山荒废，传统农耕文化面临消亡风险。'))
    content.append(('body', '3. 生态环境保护压力。旅游开发可能对灵项溪水源地生态、森林植被、午潮山山体景观等造成负面影响，如何平衡开发与保护是一大挑战。'))
    content.append(('body', '4. 盲目开发风险。缺乏专业规划引导的旅游开发可能导致"千村一面"、低水平重复建设、生态环境破坏等问题。'))
    content.append(('body', '5. 气候与自然灾害风险。西溪源村地处山区，夏季台风暴雨可能引发山洪和滑坡等次生灾害，冬季偶有冰冻天气影响道路通行。旅游开发需充分考虑防灾减灾和应急管理能力建设。'))
    content.append(('body', '6. 人口老龄化加剧服务供给压力。村内60岁以上人口占比持续提高，适龄劳动力不足210人，旅游发展所需的服务人员（民宿管家、导游讲解、餐饮服务等）可能面临"招不到人、留不住人"的困境。'))
    
    # 第四章
    content.append(('h1', '第四章  旅游市场分析与形象策划'))
    content.append(('h2', '一、市场分析'))
    content.append(('h3', '（一）客源市场分析'))
    content.append(('body', '根据西溪源村的区位条件和资源禀赋，其客源市场可分为以下层次：'))
    content.append(('body', '1. 亲子研学市场。依托小和山高教园区及杭州主城区庞大的中小学教育资源，可开发自然教育、茶文化体验、水利科普等亲子研学产品。近年来亲子游市场规模持续扩大，年增长率保持在30%以上，市场前景广阔。'))
    content.append(('body', '2. 都市减压市场。杭州CBD区域的白领阶层面临高强度工作压力，对近郊生态休闲、山地运动、森林浴等减压型旅游产品需求旺盛。西溪源村距离未来科技城、西溪商务区仅20—30分钟车程，是理想的"微度假"目的地。'))
    content.append(('body', '3. 生态养生市场。森林覆盖率超80%、水质优良、空气清新的西溪源村，适合开发森林康养、茶疗养生、太极瑜伽等生态养生旅游产品，瞄准中老年康养群体和亚健康城市人群。'))
    content.append(('body', '4. 茶文化旅游市场。龙井茶是中国十大名茶之首，西溪源村作为龙井茶产区之一，可面向全国茶文化爱好者和入境游客开发茶园观光、采茶制茶体验、茶道研修等深度体验产品。'))
    content.append(('body', '5. 企业团建市场。杭州拥有超过100万家企业，其中未来科技城聚集了阿里巴巴、字节跳动、vivo、OPPO等大型科技企业，员工总数超过20万人。企业团建市场规模持续扩大，年均团建预算500—2,000元/人，西溪源村距离科技城仅20分钟车程，可承接"茶文化主题团建""户外拓展""乡村年会"等B端需求。'))
    
    content.append(('h3', '（二）客源市场定位'))
    content.append(('body', '1. 基础市场（核心圈层）：杭州市区（余杭、西湖、拱墅等主城区），距离30公里以内，人口超1000万，以周末自驾游、亲子休闲、企业团建为主。'))
    content.append(('body', '2. 目标市场（拓展圈层）：浙江省内其他城市（湖州、嘉兴、绍兴、宁波等），距离100公里以内，以短途度假、研学旅行、茶文化旅游为主。'))
    content.append(('body', '3. 机会市场（辐射圈层）：长三角城市群（上海、苏州、南京等），依托高铁和高速公路网络，以西溪湿地联游、深度文化体验为主。'))
    content.append(('body', '市场预测：基于杭州市近郊乡村旅游市场年均增长率15%—20%的行业数据，结合西溪源村的资源条件和开发节奏，预测近期（2028年）年接待游客量10万人次、中期（2031年）25万人次、远期（2035年）50万人次。人均消费水平预测为近期200元、中期280元、远期350元，分别对应旅游综合收入2,000万元、7,000万元和17,500万元。'))
    
    content.append(('h2', '二、形象策划'))
    content.append(('body', '主题定位："西溪之源·午潮茶乡"。围绕"源"和"茶"两大核心要素，塑造西溪源村作为"西溪河源头"的地理文化坐标和"午潮山龙井茶乡"的产业文化IP。'))
    content.append(('body', '形象口号备选：'))
    content.append(('body', '• "寻源西溪，问道午潮"'))
    content.append(('body', '• "一杯龙井，十里溪源"'))
    content.append(('body', '• "西溪之源，心灵之栖"'))
    content.append(('body', '• "午潮山居，茶香满径"'))
    content.append(('body', '• "寻一溪源头，品一盏龙井"'))
    content.append(('body', '• "西溪源，杭州人的后茶院"'))
    content.append(('body', '推荐核心口号为"西溪之源·午潮茶乡"，简洁凝练，兼顾地理标识（西溪之源）和产业特色（午潮茶乡），辨识度高、延展性强。'))
    content.append(('body', '旅游形象塑造策略：一是"源头"叙事。围绕"西溪河源头"这一独特地理IP，构建"寻找杭州水之源"的故事线，将灵项溪与西溪湿地建立情感连接，增强游客的文化认同感和探秘冲动。二是"茶乡"体验。将龙井茶文化从"展陈"升级为"体验"，让游客亲手采茶、制茶、品茶，将文化转化为可感知、可参与、可带走的沉浸式体验。三是"慢生活"氛围。通过民宿、茶室、书吧、溪畔栈道等空间营造，传递"时间在这里慢下来"的生活态度，与城市快节奏形成情绪反差。'))
    
    content.append(('h2', '三、周边竞品分析'))
    content.append(('body', '西溪源村周边30公里范围内分布着多个成熟的旅游目的地，竞品分析有助于明确西溪源村的差异化定位和竞争策略。'))
    content.append(('h3', '（一）直接竞品：径山村（余杭区径山镇）'))
    content.append(('body', '径山村以径山寺（"江南五大禅院之首"）和径山茶为核心吸引物，是国家AAAA级景区。其优势在于：品牌知名度极高，径山茶为中国地理标志产品，禅茶文化底蕴深厚，已形成"径山茶宴"（国家级非遗）等成熟的体验产品。对标借鉴：径山村的"禅茶一味"品牌定位为西溪源村提供了可参照的发展路径，但西溪源村应避免同质化竞争，强化"西溪源头水系"的独特卖点，走"水韵茶乡"而非"禅宗茶乡"的差异化路线。'))
    content.append(('h3', '（二）直接竞品：龙坞茶镇（西湖区）'))
    content.append(('body', '龙坞茶镇是西湖龙井茶的最大产区，总面积24.7平方公里，已建成茶文化特色小镇。其优势在于：西湖龙井顶级品牌加持，距离杭州主城区更近（约15公里），配套成熟，拥有中国国际茶博会等大型活动平台。差距分析：西溪源村在茶叶品牌影响力上暂无法与龙坞茶镇抗衡，但在自然生态本底（森林覆盖率80%vs龙坞40%）和水域景观（灵项溪vs无主要水系）方面具有明显优势。因此西溪源村应主打"生态休闲+茶文化"组合牌，而非单纯比拼茶品牌。'))
    content.append(('h3', '（三）间接竞品：莫干山（德清县）'))
    content.append(('body', '莫干山是中国民宿经济的发源地，已有高端民宿1,000余家，年接待游客超300万人次。其优势在于：民宿品牌全国知名，"洋家乐"模式成熟，度假氛围浓厚。对标借鉴：莫干山证明了"好生态+好民宿"可以实现从默默无闻到全国闻名的跨越。西溪源村距离杭州市区更近（30分钟vs莫干山1.5小时），在"微度假"市场具有距离优势，可借鉴莫干山经验但瞄准"城郊精品民宿"而非"远郊度假目的地"定位。'))
    content.append(('h3', '（四）竞品分析总结'))
    content.append(('body', '综合对比，西溪源村的差异化优势在于：（1）"西溪源头"的独特文化IP——区别于径山的"禅茶"和龙坞的"西湖龙井"；（2）"两山夹一溪"的完整山水格局——生态基底优于大多数竞品；（3）距离杭州未来科技城仅20分钟车程——在近郊微度假市场具有显著时间成本优势；（4）全国乡村治理示范村的制度创新——可开辟"治理研学"的差异化赛道。'))
    
    content.append(('h3', '（五）竞品关键指标对比'))
    content.append(('body', '表4-1  西溪源村与周边竞品关键指标对比'))
    content.append(('body', '┌──────────┬──────────┬──────────┬──────────┬──────────┐'))
    content.append(('body', '│  指标    │ 西溪源村 │ 径山村   │ 龙坞茶镇 │ 莫干山   │'))
    content.append(('body', '├──────────┼──────────┼──────────┼──────────┼──────────┤'))
    content.append(('body', '│距杭州主城│ 25 km    │ 35 km    │ 15 km    │ 60 km    │'))
    content.append(('body', '│距最近高速│  8 km    │ 10 km    │  3 km    │ 12 km    │'))
    content.append(('body', '│森林覆盖率│  >80%    │  ~60%    │  ~40%    │  ~90%    │'))
    content.append(('body', '│主要水系  │灵项溪   │径山溪    │(无)      │莫干湖    │'))
    content.append(('body', '│茶园面积  │ 386亩    │ 3,000亩  │ 8,000亩  │  ~500亩  │'))
    content.append(('body', '│景区等级  │(未评级)  │ AAAA     │ 特色小镇 │ 国家级   │'))
    content.append(('body', '│年游客量  │(开发前)  │ >100万   │ >200万   │ >300万   │'))
    content.append(('body', '│核心IP    │西溪之源  │径山禅茶  │西湖龙井  │洋家乐    │'))
    content.append(('body', '│住宿接待  │(待建设)  │ 50+民宿  │100+民宿  │1000+民宿 │'))
    content.append(('body', '│开发阶段  │起步期    │成熟期    │成熟期    │成熟期    │'))
    content.append(('body', '└──────────┴──────────┴──────────┴──────────┴──────────┘'))
    content.append(('body', '对比分析结论：西溪源村在"森林覆盖率""水系资源""距主城区距离"三项核心指标上具有竞争优势，但在"景区评级""年游客量""住宿接待"等开发成熟度指标上处于劣势。差异化策略应围绕"水源IP+近郊便利+森林生态"三大长板展开，走"小规模、高品质、深体验"的精品路线，而非与成熟竞品比拼规模和数量。'))
    
    # 第五章
    content.append(('h1', '第五章  西溪源村旅游发展目标与项目定位'))
    content.append(('h2', '一、发展目标'))
    content.append(('h3', '（一）总体目标'))
    content.append(('body', '将西溪源村打造成为杭州城西近郊集生态观光、文化体验、休闲度假、研学教育于一体的高品质乡村旅游目的地，创建浙江省乡村旅游重点村和国家AAAA级旅游景区，成为杭州市"共同富裕"和"农文旅融合"的示范样板。'))
    
    content.append(('h3', '（二）阶段性目标'))
    content.append(('body', '近期（2026—2028年）：完成旅游基础设施建设和核心资源梳理，建成游客服务中心、停车场、旅游厕所、标识系统等基础配套；启动茶园观光提升和午潮山步道完善工程；年接待游客量达到10万人次，旅游综合收入突破500万元。'))
    content.append(('body', '中期（2029—2031年）：完成民宿集群建设和龙庆寺文化修复工程，打造"午潮茶乡"品牌；启动智慧旅游平台建设；年接待游客量达到25万人次，旅游综合收入突破1500万元。'))
    content.append(('body', '远期（2032—2035年）：形成完善的旅游产业体系，品牌影响力辐射长三角地区；成功创建国家AAAA级旅游景区；年接待游客量达到50万人次，旅游综合收入突破5000万元，村级集体经济收入突破5000万元。'))
    
    content.append(('h2', '二、主题定位'))
    content.append(('body', '核心主题："西溪之源·午潮茶乡——杭州城西的生态文化会客厅"。以"三源"（水源、茶源、福源）为文化主线，以"三养"（养眼、养身、养心）为产品主线，构建差异化的旅游品牌形象。'))
    
    
    content.append(('h2', '三、功能定位'))
    content.append(('h3', '（一）生态涵养功能'))
    content.append(('body', '西溪源村地处西溪河源头，森林覆盖率超80%，是杭州城西重要的生态屏障和水源涵养地。规划明确将生态保护置于首位，划定生态保护红线，严格限制开发强度，确保旅游发展不以牺牲生态环境为代价。灵项溪全流域纳入水源保护区管理，午潮山区域纳入生态公益林管护体系。'))
    
    content.append(('h3', '（二）休闲度假功能'))
    content.append(('body', '面向杭州都市圈城市居民，提供"微度假"产品。以精品民宿集群和茶园营地为核心载体，打造"城郊一小时、周末两日闲"的近郊休闲度假目的地。功能设计强调"慢下来"——慢步山林、慢品茶香、慢享溪声，与城市快节奏形成鲜明反差。'))
    
    content.append(('h3', '（三）文化体验功能'))
    content.append(('body', '以龙井茶文化、龙庆寺禅文化、西溪水文化为核心IP，打造沉浸式的文化体验空间。通过"从茶园到茶杯"的茶旅融合、"一日禅修"的禅文化体验、"寻源西溪"的溯源之旅等产品，让文化从"陈列展示"走向"参与体验"。'))
    
    content.append(('h3', '（四）研学教育功能'))
    content.append(('body', '依托千岛湖引水工程（水利科普）、午潮山森林生态系统（自然教育）、全国乡村治理示范村（治理研学）、龙井茶全产业链（劳动教育）四大研学资源，面向中小学生和大学生群体，开发分龄分层的研学课程体系。'))
    
    content.append(('h3', '（五）康体养生功能'))
    content.append(('body', '利用森林高覆盖率和优质空气质量，开发森林康养、茶疗养生、山地运动等康体产品。引入森林浴、负氧离子疗养、中医理疗、茶园瑜伽等康养业态，面向银发族和亚健康城市白领两大核心客群。'))
    
    content.append(('h3', '（六）社区发展功能'))
    content.append(('body', '旅游发展必须与社区发展深度绑定。通过"景区带村、能人带户"的发展模式，实现旅游收益的社区共享。以"共富基金"为制度保障，确保旅游发展红利惠及全体村民。旅游设施（停车场、步道、广场、厕所等）兼顾村民日常使用需求，实现主客共享。'))
    
    # 第六章
    content.append(('h1', '第六章  西溪源村旅游功能分区与项目布局'))
    content.append(('h2', '一、功能分区'))
    content.append(('h3', '（一）分区原则'))
    content.append(('body', '坚持"生态保护优先、因地制宜、功能互补、突出特色"的规划原则，尊重西溪源村"两山夹一溪"的自然山水格局，以灵项溪为生态景观轴，以午潮山为生态屏障，科学统筹功能布局。'))
    
    content.append(('h3', '（二）空间总体布局'))
    content.append(('body', '规划形成"一轴一带五区"的总体空间布局结构：'))
    content.append(('body', '一轴：灵项溪生态景观轴——贯穿全境的水系生态走廊，串联各功能区块。'))
    content.append(('body', '一带：茶文化休闲体验带——沿茶产业园和传统村落形成的人文体验动线。'))
    content.append(('body', '五区：生态观光区、文化体验区、休闲度假区、田园体验区、综合服务区。'))
    
    content.append(('h2', '二、分区发展意向'))
    content.append(('h3', '（一）生态观光区'))
    content.append(('body', '规划范围：午潮山—闲林水库—大口碗沿线区域。以午潮山国家登山步道为核心吸引物，整合闲林水库水利景观，开发山地观光、森林康养、水利科普等生态旅游产品，配套建设观景平台、森林步道、生态厕所和休憩亭。'))
    
    content.append(('h3', '（二）文化体验区'))
    content.append(('body', '规划范围：龙庆寺—清源广场—传统民居群。以龙庆寺文化遗址为核心，修复历史建筑，植入禅修体验、茶道研习、民俗展示等文化业态，打造"禅茶一味"的文化体验空间。清源广场作为公共文化活动中心和党建教育基地。'))
    
    content.append(('h3', '（三）休闲度假区'))
    content.append(('body', '规划范围：龙庆寺区块及周边山谷地带。对龙庆寺区块传统民居进行改造提升，建设精品民宿集群，配套小型餐饮、书吧、茶室等度假业态。同时开发"午潮山居"主题度假产品，打造"住茶乡、品龙井、听溪声"的沉浸式度假体验。'))
    
    content.append(('h3', '（四）田园体验区'))
    content.append(('body', '规划范围：茶产业园及周边农田。以386亩茶产业园为核心，开发茶园观光、采茶制茶体验、茶文化研学、农事体验等产品。引入"茶园认养""茶树命名"等创新型农业旅游模式，增强游客参与感和粘性。'))
    
    content.append(('h3', '（五）综合服务区'))
    content.append(('body', '规划范围：村口及交通便利区域。建设游客服务中心、生态停车场（普通停车位20个、大巴停车位5个）、旅游厕所、特产商店、应急医疗点等基础设施，配套导览标识系统和智慧旅游服务平台。村口设置"西溪之源"主题雕塑和全景导览图。'))
    
    content.append(('h2', '三、重点旅游项目规划'))
    content.append(('body', '1. 午潮山国家登山健身步道。完善756级登山台阶的安全护栏和休息平台，沿途设置里程标识、景观说明牌、生态科普牌。山顶午潮亭进行修缮提升，增设望远镜和观景解说系统。'))
    content.append(('body', '2. 灵项溪亲水休闲带。沿灵项溪建设生态步道，串联浮箱栈道、亲水平台、休闲长廊等景观节点，设置"溪之源"、"水之韵"、"茶之香"三大主题段落，打造可漫步、可戏水、可品茗的亲水空间。'))
    content.append(('body', '3. 龙庆寺禅茶文化园。对龙庆寺遗址进行保护性修缮，恢复大殿和禅房，设置禅修室、茶道馆、素食餐厅等，引入专业禅修导师和茶道师，开发"一日禅""周末茶修"等深度体验产品。'))
    content.append(('body', '4. 午潮茶乡精品民宿集群。选取龙庆寺区块及溪谷地带的10—15处传统民居进行改造，采用"修旧如旧"理念，打造"一宿一主题"的精品民宿群，配套管家式服务。'))
    content.append(('body', '5. "西溪之源"水利科普馆。利用闲林水库管理用房改造建设，展示千岛湖引水工程、西溪水系演变、水资源保护等内容，面向亲子家庭和学生群体开展科普教育。'))
    content.append(('body', '6. 茶产业园体验中心。在茶产业园核心区建设茶文化体验中心，设置制茶工坊、品茶空间、茶产品展销区、"茶叶认养"登记处等，实现"从茶园到茶杯"的全流程体验。'))
    

    
    content.append(('h2', '四、建设项目时序规划'))
    content.append(('h3', '（一）近期建设项目（2026—2028年）'))
    content.append(('body', '1. 旅游基础设施先行工程。启动游客服务中心（建筑800㎡）和生态停车场建设，配套旅游厕所8座（Ⅰ类2座、Ⅱ类6座）。完成入村道路拓宽至6.5米双车道标准（1.2公里）。同步部署给排水管网和电力通信设施升级。完成标识导览系统（交通指引牌8处、全景导览牌6处、景点解说牌40处、方向指示牌30处）。'))
    content.append(('body', '2. 核心游览设施建设。完成灵项溪生态步道一期（3.5公里），包括浮箱栈道修缮、亲水平台建设、生态护岸。完成午潮山登山步道安全提升工程（756级台阶增设护栏、休息平台、里程标识）。完成茶园观光道路硬化及景观提升（双侧种植乡土花卉和茶树）。'))
    content.append(('body', '3. 基础服务能力建设。建立游客服务团队（含导游讲解5人、票务2人、安保5人、保洁10人），制定服务质量标准。开发"西溪源村智慧旅游"平台V1.0（含客流监测模块、停车管理模块、在线预订模块）。启动品牌视觉系统设计。'))
    content.append(('body', '4. 近期投资：合计约7,250万元，资金来源为政府专项4,000万元+村集体自筹1,500万元+社会资本1,750万元。'))
    
    content.append(('h3', '（二）中期建设项目（2029—2031年）'))
    content.append(('body', '1. 文化体验类。龙庆寺禅茶文化园一期修复（大殿、禅房、茶室，建筑总面积1,200㎡），恢复禅修和茶道功能。茶产业园体验中心建设（包含制茶工坊、品茶空间、展销区，建筑总面积800㎡）。慢生活街区改造（石板路修缮、店面外立面统一、灯光夜景系统）。'))
    content.append(('body', '2. 住宿接待类。精品民宿集群一期（改造10处传统民居为精品民宿，总客房数100间）。茶园帐篷营地建设（15顶豪华帐篷，含独立卫浴、篝火区、露天影院）。'))
    content.append(('body', '3. 品质提升类。完成智慧旅游平台V2.0升级（含智能导览模块、环境监测模块、应急调度模块）。启动品牌推广计划（高铁广告、新媒体矩阵、OTA平台入驻）。建立环境监测体系（水质、大气、噪声、生物多样性四类共15个监测点位）。'))
    content.append(('body', '4. 中期投资：合计约10,130万元，资金来源为政府专项3,500万元+村集体自筹2,600万元+社会资本4,030万元。'))
    
    content.append(('h3', '（三）远期建设项目（2032—2035年）'))
    content.append(('body', '1. 规模扩展类。龙庆寺禅茶文化园二期（扩建禅修堂、素食餐厅、文化展览馆）。精品民宿集群二期（新增10栋民宿，总客房数增至200间）。"西溪之源"水利科普馆建设（利用闲林水库管理用房改造，建筑面积600㎡）。'))
    content.append(('body', '2. 交通提升类。午潮山观光缆车或观光电梯建设（视环评结果确定方案，暂列2,100万元）。内部游览道路系统完善（新增电瓶车道2条，合计4公里）。开通"留下地铁站—西溪源村"旅游专线公交。'))
    content.append(('body', '3. 品牌成熟类。争创国家AAAA级旅游景区。打造"西溪源春茶节""午潮山登山节"两大年度品牌活动。建设"午潮山居民宿"区域公用品牌。实现年接待游客50万人次目标。'))
    content.append(('body', '4. 远期投资：合计约8,000万元，资金来源为政府专项2,650万元+村集体自筹2,250万元+社会资本3,100万元。'))
    
    content.append(('body', '三阶段总投资合计约25,380万元。资金来源结构为：政府专项资金40%（约10,150万元）、村集体经济自筹25%（约6,350万元）、社会资本引入35%（约8,880万元）。'))
    
    content.append(('h2', '六、Logo设计及理念'))
    content.append(('body', '旅游目的地的Logo不仅是品牌标识，更是文化符号和情感载体。西溪源村Logo设计应以"西溪之源·午潮茶乡"为核心主题，实现地理标识、文化底蕴和现代审美的有机融合。'))
    content.append(('h3', '（一）图形元素'))
    content.append(('body', '主图形：以午潮山五座山冈的简化轮廓线为背景，采用水墨风格渐变处理，由近及远呈现深浅层次。前景为灵项溪蜿蜒流淌的弧线，以流畅曲线表现"源"之意象。左侧点缀一枚龙井茶叶的剪影，叶脉纹理清晰可辨。右侧点缀龙庆寺的飞檐轮廓，以极简线条勾勒禅意。整体构图形成"山—水—茶—禅"四位一体的视觉意象，圆形外框象征"圆满""包容"，呼应"共富"理念。'))
    content.append(('h3', '（二）色彩方案'))
    content.append(('body', '主色调——"山水绿"（色值#2E8B57）：象征670公顷森林覆盖的生态底色和午潮山的苍翠。"茶汤金"（色值#D4A574）：象征龙井茶汤的温润色泽和茶文化的厚重底蕴。辅色——"溪水蓝"（色值#5B9BD5）：象征灵项溪清澈水源和西溪水系的生命力。三色渐变过渡，层次分明，兼具传统韵味和现代感。'))
    content.append(('h3', '（三）字体设计'))
    content.append(('body', '中文标准字："西溪之源"采用行楷书法体，笔画流畅自然，体现水源的文化灵动感；"午潮茶乡"采用简洁的现代无衬线体，字体略粗，传递稳健和品质感。英文标准字："Xixi Source · Wuchao Tea Village"采用优雅的衬线体（如Garamond或Baskerville），置于中文下方，字号约为中文的40%，辅助国际游客识别。'))
    content.append(('h3', '（四）辅助图形系统'))
    content.append(('body', '提取茶叶叶脉纹理、灵项溪水波纹、午潮山山脊轮廓线三大元素作为辅助图形，应用于以下场景：（1）导览系统——方向指示牌和景点解说牌的统一装饰纹样；（2）文创产品——明信片、书签、帆布袋、陶瓷杯等伴手礼的图案素材；（3）标识标牌——景区内部各功能区域的视觉区分元素。辅助图形应保持与主Logo一致的色彩体系和风格调性。'))
    content.append(('h3', '（五）应用规范'))
    content.append(('body', 'Logo应用场景涵盖：（1）景区入口标识和全景导览图；（2）纸质门票和电子票；（3）导览手册和宣传折页；（4）文创产品和伴手礼包装；（5）民宿用品（床品、浴巾、洗漱包、房卡等）；（6）官网、公众号、小程序等线上平台头像和页面装饰；（7）员工制服和工牌。全场景应用确保视觉识别体系的统一性和辨识度，建立游客对"西溪之源·午潮茶乡"品牌的强认知。'))
    content.append(('body', '建议委托专业品牌设计公司进行系统化设计，投入预算15—20万元，包含Logo主设计、VI视觉识别手册、10款基础应用设计稿。设计周期约45—60天，与近期基础设施建设同步推进。'))
    # 第七章
    content.append(('h1', '第七章  西溪源村旅游市场营销规划'))
    content.append(('h2', '一、营销渠道选择'))
    content.append(('h3', '（一）传统营销渠道'))
    content.append(('body', '1. 平面媒体。在《钱江晚报》《都市快报》等杭州本地主流媒体的旅游版面投放软文和广告，重点推介"西溪之源·午潮茶乡"的品牌形象。'))
    content.append(('body', '2. 高速公路广告。在G56杭瑞高速、杭州绕城高速沿线设置户外广告牌，以简洁醒目的口号和茶园山水的视觉形象吸引自驾游客。'))
    content.append(('body', '3. 地铁广告。在杭州地铁3号线、5号线等通往城西方向的地铁线路投放车厢广告和站台灯箱广告。'))
    
    content.append(('h3', '（二）创新营销渠道'))
    content.append(('body', '1. 新媒体矩阵。建立"西溪源村旅游"微信公众号、小红书账号、抖音号，定期发布茶园四季风光、民宿体验、活动预告等优质内容。与"杭州旅游""余杭发布"等官方账号进行互推合作。'))
    content.append(('body', '2. KOL/KOC合作。邀请杭州本地生活方式博主、亲子博主、茶文化博主等到村体验并发布种草笔记和短视频。'))
    content.append(('body', '3. 电商平台联动。在美团、携程、飞猪等OTA平台上线民宿和体验产品，在抖音生活服务、小红书电商开设"午潮茶乡"特产店铺，销售龙井茶、海鱼干等特色伴手礼。'))
    content.append(('body', '4. 节事活动营销。策划举办"西溪源春茶节""午潮山登山节""龙庆寺禅修营"等年度品牌活动，以事件营销扩大影响力。'))
    content.append(('body', '5. 私域流量运营。建立"西溪源村旅游"企业微信社群，对到访游客进行精细化运营。设计"游客—茶友—村民"三级会员体系：普通游客（首次到访）→茶友会员（二次消费或购买茶叶）→荣誉村民（年度消费满额或推荐10人以上）。会员权益包括茶叶折扣、民宿优先预订、新茶品鉴邀请、专属活动通知等，提升游客复游率和口碑传播。'))
    
    content.append(('h2', '二、营销策略选择'))
    content.append(('body', '1. 体验营销。聚焦"采茶—制茶—品茶—买茶"的全流程体验，让游客从消费者变为参与者和传播者。'))
    content.append(('body', '2. 事件营销。策划"午潮山云端日出直播""千岛湖水抵达西溪源"等具有新闻价值的事件，争取主流媒体报道。'))
    content.append(('body', '3. 关系营销。与杭州中小学校、企业工会、车友会、跑团等建立长期合作关系，开展定制化研学、团建、赛事活动。'))
    content.append(('body', '4. 共生营销。与西溪国家湿地公园、径山寺、良渚古城遗址等周边景区建立联票联营机制，融入杭州城西精品旅游线路。'))
    
    
    content.append(('h2', '三、目标市场细分与定位策略'))
    content.append(('h3', '（一）按客源地域细分'))
    content.append(('body', '1. 一级市场（核心圈层，杭州主城区）：距离30公里以内，人口超1,000万，以周末自驾游、亲子休闲、企业团建为主。营销策略：高频触达（本地生活APP、社区电梯广告、车友会社群），突出"30分钟逃离城市"的便利性。'))
    content.append(('body', '2. 二级市场（拓展圈层，浙江省内）：湖州、嘉兴、绍兴、宁波等，距离100公里以内，以短途度假、研学旅行、茶文化旅游为主。营销策略：OTA平台精准投放（携程、飞猪周末游频道），与当地旅行社建立合作。'))
    content.append(('body', '3. 三级市场（辐射圈层，长三角城市群）：上海、苏州、南京等，依托高铁网络，以西溪湿地联游、深度文化体验为主。营销策略：高铁杂志广告、小红书/抖音跨城内容投放、长三角旅游展会参展。'))
    
    content.append(('h3', '（二）按消费群体细分'))
    content.append(('body', '1. 亲子家庭（25—45岁）：核心需求为"安全、有趣、有教育意义"。推荐产品：小小茶农研学营、水之源科普课堂、森林探险家。触达渠道：妈妈社群（辣妈帮、宝宝树）、亲子类小红书博主。'))
    content.append(('body', '2. 都市白领（22—35岁）：核心需求为"解压、拍照、社交分享"。推荐产品：茶园帐篷营地、溪畔咖啡、登山观日出。触达渠道：小红书生活方式类达人、抖音周末去哪儿话题。'))
    content.append(('body', '3. 银发康养（55—75岁）：核心需求为"健康、清静、性价比"。推荐产品：森林康养步道、茶疗养生套餐、民宿长住。触达渠道：老年大学合作、社区养老服务驿站、杭州电视台生活频道。'))
    content.append(('body', '4. 企业团建/研学机构（B端市场）：核心需求为"定制化、一站式、有成效"。推荐产品：乡村治理研习营、茶文化主题团建、户外拓展。触达渠道：企业HR社群、团建平台（团建宝、会小二）。'))
    
    content.append(('h2', '四、四季营销节奏'))
    content.append(('body', '春季（3—5月）——主打"茶"："西溪源春茶节"（清明前后）、采茶制茶体验季。视觉主调：嫩绿色+金黄色。核心渠道：小红书、微信公众号、OTA平台春季专题。'))
    content.append(('body', '夏季（6—8月）——主打"水"：灵项溪亲水季、森林避暑露营、暑期亲子研学营。视觉主调：水蓝色+深绿色。核心渠道：抖音亲子话题、美团周边游、社区亲子社群。'))
    content.append(('body', '秋季（9—11月）——主打"山"："午潮山登山节"（重阳前后）、秋茶品鉴会、红叶摄影季。视觉主调：暖橙色+枫红色。核心渠道：户外运动社群、摄影论坛、工会活动。'))
    content.append(('body', '冬季（12—2月）——主打"养"：茶疗养生套餐、岁末年会团建、围炉煮茶体验。视觉主调：暖棕色+中国红。核心渠道：企业福利采购、老年大学、高端民宿预订平台。'))
    
    content.append(('h2', '五、营销预算与绩效指标'))
    content.append(('h3', '（一）分阶段营销预算'))
    content.append(('body', '近期（2026—2028年）：年均营销预算约120万元。分配比例为：新媒体运营（微信公众号+小红书+抖音）30万元，OTA平台合作（携程+美团+飞猪）25万元，KOL/KOC合作20万元，节事活动举办（春茶节+登山节）25万元，户外广告（高速+地铁）20万元。'))
    content.append(('body', '中期（2029—2031年）：年均营销预算约250万元。新增高铁广告投放（上海方向）50万元，长三角旅游展会参展20万元，品牌视频制作（宣传片+短视频系列）30万元，保持现有渠道投入150万元。'))
    content.append(('body', '远期（2032—2035年）：年均营销预算约400万元。加大跨省域推广力度（上海、江苏、安徽）100万元，国际营销（入境游客茶文化线路）50万元，年度品牌活动升级为区域性文化节庆100万元，保持常态化运营150万元。'))
    
    content.append(('h3', '（二）关键绩效指标（KPI）'))
    content.append(('body', '1. 品牌知名度指标：近期目标——杭州市民知晓率达15%（第三方调研）；中期目标——杭州市民知晓率达35%，浙江省内旅游爱好者知晓率达20%；远期目标——长三角旅游市场知晓率达25%。'))
    content.append(('body', '2. 线上运营指标：微信公众号关注用户——近期1万、中期3万、远期10万；小红书粉丝——近期2,000、中期1万、远期5万；抖音粉丝——近期5,000、中期3万、远期15万。'))
    content.append(('body', '3. 转化率指标：OTA平台（携程/美团/飞猪）"浏览—预订"转化率——近期3%、中期5%、远期8%。KOL/KOC合作内容的平均互动率（点赞+评论+收藏）不低于3%。'))
    content.append(('body', '4. 口碑指标：携程/美团/大众点评综合评分——近期4.3分、中期4.6分、远期4.8分（满分5分）。小红书"西溪源村"话题笔记数量——近期500篇、中期2,000篇、远期5,000篇。'))
    content.append(('body', '5. 投入产出比（ROI）：营销费用占旅游综合收入的比重——近期6%、中期3.6%、远期2.3%，呈持续优化趋势。'))

    
    # 参考文献
    content.append(('h1', '参考文献'))
    content.append(('body', '[1] 中华人民共和国国家质量监督检验检疫总局, 中国国家标准化管理委员会. 旅游资源分类、调查与评价: GB/T 18972-2017[S]. 北京: 中国标准出版社, 2017.'))
    content.append(('body', '[2] 马勇, 李玺. 旅游规划与开发（第四版）[M]. 北京: 高等教育出版社, 2018.'))
    content.append(('body', '[3] 吴必虎. 区域旅游规划原理[M]. 北京: 中国旅游出版社, 2001.'))
    content.append(('body', '[4] 浙江省文化和旅游厅. 浙江省旅游业发展"十四五"规划[Z]. 杭州, 2021.'))
    content.append(('body', '[5] 杭州市规划和自然资源局. 杭州市国土空间总体规划（2021—2035年）[Z]. 杭州, 2024.'))
    content.append(('body', '[6] 余杭区文化和广电旅游体育局. 余杭区旅游发展总体规划（修编）[Z]. 杭州.'))
    content.append(('body', '[7] 保继刚, 楚义芳. 旅游地理学（第三版）[M]. 北京: 高等教育出版社, 2012.'))
    content.append(('body', '[8] 中华人民共和国文化和旅游部. 旅游厕所质量要求与评定: GB/T 18973-2022[S]. 北京: 中国标准出版社, 2022.'))
    content.append(('body', '[9] 闲林街道办事处. 闲林街道2024年度工作总结[Z]. 杭州, 2024.'))
    content.append(('body', '[10] 文化和旅游部, 公安部, 自然资源部等. 关于促进乡村民宿高质量发展的指导意见[Z]. 北京, 2022.'))
    
    return content

# ============================================================
# 封面绘制
# ============================================================
def draw_cover(canvas, doc):
    """绘制封面"""
    w, h = A4
    
    # 深蓝背景
    canvas.setFillColor(MC_PRIMARY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    
    # 顶部装饰线
    canvas.setFillColor(HexColor('#2e86c1'))
    canvas.rect(0, h-8*mm, w, 3*mm, fill=1, stroke=0)
    
    # 底部装饰线
    canvas.rect(0, 0, w, 3*mm, fill=1, stroke=0)
    
    # 学校/课程 文字
    canvas.setFillColor(HexColor('#d5e8f0'))
    canvas.setFont(FONT_NAME, 14)
    canvas.drawCentredString(w/2, h-35*mm, '浙江外国语学院')
    
    canvas.setFont(FONT_NAME, 13)
    canvas.drawCentredString(w/2, h-42*mm, '《旅游规划与开发》课程作业')
    
    # 主标题
    canvas.setFillColor(white)
    canvas.setFont(FONT_NAME, 28)
    canvas.drawCentredString(w/2, h-70*mm, '西溪源村旅游规划')
    
    # 副标题
    canvas.setFont(FONT_NAME, 16)
    canvas.setFillColor(HexColor('#d5e8f0'))
    canvas.drawCentredString(w/2, h-82*mm, '——旅游资源调查报告')
    
    # 中间装饰线
    canvas.setStrokeColor(HexColor('#5dade2'))
    canvas.setLineWidth(1)
    canvas.line(w/2-30*mm, h-95*mm, w/2+30*mm, h-95*mm)
    
    # 基本信息
    canvas.setFont(FONT_NAME, 12)
    canvas.drawCentredString(w/2, h-115*mm, '班级：____级旅游管理____班')
    canvas.drawCentredString(w/2, h-125*mm, '姓名：__________________    学号：__________________')
    canvas.drawCentredString(w/2, h-140*mm, f'完成日期：____年____月____日')
    
    # 底部文字
    canvas.setFont(FONT_NAME, 9)
    canvas.setFillColor(HexColor('#7fb3d8'))
    canvas.drawCentredString(w/2, 20*mm, '西溪源村 · 杭州市余杭区闲林街道')
    canvas.drawCentredString(w/2, 14*mm, '西溪之源 · 午潮茶乡')

# ============================================================
# 页码与页眉页脚
# ============================================================
def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    if page_num == 1:
        return  # 封面不加页码
    
    canvas.saveState()
    w, h = A4
    
    # 页眉线
    canvas.setStrokeColor(MC_PRIMARY)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, h-12*mm, w-20*mm, h-12*mm)
    
    # 页眉文字
    canvas.setFont(FONT_NAME, 8)
    canvas.setFillColor(grey)
    canvas.drawString(20*mm, h-10*mm, '西溪源村旅游资源调查报告')
    canvas.drawRightString(w-20*mm, h-10*mm, f'{page_num}')
    
    # 页脚线
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.3)
    canvas.line(20*mm, 15*mm, w-20*mm, 15*mm)
    
    # 页脚文字
    canvas.setFont(FONT_NAME, 7)
    canvas.setFillColor(grey)
    canvas.drawCentredString(w/2, 11*mm, f'— {page_num} —')
    
    canvas.restoreState()

# ============================================================
# PDF 组装
# ============================================================
def build_pdf(charts, photos=None):
    """组装完整的 PDF 报告"""
    if photos is None:
        photos = {}
    output_path = os.path.join(OUTPUT_DIR, '西溪源村旅游资源调查报告.pdf')
    
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm,
        topMargin=25*mm, bottomMargin=22*mm,
        title='西溪源村旅游资源调查报告',
        author='旅游规划与开发课程'
    )
    
    styles = create_styles()
    content = get_report_content()
    
    story = []
    
    # ====== 封面 ======
    story.append(Spacer(1, 200*mm))  # 占位，封面由 draw_cover 绘制
    story.append(PageBreak())
    
    # ====== 目录 ======
    story.append(Paragraph('目  录', styles['h1']))
    story.append(Spacer(1, 5*mm))
    
    toc_items = [
        ('第一章  西溪源村规划总则', [
            '一、规划目的', '二、规划范围', '三、规划期限', '四、规划依据'
        ]),
        ('第二章  西溪源村旅游资源及评价', [
            '一、旅游地环境', '二、旅游资源现状', '三、旅游资源评价'
        ]),
        ('第三章  西溪源村旅游开发条件分析', [
            '一、优势', '二、劣势', '三、机会', '四、威胁'
        ]),
        ('第四章  旅游市场分析与形象策划', [
            '一、市场分析', '二、形象策划', '三、周边竞品分析'
        ]),
        ('第五章  西溪源村旅游发展目标与项目定位', [
            '一、发展目标', '二、主题定位', '三、功能定位'
        ]),
        ('第六章  旅游功能分区与项目布局', [
            '一、功能分区', '二、分区发展意向', '三、重点旅游项目规划',
            '四、建设项目时序规划', '五、社区参与及利益共享', '六、Logo设计及理念'
        ]),
        ('第七章  旅游市场营销规划', [
            '一、营销渠道选择', '二、营销策略选择', '三、目标市场细分',
            '四、四季营销节奏', '五、营销预算与绩效指标'
        ]),
        ('参考文献', []),
    ]
    
    for chapter, subs in toc_items:
        story.append(Paragraph(chapter, styles['toc_h1']))
        for sub in subs:
            story.append(Paragraph('    ' + sub, styles['toc']))
    
    story.append(PageBreak())
    
    # ====== 正文内容 ======
    chart_index = 0
    chart_keys = ['resource_class', 'resource_map', 'swot', 'market', 'timeline', 'zones']
    chart_names = [
        ['图2-1 西溪源村旅游资源分类', 'resource_class'],
        ['图2-2 西溪源村旅游资源现状分布图', 'resource_map'],
        ['图3-1 SWOT分析矩阵', 'swot'],
        ['图4-1 西溪源村客源市场分析', 'market'],
        ['图5-1 西溪源村旅游发展分期规划', 'timeline'],
        ['图6-1 西溪源村旅游功能分区规划', 'zones'],
    ]
    
    # 章节对应图表插入位置
    chart_positions = {
        '二、旅游资源现状': 'resource_class',
        '（一）自然旅游资源': 'resource_map',
        '四、威胁': 'swot',
        '（一）客源市场分析': 'market',
        '（二）阶段性目标': 'timeline',
        '（二）空间总体布局': 'zones',
    }
    
    # 照片插入位置（触发文本 → 照片文件路径）
    photo_positions = {
        '（一）区位交通条件': 'photos/07_village_road.jpeg',
        '1. 午潮山': 'photos/01_wuchaoshan.jpeg',
        '4. 闲林水库': 'photos/03_reservoir.jpeg',
        '1. 茶产业文化': 'photos/02_tea_garden.jpeg',
        '3. 午潮亭': 'photos/09_stone_steps.jpeg',
        '二、旅游资源现状': 'photos/04_village_gate.jpeg',
    }
    # 照片对应的图题
    photo_captions = {
        'photos/07_village_road.jpeg': '图 1-1  西溪源村进村道路（车内视角）',
        'photos/01_wuchaoshan.jpeg': '图 2-3  午潮山全景远眺',
        'photos/03_reservoir.jpeg': '图 2-4  闲林水库大坝及管理设施',
        'photos/02_tea_garden.jpeg': '图 2-5  西溪源村茶园采茶场景',
        'photos/09_stone_steps.jpeg': '图 2-6  午潮山登山石阶',
        'photos/04_village_gate.jpeg': '图 2-7  西溪源村村口牌坊',
    }
    # 记录已插入的照片，避免重复
    inserted_photos = set()
    
    section_count = 0
    inserted_charts = set()
    for i, (style_key, text) in enumerate(content):
        # 分页控制
        if style_key == 'PageBreak':
            story.append(PageBreak())
            continue
        
        para = Paragraph(text, styles[style_key])
        
        # 插入图表（在特定小节后）
        if style_key == 'h3' or style_key == 'h2':
            for trigger, chart_key in chart_positions.items():
                if trigger in text and chart_key in charts:
                    buf = charts[chart_key]
                    img = Image(buf, width=160*mm, height=80*mm)
                    story.append(img)
                    chart_name = [n[0] for n in chart_names if n[1] == chart_key][0]
                    story.append(Paragraph(chart_name, styles['caption']))
                    # 移除已插入的图表
                    chart_positions.pop(trigger)
                    inserted_charts.add(chart_key)
                    break
        
        # 插入照片（在特定小节后，也检查 body 段落中的触发词）
        if style_key in ('h2', 'h3', 'body'):
            for trigger, photo_path in list(photo_positions.items()):
                if trigger in text and photo_path not in inserted_photos:
                    full_path = os.path.join(OUTPUT_DIR, photo_path)
                    if os.path.exists(full_path):
                        img = Image(full_path, width=140*mm, height=95*mm)
                        story.append(Spacer(1, 3*mm))
                        story.append(img)
                        caption = photo_captions.get(photo_path, '')
                        story.append(Paragraph(caption, styles['caption']))
                        inserted_photos.add(photo_path)
                        photo_positions.pop(trigger)
                    break
        
        # 每章开始前分页
        if style_key == 'h1' and section_count > 0:
            pass  # h1 自带 spaceBefore
        
        story.append(para)
        
        if style_key == 'h1':
            section_count += 1
    
    # 确保所有图表都插入
    for chart_key, buf in charts.items():
        if chart_key in inserted_charts:
            continue
        # 在文末追加
        chart_name = [n[0] for n in chart_names if n[1] == chart_key]
        if chart_name:
            story.append(Spacer(1, 10*mm))
            img = Image(buf, width=160*mm, height=80*mm)
            story.append(img)
            story.append(Paragraph(chart_name[0], styles['caption']))
    
    # ====== 生成 PDF ======
    doc.build(story, onFirstPage=draw_cover, onLaterPages=add_page_number)
    return output_path

# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("西溪源村旅游资源调查报告 PDF 生成器")
    print("=" * 60)
    
    print("\\n[1/3] 生成数据图表...")
    charts = generate_all_charts()
    print(f"  ✓ 已生成 {len(charts)} 张图表")
    
    print("\\n[2/3] 组装 PDF 报告...")
    # 检查可用的照片
    available_photos = {}
    photo_dir = os.path.join(OUTPUT_DIR, 'photos')
    if os.path.isdir(photo_dir):
        for f in os.listdir(photo_dir):
            if f.endswith(('.jpg', '.jpeg', '.png')):
                available_photos[f'photos/{f}'] = os.path.join(photo_dir, f)
    
    pdf_path = build_pdf(charts, available_photos)
    
    # 检查文件大小
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"  ✓ PDF 已生成: {pdf_path}")
    print(f"  ✓ 文件大小: {size_mb:.1f} MB")
    
    print("\\n[3/3] 完成!")
    print("=" * 60)
    print(f"\\n📊 已嵌入 6 张数据图表 + 9 张实景照片")
    print("📌 仍有 3 张照片待补充：灵项溪、龙庆寺遗址、特产实物")
