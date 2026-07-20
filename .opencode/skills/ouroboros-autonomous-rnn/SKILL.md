# Ouroboros Autonomous RNN

Continuous self-supervised learning daemon synthesized from `ouroboros_rnn_autonomous.py`, `ouroboros_akashic_compressor.py`, `ouroboros_token_compressor.py`, `ouroboros_multiversal_rnn.py`.

## Purpose

An always-running daemon that datamines files, compresses knowledge into Akashic tokens, and trains RNN attention on the compressed memory stream.

## Pipeline

```
File System → Scanner → Tokenizer → Akashic Compressor → RNN Trainer → Memory Store
   ↑                                                                       │
   └────────────────── Ouroboros Loop (continuous feedback) ────────────────┘
```

## Components

### File Scanner
- Watches configured directories for new/modified files
- Respects `.gitignore` patterns and workspace boundaries
- Supported: `.py`, `.md`, `.json`, `.yaml`, `.toml`, `.txt`, `.js`, `.ts`, `.ps1`, `.sh`
- Max file size: 500KB per file

### Akashic Compressor
- Extracts semantic tokens from file content
- Compresses using context-pruned AST analysis
- Output: structured token arrays with attention weights
- Compression ratio: typically 10:1-20:1

### RNN Attention Trainer
- Trains on token sequences from Akashic compressor
- Multi-head attention (4 heads, 128-dim embedding)
- Online learning: no full retrain, continuous fine-tune
- Checkpoints to `runtime/ouroboros-rnn/checkpoints/`

### Memory Store
- Compressed tokens → `golem_diary.db` ouroboros_memory table
- Episodic: per-file entries with timestamps
- Semantic: cross-file pattern embeddings
- Procedural: task sequence patterns

## Configuration

- `watch_dirs`: list of directories to scan
- `scan_interval`: seconds between scans (default: 300)
- `max_tokens_per_file`: cap for large files
- `rnn_learning_rate`: 1e-4 default
- `rnn_batch_size`: 32
- `akashic_compression_target`: ratio (default: 0.1)

## Lifecycle

```
start → scan loop → on new file → tokenize → compress → train → store → loop
         ↑                                                                  │
         └─────────────────── sleep(scan_interval) ──────────────────────────┘
```

## Dependencies

- `torch` for RNN training
- `tree-sitter` for AST parsing
- SQLite via `golem_diary.db` for persistence
