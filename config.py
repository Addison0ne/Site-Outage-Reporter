import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    sql_server: str = os.getenv("SQL_SERVER", "localhost")
    sql_database: str = os.getenv("SQL_DATABASE", "OutageReporter")
    sql_username: str = os.getenv("SQL_USERNAME", "sa")
    sql_password: str = os.getenv("SQL_PASSWORD", "YourStrong!Passw0rd")
    sql_driver: str = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
    poll_interval_minutes: int = int(os.getenv("POLL_INTERVAL_MINUTES", "10"))
    enable_scheduler: bool = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    require_auth: bool = os.getenv("REQUIRE_AUTH", "true").lower() == "true"

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"mssql+pyodbc://{self.sql_username}:{self.sql_password}@"
            f"{self.sql_server}/{self.sql_database}"
            f"?driver={self.sql_driver.replace(' ', '+')}&TrustServerCertificate=yes"
        )


settings = Settings()
