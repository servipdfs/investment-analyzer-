from enum import Enum
from typing import List, Dict

class AssetType(Enum):
    CRYPTO = "crypto"
    STOCK = "stock"
    COMMODITY = "commodity"
    FOREX = "forex"
    INDEX = "index"
    ETF = "etf"

# Activos disponibles por categoría
ASSETS_DB = {
    AssetType.CRYPTO: {
        "BTC-USD": {"name": "Bitcoin", "symbol": "BTC", "risk": "high"},
        "ETH-USD": {"name": "Ethereum", "symbol": "ETH", "risk": "high"},
        "BNB-USD": {"name": "Binance Coin", "symbol": "BNB", "risk": "high"},
        "SOL-USD": {"name": "Solana", "symbol": "SOL", "risk": "high"},
        "ADA-USD": {"name": "Cardano", "symbol": "ADA", "risk": "high"},
        "XRP-USD": {"name": "Ripple", "symbol": "XRP", "risk": "high"},
        "DOGE-USD": {"name": "Dogecoin", "symbol": "DOGE", "risk": "very_high"},
        "DOT-USD": {"name": "Polkadot", "symbol": "DOT", "risk": "high"},
    },
    AssetType.STOCK: {
        "AAPL": {"name": "Apple Inc", "sector": "Technology", "risk": "medium"},
        "MSFT": {"name": "Microsoft", "sector": "Technology", "risk": "medium"},
        "GOOGL": {"name": "Alphabet", "sector": "Technology", "risk": "medium"},
        "AMZN": {"name": "Amazon", "sector": "Consumer", "risk": "medium"},
        "TSLA": {"name": "Tesla", "sector": "Automotive", "risk": "high"},
        "NVDA": {"name": "NVIDIA", "sector": "Technology", "risk": "high"},
        "META": {"name": "Meta Platforms", "sector": "Technology", "risk": "medium"},
        "NFLX": {"name": "Netflix", "sector": "Entertainment", "risk": "medium"},
        "JPM": {"name": "JPMorgan Chase", "sector": "Finance", "risk": "low"},
        "V": {"name": "Visa", "sector": "Finance", "risk": "low"},
    },
    AssetType.COMMODITY: {
        "GC=F": {"name": "Gold", "category": "Precious Metals", "risk": "low"},
        "SI=F": {"name": "Silver", "category": "Precious Metals", "risk": "medium"},
        "CL=F": {"name": "Crude Oil WTI", "category": "Energy", "risk": "high"},
        "BZ=F": {"name": "Brent Oil", "category": "Energy", "risk": "high"},
        "NG=F": {"name": "Natural Gas", "category": "Energy", "risk": "very_high"},
        "HG=F": {"name": "Copper", "category": "Industrial Metals", "risk": "medium"},
    },
    AssetType.FOREX: {
        "EURUSD=X": {"name": "EUR/USD", "type": "Major", "risk": "low"},
        "GBPUSD=X": {"name": "GBP/USD", "type": "Major", "risk": "low"},
        "USDJPY=X": {"name": "USD/JPY", "type": "Major", "risk": "low"},
        "USDCHF=X": {"name": "USD/CHF", "type": "Major", "risk": "low"},
        "AUDUSD=X": {"name": "AUD/USD", "type": "Major", "risk": "medium"},
        "USDCAD=X": {"name": "USD/CAD", "type": "Major", "risk": "low"},
    },
    AssetType.INDEX: {
        "^GSPC": {"name": "S&P 500", "region": "USA", "risk": "medium"},
        "^IXIC": {"name": "NASDAQ", "region": "USA", "risk": "high"},
        "^DJI": {"name": "Dow Jones", "region": "USA", "risk": "medium"},
        "^FTSE": {"name": "FTSE 100", "region": "UK", "risk": "medium"},
        "^GDAXI": {"name": "DAX", "region": "Germany", "risk": "medium"},
        "^N225": {"name": "Nikkei 225", "region": "Japan", "risk": "medium"},
    },
    AssetType.ETF: {
        "SPY": {"name": "SPDR S&P 500 ETF", "category": "Index", "risk": "low"},
        "QQQ": {"name": "Invesco QQQ", "category": "Technology", "risk": "medium"},
        "GLD": {"name": "SPDR Gold Shares", "category": "Commodity", "risk": "low"},
        "VTI": {"name": "Vanguard Total Stock", "category": "Diversified", "risk": "low"},
        "ARKK": {"name": "ARK Innovation ETF", "category": "Growth", "risk": "high"},
    }
}

def get_all_assets() -> List[Dict]:
    """Retorna todos los activos disponibles"""
    all_assets = []
    for asset_type, assets in ASSETS_DB.items():
        for symbol, info in assets.items():
            all_assets.append({
                "symbol": symbol,
                "name": info["name"],
                "type": asset_type.value,
                "risk": info.get("risk", "medium"),
                "extra_info": {k: v for k, v in info.items() if k != "name" and k != "risk"}
            })
    return all_assets

def get_asset_info(symbol: str) -> Dict:
    """Busca información de un activo por su símbolo"""
    for asset_type, assets in ASSETS_DB.items():
        if symbol in assets:
            return {
                "symbol": symbol,
                "name": assets[symbol]["name"],
                "type": asset_type.value,
                **assets[symbol]
            }
    return None
