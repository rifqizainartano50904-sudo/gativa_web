from flask_socketio import emit
from app import socketio

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

# We'll use this event to push updates from the backend to the frontend
def broadcast_patient_update(patient_data):
    """
    Broadcast patient status change to all connected dashboards.
    """
    socketio.emit('patient_updated', patient_data)

def broadcast_anomaly_alert(alert_data):
    """
    Broadcast anomaly alert to nurses on duty.
    """
    socketio.emit('anomaly_alert', alert_data)
