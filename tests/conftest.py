import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient  # noqa: E402

from voxserve.main import create_app  # noqa: E402
from voxserve.settings import Settings  # noqa: E402


def make_client(**settings_overrides) -> TestClient:
    settings = Settings(engine="stub", **settings_overrides)
    return TestClient(create_app(settings))
