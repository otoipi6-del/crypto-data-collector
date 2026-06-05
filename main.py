"""
Главный оркестратор сбора и анализа крипто-данных
Запускает все коллекторы и анализаторы
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('crypto_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Импорты API-коллекторов
from collectors.coingecko_collector import CoinGeckoCollector
from collectors.defillama_collector import DeFiLlamaCollector
from collectors.alternative_collector import AlternativeMeCollector
from collectors.nansen_collector import NansenCollector

# Импорты парсеров
from parsers.coinglass_parser import CoinGlassParser
from parsers.token_unlocks_parser import TokenUnlocksParser
from parsers.coinmarketcal_parser import CoinMarketCalParser
from parsers.cryptorank_parser import CryptoRankParser
from parsers.intotheblock_parser import IntoTheBlockParser
from parsers.arkham_parser import ArkhamParser
from parsers.kyberswap_parser import KyberSwapParser
from parsers.tokenterminal_parser import TokenTerminalParser
from parsers.openorgs_parser import OpenOrgsParser
from parsers.cryptomiso_parser import CryptoMisoParser
from parsers.cypherhunter_parser import CypherHunterParser
from parsers.tweetscout_parser import TweetScoutParser
from parsers.dune_parser import DuneParser

# Импорт анализатора
from analyzers.crypto_analyzer import CryptoAnalyzer


class CryptoDataOrchestrator:
    """Оркестратор полного цикла сбора и анализа"""

    def __init__(self, 
                 coingecko_api_key: str = None,
                 nansen_api_key: str = None,
                 proxy: str = None,
                 arkham_cookie: str = None,
                 tokenterminal_cookie: str = None,
                 tweetscout_cookie: str = None):
        self.coingecko_api_key = coingecko_api_key
        self.nansen_api_key = nansen_api_key
        self.proxy = proxy
        self.arkham_cookie = arkham_cookie
        self.tokenterminal_cookie = tokenterminal_cookie
        self.tweetscout_cookie = tweetscout_cookie
        self.collected_data = {}
        self.analyzer = CryptoAnalyzer()

    async def run_api_collectors(self) -> Dict[str, Any]:
        """Запуск API-коллекторов"""
        logger.info("=" * 60)
        logger.info("🚀 ЗАПУСК API-КОЛЛЕКТОРОВ")
        logger.info("=" * 60)

        api_data = {}

        # 1. CoinGecko (бесплатный tier)
        try:
            logger.info("📡 Подключаемся к CoinGecko...")
            async with CoinGeckoCollector(api_key=self.coingecko_api_key) as cg:
                api_data["coingecko"] = await cg.get_all_data()
                cg.save_data(api_data["coingecko"], "coingecko_raw.json")
                logger.info("✅ CoinGecko: данные собраны")
        except Exception as e:
            logger.error(f"❌ CoinGecko ошибка: {e}")
            api_data["coingecko"] = {}

        # 2. DeFi Llama (полностью бесплатный)
        try:
            logger.info("📡 Подключаемся к DeFi Llama...")
            async with DeFiLlamaCollector() as llama:
                api_data["defillama"] = await llama.get_all_data()
                llama.save_data(api_data["defillama"], "defillama_raw.json")
                logger.info("✅ DeFi Llama: данные собраны")
        except Exception as e:
            logger.error(f"❌ DeFi Llama ошибка: {e}")
            api_data["defillama"] = {}

        # 3. Alternative.me (Fear & Greed)
        try:
            logger.info("📡 Подключаемся к Alternative.me...")
            async with AlternativeMeCollector() as alt:
                api_data["alternative_me"] = await alt.get_all_data()
                alt.save_data(api_data["alternative_me"], "alternative_me_raw.json")
                logger.info("✅ Alternative.me: данные собраны")
        except Exception as e:
            logger.error(f"❌ Alternative.me ошибка: {e}")
            api_data["alternative_me"] = {}

        # 4. Nansen (если есть API ключ)
        if self.nansen_api_key:
            try:
                logger.info("📡 Подключаемся к Nansen...")
                async with NansenCollector(api_key=self.nansen_api_key) as nansen:
                    api_data["nansen"] = await nansen.get_all_data()
                    nansen.save_data(api_data["nansen"], "nansen_raw.json")
                    logger.info("✅ Nansen: данные собраны")
            except Exception as e:
                logger.error(f"❌ Nansen ошибка: {e}")
                api_data["nansen"] = {}
        else:
            logger.info("⏭️ Nansen пропущен (нет API ключа)")

        return api_data

    async def run_parsers(self) -> Dict[str, Any]:
        """Запуск парсеров"""
        logger.info("=" * 60)
        logger.info("🔍 ЗАПУСК ПАРСЕРОВ")
        logger.info("=" * 60)

        parsed_data = {}

        # 1. CoinMarketCal (простой парсинг)
        try:
            logger.info("🔍 Парсим CoinMarketCal...")
            parser = CoinMarketCalParser()
            parsed_data["coinmarketcal"] = parser.get_all_data()
            self._save_json(parsed_data["coinmarketcal"], "coinmarketcal_raw.json")
            logger.info("✅ CoinMarketCal: события спарсены")
        except Exception as e:
            logger.error(f"❌ CoinMarketCal ошибка: {e}")
            parsed_data["coinmarketcal"] = {}

        # 2. OpenOrgs (простой парсинг)
        try:
            logger.info("🔍 Парсим OpenOrgs...")
            parser = OpenOrgsParser()
            parsed_data["openorgs"] = parser.get_all_data()
            self._save_json(parsed_data["openorgs"], "openorgs_raw.json")
            logger.info("✅ OpenOrgs: данные спарсены")
        except Exception as e:
            logger.error(f"❌ OpenOrgs ошибка: {e}")
            parsed_data["openorgs"] = {}

        # 3. CryptoMiso (простой парсинг)
        try:
            logger.info("🔍 Парсим CryptoMiso...")
            parser = CryptoMisoParser()
            parsed_data["cryptomiso"] = parser.get_all_data()
            self._save_json(parsed_data["cryptomiso"], "cryptomiso_raw.json")
            logger.info("✅ CryptoMiso: рейтинги спарсены")
        except Exception as e:
            logger.error(f"❌ CryptoMiso ошибка: {e}")
            parsed_data["cryptomiso"] = {}

        # 4. CypherHunter (простой парсинг)
        try:
            logger.info("🔍 Парсим CypherHunter...")
            parser = CypherHunterParser()
            parsed_data["cypherhunter"] = parser.get_all_data()
            self._save_json(parsed_data["cypherhunter"], "cypherhunter_raw.json")
            logger.info("✅ CypherHunter: данные спарсены")
        except Exception as e:
            logger.error(f"❌ CypherHunter ошибка: {e}")
            parsed_data["cypherhunter"] = {}

        # 5. Token Unlocks (Playwright)
        try:
            logger.info("🔍 Парсим Token Unlocks...")
            async with TokenUnlocksParser(proxy=self.proxy) as parser:
                parsed_data["token_unlocks"] = await parser.get_all_data()
                self._save_json(parsed_data["token_unlocks"], "token_unlocks_raw.json")
                logger.info("✅ Token Unlocks: данные спарсены")
        except Exception as e:
            logger.error(f"❌ Token Unlocks ошибка: {e}")
            parsed_data["token_unlocks"] = {}

        # 6. KyberSwap (Playwright)
        try:
            logger.info("🔍 Парсим KyberSwap...")
            async with KyberSwapParser(proxy=self.proxy) as parser:
                parsed_data["kyberswap"] = await parser.get_all_data()
                self._save_json(parsed_data["kyberswap"], "kyberswap_raw.json")
                logger.info("✅ KyberSwap: данные спарсены")
        except Exception as e:
            logger.error(f"❌ KyberSwap ошибка: {e}")
            parsed_data["kyberswap"] = {}

        # 7. CoinGlass (Playwright + прокси)
        try:
            logger.info("🔍 Парсим CoinGlass...")
            async with CoinGlassParser(proxy=self.proxy) as parser:
                parsed_data["coinglass"] = await parser.get_all_data()
                self._save_json(parsed_data["coinglass"], "coinglass_raw.json")
                logger.info("✅ CoinGlass: данные спарсены")
        except Exception as e:
            logger.error(f"❌ CoinGlass ошибка: {e}")
            parsed_data["coinglass"] = {}

        # 8. CryptoRank (Playwright)
        try:
            logger.info("🔍 Парсим CryptoRank...")
            async with CryptoRankParser(proxy=self.proxy) as parser:
                parsed_data["cryptorank"] = await parser.get_all_data()
                self._save_json(parsed_data["cryptorank"], "cryptorank_raw.json")
                logger.info("✅ CryptoRank: данные спарсены")
        except Exception as e:
            logger.error(f"❌ CryptoRank ошибка: {e}")
            parsed_data["cryptorank"] = {}

        # 9. IntoTheBlock (Playwright + auth)
        try:
            logger.info("🔍 Парсим IntoTheBlock...")
            async with IntoTheBlockParser(proxy=self.proxy) as parser:
                parsed_data["intotheblock"] = await parser.get_all_data()
                self._save_json(parsed_data["intotheblock"], "intotheblock_raw.json")
                logger.info("✅ IntoTheBlock: данные спарсены")
        except Exception as e:
            logger.error(f"❌ IntoTheBlock ошибка: {e}")
            parsed_data["intotheblock"] = {}

        # 10. Token Terminal (Playwright + auth)
        try:
            logger.info("🔍 Парсим Token Terminal...")
            async with TokenTerminalParser(proxy=self.proxy, 
                                          auth_cookie=self.tokenterminal_cookie) as parser:
                parsed_data["tokenterminal"] = await parser.get_all_data()
                self._save_json(parsed_data["tokenterminal"], "tokenterminal_raw.json")
                logger.info("✅ Token Terminal: данные спарсены")
        except Exception as e:
            logger.error(f"❌ Token Terminal ошибка: {e}")
            parsed_data["tokenterminal"] = {}

        # 11. Arkham (Playwright + auth + прокси)
        try:
            logger.info("🔍 Парсим Arkham...")
            async with ArkhamParser(proxy=self.proxy, 
                                   auth_cookie=self.arkham_cookie) as parser:
                parsed_data["arkham"] = await parser.get_all_data()
                self._save_json(parsed_data["arkham"], "arkham_raw.json")
                logger.info("✅ Arkham: данные спарсены")
        except Exception as e:
            logger.error(f"❌ Arkham ошибка: {e}")
            parsed_data["arkham"] = {}

        # 12. TweetScout (Playwright + auth)
        try:
            logger.info("🔍 Парсим TweetScout...")
            async with TweetScoutParser(proxy=self.proxy,
                                       auth_cookie=self.tweetscout_cookie) as parser:
                parsed_data["tweetscout"] = await parser.get_all_data()
                self._save_json(parsed_data["tweetscout"], "tweetscout_raw.json")
                logger.info("✅ TweetScout: данные спарсены")
        except Exception as e:
            logger.error(f"❌ TweetScout ошибка: {e}")
            parsed_data["tweetscout"] = {}

        # 13. Dune (Playwright + auth)
        try:
            logger.info("🔍 Парсим Dune...")
            async with DuneParser(proxy=self.proxy) as parser:
                parsed_data["dune"] = await parser.get_all_data()
                self._save_json(parsed_data["dune"], "dune_raw.json")
                logger.info("✅ Dune: данные спарсены")
        except Exception as e:
            logger.error(f"❌ Dune ошибка: {e}")
            parsed_data["dune"] = {}

        return parsed_data

    def _save_json(self, data: Dict, filename: str):
        """Вспомогательный метод сохранения JSON"""
        filepath = f"outputs/{filename}"
        os.makedirs("outputs", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    async def run_analysis(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Запуск анализа"""
        logger.info("=" * 60)
        logger.info("📊 АНАЛИЗ ДАННЫХ")
        logger.info("=" * 60)

        report = self.analyzer.generate_comprehensive_report(all_data)
        self.analyzer.save_report("full_analysis_report.json")

        return report

    def print_report_summary(self, report: Dict[str, Any]):
        """Красивый вывод отчёта"""
        print("\n" + "=" * 70)
        print("📊 КОМПЛЕКСНЫЙ ОТЧЁТ ПО КРИПТО-РЫНКУ")
        print("=" * 70)
        print(f"🕐 Сгенерирован: {report['generated_at']}")
        print(f"📡 Источники ({len(report['sources_analyzed'])}): {', '.join(report['sources_analyzed'])}")

        # Рыночный обзор
        overview = report.get("market_overview", {})
        if overview:
            print("\n📈 РЫНОЧНЫЙ ОБЗОР")
            print("-" * 40)
            mcap = overview.get("total_market_cap", 0)
            if mcap:
                print(f"   💰 Общая капитализация: ${mcap:,.0f}")
            btc_dom = overview.get("btc_dominance", 0)
            if btc_dom:
                print(f"   ₿ BTC доминирование: {btc_dom:.1f}%")

            top_gainer = overview.get("top_gainer")
            if top_gainer:
                print(f"   🚀 Топ-растущий: {top_gainer.get('symbol', '')} (+{top_gainer.get('change', 0):.1f}%)")

            top_loser = overview.get("top_loser")
            if top_loser:
                print(f"   📉 Топ-падающий: {top_loser.get('symbol', '')} ({top_loser.get('change', 0):.1f}%)")

        # Оценка рисков
        risk = report.get("risk_assessment", {})
        if risk:
            print("\n⚠️ ОЦЕНКА РИСКОВ")
            print("-" * 40)
            score = risk.get("score", 50)
            level = risk.get("level", "Unknown")

            risk_emoji = "🔴" if level == "High" else "🟡" if level == "Medium" else "🟢"
            print(f"   {risk_emoji} Уровень риска: {level} (Score: {score}/100)")

            factors = risk.get("factors", [])
            if factors:
                print("   📋 Факторы риска:")
                for f in factors:
                    print(f"      • {f}")

        # Возможности
        opportunities = report.get("opportunities", [])
        if opportunities:
            print("\n💎 ВОЗМОЖНОСТИ")
            print("-" * 40)
            for opp in opportunities[:5]:
                print(f"   • {opp.get('description', '')}")

        # Рекомендации
        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\n📋 РЕКОМЕНДАЦИИ")
            print("-" * 40)
            for rec in recommendations:
                print(f"   {rec}")

        # Алерты
        alerts = report.get("alerts", [])
        if alerts:
            print("\n🚨 АЛЕРТЫ")
            print("-" * 40)
            for alert in alerts:
                print(f"   ⚡ {alert}")

        print("\n" + "=" * 70)
        print("✅ Отчёт сохранён в outputs/full_analysis_report.json")
        print("=" * 70 + "\n")

    async def run_full_pipeline(self):
        """Полный цикл: сбор → анализ → отчёт"""
        logger.info("🎯 НАЧИНАЕМ ПОЛНЫЙ ЦИКЛ СБОРА ДАННЫХ")

        start_time = datetime.now()

        # Шаг 1: API коллекторы
        api_data = await self.run_api_collectors()
        self.collected_data.update(api_data)

        # Шаг 2: Парсеры
        parsed_data = await self.run_parsers()
        self.collected_data.update(parsed_data)

        # Шаг 3: Анализ
        report = await self.run_analysis(self.collected_data)

        # Шаг 4: Вывод отчёта
        self.print_report_summary(report)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"⏱️ Полный цикл завершён за {elapsed:.1f} секунд")
        logger.info(f"📊 Обработано источников: {len(self.collected_data)}")

        return report


async def main():
    """Точка входа"""
    # Настройки (замените на свои ключи)
    COINGECKO_API_KEY = None      # или "your_key" для paid tier
    NANSEN_API_KEY = None          # или "your_key"
    PROXY = None                   # или "http://user:pass@proxy:port"
    ARKHAM_COOKIE = None           # путь к cookie файлу
    TT_COOKIE = None               # путь к cookie файлу
    TWEETSCOUT_COOKIE = None       # путь к cookie файлу

    orchestrator = CryptoDataOrchestrator(
        coingecko_api_key=COINGECKO_API_KEY,
        nansen_api_key=NANSEN_API_KEY,
        proxy=PROXY,
        arkham_cookie=ARKHAM_COOKIE,
        tokenterminal_cookie=TT_COOKIE,
        tweetscout_cookie=TWEETSCOUT_COOKIE
    )

    report = await orchestrator.run_full_pipeline()
    return report


if __name__ == "__main__":
    asyncio.run(main())
