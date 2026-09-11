#!/usr/bin/env python3
"""
Report Generator — конвертация Markdown отчёта в PDF
"""

import argparse
import markdown
from pathlib import Path


def md_to_pdf(input_file, output_file):
    """
    Конвертация Markdown файла в PDF.
    Использует markdown -> HTML -> WeasyPrint/PDF
    """
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        print("❌ WeasyPrint не установлен. Установите: pip install weasyprint")
        print("📝 Создаю HTML-версию отчёта...")
        
        # Читаем Markdown
        md_content = Path(input_file).read_text(encoding='utf-8')
        
        # Конвертируем в HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # Добавляем стили
        html_full = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>UX Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #2563eb; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        h2 {{ color: #374151; margin-top: 30px; }}
        h3 {{ color: #4b5563; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #e5e7eb; padding: 12px; text-align: left; }}
        th {{ background: #f3f4f6; font-weight: 600; }}
        code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
        ul, ol {{ margin: 10px 0; padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 30px 0; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        # Сохраняем HTML
        html_path = output_file.replace('.pdf', '.html')
        Path(html_path).write_text(html_full, encoding='utf-8')
        print(f"💾 HTML отчёт сохранён: {html_path}")
        print("📄 Для конвертации в PDF установите WeasyPrint:")
        print("   pip install weasyprint")
        return
    
    # Читаем Markdown
    md_content = Path(input_file).read_text(encoding='utf-8')
    
    # Конвертируем в HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc']
    )
    
    # CSS стили для PDF
    css = CSS(string='''
        @page { size: A4; margin: 2cm; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        h1 { color: #2563eb; font-size: 24px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
        h2 { color: #374151; font-size: 20px; margin-top: 30px; }
        h3 { color: #4b5563; font-size: 16px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #e5e7eb; padding: 12px; text-align: left; }
        th { background: #f3f4f6; font-weight: 600; }
        code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
        ul, ol { margin: 10px 0; padding-left: 20px; }
        li { margin: 5px 0; }
        hr { border: none; border-top: 1px solid #e5e7eb; margin: 30px 0; }
    ''')
    
    # Генерируем PDF
    html_full = f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>UX Test Report</title></head>
<body>{html_content}</body>
</html>"""
    
    HTML(string=html_full).write_pdf(output_file, stylesheets=[css])
    print(f"✅ PDF отчёт сохранён: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Report Generator')
    parser.add_argument('--input', '-i', required=True, help='Входной Markdown файл')
    parser.add_argument('--output', '-o', required=True, help='Выходной PDF файл')
    
    args = parser.parse_args()
    
    md_to_pdf(args.input, args.output)


if __name__ == '__main__':
    main()
