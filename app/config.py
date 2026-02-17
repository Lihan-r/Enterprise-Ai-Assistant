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
    debug: bool = True

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/enterprise_assistant"

    # Gemini
    gemini_api_key: str = ""

    class Config:
        # This tells pydantic to read from the .env file
        env_file = ".env"


# Create a single instance (like a @Bean in Spring)
# Other files will import this directly
settings = Settings()
