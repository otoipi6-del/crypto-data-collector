"""
CoinMarketCal Parser
Собирает: календарь событий, листинги, обновления
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CoinMarketCalParser:
    """Парсер CoinMarketCal (простой, без JS)"""

    def __init__(self):
        self.base_url = "https://coinmarketcal.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def parse_events(self, page: int = 1) -> List[Dict]:
        """Парсинг событий"""
        logger.info(f"📅 Парсим события (страница {page})...")

        url = f"{self.base_url}/en/?page={page}"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        events = []
        event_cards = soup.find_all('article', class_='card')

        for card in event_cards:
            try:
                title = card.find('h5', class_='card__title')
                coin = card.find('h5', class_='card__coins')
                date = card.find('time')
                category = card.find('span', class_='badge')
                votes = card.find('span', class_='vote-count')

                events.append({
                    "title": title.get_text(strip=True) if title else "N/A",
                    "coin": coin.get_text(strip=True) if coin else "N/A",
                    "date": date.get_text(strip=True) if date else "N/A",
                    "category": category.get_text(strip=True) if category else "N/A",
                    "votes": votes.get_text(strip=True) if votes else "0",
                    "parsed_at": datetime.now().isoformat()
                })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(events)} событий")
        return events

    def parse_all_pages(self, max_pages: int = 5) -> List[Dict]:
        """Парсинг нескольких страниц"""
        all_events = []
        for page in range(1, max_pages + 1):
            events = self.parse_events(page)
            all_events.extend(events)
            if len(events) == 0:
                break
        return all_events

    def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг CoinMarketCal...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "coinmarketcal",
            "events": []
        }

        try:
            data["events"] = self.parse_all_pages(max_pages=5)
            logger.info(f"✅ Всего событий: {len(data['events'])}")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
