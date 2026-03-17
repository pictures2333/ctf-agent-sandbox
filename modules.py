"""Functional pipeline steps that mutate a shared build context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .agent_cli_tools import ensure_builtin_agent_cli_tools_registered
from .agent_cli_tools.registry import (
    apply_registered_agent_cli_tools,
    collect_agent_cli_prompt_volumes,
    collect_agent_cli_skill_volumes,
)
from .models import SandboxConfig
from .service_registry import (
    apply_registered_background_services,
    collect_background_service_skills,
)

ModuleFunc = Callable[[SandboxConfig, "BuildContext"], None]


@dataclass
class BuildContext:
    """Accumulator object used while composing Docker and runtime outputs."""

    env: dict[str, str] = field(default_factory=dict)
    pacman_packages: set[str] = field(default_factory=set)
    yay_packages: set[str] = field(default_factory=set)
    gem_packages: set[str] = field(default_factory=set)
    npm_packages: set[str] = field(default_factory=set)
    pip_packages: set[str] = field(default_factory=set)

    copy_files: list[tuple[str, str]] = field(default_factory=list)
    root_commands: list[str] = field(default_factory=list)
    agent_commands: list[str] = field(default_factory=list)

    startup_commands: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)
    privileged: bool = True


def apply_timezone(config: SandboxConfig, context: BuildContext) -> None:
    """Apply timezone environment variable."""
    context.env["TZ"] = config.timezone


def apply_locale(config: SandboxConfig, context: BuildContext) -> None:
    """Generate locale setup commands and locale-related environment values."""
    # Generate locale files and locale environment values inside the image.
    context.root_commands.append(
        "printf '%s\\n' "
        + " ".join(f"'{line}'" for line in config.locale.install)
        + " > /etc/locale.gen"
    )
    context.root_commands.extend(
        [
            f"echo 'LANG={config.locale.main}' > /etc/locale.conf",
            "locale-gen",
        ]
    )
    context.env["LANG"] = config.locale.main
    context.env["LC_ALL"] = config.locale.main


def apply_background_services(config: SandboxConfig, context: BuildContext) -> None:
    """Install and wire enabled background services via registry dispatch."""
    apply_registered_background_services(config, context)


def apply_agent_cli_tools(config: SandboxConfig, context: BuildContext) -> None:
    """Install selected agent CLI tools and mount tool-specific prompt/auth/config."""
    # Bootstrap and dispatch all enabled agent CLI tool plugins.
    ensure_builtin_agent_cli_tools_registered()
    apply_registered_agent_cli_tools(config, context)
    # Mount the same prompt source to each tool-specific target prompt filename.
    context.volumes.extend(collect_agent_cli_prompt_volumes(config))


def apply_packages(config: SandboxConfig, context: BuildContext) -> None:
    """Merge baseline packages with user-defined package groups."""
    # Baseline packages always installed in this sandbox image.
    context.pacman_packages.update(
        {
            "base-devel",
            "glibc",
            "wget",
            "curl",
            "zip",
            "unzip",
            "ripgrep",
            "file",
            "sudo",
            "git",
            "openssl",
            "gdb",
            "openbsd-netcat",
            "openssh",
            "vim",
            "ruby",
            "nodejs",
            "npm",
            "python",
            "python-uv",
        }
    )

    # Merge user-defined package groups by package manager.
    for group in config.packages:
        context.pacman_packages.update(group.pacman)
        context.yay_packages.update(group.yay)
        context.gem_packages.update(group.gem)
        context.npm_packages.update(group.npm)
        context.pip_packages.update(group.pip)


def apply_custom_install_commands(config: SandboxConfig, context: BuildContext) -> None:
    """Append user-defined install commands to root/agent execution phases."""
    # Route each custom command into the correct Dockerfile execution phase.
    for item in config.custom_install_commands:
        if item.run_as == "root":
            context.root_commands.append(item.command)
        else:
            context.agent_commands.append(item.command)


def apply_skills(config: SandboxConfig, context: BuildContext) -> None:
    """Mount shared and service skills to tool-specific skill locations."""
    # Compose full skill path list: explicit skills + generated env skill + service skills.
    skill_paths = list(config.skills)
    if config.sandbox_env_skill_path:
        skill_paths.insert(0, config.sandbox_env_skill_path)
    skill_paths.extend(collect_background_service_skills(config))
    # Expand skill mounts per enabled agent CLI tool.
    context.volumes.extend(collect_agent_cli_skill_volumes(config, skill_paths))


DEFAULT_PIPELINE: list[ModuleFunc] = [
    # Execution order follows the planned assembly priority.
    apply_timezone,
    apply_locale,
    apply_background_services,
    apply_agent_cli_tools,
    apply_packages,
    apply_custom_install_commands,
    apply_skills,
]
