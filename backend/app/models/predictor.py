import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from datetime import datetime
from typing import List, Dict, Tuple

class InvestmentPredictor:
    """
    Modelo de predicción ensemble que combina:
    - Random Forest
    - Gradient Boosting
    - Análisis de momentum
    - Análisis de volumen
    
    Objetivo: Maximizar el % de acierto en predicciones direccionales
    """
    
    def __init__(self):
        self.model_rf = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model_gb = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=10,
            learning_rate=0.1,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "backend/app/models/saved_model"
        
        # Features que usamos para predecir
        self.features = [
            'Daily_Return', 'RSI', 'MACD', 'Volatility',
            'MA7', 'MA30', 'volume'
        ]
        
        self.load_model()
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara las features para el modelo
        """
        data = df.copy()
        
        # Normalizar volumen
        data['volume'] = data['Volume'] / data['Volume'].rolling(window=20).mean()
        
        # Posición relativa a medias móviles
        data['MA7_position'] = (data['Close'] - data['MA7']) / data['MA7']
        data['MA30_position'] = (data['Close'] - data['MA30']) / data['MA30']
        
        # Momentum
        data['momentum_5'] = data['Close'].pct_change(periods=5)
        data['momentum_10'] = data['Close'].pct_change(periods=10)
        
        # Llenar NaN
        data = data.fillna(method='ffill').fillna(method='bfill')
        
        return data
    
    def train(self, historical_data: pd.DataFrame, symbol: str) -> Dict:
        """
        Entrena el modelo con datos históricos
        """
        try:
            # Preparar datos
            data = self.prepare_features(historical_data)
            
            # Features y target
            X = data[self.features + ['MA7_position', 'MA30_position', 'momentum_5', 'momentum_10']]
            y = data['Next_Day_Return'].shift(-1).dropna()
            X = X.loc[y.index]
            
            if len(X) < 30:
                return {"error": "No hay suficientes datos para entrenar"}
            
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entrenar Random Forest
            self.model_rf.fit(X_train_scaled, y_train)
            y_pred_rf = self.model_rf.predict(X_test_scaled)
            
            # Entrenar Gradient Boosting
            self.model_gb.fit(X_train_scaled, y_train)
            y_pred_gb = self.model_gb.predict(X_test_scaled)
            
            # Calcular métricas
            mse_rf = mean_squared_error(y_test, y_pred_rf)
            mse_gb = mean_squared_error(y_test, y_pred_gb)
            
            # Accuracy direccional (si predice bien si sube o baja)
            direction_rf = (np.sign(y_pred_rf) == np.sign(y_test.values)).mean()
            direction_gb = (np.sign(y_pred_gb) == np.sign(y_test.values)).mean()
            
            self.is_trained = True
            self.save_model(symbol)
            
            return {
                "status": "success",
                "symbol": symbol,
                "samples": len(X_train),
                "mse_rf": round(mse_rf, 6),
                "mse_gb": round(mse_gb, 6),
                "accuracy_rf": round(direction_rf * 100, 2),
                "accuracy_gb": round(direction_gb * 100, 2),
                "best_model": "Random Forest" if direction_rf > direction_gb else "Gradient Boosting",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def predict(self, current_data: pd.DataFrame) -> float:
        """
        Predice el retorno del día siguiente
        Retorna: porcentaje esperado de cambio
        """
        if not self.is_trained:
            return 0.0
        
        try:
            data = self.prepare_features(current_data)
            
            # Obtener última fila
            X = data[self.features + ['MA7_position', 'MA30_position', 'momentum_5', 'momentum_10']].tail(1)
            
            # Escalar
            X_scaled = self.scaler.transform(X)
            
            # Predicciones de ambos modelos
            pred_rf = self.model_rf.predict(X_scaled)[0]
            pred_gb = self.model_gb.predict(X_scaled)[0]
            
            # Ensemble: promedio ponderado (RF tiene más peso por ser más estable)
            prediction = (pred_rf * 0.6) + (pred_gb * 0.4)
            
            return round(prediction * 100, 4)  # Retornar en porcentaje
        
        except Exception as e:
            print(f"❌ Error en predicción: {str(e)}")
            return 0.0
    
    def predict_multiple_assets(self, assets_data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        Predice para múltiples activos y retorna los mejores
        """
        predictions = []
        
        for symbol, data in assets_data.items():
            pred = self.predict(data)
            
            # Obtener último precio
            last_price = data['Close'].iloc[-1]
            
            predictions.append({
                "symbol": symbol,
                "predicted_return": pred,
                "current_price": round(last_price, 4),
                "predicted_price": round(last_price * (1 + pred/100), 4),
                "confidence": "high" if abs(pred) > 2 else "medium" if abs(pred) > 1 else "low"
            })
        
        # Ordenar por predicción descendente
        predictions.sort(key=lambda x: x['predicted_return'], reverse=True)
        
        return predictions
    
    def save_model(self, symbol: str):
        """Guarda el modelo entrenado"""
        os.makedirs(self.model_path, exist_ok=True)
        joblib.dump(self.model_rf, f"{self.model_path}/rf_{symbol}.pkl")
        joblib.dump(self.model_gb, f"{self.model_path}/gb_{symbol}.pkl")
        joblib.dump(self.scaler, f"{self.model_path}/scaler_{symbol}.pkl")
    
    def load_model(self):
        """Carga el modelo si existe"""
        # Se cargará dinámicamente según el símbolo
        pass
    
    def get_feature_importance(self) -> Dict:
        """Retorna la importancia de las features"""
        if not self.is_trained:
            return {}
        
        importance = dict(zip(self.features, self.model_rf.feature_importances_))
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return {k: round(v, 4) for k, v in sorted_importance}
