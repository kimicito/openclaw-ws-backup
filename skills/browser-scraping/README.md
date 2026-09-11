# Browser Scraping Skill

Доступ к сайтам с геоблоком, антибот-защитой или JS-рендерингом через browser automation (Chromium).

## Проблема

Многие российские государственные сайты (ФГИС ЦС, pravo.gov.ru) блокируют curl/requests, но открываются в браузере:

- **Геоблок** — сервер вне РФ получает 403
- **WAF/anti-bot** — Cloudflare, Sucuri и др.
- **JS-рендеринг** — SPA без SSR (React, Angular)

## Решение

**Browser automation** — OpenClaw управляет Chromium, который обходит геоблок и WAF (реальный User-Agent, cookies, WebGL).

## Проверенные сайты

| Сайт | curl | browser | Примечание |
|------|------|---------|------------|
| [fgiscs.minstroyrf.ru](https://fgiscs.minstroyrf.ru) | ⚠️ SPA | ✅ Полная навигация | JS-дерево документов |
| [pravo.gov.ru](http://pravo.gov.ru) | ❌ 403 | ✅ Документы, экспорт RTF | Геоблок обходится |
| [gge.ru (PDF)](https://gge.ru) | ❌ 403 | ❌ 403 | **Нужен VPN/прокси РФ** |

## Пример использования

```bash
# Проверить через curl
curl -s -o /dev/null -w "HTTP: %{http_code}\n" https://fgiscs.minstroyrf.ru/prices
# → HTTP: 200 (но SPA — контента нет)

# Открыть через browser
browser action="navigate" url="https://fgiscs.minstroyrf.ru/prices"

# Подождать, сделать snapshot
browser action="snapshot"
# → Виден полный контент: дерево индексов, таблицы

# Кликнуть по элементу (раскрыть год)
browser action="act" request="{\"kind\":\"click\",\"ref\":\"e30\"}"
```

## Структура

```
browser-scraping/
├── SKILL.md         # Правила для LLM (когда и как использовать)
├── README.md        # Эта документация
├── src/
│   └── check_site.sh  # Скрипт: curl → browser fallback
└── docs/
    └── sites.md     # Список проверенных сайтов
```

## Интеграция с другими skills

### smeta
```python
# Мониторинг ФГИС ЦС
browser navigate https://fgiscs.minstroyrf.ru/frsn/reference/indexes
# → раскрыть квартал → извлечь индексы → обновить knowledge_base.md
```

### price-comparison
```python
# Сайт поставщика с WAF
browser navigate https://supplier-site.ru/prices
# → скриншот → OCR → извлечь цены
```

## Ограничения

- **Капча** — не обходим, делегируем пользователю
- **Логин** — только если пользователь дал credentials
- **Rate limit** — делать паузы между запросами

---

*Version: 1.0*
*Created: 2026-06-30*
