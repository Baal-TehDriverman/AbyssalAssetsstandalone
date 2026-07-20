# Frontier Cognitive Maps

Model-agnostic reasoning patterns and prompt engineering strategies synthesized from `frontier_model_cognitive_map.md` (498 lines).

## 7 Reasoning Patterns

| Pattern | Use Case |
|---------|----------|
| Chain-of-Thought (CoT) | Multi-step logic, debugging |
| Tree-of-Thought (ToT) | Branching exploration, strategy |
| ReAct (Reason+Act) | Tool use, interactive tasks |
| Structured Output (JSON) | Data extraction, API responses |
| Reflection | Self-critique, error recovery |
| Skeleton-of-Thought | Outline-first long-form writing |
| Ouroboros Loop | Recursive self-improvement |

## Ouroboros Loop

The recursive self-improvement cycle:
1. **Inject** skill context into system prompt
2. **Generate** output with COT_REASONING marker
3. **Extract** reasoning from `[COT_REASONING]...[/COT_REASONING]`
4. **Evaluate** confidence, precision, recall
5. **Loop** — feed extracted reasoning back as context

## Local Model Prompt Engineering

When using Ollama (nemotron-mini, deepseek-r1, etc.):
- Remove `<think>` token wrapper from responses
- Use explicit JSON formatting over markdown
- Keep context window within 4k-8k tokens
- Chain state explicitly in each turn (the model has no memory)
- Temperature: 0.3 for code, 0.7 for creative, 0.0 for parsing

## Skill Injection

Skills are injected into prompts with this template:
```
[SKILL: {skill_name}]
{skill_description}
[USAGE: {trigger_patterns}]
```

The `frontier_skill_injector.py` tool automates this for any discovered skill.

## Cognitive Architecture

```
User Intent → Skill Selector → Context Builder → LLM Call → Output Parser → Response
                                  ↑                                      |
                                  └── Ouroboros Loop ────────────────────┘
```
