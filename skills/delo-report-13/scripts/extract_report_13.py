#!/usr/bin/env python3
"""
ДЕЛО ТЕХ — Отчёт №13: Движение по импорту
Автоматический скрипт для извлечения отчёта с rlisystems.ru/conterra/

Использование:
    python3 extract_report_13.py --start 01.08.2026 --end 10.08.2026 --output report.xlsx
"""

import asyncio
import argparse
import sys
from playwright.async_api import async_playwright

# Конфигурация
LOGIN = "pl_11640"
PASSWORD = "Qwerty123"
TERMINAL = "Терминал Врангель"
BASE_URL = "https://rlisystems.ru/conterra/"

# Координаты меню (viewport 1280x1024)
MENU_DOP_USLUGI = (200, 570)
MENU_OTCHETNOST = (150, 700)


async def extract_report(start_date: str, end_date: str, output_file: str):
    """Извлечь отчёт #13 за указанный период"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = await browser.new_page(viewport={'width': 1280, 'height': 1024})
        
        print("[1/6] Открываю сайт...")
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(10)
        
        print("[2/6] Авторизация...")
        await page.evaluate(f"""() => {{
            var inputs = document.querySelectorAll('.v-textfield');
            if(inputs.length >= 2) {{
                inputs[0].value = '{LOGIN}';
                inputs[0].dispatchEvent(new Event('input', {{bubbles:true}}));
                inputs[0].dispatchEvent(new Event('change', {{bubbles:true}}));
                inputs[1].value = '{PASSWORD}';
                inputs[1].dispatchEvent(new Event('input', {{bubbles:true}}));
                inputs[1].dispatchEvent(new Event('change', {{bubbles:true}}));
            }}
            var buttons = document.querySelectorAll('.v-button');
            for(var b of buttons) {{
                if(b.textContent.includes('Вход')) {{ b.click(); break; }}
            }}
        }}""")
        await asyncio.sleep(20)
        
        print("[3/6] Навигация к меню...")
        await page.mouse.click(*MENU_DOP_USLUGI)
        await asyncio.sleep(3)
        await page.mouse.click(*MENU_OTCHETNOST)
        await asyncio.sleep(5)
        
        print("[4/6] Открытие отчёта #13...")
        await page.dblclick('text=13. Движение по импорту')
        await asyncio.sleep(5)
        
        print("[5/6] Установка дат...")
        await page.evaluate(f"""() => {{
            var inputs = document.querySelectorAll('.v-datefield-textfield');
            if(inputs.length >= 2) {{
                inputs[0].value = '{start_date} 00:00';
                inputs[0].dispatchEvent(new Event('change', {{bubbles:true}}));
                inputs[1].value = '{end_date} 23:59';
                inputs[1].dispatchEvent(new Event('change', {{bubbles:true}}));
            }}
        }}""")
        await asyncio.sleep(2)
        
        print("[6/6] Генерация отчёта...")
        await page.evaluate("""() => {
            var buttons = document.querySelectorAll('.v-button');
            for(var b of buttons) {
                if(b.textContent.includes('Показать отчет')) {
                    b.click();
                    return true;
                }
            }
            return false;
        }""")
        await asyncio.sleep(20)
        
        # Скриншот отчёта
        screenshot_path = output_file.replace('.xlsx', '.png')
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Скриншот сохранён: {screenshot_path}")
        
        print("=" * 60)
        print("ОТЧЁТ СГЕНЕРИРОВАН")
        print("=" * 60)
        print(f"Период: {start_date} — {end_date}")
        print(f"Скриншот: {screenshot_path}")
        print()
        print("ВАЖНО: Данные нужно извлечь вручную из скриншота и создать Excel.")
        print("Автоматическое извлечение таблицы из Vaadin 7 невозможно.")
        print()
        print("Колонки отчёта:")
        print("  1. № | 2. Контейнер | 3. ISO тип | 4. Размер | 5. Вместимость")
        print("  6. Вес брутто | 7. Вес нетто | 8. Вес тары | 9. Трафарет")
        print("  10. Порожний | 11. Пломбы | 12. № коносамента")
        print("  13. Порожний как груз | 14. Дата коносамента")
        print("  15. Наименование груза | 16. Грузоотправитель")
        
        await browser.close()
        return screenshot_path


def main():
    parser = argparse.ArgumentParser(description='Извлечь отчёт #13 из ДЕЛО ТЕХ')
    parser.add_argument('--start', required=True, help='Начальная дата (ДД.ММ.ГГГГ)')
    parser.add_argument('--end', required=True, help='Конечная дата (ДД.ММ.ГГГГ)')
    parser.add_argument('--output', default='report_13.xlsx', help='Имя выходного файла')
    
    args = parser.parse_args()
    
    screenshot = asyncio.run(extract_report(args.start, args.end, args.output))
    print(f"\nГотово! Скриншот: {screenshot}")


if __name__ == '__main__':
    main()
