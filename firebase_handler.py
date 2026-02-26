"""
Firebase State Management Handler
Manages all Firestore operations for AARME state persistence
"""
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError

from config import config

@dataclass
class AARMEState:
    """Data class for AARME system state"""
    timestamp: datetime
    portfolio_value: float
    current_risk_score: float
    market_sentiment: float
    positions: Dict[str, Dict[str, float]]  # symbol -> {quantity, entry_price}
    last_adjustment: Optional[datetime] = None
    daily_pnl: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Firestore-compatible dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.last_adjustment:
            data['last_adjustment'] = self.last_adjustment.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AARMEState':
        """Create from Firestore dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('last_adjustment'):
            data['last_adjustment'] = datetime.fromisoformat(data['last_adjustment'])
        return cls(**data)

class FirebaseHandler:
    """Handles all Firebase Firestore operations"""
    
    def __init__(self):
        self.app = None
        self.db = None
        self._initialize_firebase()
        
    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK with error handling"""
        try:
            # Check if Firebase app already exists
            if not firebase_admin._apps:
                cred = credentials.Certificate(config.firebase.credential_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': config.firebase.project_id,
                    'databaseURL': config.firebase.database_url
                })
                logging.info("Firebase initialized successfully")
            
            self.app = firebase_admin.get_app()
            self.db = firestore.client()
            
            # Test connection
            self.db.collection('health_check').document('test').set({
                'timestamp': datetime.now(timezone.utc),
                'status': 'connected'
            })
            logging.info("Firestore connection verified")
            
        except FileNotFoundError as e:
            logging.error(f"Firebase credentials file not found: {e}")
            raise
        except ValueError as e:
            logging.error(f"Invalid Firebase configuration: {e}")
            raise
        except FirebaseError as e:
            logging.error(f"Firebase initialization error: {e}")
            raise
        except Exception as