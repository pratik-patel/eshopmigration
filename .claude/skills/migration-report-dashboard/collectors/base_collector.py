"""
Base Collector Class
All metric collectors inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """
    Abstract base class for metric collectors

    Each collector is responsible for gathering specific metrics
    from either legacy or modern applications.
    """

    def __init__(self, config: Any, app_type: str = "modern"):
        """
        Initialize collector

        Args:
            config: Application configuration
            app_type: "legacy" or "modern"
        """
        self.config = config
        self.app_type = app_type
        self.logger = logger

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """
        Collect metrics

        Returns:
            Dictionary containing collected metrics
        """
        pass

    def validate(self, metrics: Dict[str, Any]) -> bool:
        """
        Validate collected metrics

        Args:
            metrics: Metrics to validate

        Returns:
            True if valid, False otherwise
        """
        return metrics is not None and len(metrics) > 0

    def enrich(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich metrics with metadata

        Args:
            metrics: Raw metrics

        Returns:
            Enriched metrics with metadata
        """
        enriched = metrics.copy()
        enriched['timestamp'] = datetime.now().isoformat()
        enriched['app_type'] = self.app_type
        enriched['collector'] = self.__class__.__name__
        return enriched

    def safe_collect(self) -> Dict[str, Any]:
        """
        Safely collect metrics with error handling

        Returns:
            Collected metrics or empty dict on error
        """
        try:
            self.logger.info(f"Collecting metrics with {self.__class__.__name__}...")
            metrics = self.collect()

            if not self.validate(metrics):
                self.logger.warning(f"Validation failed for {self.__class__.__name__}")
                return {}

            enriched = self.enrich(metrics)
            self.logger.info(f"Successfully collected metrics with {self.__class__.__name__}")
            return enriched

        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__}: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'collector': self.__class__.__name__
            }
