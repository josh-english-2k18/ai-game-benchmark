from __future__ import annotations

from typing import Dict

from ..adapters.base import PolicyValueModel
from ..adapters.cpu_adapter import HeuristicCpuModel
from ..adapters.gpu_adapter import SimulatedGpuModel
from ..adapters.tpu_adapter import SimulatedTpuModel


class AdapterRegistry:
    """Keeps singletons for inference backends."""

    def __init__(self) -> None:
        self._models: Dict[str, PolicyValueModel] = {
            "cpu": HeuristicCpuModel(),
            "gpu": SimulatedGpuModel(),
            "tpu": SimulatedTpuModel(),
        }

    def get(self, backend: str) -> PolicyValueModel:
        key = backend.lower()
        if key not in self._models:
            raise KeyError(f"Unsupported backend '{backend}'")
        return self._models[key]

    def available(self) -> Dict[str, str]:
        return {key: model.name for key, model in self._models.items()}


registry = AdapterRegistry()
