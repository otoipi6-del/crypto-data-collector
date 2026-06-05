"""
CryptoMiso Parser
Собирает: GitHub activity rankings, developer metrics
"""
import requests
from typing import Dict, List, Any
from datetime import datetime
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CryptoMisoParser:
    """Парсер CryptoMiso (простой, но лучше использовать GitHub API напрямую)"""

    def __init__(self):
        self.base_url = "https://www.cryptomiso.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def parse_rankings(self, period: str = "365") -> List[Dict]:
        """Парсинг рейтингов по коммитам"""
        logger.info(f"📊 Парсим CryptoMiso rankings (period: {period}d)...")

        url = f"{self.base_url}/?period={period}"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        projects = []

        # Ищем таблицу рейтингов
        rows = soup.find_all('tr')
        for row in rows[1:101]:  # топ-100
            try:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    rank = cols[0].get_text(strip=True)
                    name = cols[1].get_text(strip=True)
                    commits = cols[2].get_text(strip=True)

                    projects.append({
                        "rank": rank,
                        "name": name,
                        "commits": commits,
                        "period_days": period,
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(projects)} проектов")
        return projects

    def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг CryptoMiso...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "cryptomiso",
            "rankings": [],
            "note": "Рекомендуется использовать GitHub API напрямую для точности"
        }

        try:
            data["rankings"] = self.parse_rankings("365")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
