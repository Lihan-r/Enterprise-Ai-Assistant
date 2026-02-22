"""
config.py - Application Configuration

Think of this like application.properties in Spring Boot.
It loads values from the .env file and makes them available
throughout the app.

In Java you'd use @Value("${property}") — in Python we use
pydantic-settings to do the same thing but with type safety.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # These fields map directly to your .env file keys
    # Python convention: lowercase with underscores (not camelCase like Java)

    app_name: str = "Enterprise AI Assistant"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database — no default, so the app fails fast if DATABASE_URL is not set
    database_url: str

    # Gemini — no default, so the app fails fast if the key is missing
    gemini_api_key: str

    # Security — empty api_key means auth is disabled (dev convenience)
    api_key: str = ""
    cors_origins: str = "http://localhost:8000,http://localhost:8001"

    # Rate limiting
    rate_limit_default: str = "30/minute"
    rate_limit_query: str = "10/minute"  # tighter for expensive Gemini calls

    model_config = {
        "env_file": ".env",
    }


# Create a single instance (like a @Bean in Spring)
# Other files will import this directly
settings = Settings()
