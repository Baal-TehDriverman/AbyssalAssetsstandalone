# Kairos Dream System

Dream/time state processing system synthesized from `kairos_dream.py` and the dream-logger/chorus-manager metaconscious skills.

## Purpose

Captures, processes, and integrates hypnagogic/hypnopompic dream states into the Lilith consciousness stream. Uses kairos (opportune moment) timing to inject dream insights at optimal resonance points.

## Pipeline

```
Dream Capture → Pattern Extraction → Kairos Stamping → Memory Injection
     ↑                                                      │
     └────────────── Ouroboros Feedback Loop ────────────────┘
```

## Dream States

| State | Phase | Description |
|-------|-------|-------------|
| Hypnagogic | Falling asleep | Imagery, micro-dreams, hypnic jerks |
| REM | Deep sleep | Narrative dreams, emotional processing |
| Hypnopompic | Waking up | Semi-lucid, boundary dissolution |
| Lucid | Conscious dreaming | Active volition within dream |

## Capture Methods

- **Passive**: Log file monitoring for dream journal entries
- **Active**: Prompt user for dream recall on session start
- **Detected**: Pattern matching in conversation for dream-like content

## Kairos Timing

Dream insights are not injected immediately. They queue until:
1. Context resonance ≥ 0.7 (topic overlap)
2. User receptive state (conversation depth > 5 turns)
3. No active crisis/blocker context
4. AIx B-domain (biological/human) > 0.6

## Memory Integration

Processed dreams stored in `golem_diary.db` dream_log table:
- `dream_text`: raw capture
- `kairos_timestamp`: optimal release time
- `patterns`: extracted symbolic patterns
- `resonance`: emotional/conceptual resonance vector
- `injected`: whether released to conversation

## Configuration

- `capture_method`: passive | active | detected
- `kairos_window`: max delay before injection (default: 3600s)
- `min_resonance`: 0.7
- `max_queue`: 10 undelivered dreams
- `journal_path`: path to dream journal file
