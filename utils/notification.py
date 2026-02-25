"""
Notification system for Auralite
"""

from datetime import datetime
import json

class NotificationManager:
    """Manage notifications for the Auralite system"""
    
    def __init__(self):
        self.notifications = []
        self.subscribers = []
    
    def create_notification(self, title, message, severity='INFO', location_id=None):
        """Create a new notification"""
        notification = {
            'id': f'notif_{datetime.now().timestamp()}',
            'title': title,
            'message': message,
            'severity': severity,
            'location_id': location_id,
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'acknowledged': False
        }
        self.notifications.append(notification)
        return notification
    
    def get_unread(self):
        """Get unread notifications"""
        return [n for n in self.notifications if not n['read']]
    
    def mark_read(self, notification_id):
        """Mark a notification as read"""
        for n in self.notifications:
            if n['id'] == notification_id:
                n['read'] = True
                return True
        return False
    
    def acknowledge(self, notification_id):
        """Acknowledge a notification"""
        for n in self.notifications:
            if n['id'] == notification_id:
                n['acknowledged'] = True
                n['acknowledged_at'] = datetime.now().isoformat()
                return True
        return False
    
    def get_recent(self, limit=50):
        """Get recent notifications"""
        return self.notifications[-limit:]
    
    def get_by_severity(self, severity):
        """Get notifications by severity level"""
        return [n for n in self.notifications if n['severity'] == severity]
