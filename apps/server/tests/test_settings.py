import pytest
from app.core.config import Settings
from app.core.errors import ConfigError

_JWT = "x" * 32


def _settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_dev_local_defaults_ok():
    settings = _settings(app_env="dev", platform="local")
    assert settings.platform.value == "local"
    assert settings.docs_enabled is True
    assert settings.seed_enabled is True


def test_prod_refuses_wildcard_cors():
    with pytest.raises(ConfigError, match="CORS"):
        _settings(
            app_env="prod",
            platform="local",
            cors_origins="*",
            jwt_secret=_JWT,
            anthropic_api_key="key",
        )


def test_prod_requires_strong_jwt_secret():
    with pytest.raises(ConfigError, match="JWT_SECRET"):
        _settings(
            app_env="prod",
            platform="local",
            cors_origins="https://app.example.com",
            jwt_secret="short",
            anthropic_api_key="key",
        )


def test_prod_names_missing_platform_vars():
    with pytest.raises(ConfigError) as exc:
        _settings(
            app_env="prod",
            platform="gcp",
            cors_origins="https://app.example.com",
            jwt_secret=_JWT,
        )
    message = str(exc.value)
    assert "GCP_PROJECT" in message
    assert "VERTEX_MODEL" in message


def test_dev_starts_degraded_with_incomplete_platform():
    settings = _settings(app_env="dev", platform="gcp")
    # Postgres is the repository on every platform; gcp still needs its LLM and bucket.
    assert settings.missing_env_for("repository") == []
    assert "GCP_PROJECT" in settings.missing_env_for("llm")
    assert "GCS_BUCKET" in settings.missing_env_for("storage")


def test_prod_complete_aws_config_ok():
    settings = _settings(
        app_env="prod",
        platform="aws",
        cors_origins="https://app.example.com",
        jwt_secret=_JWT,
        aws_region="us-east-1",
        ddb_table_prefix="quantastica",
        sqs_queue_url="https://sqs.example/q",
        s3_bucket="bucket",
        bedrock_model_id="anthropic.claude-3-haiku-20240307-v1:0",
    )
    assert settings.is_prod
    assert settings.auth_enabled is True
    assert settings.docs_enabled is False
