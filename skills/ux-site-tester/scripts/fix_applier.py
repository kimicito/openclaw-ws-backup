#!/usr/bin/env python3
"""
Fix Applier — применение исправлений на основе отчёта тестирования
Читает actionable.json и генерирует патчи или предлагает исправления
"""

import json
import argparse
from pathlib import Path


class FixApplier:
    def __init__(self, report_path):
        self.report_path = Path(report_path)
        self.data = json.loads(self.report_path.read_text(encoding='utf-8'))
        self.fixes = []
    
    def analyze(self):
        """Анализ проблем и генерация исправлений."""
        print(f"🔧 Анализ {self.data['total_issues']} проблем...")
        print(f"   Auto-fixable: {self.data['auto_fixable']}")
        print(f"   Critical: {self.data['critical']}")
        print(f"   Major: {self.data['major']}\n")
        
        for issue in self.data['issues']:
            if issue['auto_fixable']:
                fix = self._generate_fix(issue)
                if fix:
                    self.fixes.append(fix)
            else:
                self._print_manual_fix(issue)
        
        return self.fixes
    
    def _generate_fix(self, issue):
        """Генерация конкретного исправления."""
        fix = {
            'issue_id': issue['id'],
            'title': issue['title'],
            'location': issue['location'],
            'action': None,
            'code': None,
            'files_to_edit': []
        }
        
        category = issue['category']
        
        if category == 'forms':
            if 'без label' in issue['title']:
                fix['action'] = 'add_label'
                fix['description'] = 'Добавить label к полю формы'
                # Парсим location для получения файла
                fix['files_to_edit'] = self._extract_files_from_location(issue['location'])
            
            elif 'без кнопки' in issue['title']:
                fix['action'] = 'add_submit_button'
                fix['description'] = 'Добавить кнопку submit в форму'
                fix['files_to_edit'] = self._extract_files_from_location(issue['location'])
        
        elif category == 'navigation':
            fix['action'] = 'fix_link'
            fix['description'] = 'Исправить или удалить битую ссылку'
            fix['files_to_edit'] = self._extract_files_from_location(issue['location'])
        
        elif category == 'responsive':
            fix['action'] = 'add_media_query'
            fix['description'] = 'Добавить адаптивные стили'
            fix['files_to_edit'] = ['styles.css', 'style.css', 'main.css']
        
        elif category == 'seo':
            fix['action'] = 'add_meta_tags'
            fix['description'] = 'Добавить/исправить мета-теги'
            fix['files_to_edit'] = self._extract_files_from_location(issue['location'])
        
        return fix
    
    def _extract_files_from_location(self, location):
        """Извлечение файлов из location строки."""
        # Пытаемся найти URL и преобразовать в файл
        if 'safemind.pro' in location or '.html' in location:
            # Для HTML страниц — это файлы .html
            if '.html' in location:
                return [location.split('/')[-1]]
            else:
                return ['index.html']
        return ['index.html']  # По умолчанию
    
    def _print_manual_fix(self, issue):
        """Вывод инструкции для ручного исправления."""
        severity_emoji = {'critical': '🔴', 'major': '🟡', 'minor': '🟢'}
        emoji = severity_emoji.get(issue['severity'], '⚪')
        
        print(f"{emoji} #{issue['id']}: {issue['title']}")
        print(f"   Локация: {issue['location']}")
        print(f"   Описание: {issue['description']}")
        print(f"   Исправление: {issue['fix_suggestion']}")
        print()
    
    def generate_fix_plan(self):
        """Генерация плана исправлений."""
        if not self.fixes:
            print("✅ Нет автоматических исправлений для применения.")
            return
        
        print(f"📋 План исправлений ({len(self.fixes)} пунктов):\n")
        
        for i, fix in enumerate(self.fixes, 1):
            print(f"{i}. {fix['title']}")
            print(f"   Действие: {fix['action']}")
            print(f"   Файлы: {', '.join(fix['files_to_edit'])}")
            print()
        
        # Сохраняем план
        plan_path = self.report_path.parent / 'fix_plan.json'
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(self.fixes, f, ensure_ascii=False, indent=2)
        
        print(f"💾 План сохранён: {plan_path}")
    
    def generate_html_patches(self):
        """Генерация HTML-патчей для исправлений."""
        patches = []
        
        for fix in self.fixes:
            if fix['action'] == 'add_submit_button':
                patch = {
                    'action': 'insert_before',
                    'selector': 'form',
                    'html': '<button type="submit">Отправить</button>',
                    'description': 'Добавить кнопку отправки в форму'
                }
                patches.append(patch)
            
            elif fix['action'] == 'add_label':
                patch = {
                    'action': 'insert_before',
                    'selector': 'input:not([type="hidden"]):not([type="submit"])',
                    'html': '<label>{{field_name}}</label>',
                    'description': 'Добавить label к полю ввода'
                }
                patches.append(patch)
        
        return patches
    
    def generate_summary(self):
        """Генерация итогового summary для пользователя."""
        summary = f"""
╔══════════════════════════════════════════╗
║     UX TEST FIX SUMMARY                 ║
╠══════════════════════════════════════════╣
║ URL: {self.data['url'][:40]:40} ║
║ Total Issues: {self.data['total_issues']:28} ║
║ Critical:     {self.data['critical']:28} ║
║ Major:        {self.data['major']:28} ║
║ Minor:        {self.data['minor']:28} ║
║ Auto-fixable: {self.data['auto_fixable']:28} ║
╚══════════════════════════════════════════╝

Рекомендации:
"""
        
        if self.data['critical'] > 0:
            summary += "🔴 Срочно исправить critical issues!\n"
        if self.data['major'] > 0:
            summary += "🟡 Исправить major issues в ближайшем релизе\n"
        if self.data['auto_fixable'] > 0:
            summary += f"🤖 {self.data['auto_fixable']} проблем можно исправить автоматически\n"
        
        summary += "\nДля применения исправлений:\n"
        summary += "1. Откройте fix_plan.json\n"
        summary += "2. Примените изменения в указанных файлах\n"
        summary += "3. Перезапустите тест для проверки\n"
        
        return summary


def main():
    parser = argparse.ArgumentParser(description='Fix Applier')
    parser.add_argument('--report', '-r', required=True, help='Путь к actionable.json')
    parser.add_argument('--dry-run', action='store_true', help='Только показать план, не применять')
    
    args = parser.parse_args()
    
    applier = FixApplier(args.report)
    
    print("=" * 50)
    print("🔧 UX SITE TEST — FIX APPLIER")
    print("=" * 50 + "\n")
    
    # Анализируем проблемы
    applier.analyze()
    
    # Генерируем план
    applier.generate_fix_plan()
    
    # Показываем summary
    print(applier.generate_summary())
    
    if not args.dry_run:
        print("\n⚠️ Для применения исправлений отредактируйте файлы вручную")
        print("   или используйте --dry-run для просмотра плана")


if __name__ == '__main__':
    main()
