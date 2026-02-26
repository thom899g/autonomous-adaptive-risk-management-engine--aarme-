"""
AARME Configuration Management
Centralized configuration with environment variables and defaults
"""
import os
from dataclasses import dataclass
from typing import Dict, Any
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    credential_path: str = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
    project_id: str = os.getenv('FIREBASE_PROJECT_ID', 'aarme-system')
    database_url: str = os.getenv('FIREBASE_DATABASE_URL', '')
    collection_name: str = 'aarme_states'

@dataclass
class TradingConfig:
    """Trading and risk configuration"""
    max_position_size: float = float(os.getenv('MAX_POSITION_SIZE', '0.1'))  # 10% of portfolio
    max_daily_loss: float = float(os.getenv('MAX_DAILY_LOSS', '0.02'))  # 2% daily loss limit
    risk_free_rate: float = float(os.getenv('RISK_FREE_RATE', '0.04'))  # 4% annual
    volatility_window: int = int(os.getenv('VOLATILITY_WINDOW', '20'))  # 20-day volatility
    confidence_threshold: float = float(os.getenv('CONFIDENCE_THRESHOLD', '0.65'))

@dataclass
class APIConfig:
    """External API configurations"""
    news_api_key: str = os.getenv('NEWS_API_KEY', '')
    twitter_bearer_token: str = os.getenv('TWITTER_BEARER_TOKEN', '')
    polygon_api_key: str = os.getenv('POLYGON_API_KEY', '')
    sentiment_endpoint: str = os.getenv('SENTIMENT_ENDPOINT', 'https://api.example.com/sentiment')

@dataclass
class ModelConfig:
    """ML model configurations"""
    retrain_interval_hours: int = int(os.getenv('RETRAIN_INTERVAL', '24'))
    feature_window: int = int(os.getenv('FEATURE_WINDOW', '50'))
    min_training_samples: int = int(os.getenv('MIN_TRAINING_SAMPLES', '100'))

class AARMEConfig:
    """Main configuration class"""
    def __init__(self):
        self.firebase = FirebaseConfig()
        self.trading = TradingConfig()
        self.api = APIConfig()
        self.model = ModelConfig()
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        # Validate critical configurations
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate critical configuration values"""
        if not self.firebase.credential_path or not os.path.exists(self.firebase.credential_path):
            logging.warning("Firebase credentials path not found or not configured")
        
        if self.trading.max_position_size > 0.5:
            logging.error("Max position size exceeds safe limit (50%), resetting to 10%")
            self.trading.max_position_size = 0.1
        
        if self.trading.max_daily_loss > 0.05:
            logging.error("Max daily loss exceeds safe limit (5%), resetting to 2%")
            self.trading.max_daily_loss = 0.02

# Singleton instance
config = AARMEConfig()