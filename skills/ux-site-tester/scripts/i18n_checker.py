#!/usr/bin/env python3
"""
i18n / Language Consistency Checker
Проверка мультиязычности сайта
"""

import os
import re
import json
import argparse
from pathlib import Path
from urllib.parse import urljoin

class I18nChecker:
    def __init__(self, base_path, base_url=""):
        self.base_path = Path(base_path)
        self.base_url = base_url
        self.issues = []
        self.lang_patterns = {
            'en': '-en.html',
            'es': '-es.html',
            'ru': '.html'  # RU без суффикса
        }
    
    def check_all(self):
        """Запустить все проверки"""
        self.check_language_switchers()
        self.check_cross_language_links()
        self.check_ui_consistency()
        self.check_mobile_menu_consistency()
        self.check_duplicate_elements()
        return self.issues
    
    def check_language_switchers(self):
        """Проверить наличие и корректность переключателей языков"""
        html_files = list(self.base_path.glob('*.html'))
        
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = html_file.name
            
            # Пропускаем страницы без языковой версии (index.html может быть исключением)
            if '-' not in filename and filename != 'index.html':
                continue
            
            # Определяем текущий язык
            current_lang = 'ru'
            for lang, suffix in self.lang_patterns.items():
                if filename.endswith(suffix) and suffix != '.html':
                    current_lang = lang
                    break
            
            # Проверяем наличие переключателей
            lang_links = re.findall(r'<a[^>]*href="([^"]*-(?:en|es)\.html|[^"]*\.html)"[^>]*class="[^"]*nav-link[^"]*"[^>]*>([^<]*)</a>', content)
            
            if not lang_links:
                self.issues.append({
                    'severity': 'major',
                    'category': 'i18n',
                    'title': f'No language switchers found on {filename}',
                    'location': filename,
                    'fix_suggestion': 'Add EN/RU/ES language links in header nav'
                })
            else:
                # Проверяем корректность href
                expected_langs = ['en', 'ru', 'es']
                found_langs = []
                
                for href, text in lang_links:
                    if 'en' in href or text.strip() == 'EN':
                        found_langs.append('en')
                    elif 'es' in href or text.strip() == 'ES':
                        found_langs.append('es')
                    elif text.strip() == 'RU':
                        found_langs.append('ru')
                
                missing = set(expected_langs) - set(found_langs)
                if missing:
                    self.issues.append({
                        'severity': 'major',
                        'category': 'i18n',
                        'title': f'Missing language links on {filename}',
                        'location': filename,
                        'details': f'Missing: {", ".join(missing)}',
                        'fix_suggestion': f'Add links for: {", ".join(missing)}'
                    })
    
    def check_cross_language_links(self):
        """Проверить, что ссылки ведут на правильные языковые версии"""
        html_files = list(self.base_path.glob('*.html'))
        
        # Сопоставление: какая главная какие версии игр должна использовать
        lang_suffixes = {
            'index.html': '-en.html',  # EN главная
            'index-en.html': '-en.html',
            'index-es.html': '-es.html',
            'index-ru.html': '.html',
        }
        
        for html_file in html_files:
            filename = html_file.name
            
            # Определяем ожидаемый суффикс для игр
            expected_suffix = None
            for prefix, suffix in lang_suffixes.items():
                if filename == prefix:
                    expected_suffix = suffix
                    break
            
            if not expected_suffix:
                continue
            
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем ссылки на страницы игр
            game_links = re.findall(r'href="([^"]*(?:storewars|heroes-rack|market-plays|kadena|thebeergame)[^"]*)"', content)
            
            for link in game_links:
                # Проверяем, что ссылка ведёт на правильную языковую версию
                if expected_suffix == '.html':
                    # RU версия должна вести на .html (без суффикса)
                    if '-en' in link or '-es' in link:
                        self.issues.append({
                            'severity': 'critical',
                            'category': 'i18n',
                            'title': f'Wrong language link on {filename}',
                            'location': f'{filename} → {link}',
                            'details': f'RU page links to {link}, should link to RU version',
                            'fix_suggestion': f'Change href to use RU version (without -en/-es suffix)'
                        })
                else:
                    # EN/ES версии должны вести на -en/-es
                    if not link.endswith(expected_suffix):
                        # Проверяем, что это не якорь или внешняя ссылка
                        if not link.startswith('#') and not link.startswith('http'):
                            self.issues.append({
                                'severity': 'critical',
                                'category': 'i18n',
                                'title': f'Wrong language link on {filename}',
                                'location': f'{filename} → {link}',
                                'details': f'Expected suffix {expected_suffix}, got {link}',
                                'fix_suggestion': f'Change href to use {expected_suffix} suffix'
                            })
    
    def check_ui_consistency(self):
        """Проверить единообразие стилей между страницами"""
        html_files = list(self.base_path.glob('*.html'))
        
        # Собираем стили nav-langs / nav-right
        styles = {}
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем стили переключателей
            nav_lang_styles = re.findall(r'\.nav-langs\s*\{([^}]+)\}', content)
            nav_right_styles = re.findall(r'\.nav-right\s*\{([^}]+)\}', content)
            
            if nav_lang_styles:
                styles[html_file.name] = nav_lang_styles[0]
            elif nav_right_styles:
                styles[html_file.name] = nav_right_styles[0]
        
        # Сравниваем стили
        if len(styles) > 1:
            first_style = list(styles.values())[0]
            for filename, style in styles.items():
                if style != first_style:
                    self.issues.append({
                        'severity': 'minor',
                        'category': 'i18n',
                        'title': 'Inconsistent language switcher styles',
                        'location': filename,
                        'details': f'Style differs from reference',
                        'fix_suggestion': 'Unify nav-langs/nav-right CSS across all pages'
                    })
    
    def check_mobile_menu_consistency(self):
        """Проверить единообразие мобильного меню"""
        html_files = list(self.base_path.glob('*.html'))
        
        menu_types = {}
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Определяем тип мобильного меню
            if 'mobile-menu' in content and 'id="mobileMenu"' in content:
                menu_types[html_file.name] = 'mobile-menu-div'
            elif 'nav-links' in content and 'right: -100%' in content:
                menu_types[html_file.name] = 'nav-links-slide'
            else:
                menu_types[html_file.name] = 'unknown'
        
        # Проверяем единообразие
        if menu_types:
            first_type = list(menu_types.values())[0]
            for filename, menu_type in menu_types.items():
                if menu_type != first_type:
                    self.issues.append({
                        'severity': 'major',
                        'category': 'i18n',
                        'title': 'Inconsistent mobile menu implementation',
                        'location': filename,
                        'details': f'Uses {menu_type}, expected {first_type}',
                        'fix_suggestion': 'Unify mobile menu to use mobile-menu div pattern'
                    })
    
    def check_duplicate_elements(self):
        """Проверить наличие дублирующихся элементов"""
        html_files = list(self.base_path.glob('*.html'))
        
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем дублирование nav-langs
            nav_langs_count = content.count('class="nav-langs"')
            if nav_langs_count > 1:
                self.issues.append({
                    'severity': 'major',
                    'category': 'i18n',
                    'title': f'Duplicate nav-langs blocks',
                    'location': html_file.name,
                    'details': f'Found {nav_langs_count} nav-langs blocks',
                    'fix_suggestion': 'Remove duplicate nav-langs div'
                })
            
            # Проверяем дублирование embed.js
            embed_count = content.count('yandex.ru/.../embed.js')
            if embed_count > 1:
                self.issues.append({
                    'severity': 'major',
                    'category': 'forms',
                    'title': f'Duplicate Yandex Form embed scripts',
                    'location': html_file.name,
                    'details': f'Found {embed_count} embed.js references',
                    'fix_suggestion': 'Remove duplicate embed.js script tags'
                })


def main():
    parser = argparse.ArgumentParser(description='i18n Consistency Checker')
    parser.add_argument('--path', default='.', help='Path to HTML files')
    parser.add_argument('--output', default='i18n_report.json', help='Output JSON report')
    args = parser.parse_args()
    
    checker = I18nChecker(args.path)
    issues = checker.check_all()
    
    report = {
        'total_issues': len(issues),
        'critical': len([i for i in issues if i['severity'] == 'critical']),
        'major': len([i for i in issues if i['severity'] == 'major']),
        'minor': len([i for i in issues if i['severity'] == 'minor']),
        'issues': issues
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Check complete. Found {len(issues)} issues.")
    print(f"   Critical: {report['critical']}, Major: {report['major']}, Minor: {report['minor']}")
    print(f"   Report saved to: {args.output}")


if __name__ == '__main__':
    main()
