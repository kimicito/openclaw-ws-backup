# HARNESS.md — UX Site Tester

## Контекст
- **Язык:** Python 3.8+, Playwright
- **Паттерн:** Crawler + Analyzer + Reporter
- **Статус:** Production-ready

## Назначение
Автоматизированное тестирование веб-сайтов с проверкой:
- Всех внутренних ссылок на 404/500
- Форм (label, submit, валидация)
- Изображений (битые, alt-текст)
- SEO (title, description, H1)
- Адаптивности (desktop/tablet/mobile скриншоты)
- Скорости загрузки
- JS-ошибок консоли

## Ключевой метод — проверка 404

### Crawl-mode (по умолчанию)
Обходит сайт, переходя по каждой ссылке. Находит битые страницы, на которые есть ссылки.

### Link-checker mode (усиленный)
Проверяет ВСЕ ссылки на странице через HEAD-запрос, без перехода:
- Быстрее (не загружает страницу полностью)
- Находит 404 даже на страницах, до которых краулер не дошёл
- Проверяет внешние ссылки (опционально)

## Запуск

```bash
# Полный тест
python scripts/site_tester.py --url https://example.com/

# Только проверка 404
python scripts/site_tester.py --url https://example.com/ --check-404-only

# С внешними ссылками
python scripts/site_tester.py --url https://example.com/ --check-external

# i18n проверка
python scripts/i18n_checker.py --path ./site/
```

## Выход
`reports/YYYY-MM-DD_HH-MM-SS/`:
- `report.md` — читаемый отчёт
- `actionable.json` — структурированные проблемы
- `screenshots/*.png` — скриншоты адаптивности

## Severity mapping
| Статус | Severity |
|--------|----------|
| 404 | major |
| 500+ | critical |
| 403 | major |
| Таймаут | critical |

## Флаги командной строки
- `--url` — URL для тестирования (обязательный)
- `--email` — Email для тестирования форм
- `--output`, `-o` — Директория отчёта
- `--check-404-only` — Только проверка битых ссылок
- `--check-external` — Проверять внешние ссылки
- `--max-pages` — Лимит страниц (default: 50)
