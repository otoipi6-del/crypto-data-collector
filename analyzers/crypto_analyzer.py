"""
Анализатор крипто-данных
Анализирует собранные данные и генерирует рекомендации
"""
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CryptoAnalyzer:
    """Анализатор крипто-данных из всех источников"""

    def __init__(self, data_dir: str = "outputs"):
        self.data_dir = data_dir
        self.analysis_results = {}

    def analyze_coingecko(self, data: Dict) -> Dict[str, Any]:
        """Анализ данных CoinGecko"""
        results = {
            "source": "coingecko",
            "timestamp": datetime.now().isoformat(),
            "market_summary": {},
            "top_movers": [],
            "trending_analysis": {},
            "risk_signals": []
        }

        # Глобальные метрики
        global_data = data.get("global", {}).get("data", {})
        if global_data:
            results["market_summary"] = {
                "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
                "total_volume": global_data.get("total_volume", {}).get("usd", 0),
                "btc_dominance": global_data.get("market_cap_percentage", {}).get("btc", 0),
                "eth_dominance": global_data.get("market_cap_percentage", {}).get("eth", 0),
                "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                "markets": global_data.get("markets", 0)
            }

        # Топ-растущие и падающие
        top_coins = data.get("top_coins", [])
        if top_coins:
            sorted_by_24h = sorted(top_coins, 
                                  key=lambda x: x.get("price_change_percentage_24h", 0) or 0,
                                  reverse=True)

            results["top_movers"] = {
                "gainers_24h": [
                    {
                        "symbol": c.get("symbol", "").upper(),
                        "name": c.get("name", ""),
                        "change_24h": c.get("price_change_percentage_24h", 0),
                        "price": c.get("current_price", 0),
                        "market_cap": c.get("market_cap", 0)
                    }
                    for c in sorted_by_24h[:10]
                ],
                "losers_24h": [
                    {
                        "symbol": c.get("symbol", "").upper(),
                        "name": c.get("name", ""),
                        "change_24h": c.get("price_change_percentage_24h", 0),
                        "price": c.get("current_price", 0)
                    }
                    for c in sorted_by_24h[-10:]
                ]
            }

        # Анализ трендов
        trending = data.get("trending", [])
        if trending:
            results["trending_analysis"] = {
                "trending_count": len(trending),
                "top_trending": [
                    {
                        "name": t.get("item", {}).get("name", ""),
                        "symbol": t.get("item", {}).get("symbol", "").upper(),
                        "market_cap_rank": t.get("item", {}).get("market_cap_rank", 0),
                        "score": t.get("item", {}).get("score", 0)
                    }
                    for t in trending[:5]
                ]
            }

        # Сигналы риска
        if top_coins:
            btc_data = next((c for c in top_coins if c.get("symbol") == "btc"), None)
            if btc_data:
                change = btc_data.get("price_change_percentage_24h", 0) or 0
                if change < -10:
                    results["risk_signals"].append("🚨 BTC упал более чем на 10% за 24ч — возможен рыночный крах")
                elif change < -5:
                    results["risk_signals"].append("⚠️ BTC упал более чем на 5% — повышенная волатильность")
                elif change > 10:
                    results["risk_signals"].append("🚀 BTC вырос более чем на 10% — бычий импульс")

        return results

    def analyze_defillama(self, data: Dict) -> Dict[str, Any]:
        """Анализ данных DeFi Llama"""
        results = {
            "source": "defillama",
            "timestamp": datetime.now().isoformat(),
            "defi_summary": {},
            "top_protocols": [],
            "chain_analysis": [],
            "yield_opportunities": [],
            "risk_signals": []
        }

        # Глобальный TVL
        results["defi_summary"]["global_tvl"] = data.get("global_tvl", 0)

        # Топ протоколы
        protocols = data.get("protocols", [])
        if protocols:
            sorted_protocols = sorted(protocols, 
                                     key=lambda x: x.get("tvl", 0) or 0,
                                     reverse=True)
            results["top_protocols"] = [
                {
                    "name": p.get("name", ""),
                    "tvl": p.get("tvl", 0),
                    "change_1d": p.get("change_1d", 0),
                    "change_7d": p.get("change_7d", 0),
                    "category": p.get("category", ""),
                    "chain": p.get("chain", "")
                }
                for p in sorted_protocols[:20]
            ]

            # Сигналы риска по TVL
            major_protocols = [p for p in sorted_protocols[:10] if p.get("change_7d", 0) is not None]
            declining = [p for p in major_protocols if p.get("change_7d", 0) < -20]
            if len(declining) >= 3:
                results["risk_signals"].append(
                    f"⚠️ {len(declining)} из топ-10 протоколов потеряли >20% TVL за неделю"
                )

        # Анализ чейнов
        chains = data.get("chains", [])
        if chains:
            sorted_chains = sorted(chains, 
                                  key=lambda x: x.get("tvl", 0) or 0,
                                  reverse=True)
            results["chain_analysis"] = [
                {
                    "name": c.get("name", ""),
                    "tvl": c.get("tvl", 0),
                    "token_symbol": c.get("tokenSymbol", ""),
                    "change_1d": c.get("change_1d", 0)
                }
                for c in sorted_chains[:10]
            ]

        # Yield opportunities
        yields = data.get("yields", [])
        if yields:
            high_yields = [y for y in yields if y.get("apy", 0) > 10 and y.get("apy", 0) < 100]
            results["yield_opportunities"] = [
                {
                    "pool": y.get("pool", ""),
                    "project": y.get("project", ""),
                    "chain": y.get("chain", ""),
                    "apy": y.get("apy", 0),
                    "tvl": y.get("tvlUsd", 0)
                }
                for y in sorted(high_yields, key=lambda x: x.get("apy", 0), reverse=True)[:10]
            ]

        return results

    def analyze_fear_greed(self, data: Dict) -> Dict[str, Any]:
        """Анализ Fear & Greed Index"""
        results = {
            "source": "alternative_me",
            "timestamp": datetime.now().isoformat(),
            "current_sentiment": {},
            "trend": [],
            "interpretation": "",
            "trading_signals": []
        }

        fg_data = data.get("fear_greed", {}).get("data", [])
        if fg_data:
            current = fg_data[0]
            value = int(current.get("value", 50))
            classification = current.get("value_classification", "Neutral")

            results["current_sentiment"] = {
                "value": value,
                "classification": classification,
                "timestamp": current.get("timestamp", "")
            }

            # Тренд за последние 7 дней
            results["trend"] = [
                {
                    "date": d.get("timestamp", ""),
                    "value": int(d.get("value", 50)),
                    "classification": d.get("value_classification", "")
                }
                for d in fg_data[:7]
            ]

            # Интерпретация
            if value <= 20:
                results["interpretation"] = "🟢 Экстремальный страх — возможная точка входа для покупки"
                results["trading_signals"].append("Сильный бычий сигнал: рынок перепродан")
                results["trading_signals"].append("Рассмотреть DCA-стратегию")
            elif value <= 40:
                results["interpretation"] = "🟡 Страх — осторожный оптимизм"
                results["trading_signals"].append("Умеренный бычий сигнал")
            elif value <= 60:
                results["interpretation"] = "⚪ Нейтральный сентимент"
                results["trading_signals"].append("Нет чёткого сигнала, ждать")
            elif value <= 80:
                results["interpretation"] = "🟠 Жадность — возможная точка фиксации прибыли"
                results["trading_signals"].append("Умеренный медвежий сигнал")
            else:
                results["interpretation"] = "🔴 Экстремальная жадность — высокий риск коррекции"
                results["trading_signals"].append("Сильный медвежий сигнал: рынок перекуплен")
                results["trading_signals"].append("Рассмотреть фиксацию части прибыли")

        return results

    def analyze_token_unlocks(self, data: Dict) -> Dict[str, Any]:
        """Анализ данных Token Unlocks"""
        results = {
            "source": "token_unlocks",
            "timestamp": datetime.now().isoformat(),
            "upcoming_unlocks_summary": {},
            "high_risk_unlocks": [],
            "trading_signals": []
        }

        unlocks = data.get("upcoming_unlocks", [])
        if unlocks:
            results["upcoming_unlocks_summary"] = {
                "total_count": len(unlocks),
                "next_7_days": len([u for u in unlocks if "day" in u.get("unlock_date", "").lower()]),
                "next_30_days": len(unlocks)
            }

            # Высокорисковые unlock'и (крупные суммы)
            # Примечание: парсинг сумм может быть неточным
            results["high_risk_unlocks"] = unlocks[:10]

            if len(unlocks) > 5:
                results["trading_signals"].append(
                    f"⚠️ {len(unlocks)} токенов с предстоящими unlock'ами — возможно давление на цены"
                )

        return results

    def generate_comprehensive_report(self, all_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Генерация комплексного отчёта"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "sources_analyzed": list(all_data.keys()),
            "market_overview": {},
            "risk_assessment": {},
            "opportunities": [],
            "recommendations": [],
            "alerts": []
        }

        # Анализируем каждый источник
        analyses = {}
        for source, data in all_data.items():
            if source == "coingecko":
                analyses["coingecko"] = self.analyze_coingecko(data)
            elif source == "defillama":
                analyses["defillama"] = self.analyze_defillama(data)
            elif source == "alternative_me":
                analyses["alternative_me"] = self.analyze_fear_greed(data)
            elif source == "token_unlocks":
                analyses["token_unlocks"] = self.analyze_token_unlocks(data)

        # Комплексный анализ
        # Рыночный обзор
        cg_analysis = analyses.get("coingecko", {})
        if cg_analysis:
            report["market_overview"] = {
                "total_market_cap": cg_analysis.get("market_summary", {}).get("total_market_cap", 0),
                "btc_dominance": cg_analysis.get("market_summary", {}).get("btc_dominance", 0),
                "top_gainer": cg_analysis.get("top_movers", {}).get("gainers_24h", [{}])[0] if cg_analysis.get("top_movers") else None,
                "top_loser": cg_analysis.get("top_movers", {}).get("losers_24h", [{}])[0] if cg_analysis.get("top_movers") else None
            }

        # Оценка рисков
        risk_score = 0
        risk_factors = []

        # Риск от F&G
        fg_analysis = analyses.get("alternative_me", {})
        if fg_analysis:
            fg_value = fg_analysis.get("current_sentiment", {}).get("value", 50)
            if fg_value > 75:
                risk_score += 30
                risk_factors.append("Высокий Fear & Greed (>75) — перекупленность")
            elif fg_value < 25:
                risk_score -= 20
                risk_factors.append("Низкий Fear & Greed (<25) — возможность покупки")

        # Риск от DeFi TVL
        defi_analysis = analyses.get("defillama", {})
        if defi_analysis:
            tvl = defi_analysis.get("defi_summary", {}).get("global_tvl", 0)
            if tvl < 50000000000:  # < $50B
                risk_score += 15
                risk_factors.append("Низкий глобальный TVL — слабый DeFi-сектор")

        # Риск от unlock'ов
        unlock_analysis = analyses.get("token_unlocks", {})
        if unlock_analysis:
            unlock_count = unlock_analysis.get("upcoming_unlocks_summary", {}).get("total_count", 0)
            if unlock_count > 10:
                risk_score += 10
                risk_factors.append(f"Много предстоящих unlock'ов ({unlock_count}) — давление на рынок")

        report["risk_assessment"] = {
            "score": max(0, min(100, risk_score + 50)),  # нормализуем 0-100
            "factors": risk_factors,
            "level": "High" if risk_score > 30 else "Medium" if risk_score > 10 else "Low"
        }

        # Возможности
        if cg_analysis and cg_analysis.get("top_movers"):
            gainers = cg_analysis["top_movers"].get("gainers_24h", [])
            for g in gainers[:3]:
                report["opportunities"].append({
                    "type": "momentum",
                    "asset": g.get("symbol", ""),
                    "change": g.get("change_24h", 0),
                    "description": f"Сильный рост {g.get('symbol', '')} на {g.get('change_24h', 0):.1f}%"
                })

        if defi_analysis and defi_analysis.get("yield_opportunities"):
            yields = defi_analysis["yield_opportunities"]
            for y in yields[:3]:
                report["opportunities"].append({
                    "type": "yield",
                    "pool": y.get("pool", ""),
                    "apy": y.get("apy", 0),
                    "description": f"Доходность {y.get('apy', 0):.1f}% APY в {y.get('project', '')}"
                })

        # Рекомендации
        if report["risk_assessment"]["level"] == "High":
            report["recommendations"].append("🛡️ Снизить экспозицию, увеличить долю стейблкоинов")
            report["recommendations"].append("📉 Избегать новых позиций, фиксировать прибыль")
        elif report["risk_assessment"]["level"] == "Low":
            report["recommendations"].append("🟢 Благоприятное время для накопления (DCA)")
            report["recommendations"].append("📈 Рассмотреть увеличение позиций в BTC/ETH")
        else:
            report["recommendations"].append("⚖️ Сохранять текущие позиции, мониторить рынок")

        # Алерты
        all_risk_signals = []
        for analysis in analyses.values():
            all_risk_signals.extend(analysis.get("risk_signals", []))

        report["alerts"] = all_risk_signals[:5]  # топ-5 алертов

        self.analysis_results = report
        return report

    def save_report(self, filename: str = None):
        """Сохранение отчёта"""
        if not filename:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = f"{self.data_dir}/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"📊 Отчёт сохранён: {filepath}")
        return filepath
