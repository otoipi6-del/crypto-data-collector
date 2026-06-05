"""
CypherHunter Parser
Собирает: project profiles, investor profiles, funding connections
"""
import requests
from typing import Dict, List, Any
from datetime import datetime
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CypherHunterParser:
    """Парсер CypherHunter (простой, без JS)"""

    def __init__(self):
        self.base_url = "https://www.cypherhunter.com/en"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def parse_projects(self) -> List[Dict]:
        """Парсинг списка проектов"""
        logger.info("🔍 Парсим CypherHunter projects...")

        response = self.session.get(f"{self.base_url}/projects", timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        projects = []

        cards = soup.find_all(['div', 'article', 'tr'],
                             class_=lambda x: x and ('project' in str(x).lower() or 'card' in str(x).lower()))

        for card in cards[:50]:
            try:
                name = card.find(['h3', 'h2', 'h4', 'a'])
                category = card.find(['span', 'div'], 
                                    class_=lambda x: x and 'category' in str(x).lower())
                funding = card.find(['span', 'div'], 
                                   class_=lambda x: x and 'funding' in str(x).lower())

                if name:
                    projects.append({
                        "name": name.get_text(strip=True),
                        "category": category.get_text(strip=True) if category else "Unknown",
                        "funding": funding.get_text(strip=True) if funding else "Unknown",
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(projects)} проектов")
        return projects

    def parse_investors(self) -> List[Dict]:
        """Парсинг инвесторов"""
        logger.info("💼 Парсим CypherHunter investors...")

        response = self.session.get(f"{self.base_url}/investors", timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        investors = []

        cards = soup.find_all(['div', 'article', 'tr'],
                             class_=lambda x: x and ('investor' in str(x).lower() or 'card' in str(x).lower()))

        for card in cards[:30]:
            try:
                name = card.find(['h3', 'h2', 'h4', 'a'])
                deals = card.find(['span', 'div'], 
                                 class_=lambda x: x and 'deal' in str(x).lower())

                if name:
                    investors.append({
                        "name": name.get_text(strip=True),
                        "deals": deals.get_text(strip=True) if deals else "Unknown",
                        "parsed_at": datetime.now().isoformat()
                    })
            except Exception:
                continue

        logger.info(f"✅ Найдено {len(investors)} инвесторов")
        return investors

    def get_all_data(self) -> Dict[str, Any]:
        """Сбор всех данных"""
        logger.info("🚀 Начинаем парсинг CypherHunter...")

        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "cypherhunter",
            "projects": [],
            "investors": []
        }

        try:
            data["projects"] = self.parse_projects()
            data["investors"] = self.parse_investors()
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

        return data
