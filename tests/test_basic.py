"""
Базовые тесты для коллекторов
"""
import asyncio
import pytest
from datetime import datetime

from collectors.coingecko_collector import CoinGeckoCollector
from collectors.defillama_collector import DeFiLlamaCollector
from collectors.alternative_collector import AlternativeMeCollector


@pytest.mark.asyncio
async def test_coingecko_basic():
    """Тест CoinGecko API"""
    async with CoinGeckoCollector() as cg:
        # Тест получения глобальных данных
        global_data = await cg.get_global_data()
        assert global_data is not None
        assert "data" in global_data
        print(f"✅ CoinGecko global: ${global_data['data']['total_market_cap']['usd']:,.0f}")


@pytest.mark.asyncio
async def test_defillama_basic():
    """Тест DeFi Llama API"""
    async with DeFiLlamaCollector() as llama:
        protocols = await llama.get_protocols()
        assert protocols is not None
        assert len(protocols) > 0
        print(f"✅ DeFi Llama protocols: {len(protocols)}")


@pytest.mark.asyncio
async def test_alternative_me_basic():
    """Тест Alternative.me API"""
    async with AlternativeMeCollector() as alt:
        fg = await alt.get_fear_greed()
        assert fg is not None
        assert "data" in fg
        current = fg["data"][0]
        print(f"✅ F&G: {current['value']} ({current['value_classification']})")


if __name__ == "__main__":
    asyncio.run(test_coingecko_basic())
    asyncio.run(test_defillama_basic())
    asyncio.run(test_alternative_me_basic())
    print("\n✅ Все базовые тесты пройдены!")
