# Competition v3: rated rounds 54–60

The seven archived PGNs confirm **4 wins and 3 losses**. All 500 recorded plies replay legally, and every game ends in a board-supported checkmate. There were no PGN clock-accounting anomalies or moves after an automatic terminal position.

The user identifies the submission as competition v3 (internal v7-01), uploaded after round 53 began. The authenticated dashboard shows v3 ACTIVE, with displayed ZIP hash prefix 0053272feb11 matching the delivered internal-v7 archive. Its validation result is valid. The submission transition and displayed initialization timings corroborate associating rounds 54-60 with v3; the full platform ZIP hash and individual per-game build hashes were not exposed.

| Round | SearchMate | Opponent | Result | Last move | SearchMate clock |
|---|---|---|---|---|---|
| [54](https://aichessathon.com/game/77175286-01dd-42e2-adc6-140ae93fc723) | Black | Cagnus_Marlsen | Win | 58...Qg1# | 74.405 s |
| [55](https://aichessathon.com/game/5ea2d0ac-1d19-422f-b0b6-290c82e993de) | White | Rook and Roll | Loss | 32...Qxe1# | 101.784 s |
| [56](https://aichessathon.com/game/1f35185d-387f-45b0-88e7-468031323f59) | White | Brownies | Win | 50.Qxh6# | 80.754 s |
| [57](https://aichessathon.com/game/91abd2af-f54b-4903-a7bb-fd369b84e07b) | Black | Columbia Trader | Win | 31...Qg2# | 98.112 s |
| [58](https://aichessathon.com/game/0c2e7026-4ebd-4d48-9a4a-2e6549da07e5) | White | Stocked Fish | Win | 37.Qxe8# | 94.475 s |
| [59](https://aichessathon.com/game/9efa9ab5-53c6-478f-9181-5bb5ed43feb8) | White | 404 Not Found | Loss | 49...Qg4# | 85.589 s |
| [60](https://aichessathon.com/game/0fe9126b-cf2e-490c-bd9a-2462e47d86ee) | Black | dhav | Loss | 42.Qh8# | 89.784 s |

The dashboard displayed per-game initialization times of 16.5–19.9 seconds for rounds 54–60; the submission's validation runs reported 20.8 and 26.1 seconds and a valid result. These are platform observations, separate from the slower cold-start measurements in the local overnight research.

## Recorded continuations

**Round 54 (win; Italian Game).** SearchMate converted a queenless ending with its knight, king and queenside pawns. After 42.Qxe6 Qxe6 43.Rxe6, the record continues with ...c3, ...c2 and ...b4-b3-b2. White's 54.Rxc2 was answered by 54...Kxc2; 57...b1=Q+ promoted the other pawn and 58...Qg1# finished. This is a recorded conversion, without a claim that every preceding move was best.

**Round 55 (loss; Petroff Defence).** The loss ended in a direct attack on White's king. The record includes 18...Bxf3 19.gxf3, followed later by the bishop captures 23...gxh6 and 25...Kxh7. The closing line is 28.Qxa7 Rg8+ 29.Qg7+ Rxg7+ 30.Kh2 Nxf3+ 31.Kh1 Re1+ 32.Rxe1 Qxe1#. The replies 31.Kh1 and 32.Rxe1 were each the only legal move at those positions. White still had 101.784 seconds recorded after its last move; this was a board checkmate, not a flag fall. The sequence does not locate the earliest avoidable mistake.

**Round 56 (win; Catalan Opening).** Both queens disappeared through 19...Rxd3 20.axb6, followed by a rook/pawn exchange sequence ending 23...Rxa7 24.Rxa7. SearchMate then captured the remaining bishop with 27.Bxc8 and later exchanged its other bishop for the knight with 31.Bxf6 Kxf6. Its remaining rook and bishop supported a pawn advance that reached 47.f8=Q and 50.Qxh6#. These are legal material and promotion events, not position evaluations.

**Round 57 (win; English Symmetrical).** SearchMate's kingside attack advanced ...h5-h4-h3, while the rook reached f4 and captured the bishop with 25...Rxf3. The finish was 29...Rg3 30.hxg3 Qf3+ 31.Kg1 Qg2#. White's pawn captured the offered rook, and the queen then delivered the recorded mate.

**Round 58 (win; Four Knights Game).** After 24.Rb3, Black could legally play 24...Qa2 to create a third occurrence of the position already seen after 20...Kg8 and 22...Qa2. There was no actual third occurrence: Black instead played 24...Rf8, leaving the queen on b2 for 25.Rxb2. SearchMate later finished 33.Rb8+ Nf8 34.Rxf8+ Kxf8 35.Qd8+ Re8 36.Bc5+ Kg8 37.Qxe8#. This is another concrete example of the rated game continuing past a prospective repetition claim; it does not prove that every draw-rule detail matches the local harness.

**Round 59 (loss; Ruy Lopez, Closed).** The opponent's attack developed through 33...Bxh4 and 34...Bf2+. The sequence 37...Rxf3 38.Ne4 Bxe4 39.gxf3 Bxf3+ removed both White knights for a rook before further checks. White's 40.Kh2 was its only legal reply. The recorded finish is 47.Qc2 Qe6+ 48.Qf5 Qxf5+ 49.Kg3 Qg4#. SearchMate retained 85.589 seconds after its final move. The site's zero-blunder label does not overturn the observed material losses and checkmate, or establish error-free play.

**Round 60 (loss; English Symmetrical).** The game moved from exchanges into a passed-pawn conversion. After 25.Rxd4 cxd4 26.Bxe6 Kf8 27.Bxf7 Kxf7, queens came off with 29.Qb7 Qxb7 30.Rxb7. White advanced 31.c6 and captured Black's last knight with 32.cxd7. That pawn promoted with 39.d8=Q+; the finish was 40.Qf8 Kg5 41.Rg7+ Kh5 42.Qh8#. Black still had 89.784 seconds recorded after its last move. This identifies an observed endgame failure and promotion sequence, not its earliest cause or a proven saving defense.

## Interpretation limits

- This is seven games against different opponents and openings, not a controlled strength or Elo comparison.
- Final clocks are PGN observations; they do not reveal search depth, search efficiency, initialization time or stderr.
- The recorded mating continuations do not locate the earliest losing decision or prove that another move saves a game.
- Site accuracy, centipawn-loss and blunder labels are attributed site estimates, not independent verdicts. Zero labelled blunders does not imply error-free play.
- Opening names and initialization timings are attributed to the displayed platform data, not derived from a new search or independently measured here.
- Repetition findings use only the history present after each PGN's supplied opening FEN.
- No engine search, reference-engine query, local game, candidate change or upload was made in this intake.
- The Recuris-inspired process preserves observations and versioned decisions; a causal benefit from memory evolution remains unmeasured.

The machine-readable companion preserves each PGN's SHA-256 and the attributed site review values.
