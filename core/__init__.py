"""
Core processing modules
"""
from .classifier import SenderClassifier
from .intent_detector import IntentDetector
from .priority_scorer import PriorityScorer
from .categorizer import EmailCategorizer
from .spam_filter import SpamFilter

__all__ = [
    'SenderClassifier',
    'IntentDetector',
    'PriorityScorer',
    'EmailCategorizer',
    'SpamFilter'
]
