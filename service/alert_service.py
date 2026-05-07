#!/usr/bin/env python3
"""
Alert Service - Compatibility Wrapper
"""

from service.alert import (
    AlertLevel, AlertThreshold, Alert,
    AlertNotifier,
    AlertManager,
    get_alert_manager
)

__all__ = [
    'AlertLevel', 'AlertThreshold', 'Alert',
    'AlertNotifier',
    'AlertManager', 'get_alert_manager'
]
