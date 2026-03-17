# ctf_agent_sandbox

Build/run CTF sandbox containers with Docker SDK.

## CLI

```bash
./setup.sh
uv sync
```

```bash
uv run -m ctf_agent_sandbox assemble --config config.example.yaml --output-dir .
uv run -m ctf_agent_sandbox build-image --config config.example.yaml
uv run -m ctf_agent_sandbox run-container
uv run -m ctf_agent_sandbox stop-container --container-id <container_id>
```

If console script is installed:

```bash
uv run ctf_agent_sandbox assemble --config config.example.yaml --output-dir .
```

## Module

```bash
[tool.uv.sources]
ctf_agent_sandbox = { path = "../ctf_agent_sandbox" }
```

```python
from ctf_agent_sandbox import build_image, run_container, stop_container
```

`build_image(config)` writes `.sandbox_state.json` (image id + run params).  
`run_container(...)` runs from state and returns container id.  
`stop_container(container_id)` stops/removes container.

## Config

Template: [config.example.yaml](/home/p23/develope/Agent-CTF-Bot_I-love-suisei/src/ctf_agent_sandbox/config.example.yaml)

Main keys:
- `services`: background services (`name` + `options`)
- `agent-cli-tools`: tool plugins (`name` + `options`)
- `prompt_file`: prompt source file; mounted only when each tool sets `options.prompt_filename`
- `packages`: package groups
- `custom_install_commands`: custom install commands (`run_as: root|agent`)
