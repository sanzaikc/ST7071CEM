"""
Text Classification Module

This module implements supervised text classification using Multinomial Naive Bayes.
It replaces the previous unsupervised clustering approach with a proper supervised
learning pipeline that uses labeled training data to predict document categories.

Categories:
- Business: Financial news, market trends, corporate reports
- Entertainment: Movies, music, celebrity news, arts
- Health: Medical articles, wellness, public health
"""

from .model import classifier_service
from .data import get_documents, CATEGORIES

__all__ = ["classifier_service", "get_documents", "CATEGORIES"]
