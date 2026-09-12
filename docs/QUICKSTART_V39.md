# Run the final SearchMate engine

The final competition submission is **internal v39-01**. This guide runs that frozen player. The repository's root `agent.py`, generic CI and `make zip` still describe historical v0.

## 1. Get and verify the exact release

Clone or download this repository, then run this command from its root:

```text
python research/releases/final-internal-v39-01/verify_artifacts.py
```

This standard-library check verifies the archive, its nine payload files, source syntax and recorded smoke-game hashes. It does not import the engine or play games.

The [release directory](../research/releases/final-internal-v39-01/README.md) contains the original ZIP and its unpacked `player/` directory. Both include the trained weights and endgame tables. Copy the whole player directory when moving the engine.

- ZIP: `SearchMate-next-submission-internal-v39-01.zip`
- ZIP SHA-256: `bad3347ceae0fed3a09397641f90b4789224e4e7d23206c1fc2c04d0aba8b83f`
- `agent.py` SHA-256: `c3a03de24e3aa9c9caa1ac1323f4955146ee12a6ace3ef4b18d074eb1e8f8bc5`

## 2. Prepare a local Python environment

Use Python 3.12 in a separate virtual environment. The runtime dependencies recorded in this repository are:

```text
chess==1.11.2
numpy==2.5.2
numba==0.67.0
```

For example, in Windows PowerShell from the repository root:

```powershell
py -3.12 -m venv .venv-v39
.\.venv-v39\Scripts\python.exe -m pip install chess==1.11.2 numpy==2.5.2 numba==0.67.0
```

On macOS/Linux:

```sh
python3.12 -m venv .venv-v39
.venv-v39/bin/python -m pip install chess==1.11.2 numpy==2.5.2 numba==0.67.0
```

These are the recorded dependency pins, not a promise of compatibility with every future platform. V39 inference needs neither PyTorch nor ONNX Runtime. The submission contains the fixed, CPU-trained network weights used by its original evaluator.

## 3. Ask the frozen player for a move

Run from the final player's directory so that `import agent` resolves to v39.

Windows PowerShell:

```powershell
Push-Location research/releases/final-internal-v39-01/player
..\..\..\..\.venv-v39\Scripts\python.exe -c "import agent; print(agent.get_move('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 1000))"
Pop-Location
```

macOS/Linux:

```sh
cd research/releases/final-internal-v39-01/player
../../../../.venv-v39/bin/python -c "import agent; print(agent.get_move('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 1000))"
```

The API is `get_move(fen: str, time_left_ms: int) -> str`; the return value is a UCI move. The side to move comes from the FEN. Import warms the compiled functions before a request. Local startup and search timings depend on the machine.

## Read the evidence

Start with the [standalone case study](../publication/README.md), [research index](../research/README.md), [model card](../research/releases/competition-v6-internal-v37-01/MODEL_CARD.md) and [final Swiss results](../research/tournament-results/README.md).

The public repository contains reviewed evidence and frozen releases. Bulk research data, raw private logs and exploratory candidates are maintained separately. The model does not learn during a game; neither the tournament record nor the development history establishes a causal RSI or memory benefit.

This is a documentation guide for the completed project. It does not reopen competition submissions or engine development.
