import time
from app import create_app, db
from app.models import Patient, HealthMetric, FoodLog
from app.main.events import broadcast_anomaly_alert
from datetime import datetime, timedelta

app = create_app()

def check_anomalies():
    """
    Background job to detect anomalies:
    Trend BP naik + riwayat sodium tinggi 3 hari berturut-turut.
    """
    with app.app_context():
        print("Running Anomaly Detection Job...")
        patients = Patient.query.all()
        for p in patients:
            # Check 3 days sodium history
            # For mockup, we just check if current status is Bahaya and BP is high
            metrics = HealthMetric.query.filter_by(patient_id=p.id).order_by(HealthMetric.recorded_at.desc()).limit(2).all()
            
            bp_rising = False
            if len(metrics) >= 2:
                # If latest systolic is higher than previous
                if metrics[0].systolic_bp > metrics[1].systolic_bp and metrics[0].systolic_bp > 130:
                    bp_rising = True
            
            # Simple mock logic for 3 days:
            # Since generating 3 days of historical mock data is complex, we use current status.
            sodium_high = (p.status == 'Bahaya')
            
            if bp_rising and sodium_high:
                alert_data = {
                    'patient_id': p.id,
                    'patient_name': p.name,
                    'message': f"Peringatan: Tren BP {p.name} meningkat (Sys: {metrics[0].systolic_bp}) dengan asupan Natrium berlebih!"
                }
                print(f"ANOMALY DETECTED: {alert_data}")
                broadcast_anomaly_alert(alert_data)

# NOTE: In a real app, use APScheduler or Celery. 
# For demonstration, we could call this function manually via a test route or script.
