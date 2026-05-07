"""
Widgets package for Pop Assistant
Contains custom dialogs and windows
"""

from .history_window import HistoryWindow
from .dialogs import (
    SettingsDialog,
    AudioDialog, 
    PersonalInfoDialog,
    HistoryUsageDialog
)
from .dashboard_dialog import DashboardDialog

__all__ = [
    'HistoryWindow',
    'SettingsDialog',
    'AudioDialog',
    'PersonalInfoDialog',
    'HistoryUsageDialog',
    'DashboardDialog'
]
