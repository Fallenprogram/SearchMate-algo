# Release and submission identity index

**Final user-confirmed submission: [internal v39-01](final-internal-v39-01/README.md).** Internal numbers identify experiments. A competition label in an archive name is historical packaging metadata, not proof of a queued game's source identity.

| Internal build | Common submission/archive label | Role and evidence |
|---|---|---|
| [v0](v0/STATUS.md) | Initial submission; root player | Historical classical baseline; root `make zip` still builds this lineage |
| [v2-01](v2-01/STATUS.md) | Competition v2 | Same source as earlier internal v1, admitted by a separate successful campaign |
| [v7-01](competition-v3-internal-v7-01/README.md) | Competition v3 | Original Numba core; submitted after rated53 |
| [v14-01](competition-v4-internal-v14-01/README.md) | Competition v4 | KQK maintenance; reported for rounds 76–79 |
| [v16-01](competition-v5-internal-v16-01/README.md) | User's **v16.1**; competition v5 | Classical search/order/history improvements; exact earlier submitted rollback |
| [v37-01](competition-v6-internal-v37-01/README.md) | Prepared competition-v6 / next-submission ZIP | Neural/search package qualified against v16.1; do not infer rated deployment from the folder name |
| [v39-01](final-internal-v39-01/README.md) | **Final next-submission archive** | V37 lineage plus KBBK and draw-boundary maintenance; user confirmed final submission |

V29 was the first neural experiment; v31 trained the network retained in v37 and v39. V12's seven fitted classical weights were not a neural network. V20 and other unqualified source/model payloads are not published. Their results remain in the [study record](../studies/README.md).

[Current state and exact hashes](../CURRENT_STATE.md) · [Rated boundaries and caveats](../rated-results/README.md) · [Full retrospective](../RETROSPECTIVE.md).

Each release's original manifest, player, model, tablebase assets and archive bytes remain frozen. Root `agent.py`, generic CI and the old harness do not automatically exercise the final packaged player. Use the verifier belonging to the selected preserved release; no root rebuild is a substitute for its exact ZIP.
