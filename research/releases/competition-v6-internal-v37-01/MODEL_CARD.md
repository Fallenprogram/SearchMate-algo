# Original CPU neural residual used in v37

The model was trained for SearchMate in the v31 relational-residual study and reused unchanged in v37. It does not update itself during competition games. No GPU or published pretrained chess network was used.

## Representation and inference

There are 36 normalized geometric features per color: piece activity and attacks, pawn structure and advancement, king pressure/shelter, piece counts and related material/context features. The shared 72-input layer is evaluated with own/opponent feature ordering from each color's perspective. Eight clipped-ReLU activations per view are subtracted and combined with shared output weights. There are 576 input weights, eight hidden biases and eight output weights: 592 parameters. A bounded correction of at most 400 cp in either direction is rounded once and added to the existing classical evaluation, with side-to-move sign handling.

Weights are three finite float32 arrays of shapes (72, 8), (8,), (8,), loaded with a fixed file hash and made read-only. Inference uses the player's original Numba code. This is not incremental NNUE; its geometric features are recomputed when needed. The runtime cache is an acceleration of the player's own static calculation, not a shipped position-to-answer table.

## Fitting and data

CPU fitting used seed 2026091031, one thread, 80 fixed epochs, batch size 512, AdamW, learning rate 0.001 decaying by cosine to 0.0001, weight decay 0.05, dropout 0.25, a game-group-balanced Huber objective with 100-cp transition, and residual L2 0.05. There was no validation-based early stopping or refit after metric disclosure.

Training reused 15,081 previously generated training-only labels in 164 ECO groups. New validation and test data came from 24 fresh ECO families, divided 12/12, with 678 and 649 usable labels. Whole-family partitioning and exposure exclusions were frozen before queries/fitting; rejected queries were not replaced. The fresh label query budget was 960 per split at 100,000 requested nodes each. The offline reference supplied labels only; none of its executable code or answer database ships.

| Historical v31 split | Labels / groups | Baseline MAE cp | Residual MAE cp | Reduction |
|---|---:|---:|---:|---:|
| Training | 15,081 / 164 | 172.19 | 148.52 | 13.74% |
| Validation | 678 / 12 | 155.65 | 133.28 | 14.37% |
| Test | 649 / 12 | 166.08 | 144.43 | 13.04% |

These group-balanced metrics use integer-cp inference. All three material strata improved in those splits, with no saturated correction. They are historical measurements for identical weights; repeated reuse in later candidates does not create fresh independent accuracy evidence. The narrower v31 build failed its own competitive screen, which is why model accuracy alone was not used to recommend a submission. V37 qualifies on its separate frozen game screens as a combined build.

## Limits and provenance

The residual omits castling, en-passant and draw-history context; geometric attacks include pinned-piece approximations. Training prefilters and reference-score acceptance only approximate tactical quietness. The model does not solve every tactical loss or uncovered ending. Many candidate screens occurred during development, limiting inferences about selection bias and generalization.

[Exact recipe and source hashes](training-recipe.json), [accuracy and material strata](model-accuracy.json), [release/model identity](release.json), and [inference source](player/agent.py) preserve the audit trail. Raw teacher data and local training orchestration remain private, so this publication is not a complete standalone training reproduction bundle. Only original weights and player code enter the submission. Recuris's causal benefit has not been separately measured.
