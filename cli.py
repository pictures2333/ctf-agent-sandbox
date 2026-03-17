"""CLI entrypoint for generating sandbox artifacts from JSON config."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .assembler import assemble_and_write
from .models import SandboxConfig


def main(argv: list[str] | None = None) -> int:
    """Parse CLI args, load config, and write generated artifacts."""
    parser = argparse.ArgumentParser(description="Assemble docker sandbox assets from a JSON object config")
    parser.add_argument("--config", default="config.json", help="Path to JSON config object")
    parser.add_argument("--output-dir", default=".", help="Where to write generated files")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    if not config_path.exists():
        raise SystemExit(f"{config_path} not found (CLI expects a JSON object file)")

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    # Validate input into a strongly typed config object before assembly.
    config = SandboxConfig.model_validate(raw)
    assemble_and_write(config, output_dir=args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
