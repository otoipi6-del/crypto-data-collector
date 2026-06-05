"""
OpenOrgs Parser
Собирает: treasury data, governance proposals, multisig wallets
"""
import requests
from typing import Dict, List, Any
from datetime import datetime
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class OpenOrgsParser:
    """Парсер OpenOrgs (простой, без JS)"""

    def __init__(self):
        self.base_url = "https://openorgs.info"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def parse_organizations(self) -> List[Dict]:
        """Парсинг списка организаций"""
        logger.info("🏛️ Парсим OpenOrgs...")

        response = self.session.get(self.base_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        orgs = []

        # Ищем карточки организаций
        cards = soup.find_all(['div', 'article', 'tr'], 
                             class_=lambda x: x and ('org' in str(x).lower() or 'card' in str(x).lower()))

        for card in cards[:50]:
            try:
                name = card.find(['h3', 'h2', 'h4', 'a', 'span'])
                treasury = card.find(['span', 'div'], 
                                    class_=lambda x: x and 'treasury' in str(x).lower())
                proposals = card.find(['span', 'div'], 
                                     class_=lambda x: x and 'proposal' in str(x).lower())

                if name:
                    orgs.append({
                        "name": name.get_text(strip=True),
                        "treasury": treasury.get_text(strip=True) if treasury else "Unknown",
                        "proposals": proposals.get_text(strip=True) if proposals else "Unknown",
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(orgs)} организаций")
        return orgs

    def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг OpenOrgs...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "openorgs",
            "organizations": []
        }

        try:
            data["organizations"] = self.parse_organizations()
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
