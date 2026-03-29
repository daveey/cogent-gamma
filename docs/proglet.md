# ProgLet: Unified Program Table for Coglets

## Problem

CodeLet manages a dictionary of Python functions. LLM logic lives outside the coglet framework in ad-hoc policy code (`cvc_policy.py`). This means:

- LLM-based coglets can't use the COG/LET protocol to manage their prompts
- No uniform way to compose Python functions with LLM calls
- Adding new execution backends (MeTTa, shell) requires new mixins each time

## Core Insight

A function and a prompt are both programs. The only difference is the executor. CodeLet should manage programs, not just Python callables.

## Design

### Program

A named unit of computation with an executor type.

```python
@dataclass
class Program:
    executor: str                                    # "code", "llm", "metta", ...
    fn: Callable | None = None                       # code executor
    system: str | Callable[..., str] | None = None   # llm executor: prompt or builder
    tools: list[str] = []                            # program names this can invoke
    parser: Callable[[str], Any] | None = None       # extract structured output
    config: dict[str, Any] = field(default_factory=dict)  # executor-specific
```

The `config` dict holds executor-specific settings:
- **llm**: `model`, `temperature`, `max_tokens`, `max_turns`
- **metta**: expression, space bindings
- **code**: nothing needed — `fn` is sufficient

### Executor

Pluggable backend that runs a Program.

```python
class Executor(Protocol):
    async def run(
        self,
        program: Program,
        context: Any,
        invoke: Callable[[str, Any], Awaitable[Any]],  # callback to invoke other programs
    ) -> Any: ...
```

The `invoke` callback is how programs chain — an LLM program calls `invoke("move", args)` to run a code program as a tool, or `invoke("scout", args)` to chain into another LLM program. The executor doesn't need to know about ProgLet internals.

### Built-in Executors

**CodeExecutor** — runs `program.fn(context)`:

```python
class CodeExecutor:
    async def run(self, program, context, invoke):
        return program.fn(context)
```

**LLMExecutor** — runs a multi-turn LLM conversation:

```python
class LLMExecutor:
    def __init__(self, client):
        self.client = client

    async def run(self, program, context, invoke):
        # 1. Build system prompt
        system = program.system(context) if callable(program.system) else program.system

        # 2. Build tool definitions from program.tools
        #    Each tool name maps to another program via invoke()
        tools = self._build_tools(program.tools, invoke)

        # 3. Conversation loop
        messages = [{"role": "user", "content": context}]
        for _ in range(program.config.get("max_turns", 1)):
            response = self.client.messages.create(
                model=program.config.get("model", "claude-sonnet-4-20250514"),
                system=system,
                messages=messages,
                tools=tools,
                max_tokens=program.config.get("max_tokens", 1024),
                temperature=program.config.get("temperature", 0.2),
            )
            if response.stop_reason == "tool_use":
                # Execute tool calls via invoke(), append results, continue
                ...
            else:
                text = self._extract_text(response)
                return program.parser(text) if program.parser else text

        return None  # max_turns exhausted
```

### ProgLet Mixin

Replaces CodeLet. Same pattern — managed dictionary + enact handler.

```python
class ProgLet:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.programs: dict[str, Program] = {}
        self.executors: dict[str, Executor] = {"code": CodeExecutor()}

    @enact("register")
    async def _proglet_register(self, programs: dict[str, Program]) -> None:
        self.programs.update(programs)

    @enact("executor")
    async def _proglet_executor(self, executors: dict[str, Executor]) -> None:
        self.executors.update(executors)

    async def invoke(self, name: str, context: Any = None) -> Any:
        program = self.programs[name]
        executor = self.executors[program.executor]
        return await executor.run(program, context, self.invoke)
```

### No Backwards Compatibility

CodeLet is deleted. All callsites migrate to `self.programs` and `Program(...)` directly.

## CvC Integration

### Before (cvc_policy.py)

LLM logic hardcoded in `CogletPolicyImpl._llm_analyze()`:
- Builds prompt string from game state
- Calls `anthropic.Anthropic().messages.create()`
- Parses JSON response
- Sets `engine._llm_resource_bias`

### After

PolicyCoglet gains LLM capability through ProgLet:

```python
class PolicyCoglet(Coglet, ProgLet, LifeLet, TickLet):
    ...
```

The `analyze_resources` program is registered as a Program:

```python
def build_analysis_prompt(context: dict) -> str:
    """Build the resource analysis prompt from game state."""
    inv = context["inventory"]
    resources = context["resources"]
    # ... same prompt construction as before ...
    return "\n".join(lines)

def parse_analysis(text: str) -> dict:
    """Parse LLM response into resource_bias + analysis."""
    directive = json.loads(text)
    return {
        "resource_bias": directive.get("resource_bias"),
        "analysis": directive.get("analysis", text[:100]),
    }

# Register the program
guide(handle, Command("register", {
    "analyze_resources": Program(
        executor="llm",
        system=build_analysis_prompt,
        parser=parse_analysis,
        config={"model": "claude-sonnet-4-20250514", "temperature": 0.2, "max_tokens": 150},
    ),
    "step": Program(executor="code", fn=step_fn),
}))
```

Calling it from the LET:

```python
result = await self.invoke("analyze_resources", game_state_context)
```

### What This Enables

Once `analyze_resources` is a registered program, the COG can:
- **Replace it** at runtime with a better prompt via `Command("register", ...)`
- **Add tools** — give it access to code programs like `"count_junctions"` or `"evaluate_position"`
- **Chain** — an LLM program `"strategize"` could invoke `"analyze_resources"` as a sub-program
- **Swap executors** — move from LLM to a fine-tuned code function without changing the call site

## Migration

1. **Create** `src/coglet/proglet.py` with `Program`, `Executor`, `CodeExecutor`, `ProgLet`
2. **Create** `src/coglet/llm_executor.py` with `LLMExecutor`
3. **Update** `PolicyCoglet` to use `ProgLet` instead of `CodeLet`
4. **Refactor** `cvc_policy.py` — extract LLM logic into registered Program
5. **Deprecate** `codelet.py` — ProgLet is the replacement
6. **Update** tests

## Open Questions

- **Async code programs**: Should `CodeExecutor` detect and await async `fn`? Probably yes.
- **Streaming**: Should `LLMExecutor` support streaming responses? Not for v1.
- **Error handling**: Should `invoke()` catch executor errors and let the coglet's error handling decide? Or let them propagate?
- **LLM client lifecycle**: Who owns the anthropic client — the LLMExecutor, or passed in via config?
