---
name: ux-site-tester
description: |
  UX/UI тестировщик сайтов с проверкой форм, email-рассылок, адаптивности, скорости и автоматическим loop-улучшением.
  Использовать когда пользователь просит протестировать сайт, проверить UX/UI, найти баги,
  или запустить цикл тестирование-исправление-тестирование (loop).
  Триггеры: "протестируй сайт", "проверь формы", "ux тестирование", "проверь email",
  "проверь адаптивность", "тест скорости", "найди баги", "улучши сайт", "loop тестирование".
---

# UX Site Tester

## Описание

Автоматизированное тестирование веб-сайтов с **циклом улучшения**:
1. **Тестирование** — находит проблемы
2. **Анализ** — генерирует actionable отчёт
3. **Исправление** — предлагает или применяет фиксы
4. **Ретест** — проверяет исправления

## Требования

- Python 3.8+
- Playwright
- Доступ к IMAP (Mail.ru)

## Что проверяется

| Проверка | Описание | Уровень |
|----------|----------|---------|
| **Обход страниц** | Все внутренние ссылки | Critical |
| **Битые ссылки** | 404, 500 и другие ошибки | Critical |
| **Формы** | Label, кнопки отправки, обязательные поля | Major |
| **Изображения** | Битые картинки, отсутствие alt-текста | Major/Minor |
| **SEO** | Title, description, H1, robots.txt, sitemap | Major/Minor |
| **Адаптивность** | Desktop, tablet, mobile + скриншоты | Major |
| **Скорость** | Время загрузки | Major |
| **JS ошибки** | Консольные ошибки | Major |
| **i18n / Мультиязычность** | Переключатели, кросс-ссылки, единообразие | Critical/Major |
| **Дублирование** | Повторяющиеся элементы | Major |
| **Мобильное меню** | Единообразие реализации burger-меню | Major |

## Workflow: Loop улучшения

```bash
# 1. Запустить тест
python scripts/site_tester.py --url https://safemind.pro/ru/

# 2. Только проверка 404 (быстрее)
python scripts/site_tester.py --url https://safemind.pro/ru/ --check-404-only

# 3. Проверка с внешними ссылками
python scripts/site_tester.py --url https://safemind.pro/ru/ --check-external

# 4. Проверить i18n / мультиязычность
python scripts/i18n_checker.py --path ./projects/logistoria-website/

# 5. Проанализировать результаты
python scripts/fix_applier.py --report reports/2026-01-01_12-00-00/actionable.json

# 6. Применить исправления (вручную или автоматически)
# Редактируем файлы по fix_plan.json

# 7. Перетестировать
python scripts/site_tester.py --url https://safemind.pro/ru/
```

## Выходные файлы

После теста создаётся папка `reports/YYYY-MM-DD_HH-MM-SS/`:

| Файл | Назначение |
|------|------------|
| `report.md` | Читаемый отчёт для человека |
| `actionable.json` | Структурированные проблемы для AI-обработки |
| `fix_plan.json` | План автоматических исправлений |
| `screenshots/*.png` | Скриншоты адаптивности |

## Структура actionable.json

```json
{
  "url": "https://example.com",
  "total_issues": 5,
  "critical": 1,
  "major": 3,
  "minor": 1,
  "auto_fixable": 2,
  "issues": [
    {
      "id": 1,
      "severity": "critical",
      "category": "forms",
      "title": "Форма без кнопки отправки",
      "location": "order.html — форма #0",
      "fix_suggestion": "Добавить <button type=\"submit\">",
      "auto_fixable": true
    }
  ]
}
```

## Использование

### Полный тест
```bash
python scripts/site_tester.py --url https://safemind.pro/ru/ --email Art_east@internet.ru
```

### Только проверка 404 (быстрый режим)
```bash
python scripts/site_tester.py --url https://safemind.pro/ru/ --check-404-only
```
Проверяет ВСЕ ссылки на сайте через HEAD-запросы. Не загружает страницы полностью — работает быстрее.

### С проверкой внешних ссылок
```bash
python scripts/site_tester.py --url https://safemind.pro/ru/ --check-external
```
По умолчанию внешние ссылки не проверяются.

### Ограничение глубины обхода
```bash
python scripts/site_tester.py --url https://safemind.pro/ru/ --max-pages 100
```

### Проверка мультиязычности (i18n)
```bash
python scripts/i18n_checker.py --path ./projects/logistoria-website/
```

Проверяет:
- Наличие переключателей языков на всех страницах
- Корректность href (EN → `-en.html`, RU → `.html`)
- Активное состояние текущего языка
- Видимость на мобильной версии
- Единообразие стилей
- Кросс-ссылки между языковыми версиями

### Проверка почты
```bash
python scripts/email_checker.py --check-safemind
```

### Применение исправлений
```bash
python scripts/fix_applier.py --report reports/.../actionable.json --dry-run
```

### Генерация PDF
```bash
python scripts/report_generator.py --input report.md --output report.pdf
```

## Переменные окружения

```bash
export TESTER_EMAIL="Art_east@internet.ru"
export TESTER_EMAIL_PASSWORD="your_app_password"
export TESTER_IMAP_SERVER="imap.mail.ru"
```

## Категории проблем

| Категория | Что проверяет |
|-----------|---------------|
| `navigation` | Битые ссылки, 404, 500, таймауты |
| `forms` | Поля, валидация, кнопки |
| `email` | Доставка, формат, вложения |
| `responsive` | Адаптивность, скролл |
| `performance` | Скорость, TTFB |
| `content` | JS ошибки, консоль |
| `seo` | Мета-теги, заголовки |
| `security` | HTTPS, cookie |
| `i18n` | Мультиязычность, переключатели, кросс-ссылки |
| `consistency` | Единообразие UI между страницами |
| `duplicates` | Дублирующиеся элементы |

## Severity levels

- 🔴 **critical** — Блокирует использование
- 🟡 **major** — Ухудшает UX
- 🟢 **minor** — Косметические проблемы

## Auto-fixable проблемы

Скрипт `fix_applier.py` может автоматически предложить исправления для:
- Отсутствующих label в формах
- Отсутствующих кнопок submit
- Битых ссылок
- Отсутствующих meta-тегов
- CSS media queries
- **Неправильных href в языковых переключателях**
- **Дублирующихся nav-langs блоков**
- **Несоответствия стилей между страницами**

## Цикл улучшения (Loop)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Тест      │────▶│   Анализ    │────▶│  Исправление│
│  (site_tester)│    │(fix_applier)│    │  (редакция) │
└─────────────┘     └─────────────┘     └──────┬──────┘
       ▲                                        │
       └────────────────────────────────────────┘
                    (ретест)
```

Каждый цикл генерирует новый отчёт для сравнения прогресса.
