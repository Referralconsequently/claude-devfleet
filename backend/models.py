from pydantic import BaseModel
from typing import Optional, List


class ProjectCreate(BaseModel):
    name: str
    path: str
    description: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    path: Optional[str] = None
    description: Optional[str] = None


# ── Dispatch Configuration ──
# Controls how the Claude CLI agent is spawned per mission

TOOL_PRESETS = {
    "full": ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebFetch", "WebSearch"],
    "implement": ["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
    "review": ["Read", "Grep", "Glob", "Bash(git diff *)", "Bash(git log *)"],
    "test": ["Read", "Edit", "Bash(npm test *)", "Bash(pytest *)", "Bash(cargo test *)", "Grep", "Glob"],
    "explore": ["Read", "Grep", "Glob", "Bash(git *)", "Bash(ls *)", "Bash(find *)"],
    "fix": ["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
}

GATEWAY_OPUS_MODEL = "glm-5.1"
GATEWAY_SONNET_MODEL = "tencent/hy3-preview"
GATEWAY_HAIKU_MODEL = "minimax-m2.7"
GATEWAY_SMALL_FAST_MODEL = "gemini-3.1-flash-lite-preview"
GATEWAY_CUSTOM_MODEL = "kimi-k2.6"
DEFAULT_MODEL = GATEWAY_OPUS_MODEL
PLANNER_MODEL = GATEWAY_SONNET_MODEL

MODEL_CHOICES = [GATEWAY_OPUS_MODEL, GATEWAY_SONNET_MODEL, GATEWAY_HAIKU_MODEL]
SUPPORTED_CAPABILITIES = "effort,thinking,adaptive_thinking,interleaved_thinking"

MODEL_OPTIONS = [
    {
        "value": GATEWAY_OPUS_MODEL,
        "label": "GLM 5.1",
        "tier": "high",
        "icon": "\U0001F9E0",
        "cost": "LiteLLM metered",
        "tagline": "Maximum intelligence",
    },
    {
        "value": GATEWAY_SONNET_MODEL,
        "label": "HY3 Preview",
        "tier": "mid",
        "icon": "\u26A1",
        "cost": "LiteLLM metered",
        "tagline": "Speed meets smarts",
    },
    {
        "value": GATEWAY_HAIKU_MODEL,
        "label": "MiniMax M2.7",
        "tier": "low",
        "icon": "\U0001F680",
        "cost": "LiteLLM metered",
        "tagline": "Fast execution",
    },
]

LEGACY_MODEL_ALIASES = {
    "claude-opus-4-6": GATEWAY_OPUS_MODEL,
    "claude-sonnet-4-6": GATEWAY_SONNET_MODEL,
    "claude-haiku-4-5-20251001": GATEWAY_HAIKU_MODEL,
    "claude-sonnet-4-20250514": GATEWAY_SONNET_MODEL,
}


def normalize_model(model: Optional[str], default: str = DEFAULT_MODEL) -> str:
    candidate = model or default
    if candidate.startswith("anthropic/"):
        candidate = candidate.split("/", 1)[1]
    if candidate in LEGACY_MODEL_ALIASES:
        return LEGACY_MODEL_ALIASES[candidate]
    if candidate.startswith("claude-opus-"):
        return GATEWAY_OPUS_MODEL
    if candidate.startswith("claude-sonnet-"):
        return GATEWAY_SONNET_MODEL
    if candidate.startswith("claude-haiku-"):
        return GATEWAY_HAIKU_MODEL
    return candidate


def claude_code_gateway_env(model: Optional[str] = None) -> dict[str, str]:
    """Force Claude Code's internal model defaults onto LiteLLM gateway aliases."""
    selected_model = normalize_model(model, DEFAULT_MODEL)
    return {
        "ANTHROPIC_MODEL": selected_model,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": GATEWAY_OPUS_MODEL,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": GATEWAY_SONNET_MODEL,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": GATEWAY_HAIKU_MODEL,
        "ANTHROPIC_SMALL_FAST_MODEL": GATEWAY_SMALL_FAST_MODEL,
        "ANTHROPIC_CUSTOM_MODEL_OPTION": GATEWAY_CUSTOM_MODEL,
        "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1",
        "CLAUDE_CODE_SUBAGENT_MODEL": GATEWAY_SONNET_MODEL,
        "ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES": SUPPORTED_CAPABILITIES,
        "ANTHROPIC_DEFAULT_SONNET_MODEL_SUPPORTED_CAPABILITIES": SUPPORTED_CAPABILITIES,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL_SUPPORTED_CAPABILITIES": SUPPORTED_CAPABILITIES,
        "ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES": SUPPORTED_CAPABILITIES,
    }


class DispatchOptions(BaseModel):
    """Per-dispatch overrides for Claude CLI invocation."""
    model: Optional[str] = None              # LiteLLM gateway alias such as glm-5.1 or tencent/hy3-preview
    max_turns: Optional[int] = None          # --max-turns N
    max_budget_usd: Optional[float] = None   # --max-budget-usd N
    allowed_tools: Optional[List[str]] = None # --allowedTools list (or preset name)
    tool_preset: Optional[str] = None        # key into TOOL_PRESETS
    append_system_prompt: Optional[str] = None  # --append-system-prompt
    fork_session: bool = False               # --fork-session (for branching from resume)
    context_mode: bool = False               # attach context-mode MCP server for context savings + session continuity


class MissionCreate(BaseModel):
    project_id: str
    title: str
    detailed_prompt: str
    acceptance_criteria: str = ""
    priority: int = 0
    tags: List[str] = []
    # Default dispatch config stored on mission
    model: str = DEFAULT_MODEL
    max_turns: Optional[int] = None
    max_budget_usd: Optional[float] = None
    allowed_tools: Optional[str] = None      # JSON string or preset name
    mission_type: str = "implement"          # implement, review, test, explore, fix
    # Phase 3: multi-agent, dependencies, scheduling
    parent_mission_id: Optional[str] = None  # parent mission for sub-missions
    depends_on: List[str] = []               # mission IDs that must complete first
    auto_dispatch: bool = False              # auto-dispatch when dependencies met
    schedule_cron: Optional[str] = None      # cron expression for recurring missions


class MissionUpdate(BaseModel):
    title: Optional[str] = None
    detailed_prompt: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    tags: Optional[List[str]] = None
    model: Optional[str] = None
    max_turns: Optional[int] = None
    max_budget_usd: Optional[float] = None
    allowed_tools: Optional[str] = None
    mission_type: Optional[str] = None
    parent_mission_id: Optional[str] = None
    depends_on: Optional[List[str]] = None
    auto_dispatch: Optional[bool] = None
    schedule_cron: Optional[str] = None
    schedule_enabled: Optional[bool] = None


class ServiceCreate(BaseModel):
    project_id: str
    name: str
    url: str
    group_name: str = "Default"
    description: str = ""
    check_interval: int = 30
    timeout_ms: int = 5000
    expected_status: int = 200


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    group_name: Optional[str] = None
    description: Optional[str] = None
    check_interval: Optional[int] = None
    timeout_ms: Optional[int] = None
    expected_status: Optional[int] = None
    enabled: Optional[bool] = None


class IncidentCreate(BaseModel):
    service_id: Optional[str] = None
    project_id: str
    title: str
    description: str = ""
    severity: str = "minor"


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    resolved_at: Optional[str] = None


# ── MCP Server Configuration ──

class McpServerCreate(BaseModel):
    """Configure an MCP server for a project — agents get access to its tools."""
    server_name: str                          # e.g. "github", "brave-search", "memory"
    server_type: str = "stdio"                # stdio, sse, http
    config: dict = {}                         # command, args, env, url, headers etc.
