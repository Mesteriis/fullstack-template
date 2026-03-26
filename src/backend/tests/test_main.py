import importlib
import runpy
import sys

import pytest

from tests.helpers import build_settings


def test_main_module_imports_and_runs_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, object]] = []
    settings = build_settings(api={"host": "127.0.0.1", "port": 9100, "reload": True})

    monkeypatch.setattr("core.settings.get_settings", lambda: settings)
    monkeypatch.setattr(
        "core.observability.setup_logging", lambda received_settings: calls.append(("logging", received_settings))
    )
    monkeypatch.setattr("core.bootstrap.create_app", lambda *, settings=None: "app")
    monkeypatch.setattr("uvicorn.run", lambda *args, **kwargs: calls.append(("uvicorn", (args, kwargs))))
    sys.modules.pop("main", None)

    main_module = importlib.import_module("main")

    assert main_module.app == "app"
    assert main_module.settings is settings
    assert calls == [("logging", settings)]

    main_module.run()

    assert calls[-1] == (
        "uvicorn",
        (
            ("main:app",),
            {"host": "127.0.0.1", "port": 9100, "reload": True, "log_config": None},
        ),
    )


def test_main_module_executes_run_when_started_as_script(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    settings = build_settings(api={"host": "0.0.0.0", "port": 8001, "reload": False})

    monkeypatch.setattr("core.settings.get_settings", lambda: settings)
    monkeypatch.setattr("core.observability.setup_logging", lambda received_settings: None)
    monkeypatch.setattr("core.bootstrap.create_app", lambda *, settings=None: "app")
    monkeypatch.setattr("uvicorn.run", lambda *args, **kwargs: calls.append((args, kwargs)))
    sys.modules.pop("main", None)

    runpy.run_module("main", run_name="__main__")

    assert calls == [(("main:app",), {"host": "0.0.0.0", "port": 8001, "reload": False, "log_config": None})]
