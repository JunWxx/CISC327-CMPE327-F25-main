# TEST/conftest.py
import pytest
import database as db

@pytest.fixture(autouse=True)
def _fresh_db(tmp_path, monkeypatch):
   
    monkeypatch.setattr(db, "DATABASE", str(tmp_path / "test_library.db"))
    db.init_database()
    db.add_sample_data()
    yield
