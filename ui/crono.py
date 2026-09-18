"""Cronómetro/temporizador por ejercicio (spec cronometro-ejercicio).

Mixin extraído de MainWindow (split Fase 2): builder del marco compacto
del HUD + toda la lógica CRONO/TEMPO. Solo toca atributos `crono_*`,
`_crono_*` y usa `MainWindow._toast` vía MRO.
"""
from __future__ import annotations

import math
import time

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QToolButton,
)


class CronoMixin:
    def _build_crono(self) -> QFrame:
        """Marco compacto del cronómetro/temporizador por ejercicio (HUD)."""
        frame = QFrame()
        frame.setObjectName("CronoFrame")
        clay = QHBoxLayout(frame)
        clay.setContentsMargins(6, 0, 6, 0)
        clay.setSpacing(4)
        self.crono_time = QLabel("00:00:00")
        self.crono_time.setObjectName("CronoTime")
        self.crono_time.setToolTip("Tiempo del ejercicio actual")
        clay.addWidget(self.crono_time)
        self.crono_mode = QToolButton()
        self.crono_mode.setObjectName("CronoMode")
        self.crono_mode.setText("CRONO")
        self.crono_mode.setCheckable(True)
        self.crono_mode.setChecked(False)
        self.crono_mode.setToolTip(
            "Cambiar entre cronómetro (cuenta hacia arriba) "
            "y temporizador (cuenta regresiva)"
        )
        self.crono_mode.toggled.connect(self._on_crono_mode)
        clay.addWidget(self.crono_mode)
        self.crono_spin = QSpinBox()
        self.crono_spin.setObjectName("CronoSpin")
        self.crono_spin.setRange(5, 3600)
        self.crono_spin.setValue(60)
        self.crono_spin.setSuffix(" s")
        self.crono_spin.setToolTip("Segundos del temporizador (5–3600)")
        self.crono_spin.setVisible(False)
        self.crono_spin.valueChanged.connect(self._on_crono_spin)
        clay.addWidget(self.crono_spin)
        self.crono_start = QPushButton("INICIAR")
        self.crono_start.setObjectName("GhostBtn")
        self.crono_start.setToolTip("Iniciar o pausar el cronómetro/temporizador")
        self.crono_start.clicked.connect(self._on_crono_start)
        clay.addWidget(self.crono_start)
        self.crono_reset = QPushButton("REINICIAR")
        self.crono_reset.setObjectName("GhostBtn")
        self.crono_reset.setToolTip("Reiniciar el cronómetro/temporizador")
        self.crono_reset.clicked.connect(self._crono_reset)
        clay.addWidget(self.crono_reset)
        return frame

    # --------------------------------------------- cronómetro / temporizador

    @staticmethod
    def _format_crono(segundos: float) -> str:
        """Formatea segundos a HH:MM:SS (tope 99:59:59, sin negativos)."""
        total = max(0, int(segundos))
        total = min(total, 99 * 3600 + 59 * 60 + 59)
        horas, resto = divmod(total, 3600)
        minutos, segs = divmod(resto, 60)
        return f"{horas:02d}:{minutos:02d}:{segs:02d}"

    def _crono_transcurrido(self) -> float:
        """Segundos acumulados incluyendo el tramo actual en marcha."""
        total = self._crono_acumulado
        if self.crono_activo:
            total += time.monotonic() - self._crono_base
        return total

    def _crono_valor(self) -> float:
        """Valor a mostrar: transcurrido (CRONO) o restante (TEMPO)."""
        if self.crono_mode.isChecked():
            return max(0.0, self.crono_spin.value() - self._crono_transcurrido())
        return self._crono_transcurrido()

    def _crono_display(self) -> str:
        """Texto del display: floor en CRONO, ceil en TEMPO (aún queda el segundo)."""
        valor = self._crono_valor()
        entero = math.ceil(valor) if self.crono_mode.isChecked() else math.floor(valor)
        return self._format_crono(entero)

    def _crono_set_alerta(self, activa: bool) -> None:
        self.crono_alerta = activa
        self.crono_time.setProperty("alerta", "true" if activa else "false")
        self.crono_time.style().unpolish(self.crono_time)
        self.crono_time.style().polish(self.crono_time)

    def _on_crono_mode(self, temporizador: bool) -> None:
        self.crono_mode.setText("TEMPO" if temporizador else "CRONO")
        self.crono_spin.setVisible(temporizador)
        self._crono_reset()

    def _on_crono_spin(self, _value: int) -> None:
        self._crono_reset()

    def _on_crono_start(self) -> None:
        if self.crono_activo:
            self._crono_acumulado += time.monotonic() - self._crono_base
            self._crono_timer.stop()
            self.crono_activo = False
            self.crono_start.setText("INICIAR")
            self._crono_tick()
        else:
            self._crono_set_alerta(False)
            self._crono_base = time.monotonic()
            self._crono_timer.start()
            self.crono_activo = True
            self.crono_start.setText("PAUSAR")
            self._crono_tick()

    def _crono_tick(self) -> None:
        valor = self._crono_valor()
        self.crono_time.setText(self._crono_display())
        if self.crono_mode.isChecked() and valor <= 0:
            self._crono_timer.stop()
            self.crono_activo = False
            self.crono_start.setText("INICIAR")
            self._crono_set_alerta(True)
            self._toast("TIEMPO AGOTADO")

    def _crono_reset(self) -> None:
        self._crono_timer.stop()
        self.crono_activo = False
        self._crono_acumulado = 0.0
        self._crono_base = 0.0
        self.crono_start.setText("INICIAR")
        self._crono_set_alerta(False)
        base = self.crono_spin.value() if self.crono_mode.isChecked() else 0
        self.crono_time.setText(self._format_crono(base))
