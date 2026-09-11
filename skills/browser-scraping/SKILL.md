---
name: browser-scraping
description: >
  Доступ к сайтам с геоблоком, антибот-защитой или JS-рендерингом через browser automation.
  Использовать когда curl/requests не работает (403, 5xx, пустой ответ), но сайт нужен для смет, нормативов, цен.
  Основной инструмент: browser (OpenClaw/Chromium).
---

# Browser Scraping Skill

## Проблема: Сайт недоступен через curl

| Симптом | Причина | Решение |
|---------|---------|---------|
| `HTTP 403` | Геоблок, WAF, User-Agent фильтр | **Browser** — реальный браузер обходит WAF |
| `HTTP 5xx` | Anti-DDoS, rate limiting | **Browser** — медленнее, но проходит |
| Пустой ответ `<html></html>` | JS-рендеринг (SPA) | **Browser** — ждём загрузки JS |
| Редирект на капчу | Anti-bot | **Browser** — иногда проходит, иначе делегировать |

---

## Методология: 3 шага

### Шаг 1: Проверить curl (быстро)

```bash
curl -s -o /dev/null -w "HTTP: %{http_code}\n" https://example.com
```

- `200` → curl работает, использовать `web_fetch` или requests
- `403/5xx/пустой` → переход к **browser**

### Шаг 2: Открыть через browser

```python
# browser action="navigate"
{
  "action": "navigate",
  "url": "https://fgiscs.minstroyrf.ru/prices"
}
```

**Правила:**
- **Подождать загрузки** — SPA требует 2-5 секунд
- **snapshot** — проверить, что контент появился
- Если капча — **делегировать пользователю**, не пытаться обойти

### Шаг 3: Извлечь данные

**Вариант A: Текстовый контент (snapshot)**
- Смотрим структуру DOM через snapshot
- Кликаем по элементам (раскрытие деревьев, пагинация)
- Читаем таблицы, списки, формы

**Вариант B: Скриншот (screenshot)**
- Если текст сложно распарсить
- Сохранить PNG → дать пользователю или OCR

**Вариант C: PDF/RTF экспорт**
- Если сайт предлагает "Скачать PDF" / "Экспорт RTF"
- Кликнуть по ссылке → файл сохранится в `/tmp/openclaw/`

---

## Проверенные сайты (2026-06-30)

| Сайт | curl | browser | Примечание |
|------|------|---------|------------|
| fgiscs.minstroyrf.ru | ⚠️ SPA | ✅ Полная навигация | JS-дерево, нужно кликать |
| pravo.gov.ru | ❌ 403 | ✅ Документы, экспорт RTF | Геоблок обходится browser |
| gge.ru (PDF) | ❌ 403 | ❌ 403 | **Нужен VPN/прокси РФ** |
| publication.pravo.gov.ru | Не проверено | Не проверено | Предположительно доступен |

---

## Пример: ФГИС ЦС — Индексы

```bash
# 1. Навигация
browser navigate https://fgiscs.minstroyrf.ru/frsn/reference/indexes

# 2. Раскрыть год (клик по 2026)
browser click ref="e30"  # или aria-ref

# 3. Раскрыть квартал (клик по II квартал)
browser click ref="e38"

# 4. Скриншот или snapshot для извлечения таблицы
browser snapshot

# 5. Сравнить с history — если новое письмо, уведомить
```

---

## Пример: pravo.gov.ru — Экспорт приказа

```bash
# 1. Открыть документ
browser navigate "http://pravo.gov.ru/proxy/ips/?nd=602117486"

# 2. Подождать загрузки

# 3. Клик "Экспорт документа в RTF"
browser click ref="e14"

# 4. Файл сохранился в /tmp/openclaw/ — прочитать, проиндексировать
```

---

## Ограничения и этика

- **Капча** — не обходить, делегировать пользователю
- **Логин** — только если пользователь предоставил credentials
- **Rate limiting** — не спамить, делать паузы между запросами
- **Не нарушать ToS** — только публично доступные данные

---

## Использование в других skills

Другие skills импортируют этот через `references/browser-scraping.md` или копируют правила:

```markdown
### Мониторинг нормативов (см. browser-scraping skill)
- ФГИС ЦС: browser automation, раз в месяц
- pravo.gov.ru: browser automation, раз в месяц
- gge.ru: пользователь присылает PDF
```

---

## Файлы

```
browser-scraping/
├── SKILL.md         # Этот файл — правила для LLM
├── README.md        # Документация для пользователя
├── src/
│   └── check_site.sh  # Скрипт проверки curl vs browser
└── docs/
    └── sites.md     # Проверенные сайты со статусами
```

---

*Version: 1.0*
*Created: 2026-06-30*
*Verified: fgiscs.minstroyrf.ru, pravo.gov.ru, gge.ru*