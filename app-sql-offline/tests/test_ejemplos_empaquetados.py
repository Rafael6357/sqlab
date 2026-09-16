"""Spec fix-ejemplos-empaquetados — presets TIENDA/BIBLIOTECA funcionan en el .exe."""
from __future__ import annotations

import os
import sys


def _app_root() -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def test_bundle_dir_dev_apunta_a_app_root():
    """EE-01: en desarrollo el dir base contiene examples/ con ambos presets."""
    from ui.main_window import MainWindow
    base = MainWindow._bundle_dir()
    assert os.path.normpath(base) == _app_root(), f"_bundle_dir()={base}"
    for f in ("ejemplo_tienda.json", "ejemplo_biblioteca.json"):
        p = os.path.join(base, "examples", f)
        assert os.path.exists(p), f"falta en dev: {p}"


def test_bundle_dir_frozen_usa_meipass(monkeypatch, tmp_path):
    """EE-02: frozen → raíz del bundle (sys._MEIPASS)."""
    from ui.main_window import MainWindow
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert MainWindow._bundle_dir() == str(tmp_path)


def test_bundle_dir_frozen_sin_meipass_fallback(monkeypatch):
    """Edge: frozen sin _MEIPASS → fallback a ruta dev (no crashea)."""
    from ui.main_window import MainWindow
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    assert os.path.normpath(MainWindow._bundle_dir()) == _app_root()


def test_runspec_empaqueta_examples():
    """EE-03: run.spec incluye app-sql-offline/examples → examples en datas."""
    spec = os.path.join(_app_root(), "..", "run.spec")
    with open(spec, encoding="utf-8") as fh:
        texto = fh.read()
    assert "app-sql-offline/examples" in texto, "run.spec no empaqueta examples/"
    assert '"examples"' in texto or "'examples'" in texto, "run.spec sin destino 'examples'"


def test_preset_tienda_carga(app):
    """EE-04: EJEMPLO: TIENDA carga tablas en el engine."""
    assert app.cargar_preset("ejemplo_tienda.json") is True
    assert len(app.engine.table_names()) >= 1


def test_preset_biblioteca_carga(app):
    """EE-04: EJEMPLO: BIBLIOTECA carga tablas en el engine."""
    assert app.cargar_preset("ejemplo_biblioteca.json") is True
    assert len(app.engine.table_names()) >= 1


def test_csvs_ejemplo_presentes():
    """EE-05: examples/csv viaja con el bundle (productos + clientes)."""
    csv_dir = os.path.join(_app_root(), "examples", "csv")
    for f in ("productos.csv", "clientes.csv"):
        assert os.path.exists(os.path.join(csv_dir, f)), f"falta: {f}"
