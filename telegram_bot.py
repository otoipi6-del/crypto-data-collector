"""
Telegram Bot Integration
Отправляет отчёты и алерты в Telegram канал
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import os

# Для Telegram Bot API
import aiohttp

logger = logging.getLogger(__name__)


class TelegramReporter:
    """Отправка отчётов и алертов в Telegram"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Отправка текстового сообщения"""
        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return True
                else:
                    logger.error(f"❌ Ошибка отправки: {await response.text()}")
                    return False

    async def send_photo(self, photo_path: str, caption: str = "") -> bool:
        """Отправка изображения"""
        url = f"{self.base_url}/sendPhoto"

        async with aiohttp.ClientSession() as session:
            with open(photo_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('chat_id', self.chat_id)
                data.add_field('photo', f, filename=os.path.basename(photo_path))
                data.add_field('caption', caption)
                data.add_field('parse_mode', 'HTML')

                async with session.post(url, data=data) as response:
                    return response.status == 200

    async def send_document(self, file_path: str, caption: str = "") -> bool:
        """Отправка документа (JSON отчёт)"""
        url = f"{self.base_url}/sendDocument"

        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('chat_id', self.chat_id)
                data.add_field('document', f, filename=os.path.basename(file_path))
                data.add_field('caption', caption)

                async with session.post(url, data=data) as response:
                    return response.status == 200

    def format_market_report(self, report: Dict[str, Any]) -> str:
        """Форматирование рыночного отчёта для Telegram"""

        text = f"📊 <b>КРИПТО-ОТЧЁТ</b>\n"
        text += f"🕐 {report.get('generated_at', 'N/A')[:19]}\n"
        text += "━" * 30 + "\n\n"

        # Рыночный обзор
        overview = report.get("market_overview", {})
        if overview:
            text += "📈 <b>РЫНОЧНЫЙ ОБЗОР</b>\n"
            mcap = overview.get("total_market_cap", 0)
            if mcap:
                text += f"💰 Капитализация: <b>${mcap/1e9:.1f}B</b>\n"
            btc_dom = overview.get("btc_dominance", 0)
            if btc_dom:
                text += f"₿ BTC доминирование: <b>{btc_dom:.1f}%</b>\n"

            top_gainer = overview.get("top_gainer")
            if top_gainer:
                text += f"🚀 Топ-растущий: {top_gainer.get('symbol', '')} <b>+{top_gainer.get('change', 0):.1f}%</b>\n"

            top_loser = overview.get("top_loser")
            if top_loser:
                text += f"📉 Топ-падающий: {top_loser.get('symbol', '')} <b>{top_loser.get('change', 0):.1f}%</b>\n"
            text += "\n"

        # Оценка рисков
        risk = report.get("risk_assessment", {})
        if risk:
            score = risk.get("score", 50)
            level = risk.get("level", "Unknown")

            risk_emoji = "🔴" if level == "High" else "🟡" if level == "Medium" else "🟢"
            text += f"⚠️ <b>ОЦЕНКА РИСКОВ</b>\n"
            text += f"{risk_emoji} Уровень: <b>{level}</b> (Score: {score}/100)\n"

            factors = risk.get("factors", [])
            if factors:
                text += "📋 Факторы:\n"
                for f in factors[:3]:
                    text += f"   • {f}\n"
            text += "\n"

        # Возможности
        opportunities = report.get("opportunities", [])
        if opportunities:
            text += "💎 <b>ВОЗМОЖНОСТИ</b>\n"
            for opp in opportunities[:5]:
                text += f"   • {opp.get('description', '')}\n"
            text += "\n"

        # Рекомендации
        recommendations = report.get("recommendations", [])
        if recommendations:
            text += "📋 <b>РЕКОМЕНДАЦИИ</b>\n"
            for rec in recommendations:
                text += f"   {rec}\n"
            text += "\n"

        # Алерты
        alerts = report.get("alerts", [])
        if alerts:
            text += "🚨 <b>АЛЕРТЫ</b>\n"
            for alert in alerts[:5]:
                text += f"   ⚡ {alert}\n"

        text += "\n" + "━" * 30
        text += "\n📡 Источники: " + ", ".join(report.get("sources_analyzed", [])[:5])

        return text

    def format_alert(self, alert_type: str, data: Dict) -> str:
        """Форматирование алерта"""

        if alert_type == "price_spike":
            return (
                f"🚨 <b>АЛЕРТ: Резкое движение цены</b>\n\n"
                f"💰 {data.get('symbol', 'N/A')}: {data.get('change', 0):+.1f}%\n"
                f"📊 Цена: ${data.get('price', 0):,.4f}\n"
                f"🕐 {datetime.now().strftime('%H:%M:%S')}"
            )

        elif alert_type == "fear_greed_extreme":
            return (
                f"😨 <b>АЛЕРТ: Экстремальный сентимент</b>\n\n"
                f"Fear & Greed: <b>{data.get('value', 50)}</b> ({data.get('classification', 'Neutral')})\n"
                f"{'🟢 Возможность покупки!' if data.get('value', 50) < 25 else '🔴 Возможная коррекция!'}"
            )

        elif alert_type == "tvl_drop":
            return (
                f"⚠️ <b>АЛЕРТ: Отток TVL</b>\n\n"
                f"📉 {data.get('protocol', 'N/A')}: {data.get('change', 0):.1f}%\n"
                f"Текущий TVL: ${data.get('tvl', 0):,.0f}"
            )

        elif alert_type == "unlock_warning":
            return (
                f"🔓 <b>АЛЕРТ: Предстоящий Unlock</b>\n\n"
                f"🪙 {data.get('token', 'N/A')}\n"
                f"📅 Дата: {data.get('date', 'N/A')}\n"
                f"💰 Объём: {data.get('amount', 'N/A')}"
            )

        else:
            return f"📢 <b>АЛЕРТ</b>\n\n{json.dumps(data, indent=2, ensure_ascii=False)}"

    async def send_market_report(self, report: Dict[str, Any]):
        """Отправка полного рыночного отчёта"""
        text = self.format_market_report(report)

        # Telegram limit: 4096 chars per message
        if len(text) > 4000:
            # Split into parts
            parts = []
            current = ""
            for line in text.split("\n"):
                if len(current) + len(line) + 1 > 4000:
                    parts.append(current)
                    current = line + "\n"
                else:
                    current += line + "\n"
            if current:
                parts.append(current)

            for i, part in enumerate(parts):
                header = f"📊 <b>КРИПТО-ОТЧЁТ (часть {i+1}/{len(parts)})</b>\n\n" if i == 0 else ""
                await self.send_message(header + part)
                await asyncio.sleep(0.5)
        else:
            await self.send_message(text)

    async def send_alert(self, alert_type: str, data: Dict):
        """Отправка алерта"""
        text = self.format_alert(alert_type, data)
        await self.send_message(text)

    async def send_raw_report(self, file_path: str):
        """Отправка JSON отчёта как документа"""
        await self.send_document(
            file_path,
            caption="📊 Полный отчёт в формате JSON"
        )


class AlertManager:
    """Менеджер алертов — проверяет условия и отправляет уведомления"""

    def __init__(self, reporter: TelegramReporter):
        self.reporter = reporter
        self.alert_history = []
        self.cooldown_minutes = 30  # минимум 30 мин между одинаковыми алертами

    def _check_cooldown(self, alert_key: str) -> bool:
        """Проверка cooldown"""
        now = datetime.now()
        for alert in self.alert_history:
            if alert["key"] == alert_key:
                elapsed = (now - alert["time"]).total_seconds() / 60
                if elapsed < self.cooldown_minutes:
                    return False
        return True

    def _record_alert(self, alert_key: str):
        """Запись алерта в историю"""
        self.alert_history.append({
            "key": alert_key,
            "time": datetime.now()
        })
        # Очищаем старую историю
        cutoff = datetime.now().timestamp() - 86400  # 24 часа
        self.alert_history = [
            a for a in self.alert_history 
            if a["time"].timestamp() > cutoff
        ]

    async def check_price_alerts(self, coins: List[Dict]):
        """Проверка ценовых алертов"""
        for coin in coins:
            symbol = coin.get("symbol", "").upper()
            change = coin.get("price_change_percentage_24h", 0) or 0

            # Алерт при изменении > 15%
            if abs(change) > 15:
                alert_key = f"price_{symbol}"
                if self._check_cooldown(alert_key):
                    await self.reporter.send_alert("price_spike", {
                        "symbol": symbol,
                        "change": change,
                        "price": coin.get("current_price", 0)
                    })
                    self._record_alert(alert_key)

    async def check_fear_greed_alerts(self, fg_value: int, classification: str):
        """Проверка алертов Fear & Greed"""
        if fg_value <= 20 or fg_value >= 80:
            alert_key = f"fg_{fg_value // 10}"
            if self._check_cooldown(alert_key):
                await self.reporter.send_alert("fear_greed_extreme", {
                    "value": fg_value,
                    "classification": classification
                })
                self._record_alert(alert_key)

    async def check_tvl_alerts(self, protocols: List[Dict]):
        """Проверка алертов TVL"""
        for protocol in protocols[:20]:  # топ-20
            change = protocol.get("change_7d", 0)
            if change and change < -30:
                alert_key = f"tvl_{protocol.get('name', '')}"
                if self._check_cooldown(alert_key):
                    await self.reporter.send_alert("tvl_drop", {
                        "protocol": protocol.get("name", ""),
                        "change": change,
                        "tvl": protocol.get("tvl", 0)
                    })
                    self._record_alert(alert_key)

    async def check_unlock_alerts(self, unlocks: List[Dict]):
        """Проверка алертов unlock'ов"""
        for unlock in unlocks[:10]:
            alert_key = f"unlock_{unlock.get('token', '')}"
            if self._check_cooldown(alert_key):
                await self.reporter.send_alert("unlock_warning", unlock)
                self._record_alert(alert_key)


# Пример использования:
# reporter = TelegramReporter(
#     bot_token="8120413197:AAE8jm2aNSSGnAd42Favfv3MTJHAcUjLYzo",
#     chat_id="-1003996736459"
# )
# alert_manager = AlertManager(reporter)
# 
# # Отправка отчёта
# await reporter.send_market_report(report)
# 
# # Проверка алертов
# await alert_manager.check_price_alerts(coins)
# await alert_manager.check_fear_greed_alerts(75, "Greed")
