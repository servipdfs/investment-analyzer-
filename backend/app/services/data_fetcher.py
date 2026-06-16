import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

class DataFetcher:
    """
    Servicio unificado para obtener datos de:
    - Criptomonedas (Yahoo Finance + CoinGecko fallback)
    - Acciones (Yahoo Finance)
    - Materias Primas (Yahoo Finance)
    - Forex (Yahoo Finance)
    - Índices (Yahoo Finance)
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.coingecko_base = "https://api.coingecko.com/api/v3"
    
    def get_historical_data(self, symbol: str, days: int = 60) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos de cualquier activo
        Retorna: DataFrame con columns: Open, High, Low, Close, Volume
        """
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                print(f"⚠️ No hay datos para {symbol}")
                return None
            
            # Calcular indicadores técnicos
            df = self._add_technical_indicators(df)
            
            return df
        
        except Exception as e:
            print(f"❌ Error obteniendo datos de {symbol}: {str(e)}")
            return None
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Obtiene precios actuales de múltiples activos
        Retorna: dict {symbol: {price, change, change_percent, volume}}
        """
        prices = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Precio actual
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                
                # Cambio porcentual
                change_percent = info.get('regularMarketChangePercent') or 0
                
                # Volumen
                volume = info.get('volume') or info.get('regularMarketVolume') or 0
                
                prices[symbol] = {
                    "price": round(current_price, 4),
                    "change_percent": round(change_percent, 2),
                    "volume": volume,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Rate limiting para no saturar API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error en {symbol}: {str(e)}")
                prices[symbol] = None
        
        return prices
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Añade indicadores técnicos al DataFrame
        """
        # Media móvil 7 días
        df['MA7'] = df['Close'].rolling(window=7).mean()
        
        # Media móvil 30 días
        df['MA30'] = df['Close'].rolling(window=30).mean()
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Volatilidad (desviación estándar)
        df['Volatility'] = df['Close'].pct_change().rolling(window=14).std()
        
        # Retorno del día siguiente (para entrenamiento del modelo)
        df['Next_Day_Return'] = df['Close'].shift(-1).pct_change()
        
        # Retorno porcentual diario
        df['Daily_Return'] = df['Close'].pct_change()
        
        return df
    
    def get_top_gainers(self, symbols: List[str], limit: int = 10) -> List[Dict]:
        """
        Obtiene los activos con mayor ganancia del día
        """
        prices = self.get_current_prices(symbols)
        
        gainers = [
            {
                "symbol": symbol,
                **data
            }
            for symbol, data in prices.items()
            if data and data['change_percent'] > 0
        ]
        
        # Ordenar por cambio porcentual descendente
        gainers.sort(key=lambda x: x['change_percent'], reverse=True)
        
        return gainers[:limit]
    
    def get_top_losers(self, symbols: List[str], limit: int = 10) -> List[Dict]:
        """
        Obtiene los activos con mayor pérdida del día
        """
        prices = self.get_current_prices(symbols)
        
        losers = [
            {
                "symbol": symbol,
                **data
            }
            for symbol, data in prices.items()
            if data and data['change_percent'] < 0
        ]
        
        # Ordenar por cambio porcentual ascendente
        losers.sort(key=lambda x: x['change_percent'])
        
        return losers[:limit]
