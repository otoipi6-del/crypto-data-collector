# 🔮 Crypto Data Collector

Полноценная система сбора и анализа крипто-данных из 18 источников: API + парсинг.

## 📁 Структура проекта

```
crypto_data_collector/
├── main.py                          # Главный оркестратор
├── config/
│   └── sources_config.json          # Конфигурация всех источников
├── collectors/                      # API-коллекторы
│   ├── base_collector.py
│   ├── coingecko_collector.py
│   ├── defillama_collector.py
│   ├── alternative_collector.py
│   └── nansen_collector.py
├── parsers/                         # Веб-парсеры
│   ├── coinglass_parser.py
│   ├── token_unlocks_parser.py
│   └── coinmarketcal_parser.py
├── analyzers/                       # Анализатор данных
│   └── crypto_analyzer.py
├── outputs/                         # Сохранённые данные и отчёты
└── tests/                           # Тесты
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Настройка (опционально)

Создайте `.env` файл:
```
COINGECKO_API_KEY=your_key_here      # для paid tier (необязательно)
NANSEN_API_KEY=your_key_here         # для Nansen (необязательно)
PROXY=http://user:pass@proxy:port    # для парсеров (рекомендуется)
```

### 3. Запуск

```bash
python main.py
```

## 📊 Источники данных

### API (бесплатные)
| Источник | Данные | Rate Limit |
|----------|--------|------------|
| **CoinGecko** | Цены, капитализация, история, тренды | 100/мин (free) |
| **DeFi Llama** | TVL, revenue, fees, yields | Безлимитно |
| **Alternative.me** | Fear & Greed Index | Безлимитно |
| **GitHub API** | Коммиты, контрибьюторы | 5000/час |

### API (платные)
| Источник | Данные | Стоимость |
|----------|--------|-----------|
| **Nansen** | Smart Money, wallet profiler | $49-69/мес |

### Парсинг
| Источник | Данные | Сложность |
|----------|--------|-----------|
| **CoinGlass** | Фьючерсы, OI, funding, ETF | 🔴 Сложно |
| **Token Unlocks** | Расписания unlock, vesting | 🟡 Средне |
| **CoinMarketCal** | Календарь событий | 🟢 Просто |
| **CryptoRank** | ICO/IEO, fundraising | 🟡 Средне |
| **IntoTheBlock** | On-chain метрики | 🔴 Сложно |
| **Arkham** | Entity labels, whale tracking | 🔴 Сложно |
| **KyberSwap** | Trending tokens | 🟡 Средне |
| **Token Terminal** | Фундаментальные метрики | 🔴 Сложно |
| **TweetScout** | Twitter аналитика | 🔴 Сложно |
| **OpenOrgs** | Treasury, governance | 🟢 Просто |
| **CryptoMiso** | GitHub активность | 🟢 Просто |
| **CypherHunter** | Профили проектов | 🟢 Просто |
| **Dune** | SQL-аналитика | 🔴 Сложно |

## 📈 Что анализируется

- **Рыночный обзор**: капитализация, доминирование BTC, топ-движения
- **DeFi метрики**: TVL, протоколы, yields, стейблкоины
- **Сентимент**: Fear & Greed Index, тренды
- **Риски**: падения >10%, отток TVL, unlock'и
- **Возможности**: моментум, высокие yields, трендовые токены

## 🛡️ Рекомендации по прокси

Для парсеров рекомендуется использовать резидентные прокси:
- Bright Data
- Oxylabs
- Smartproxy

## 📋 Пример вывода

```
======================================================================
📊 КОМПЛЕКСНЫЙ ОТЧЁТ ПО КРИПТО-РЫНКУ
======================================================================
🕐 Сгенерирован: 2026-06-04T20:15:00
📡 Источники: coingecko, defillama, alternative_me, token_unlocks

📈 РЫНОЧНЫЙ ОБЗОР
----------------------------------------
   💰 Общая капитализация: $2,450,000,000,000
   ₿ BTC доминирование: 52.3%
   🚀 Топ-растущий: PEPE (+45.2%)
   📉 Топ-падающий: LUNA (-23.1%)

⚠️ ОЦЕНКА РИСКОВ
----------------------------------------
   🟡 Уровень риска: Medium (Score: 65/100)
   📋 Факторы риска:
      • Высокий Fear & Greed (>75) — перекупленность

💎 ВОЗМОЖНОСТИ
----------------------------------------
   • Сильный рост PEPE на 45.2%
   • Доходность 23.5% APY в Aave

📋 РЕКОМЕНДАЦИИ
----------------------------------------
   ⚖️ Сохранять текущие позиции, мониторить рынок

🚨 АЛЕРТЫ
----------------------------------------
   ⚡ BTC упал более чем на 5% — повышенная волатильность
```

## 🔧 Расширение

Добавить новый источник:
1. Создать коллектор в `collectors/` или парсер в `parsers/`
2. Добавить конфигурацию в `config/sources_config.json`
3. Добавить метод анализа в `analyzers/crypto_analyzer.py`
4. Подключить в `main.py`

## 📄 Лицензия

MIT License — используйте на свой страх и риск. Уважайте ToS сайтов.
