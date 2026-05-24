#!/usr/bin/env python3
"""将西溪源村旅游规划作业.md转换为排版精美的PDF"""

import markdown
from weasyprint import HTML
import os

# 读取markdown
md_path = "/home/knooe/workspace/西溪源村旅游规划作业.md"
pdf_path = "/home/knooe/workspace/西溪源村旅游规划作业.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# 转换为HTML
md_extensions = ["tables", "fenced_code", "toc", "nl2br", "sane_lists"]
html_body = markdown.markdown(md_content, extensions=md_extensions)

# 完整HTML文档 + 中文字体 + 精美排版
html_full = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 2.5cm 2cm 2.5cm 2cm;
    @bottom-center {{
      content: "— " counter(page) " —";
      font-size: 9pt;
      color: #999;
      font-family: "SimSun", serif;
    }}
  }}
  @page :first {{
    @bottom-center {{
      content: none;
    }}
  }}

  body {{
    font-family: "SimSun", "Noto Serif CJK SC", "Source Han Serif SC", serif;
    font-size: 12pt;
    line-height: 1.8;
    color: #222;
  }}

  /* ===== 封面样式 ===== */
  h1 {{
    text-align: center;
    font-size: 26pt;
    font-weight: bold;
    margin-top: 5cm;
    margin-bottom: 1.5cm;
    font-family: "SimHei", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
    letter-spacing: 8pt;
    border-bottom: 2px solid #333;
    padding-bottom: 0.5cm;
  }}

  blockquote {{
    text-align: center;
    border-left: none;
    margin: 2cm auto;
    padding: 0;
    font-size: 11pt;
    color: #555;
    line-height: 2;
  }}
  blockquote p {{
    margin: 4px 0;
  }}

  /* ===== 章节标题 ===== */
  h2 {{
    font-family: "SimHei", "Noto Sans CJK SC", sans-serif;
    font-size: 18pt;
    font-weight: bold;
    margin-top: 1.5cm;
    margin-bottom: 0.6cm;
    padding-bottom: 4px;
    border-bottom: 2px solid #2d5a27;
    color: #2d5a27;
    page-break-before: always;
  }}
  h2:first-of-type {{
    page-break-before: avoid;
  }}

  h3 {{
    font-family: "SimHei", "Noto Sans CJK SC", sans-serif;
    font-size: 14pt;
    font-weight: bold;
    margin-top: 1cm;
    margin-bottom: 0.4cm;
    color: #3a7a32;
  }}

  h4 {{
    font-family: "SimHei", sans-serif;
    font-size: 12pt;
    font-weight: bold;
    margin-top: 0.6cm;
    margin-bottom: 0.3cm;
    color: #444;
  }}

  h5 {{
    font-family: "SimHei", sans-serif;
    font-size: 12pt;
    font-weight: bold;
    margin-top: 0.5cm;
    margin-bottom: 0.2cm;
  }}

  /* ===== 段落 ===== */
  p {{
    text-indent: 2em;
    margin: 0.3em 0;
  }}
  li p {{
    text-indent: 0;
  }}

  /* ===== 列表 ===== */
  ul, ol {{
    margin: 0.3em 0;
    padding-left: 2em;
  }}
  li {{
    margin: 0.15em 0;
  }}

  /* ===== 表格 ===== */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 0.6cm 0;
    font-size: 10.5pt;
  }}
  th, td {{
    border: 1px solid #888;
    padding: 6px 10px;
    text-align: center;
    vertical-align: middle;
  }}
  th {{
    background-color: #2d5a27;
    color: white;
    font-weight: bold;
    font-family: "SimHei", sans-serif;
  }}
  tr:nth-child(even) {{
    background-color: #f5faf3;
  }}

  /* ===== 重点强调 ===== */
  strong {{
    color: #2d5a27;
  }}
  em {{
    color: #555;
  }}

  /* ===== 水平线 ===== */
  hr {{
    border: none;
    border-top: 1px solid #ccc;
    margin: 1cm 0;
  }}

  /* ===== 代码块 ===== */
  code {{
    font-family: "SimSun", monospace;
    background: #f4f4f4;
    padding: 1px 4px;
    border-radius: 2px;
  }}
  pre {{
    background: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    overflow-x: auto;
    font-size: 10pt;
    line-height: 1.5;
  }}

  /* ===== 脚注 ===== */
  sup {{
    font-size: 0.8em;
  }}

  /* 分隔注释 */
  hr + p em {{
    display: block;
    text-align: center;
    font-size: 9pt;
    color: #999;
    border-top: 1px solid #eee;
    padding-top: 10px;
    margin-top: 1cm;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

# 生成PDF
print("正在生成PDF...")
HTML(string=html_full).write_pdf(pdf_path)

# 输出文件信息
size_kb = os.path.getsize(pdf_path) / 1024
print(f"✅ PDF已生成: {pdf_path}")
print(f"   文件大小: {size_kb:.1f} KB")
