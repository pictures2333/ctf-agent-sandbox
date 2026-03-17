"""Agent CLI tool registry and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..models import SandboxConfig

AgentCliToolHandler = Callable[[SandboxConfig, dict[str, str], Any], None]


@dataclass
class AgentCliToolSpec:
    """Registered behavior and mount conventions for one CLI tool."""

    name: str
    handler: AgentCliToolHandler
    skills_mount_dir: str


AGENT_CLI_TOOLS: dict[str, AgentCliToolSpec] = {}


def register_agent_cli_tool(spec: AgentCliToolSpec) -> None:
    """Register or override one agent CLI tool plugin."""
    AGENT_CLI_TOOLS[spec.name] = spec


def apply_registered_agent_cli_tools(config: SandboxConfig, context: Any) -> None:
    """Apply registered handlers for all enabled agent CLI tools."""
    # Dispatch each configured tool to its registered plugin handler.
    for tool in config.agent_cli_tools:
        spec = AGENT_CLI_TOOLS.get(tool.name)
        if spec is None:
            continue
        spec.handler(config, tool.options, context)


def collect_agent_cli_prompt_volumes(config: SandboxConfig) -> list[str]:
    """Build prompt-file volume specs for each enabled agent CLI tool."""
    # No prompt mounts if source prompt file is not configured.
    if not config.prompt_file:
        return []

    volumes: list[str] = []
    # Mount one shared prompt source to each tool's target prompt filename.
    for tool in config.agent_cli_tools:
        spec = AGENT_CLI_TOOLS.get(tool.name)
        if spec is None:
            continue
        prompt_filename = tool.options.get("prompt_filename")
        if not prompt_filename:
            continue
        volumes.append(f"{config.prompt_file}:{config.workspace_container_path}/{prompt_filename}")
    return volumes


def collect_agent_cli_skill_volumes(
    config: SandboxConfig,
    skill_paths: list[str],
) -> list[str]:
    """Build skill mount volume specs for each enabled agent CLI tool."""
    volumes: list[str] = []
    # Cross-product mount: each skill path into each enabled tool skill directory.
    for tool in config.agent_cli_tools:
        spec = AGENT_CLI_TOOLS.get(tool.name)
        if spec is None:
            continue
        for skill_path in skill_paths:
            skill_name = skill_path.rstrip("/").split("/")[-1]
            volumes.append(f"{skill_path}:{spec.skills_mount_dir}/{skill_name}")
    return volumes


def get_agent_cli_tool_options(config: SandboxConfig, tool_name: str) -> dict[str, str]:
    """Read normalized options for one tool from `agent-cli-tools` entries."""
    for tool in config.agent_cli_tools:
        if tool.name == tool_name:
            return tool.options
    return {}
