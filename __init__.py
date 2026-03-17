"""Public package API for the CTF sandbox assembler."""

from typing import Any

from .assembler import (
    STATE_FILE,
    AssemblyResult,
    assemble,
    assemble_and_write,
    build_image,
    run_container,
    stop_container,
)
from .models import SandboxConfig, parse_config
from .service_registry import register_background_service

__all__ = [
    "STATE_FILE",
    "AssemblyResult",
    "assemble",
    "assemble_and_write",
    "build_image",
    "run_container",
    "stop_container",
    "register_background_service",
    "SandboxConfig",
    "parse_config",
]


def assemble_from_object(config_obj: SandboxConfig | dict[str, Any]) -> AssemblyResult:
    """Backward-compatible helper for assembling from a Python object."""
    return assemble(config_obj)
