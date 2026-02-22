"""
Advanced scanning service with machine learning capabilities
"""

import asyncio
import hashlib
from typing import Dict, List, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import pickle
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AdvancedScannerService:
    """Advanced scanning with ML-based anomaly detection"""
    
    def __init__(self, db):
        self.db = db
        self.model_path = Path("models/anomaly_detector.pkl")
        self._load_model()
    
    def _load_model(self):
        """Load or create ML model"""
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                logger.info("ML model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}. Creating new one.")
                self.model = IsolationForest(contamination=0.1, random_state=42)
        else:
            self.model = IsolationForest(contamination=0.1, random_state=42)
            logger.info("Created new ML model")
    
    def _save_model(self):
        """Save ML model"""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
    
    def extract_features(self, content: str, file_metadata: Dict) -> List[float]:
        """Extract features for ML analysis"""
        features = []
        
        # Text-based features
        features.append(len(content))  # File size
        features.append(content.count('\n'))  # Number of lines
        features.append(len(content.split()))  # Word count
        
        # Entropy features
        features.append(self._calculate_entropy(content))
        
        # Structural features
        features.append(content.count('='))  # Assignment operations
        features.append(content.count('"'))  # Double quotes
        features.append(content.count("'"))  # Single quotes
        features.append(content.count('{'))  # Braces
        features.append(content.count('('))  # Parentheses
        
        # Suspicious pattern densities
        features.append(content.lower().count('password'))
        features.append(content.lower().count('secret'))
        features.append(content.lower().count('key'))
        features.append(content.lower().count('token'))
        
        return features
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0
        
        entropy = 0
        for x in range(256):
            p_x = float(text.count(chr(x))) / len(text)
            if p_x > 0:
                entropy += - p_x * np.log2(p_x)
        
        return entropy
    
    async def detect_anomalies(self, files: List[Dict]) -> List[Dict]:
        """Detect anomalous files using ML"""
        try:
            # Extract features
            features = []
            file_indices = []
            
            for i, file_data in enumerate(files):
                file_features = self.extract_features(
                    file_data['content'], 
                    file_data.get('metadata', {})
                )
                features.append(file_features)
                file_indices.append(i)
            
            if not features:
                return []
            
            # Predict anomalies
            features_array = np.array(features)
            predictions = self.model.fit_predict(features_array)
            
            # Get anomaly scores
            scores = self.model.decision_function(features_array)
            
            # Prepare results
            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:  # Anomaly detected
                    file_data = files[file_indices[i]]
                    anomalies.append({
                        'file': file_data.get('filename', 'unknown'),
                        'anomaly_score': float(score),
                        'features': features[i],
                        'reason': self._explain_anomaly(features[i])
                    })
            
            # Update model with new data (in background)
            asyncio.create_task(self._update_model_async(features_array))
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def _explain_anomaly(self, features: List[float]) -> str:
        """Generate human-readable explanation for anomaly"""
        explanations = []
        
        if features[0] > 10000:  # Large file size
            explanations.append("unusually large file")
        
        if features[3] > 4.5:  # High entropy
            explanations.append("high entropy content")
        
        if features[9] > 5:  # Many password mentions
            explanations.append("multiple password references")
        
        return ", ".join(explanations) if explanations else "statistical outlier"
    
    async def _update_model_async(self, new_features: np.ndarray):
        """Update ML model with new data asynchronously"""
        try:
            # Partial fit with new data
            self.model.partial_fit(new_features)
            self._save_model()
            logger.info("ML model updated successfully")
        except Exception as e:
            logger.error(f"Model update failed: {e}")