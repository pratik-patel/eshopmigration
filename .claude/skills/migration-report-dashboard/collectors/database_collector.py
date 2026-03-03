"""
Database Metrics Collector
Compares schemas and measures query performance
"""

from sqlalchemy import create_engine, inspect, text
from typing import Dict, Any, List
import time
from collectors.base_collector import BaseCollector

class DatabaseCollector(BaseCollector):
    """
    Collects database schema and performance metrics
    """

    def __init__(self, config: Any, app_type: str = "modern"):
        super().__init__(config, app_type)

        if app_type == "legacy":
            db_config = config.legacy.database
        else:
            db_config = config.modern.database

        self.db_url = db_config.url
        self.db_type = db_config.type

    def collect(self) -> Dict[str, Any]:
        """
        Collect database metrics

        Returns:
            Schema and performance metrics
        """
        try:
            engine = create_engine(self.db_url)

            # Get schema information
            schema_info = self.get_schema_info(engine)

            # Get performance metrics
            performance = self.get_performance_metrics(engine)

            metrics = {
                **schema_info,
                **performance
            }

            engine.dispose()
            return metrics

        except Exception as e:
            self.logger.error(f"Error collecting database metrics: {e}")
            return self.get_empty_metrics()

    def get_schema_info(self, engine) -> Dict[str, Any]:
        """
        Extract schema information

        Args:
            engine: SQLAlchemy engine

        Returns:
            Schema metrics
        """
        inspector = inspect(engine)

        tables = inspector.get_table_names()
        total_columns = 0
        total_indexes = 0
        total_foreign_keys = 0

        table_details = []

        for table in tables:
            columns = inspector.get_columns(table)
            indexes = inspector.get_indexes(table)
            foreign_keys = inspector.get_foreign_keys(table)

            total_columns += len(columns)
            total_indexes += len(indexes)
            total_foreign_keys += len(foreign_keys)

            table_details.append({
                'name': table,
                'columns': len(columns),
                'indexes': len(indexes),
                'foreign_keys': len(foreign_keys),
                'column_names': [c['name'] for c in columns]
            })

        return {
            'total_tables': len(tables),
            'total_columns': total_columns,
            'total_indexes': total_indexes,
            'total_foreign_keys': total_foreign_keys,
            'tables': table_details
        }

    def get_performance_metrics(self, engine) -> Dict[str, Any]:
        """
        Measure database performance

        Args:
            engine: SQLAlchemy engine

        Returns:
            Performance metrics
        """
        query_times = []

        # Test simple query
        test_queries = [
            "SELECT 1",
            "SELECT COUNT(*) FROM information_schema.tables" if self.db_type != 'sqlserver' else "SELECT COUNT(*) FROM sys.tables"
        ]

        for query in test_queries:
            try:
                start = time.time()
                with engine.connect() as conn:
                    conn.execute(text(query))
                elapsed = (time.time() - start) * 1000  # Convert to ms
                query_times.append(elapsed)
            except Exception as e:
                self.logger.warning(f"Query failed: {e}")

        avg_query_time = sum(query_times) / len(query_times) if query_times else 0

        return {
            'avg_query_time_ms': round(avg_query_time, 2),
            'connection_test': len(query_times) > 0
        }

    def get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'total_tables': 0,
            'total_columns': 0,
            'total_indexes': 0,
            'total_foreign_keys': 0,
            'tables': [],
            'avg_query_time_ms': 0,
            'connection_test': False
        }
