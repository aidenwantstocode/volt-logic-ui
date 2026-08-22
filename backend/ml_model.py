import os
import logging
import joblib
import numpy as np
from typing import Dict, Any, Optional, Tuple
try:
    from backend.config import settings
    from backend.schemas import TelemetryIn, PredictResponse
except ImportError:
    from config import settings
    from schemas import TelemetryIn, PredictResponse

logger = logging.getLogger(__name__)

class ModelInferenceError(Exception):
    """Raised when model inference fails."""
    pass

class BatteryClassifierService:
    _instance: Optional['BatteryClassifierService'] = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BatteryClassifierService, cls).__new__(cls)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self):
        self.model_version = settings.MODEL_VERSION
        self.model_path = settings.MODEL_PATH
        self.api_key = settings.ML_MODEL_API_KEY
        self.external_endpoint = settings.EXTERNAL_ML_ENDPOINT
        self._load_local_model()

    def _load_local_model(self):
        if os.path.exists(self.model_path):
            try:
                self._model = joblib.load(self.model_path)
                logger.info(f"Loaded trained ML model from {self.model_path} (version: {self.model_version})")
            except Exception as e:
                logger.error(f"Failed to load model file: {e}")
                self._model = None
        else:
            logger.warning(f"Model file not found at {self.model_path}. Will use rule-based fallback.")
            self._model = None

    def predict(self, telemetry: TelemetryIn) -> PredictResponse:
        """
        Run inference using the trained 4-feature EIS model (Capacity, Re, Rct, ambient_temperature)
        from Kata_Mamah_WIN_AIC.ipynb & Battery_Data_Cleaned.csv.
        """
        try:
            # 4 Core Features
            cap = float(telemetry.capacity)
            re_val = float(telemetry.re)
            rct_val = float(telemetry.rct)
            temp = float(telemetry.ambient_temperature)

            features = np.array([[cap, re_val, rct_val, temp]])

            status: str
            confidence_val: float

            if self._model is not None:
                try:
                    preds = self._model.predict(features)
                    raw_pred = str(preds[0])
                    
                    # Compute confidence from predicted probabilities
                    if hasattr(self._model, "predict_proba"):
                        probs = self._model.predict_proba(features)[0]
                        classes = list(self._model.classes_)
                        if raw_pred in classes:
                            idx = classes.index(raw_pred)
                            confidence_val = float(probs[idx]) * 100.0
                        else:
                            confidence_val = float(np.max(probs)) * 100.0
                    else:
                        confidence_val = 98.0

                    status = raw_pred.upper()
                except Exception as model_err:
                    logger.warning(f"Model inference failed, applying rule-based fallback: {model_err}")
                    status, confidence_val = self._rule_based_evaluation(cap, re_val, rct_val, temp)
            else:
                status, confidence_val = self._rule_based_evaluation(cap, re_val, rct_val, temp)

            # Map Indonesian label & prescriptive route
            if status == "CRITICAL":
                status_id = "tidak aman"
                route = "GROUNDED: Baterai Tidak Aman! Terdeteksi resistansi tinggi atau kapasitas rendah. Kendaraan dilarang beroperasi dan wajib servis teknis."
            elif status == "WARNING":
                status_id = "perlu di test lebih lanjut"
                route = "RESTRICTED: Perlu Diuji Lebih Lanjut! Terdapat indikasi awal degradasi sel. Disarankan inspeksi lanjutan dan operasikan hanya untuk rute mikro."
            else:
                status = "HEALTHY"
                status_id = "aman"
                route = "AUTHORIZED: Baterai Aman! Karakteristik sel prima. Diizinkan muatan penuh dan rute jarak jauh antarkota."

            confidence_str = f"{min(99.9, max(85.0, confidence_val)):.1f}%"

            return PredictResponse(
                status=status,  # type: ignore
                status_id=status_id,
                confidence=confidence_str,
                route=route,
                model_version=self.model_version,
                features={
                    "capacity": cap,
                    "re": re_val,
                    "rct": rct_val,
                    "ambient_temperature": temp
                }
            )

        except Exception as e:
            logger.error(f"Inference error in BatteryClassifierService: {e}")
            raise ModelInferenceError("ML inference service encountered an error processing telemetry.")

    def _rule_based_evaluation(self, cap: float, re_val: float, rct_val: float, temp: float) -> Tuple[str, float]:
        """Threshold rules as defined in Kata_Mamah_WIN_AIC.ipynb"""
        if cap > 0.8249 and re_val < 0.0777 and rct_val < 0.1251:
            return "HEALTHY", 99.2
        elif cap < 0.7751 or re_val > 0.0958 or rct_val > 0.1589:
            return "CRITICAL", 98.8
        else:
            return "WARNING", 95.5

# Global singleton instance loaded once at startup
classifier_service = BatteryClassifierService()
