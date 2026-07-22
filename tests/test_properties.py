"""Unit tests for hooks/claude/shared/config.py — the properties system."""

import sys
from pathlib import Path

import pytest

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "hooks" / "claude"))

from shared import config as props  # noqa: E402


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("ARCHON_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


@pytest.fixture
def project(tmp_path):
    proj = tmp_path / "proj"
    (proj / ".archon").mkdir(parents=True)
    return proj


class TestPrecedence:
    def test_default_when_nothing_set(self, home):
        value, source = props.resolve_property("gate/max_blocks")
        assert value == 2
        assert source == "default"

    def test_user_file_beats_default(self, home):
        props.set_property("gate/max_blocks", "5")
        value, source = props.resolve_property("gate/max_blocks")
        assert value == 5
        assert source == "user"

    def test_project_file_beats_user(self, home, project):
        props.set_property("gate/max_blocks", "5")
        props.set_property("gate/max_blocks", "7", cwd=str(project), project=True)
        value, source = props.resolve_property("gate/max_blocks", cwd=str(project))
        assert value == 7
        assert source == "project"

    def test_env_beats_everything(self, home, project, monkeypatch):
        props.set_property("gate/max_blocks", "5")
        props.set_property("gate/max_blocks", "7", cwd=str(project), project=True)
        monkeypatch.setenv("ARCHON_GATE_MAX_BLOCKS", "9")
        value, source = props.resolve_property("gate/max_blocks", cwd=str(project))
        assert value == 9
        assert source == "env"

    def test_env_var_name_derivation(self):
        assert props.env_var_name("gate", "max_blocks") == "ARCHON_GATE_MAX_BLOCKS"
        assert (
            props.env_var_name("classifier", "trivial_max_words")
            == "ARCHON_CLASSIFIER_TRIVIAL_MAX_WORDS"
        )


class TestCoercion:
    def test_bool_words(self, home, monkeypatch):
        for word, expected in [
            ("true", True),
            ("1", True),
            ("yes", True),
            ("ON", True),
            ("false", False),
            ("0", False),
            ("no", False),
            ("off", False),
        ]:
            monkeypatch.setenv("ARCHON_GATE_ENABLED", word)
            assert props.get_property("gate/enabled") is expected

    def test_malformed_bool_falls_back_to_default(self, home, monkeypatch):
        monkeypatch.setenv("ARCHON_GATE_ENABLED", "banana")
        assert props.get_property("gate/enabled") is True

    def test_malformed_int_falls_back_to_default(self, home, monkeypatch):
        monkeypatch.setenv("ARCHON_GATE_MAX_BLOCKS", "not-a-number")
        assert props.get_property("gate/max_blocks") == 2

    def test_string_passthrough(self, home, monkeypatch):
        monkeypatch.setenv("ARCHON_SCANNER_EXTRA_ALLOWLIST", r"fixtures/, \.golden$")
        assert props.get_property("scanner/extra_allowlist") == r"fixtures/, \.golden$"


class TestWriteRoundTrip:
    def test_set_get_unset(self, home):
        path = props.set_property("logging/max_log_days", "14")
        assert path == props.user_config_path()
        assert props.get_property("logging/max_log_days") == 14
        assert props.unset_property("logging/max_log_days") == path
        assert props.get_property("logging/max_log_days") == 30
        # unsetting again is a no-op returning None
        assert props.unset_property("logging/max_log_days") is None

    def test_set_rejects_bad_values(self, home):
        with pytest.raises(ValueError):
            props.set_property("gate/enabled", "banana")
        with pytest.raises(ValueError):
            props.set_property("gate/max_blocks", "banana")

    def test_unknown_key_raises(self, home):
        with pytest.raises(KeyError):
            props.get_property("nope/nothing")
        with pytest.raises(KeyError):
            props.set_property("nope/nothing", "1")

    def test_corrupt_ini_treated_as_absent(self, home):
        path = props.user_config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("this is [ not INI ][", encoding="utf-8")
        value, source = props.resolve_property("gate/max_blocks")
        assert value == 2
        assert source == "default"


class TestRegistry:
    def test_load_all_covers_registry(self, home):
        resolved = props.load_all()
        assert set(resolved) == set(props.PROPERTIES)
        assert all(source == "default" for _, source in resolved.values())

    def test_every_property_has_help(self):
        for key, prop in props.PROPERTIES.items():
            assert prop.help, f"{key} missing help text"
