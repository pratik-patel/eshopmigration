"""
Configuration loader for Migration Report Dashboard
"""

import yaml
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    type: str
    url: str

@dataclass
class ApplicationConfig:
    name: str
    frontend_url: str
    backend_url: str
    database: DatabaseConfig
    sonarqube_project: str
    source_path: str
    language: str

@dataclass
class SonarQubeConfig:
    url: str
    token: str

@dataclass
class LighthouseConfig:
    enabled: bool = True
    runs: int = 3
    throttling: str = "4g"
    categories: List[str] = field(default_factory=lambda: ["performance", "accessibility", "best-practices", "seo"])

@dataclass
class APIConfig:
    timeout: int = 30
    retries: int = 2
    verify_ssl: bool = False
    auth: Dict = field(default_factory=dict)

@dataclass
class DatabaseCollectionConfig:
    sample_queries: bool = True
    slow_query_threshold_ms: int = 100
    max_sample_size: int = 1000

@dataclass
class CoverageConfig:
    legacy_path: str
    modern_path: str
    format: str = "lcov"

@dataclass
class PerformanceConfig:
    load_test_duration: int = 60
    concurrent_users: int = 100
    ramp_up_time: int = 10

@dataclass
class CollectionConfig:
    lighthouse: LighthouseConfig
    api: APIConfig
    database: DatabaseCollectionConfig
    coverage: CoverageConfig
    performance: PerformanceConfig

@dataclass
class ScoringWeights:
    frontend: float = 0.25
    backend: float = 0.25
    database: float = 0.10
    quality: float = 0.20
    nfr: float = 0.15
    integration: float = 0.05

@dataclass
class Thresholds:
    # Frontend
    lighthouse_performance: int = 90
    lighthouse_accessibility: int = 95
    lighthouse_best_practices: int = 90
    lighthouse_seo: int = 90

    # Backend
    api_response_time_ms: int = 200
    api_error_rate: float = 0.01
    api_parity: float = 0.95

    # Database
    query_time_ms: int = 100
    schema_parity: float = 0.98

    # Quality
    test_coverage: int = 80
    sonar_reliability: str = "A"
    sonar_security: str = "A"
    sonar_maintainability: str = "A"
    code_duplication: float = 3.0

    # NFR
    response_time_p95_ms: int = 500
    response_time_p99_ms: int = 1000
    error_rate: float = 0.001
    uptime: float = 99.9

@dataclass
class ScoringConfig:
    weights: ScoringWeights
    frontend_weights: Dict = field(default_factory=dict)
    backend_weights: Dict = field(default_factory=dict)
    database_weights: Dict = field(default_factory=dict)
    quality_weights: Dict = field(default_factory=dict)
    nfr_weights: Dict = field(default_factory=dict)
    thresholds: Thresholds = field(default_factory=Thresholds)

@dataclass
class DashboardConfig:
    title: str = "Migration Assessment Dashboard"
    port: int = 8501
    theme: str = "light"
    auto_refresh: bool = False
    refresh_interval: int = 60
    cache_ttl: int = 3600
    max_data_points: int = 1000

@dataclass
class ExportConfig:
    output_dir: str = "./reports"
    formats: List[str] = field(default_factory=lambda: ["pdf", "html", "json", "excel"])
    include_screenshots: bool = True
    include_raw_data: bool = False

@dataclass
class AlertRule:
    name: str
    condition: str
    severity: str

@dataclass
class AlertsConfig:
    enabled: bool = True
    rules: List[AlertRule] = field(default_factory=list)

@dataclass
class IntegrationsConfig:
    github: Dict = field(default_factory=dict)
    jira: Dict = field(default_factory=dict)
    slack: Dict = field(default_factory=dict)

@dataclass
class AppConfig:
    legacy: ApplicationConfig
    modern: ApplicationConfig
    sonarqube: SonarQubeConfig
    collection: CollectionConfig
    scoring: ScoringConfig
    dashboard: DashboardConfig
    export: ExportConfig
    alerts: AlertsConfig
    integrations: IntegrationsConfig

def expand_env_vars(value):
    """Expand environment variables in configuration values"""
    if isinstance(value, str) and "${" in value:
        # Extract variable name
        var_name = value.replace("${", "").replace("}", "")
        return os.getenv(var_name, value)
    return value

def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to config.yaml (default: ./config.yaml)

    Returns:
        AppConfig object
    """
    if config_path is None:
        # Try to find config.yaml in skill directory
        current_dir = Path(__file__).parent.parent
        config_path = current_dir / "config.yaml"

    if not Path(config_path).exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)

    # Expand environment variables
    def expand_dict(d):
        for key, value in d.items():
            if isinstance(value, dict):
                expand_dict(value)
            else:
                d[key] = expand_env_vars(value)
        return d

    config_data = expand_dict(config_data)

    # Parse configuration
    legacy = ApplicationConfig(
        name=config_data['legacy']['name'],
        frontend_url=config_data['legacy']['frontend_url'],
        backend_url=config_data['legacy']['backend_url'],
        database=DatabaseConfig(**config_data['legacy']['database']),
        sonarqube_project=config_data['legacy']['sonarqube_project'],
        source_path=config_data['legacy']['source_path'],
        language=config_data['legacy']['language']
    )

    modern = ApplicationConfig(
        name=config_data['modern']['name'],
        frontend_url=config_data['modern']['frontend_url'],
        backend_url=config_data['modern']['backend_url'],
        database=DatabaseConfig(**config_data['modern']['database']),
        sonarqube_project=config_data['modern']['sonarqube_project'],
        source_path=config_data['modern']['source_path'],
        language=config_data['modern']['language']
    )

    sonarqube = SonarQubeConfig(**config_data['sonarqube'])

    # Collection config
    collection = CollectionConfig(
        lighthouse=LighthouseConfig(**config_data['collection']['lighthouse']),
        api=APIConfig(**config_data['collection']['api']),
        database=DatabaseCollectionConfig(**config_data['collection']['database']),
        coverage=CoverageConfig(**config_data['collection']['coverage']),
        performance=PerformanceConfig(**config_data['collection']['performance'])
    )

    # Scoring config
    scoring = ScoringConfig(
        weights=ScoringWeights(**config_data['scoring']['weights']),
        frontend_weights=config_data['scoring']['frontend_weights'],
        backend_weights=config_data['scoring']['backend_weights'],
        database_weights=config_data['scoring']['database_weights'],
        quality_weights=config_data['scoring']['quality_weights'],
        nfr_weights=config_data['scoring']['nfr_weights'],
        thresholds=Thresholds(**config_data['scoring']['thresholds'])
    )

    dashboard = DashboardConfig(**config_data['dashboard'])
    export = ExportConfig(**config_data['export'])

    # Alerts config
    alert_rules = []
    for rule_data in config_data.get('alerts', {}).get('rules', []):
        alert_rules.append(AlertRule(**rule_data))

    alerts = AlertsConfig(
        enabled=config_data.get('alerts', {}).get('enabled', True),
        rules=alert_rules
    )

    integrations = IntegrationsConfig(
        github=config_data.get('integrations', {}).get('github', {}),
        jira=config_data.get('integrations', {}).get('jira', {}),
        slack=config_data.get('integrations', {}).get('slack', {})
    )

    return AppConfig(
        legacy=legacy,
        modern=modern,
        sonarqube=sonarqube,
        collection=collection,
        scoring=scoring,
        dashboard=dashboard,
        export=export,
        alerts=alerts,
        integrations=integrations
    )

# Singleton instance
_config_instance = None

def get_config() -> AppConfig:
    """Get configuration singleton"""
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance
