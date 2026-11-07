# Allied Leisure Boogie Modernization

This repository contains Mission Pinball Framework (MPF) and Godot-based
modernization work for Allied Leisure pinball machines, including Boogie,
Rock-On, T.N.T., and Dyn-O-Mite. The Boogie project is the active example
documented here.

## Boogie hardware design

The Boogie is a hybrid electromechanical/solid-state machine. Its original
control electronics have been replaced with a CobraPin controller while
retaining the original playfield mechanisms and coils. The coil configurations
have been confirmed and the game is fully playable.

The system uses:

- A 24 V supply for the original playfield coils and mechanisms.
- A 24 V-to-5 V DC-DC converter to supply the GI lights.
- A CobraPin controller, hosted by a raspberry pi 3 b+ running MPF.
- The original playfield mechanisms and coils, controlled by CobraPin outputs
  and MPF rules.

This summary is not a wiring diagram. Use the machine's verified wiring and
controller documentation when servicing or modifying power, grounding, fusing,
drivers, coil suppression, or lamps.

The configured machine is operational and playable. Keep configuration changes
consistent with the confirmed CobraPin and playfield wiring.

## Software overview

### Mission Pinball Framework

The MPF machine configuration is in [`Boogie/config/`](./Boogie/config/), with
game modes in [`Boogie/modes/`](./Boogie/modes/).

- [`config.yaml`](./Boogie/config/config.yaml) sets up a five-ball game for up
  to two players, loads the attract, base, drop-target-scoring,
  score-milestones, and playfield-lights modes, and selects the OPP platform
  with Gen2 driver boards for CobraPin. It retains the Windows `COM9, COM10`
  ports. Tilt mode is currently disabled because no physical tilt switch is
  configured.
- [`config_raspberry_pi.yaml`](./Boogie/config/config_raspberry_pi.yaml)
  overrides only `opp.ports` for Linux, leaving the shared game config and
  Windows COM ports unchanged. It uses the two Raspberry Pi
  `/dev/serial/by-id/` device paths; update them if the connected controllers
  change.
- [`switches.yaml`](./Boogie/config/switches.yaml) maps the playfield and
  cabinet switches to logical switch names and the confirmed hardware
  assignments. Tilt and credit switches are not currently configured.
- [`balldevices.yaml`](./Boogie/config/balldevices.yaml) and
  [`playfields.yaml`](./Boogie/config/playfields.yaml) describe Boogie's
  documented EM-style, no-trough ball flow. Preserve this machine-specific
  arrangement rather than assuming a modern trough and shooter-lane layout.
  The drain device ejects its ball using `c_outhole_kicker`.
- [`base.yaml`](./Boogie/modes/base/config/base.yaml) contains the main
  switch-driven scoring and playfield logic. It awards points for configured
  targets, rollovers, pop bumper, and slingshots, tracks completion of target
  banks, and posts events that open the left and right gates.
- [`lights.yaml`](./Boogie/config/lights.yaml) defines the 25 named game
  lights and all 256 pixels available on CobraPin J12 / NEO 1 (`1-0-0` through
  `1-0-255`); the remaining 231 are generated as placeholders for testing and
  later mapping. The attract mode cycles through the named game lights while
  no game is active. The `playfield_lights` mode controls the bonus ladder,
  target-progress indicators, random 500-when-lit rollover indicator, double
  bonus, gate-open, and special lamps per ball. A special lamp requires its
  corresponding gate to be open and all four targets in its bank to have been
  hit. The gates-open lamp is on only while both gates are open. Each of the
  three 50-point rollover switches advances bonus and scores 500 when it
  matches the randomly selected rollover, or 50 otherwise; the selected light
  remains on for the ball. Accumulated bonus is awarded at ball end and doubled
  when double bonus is active. The named game lights are mapped to the
  CobraPin WS2812 output.
- [`drop_target_scoring.py`](./Boogie/modes/drop_target_scoring/code/drop_target_scoring.py)
  scores 500 points when one of the four drop targets falls after being
  detected in its raised state.
- [`score_milestones.py`](./Boogie/modes/score_milestones/code/score_milestones.py)
  plays the 10,000-point chimes once per player and awards one extra ball when
  the player crosses each of 75,000 and 125,000 points.
- [`coils.yaml`](./Boogie/config/coils.yaml) and
  [`flippers.yaml`](./Boogie/config/flippers.yaml) contain the confirmed coil
  and dual-wound flipper configurations used by the playable game. MPF
  0.80.1's OPP platform does not implement the flipper EOS cutoff hardware
  rule, so the current flipper config does not use EOS rules. OPP hardware
  rules also require the activation switch and coil to be on the same board.

## Boogie game rules and event flow

The rules below describe the current, playable MPF configuration and Python
mode logic.

### Event flow

```text
game_starting
  └─ score_milestones starts for the game

ball_starting
  ├─ base handles configured switch scoring, accruals, and gate events
  ├─ drop_target_scoring tracks raised-then-hit drop targets
  └─ playfield_lights resets per-ball bonus, rollover, gate, and target state

playfield switch event
  ├─ base awards configured points and plays configured chimes
  ├─ playfield_lights updates bonus / special-target state and lights
  └─ player_score
       └─ score_milestones checks 10k, 75k, and 125k thresholds

s_outhole_switch active
  └─ bd_drain detects the drained ball and ejects it with c_outhole_kicker
       └─ ball_ending
            └─ playfield_lights counts down the accrued bonus
                 └─ MPF serves a same-player extra ball if player.extra_balls > 0;
                    otherwise normal ball / player progression continues
```

### Game rules

- **Game setup:** Five balls per game, up to two players, and free play.
- **Basic scoring:** The top 10-point target scores 10; the raise-gate targets,
  pop bumper, and slingshots score 50; the eight `s_500_ab` bank targets score
  500. The four physical drop targets score 500 when a target falls after its
  raised state has been observed.
- **50-point rollovers and bonus:** Each `s_50_rollover` hit increases the
  bonus by 1,000. It scores 500 if it is the randomly selected rollover for
  the current ball, and 50 otherwise. The selected rollover's 500 light stays
  on for that ball. Bonus starts at 1,000 and has no code-level cap.
- **Bonus lights and countdown:** At 10,000 or more, the 10k light stays on
  while the other bonus lights show the remainder within the current 10k
  cycle. At ball end, the full accrued amount counts down in 1,000-point
  steps, cycling the lights from 10k through 1k for each 10k of bonus.
- **Double bonus:** Hitting all four drop targets after they have been
  detected raised enables double bonus for that ball. The end-of-ball bonus
  countdown then awards twice the accrued amount.
- **Special / extra ball:** Targets 1–4 qualify the left special; targets 5–8
  qualify the right. The corresponding gate must also be open. Hitting
  `s_500_rollover_1` with the left special lit, or
  `s_500_rollover_2` with the right special lit, adds an extra ball. Claiming
  it clears that side's target progress, so the bank must be completed again
  before another award on the same ball. MPF serves earned extra balls to the
  same player without advancing the normal ball number.
- **Score milestones:** Crossing 10,000 plays both chimes once per player.
  Crossing 75,000 and 125,000 awards one extra ball at each threshold per
  player. A single score change crossing both thresholds awards both.
- **Gate events:** Completing the base-mode raise-target accruals posts
  `open_gate_a` or `open_gate_d`; `s_close_gate_1_active` and
  `s_close_gate_2_active` close the corresponding gates. `l_gates_open` is
  lit only when both gates are open.
- **Tilt:** Tilt handling is not active in the current configuration.

### Key MPF events

| Event | Current behavior |
|---|---|
| `game_starting` / `game_ending` | Starts/stops the score-milestone mode. |
| `ball_starting` / `ball_ending` | Starts the per-ball modes; ball ending waits for the bonus countdown. |
| `s_500_ab_1_active`–`s_500_ab_8_active` | Score 500, advance bonus, and progress the corresponding special bank. |
| `s_50_rollover_1_active`–`s_50_rollover_3_active` | Score 50 or 500, advance bonus, and update the selected rollover's scoring. |
| `s_drop_target_N_active` / `_inactive` | Track raised state; a valid drop scores 500 and progresses double bonus. |
| `open_gate_a` / `open_gate_d` | Open the corresponding gate and update gate/special lamps. |
| `s_close_gate_1_active` / `s_close_gate_2_active` | Close the corresponding gate and update lamps. |
| `s_500_rollover_1_active` / `s_500_rollover_2_active` | Award the matching qualified special extra ball. |
| `player_score` | Checks the 10k chime and 75k / 125k extra-ball thresholds. |
| `s_outhole_switch_active` → `ball_ending` | Detects a drained ball, ejects it, and starts end-of-ball bonus. |

#### Running Boogie on Raspberry Pi

Install MPF and the project's Python dependencies on the Pi, connect the
CobraPin boards, and make sure the MPF user can access their serial devices
(commonly by adding the user to the `dialout` group and then logging out and
back in). Check the two `/dev/serial/by-id/` entries in
[`config_raspberry_pi.yaml`](./Boogie/config/config_raspberry_pi.yaml) against
the connected boards, then run:

```bash
cd Boogie
bash run_raspberry_pi.sh
```

The script changes to its own `Boogie/` directory, so it can also be called
from elsewhere with its full path. It starts the playable MPF game using
`config.yaml` plus the Linux port override. The `-b` option skips the BCP
connection; Godot/GMC is not launched by this script. The stable
`/dev/serial/by-id/` paths avoid relying on changing `/dev/ttyACM*` numbers.

On Windows, run [`run_windows.bat`](./Boogie/run_windows.bat); it uses
`config.yaml` and the configured `COM9, COM10` ports.

### Godot / MPF-GMC

The companion Godot project is in [`Boogie/boogie-gmc/`](./Boogie/boogie-gmc/).
It includes the MPF-GMC add-on, which connects a Godot front end to MPF through
the Backbox Control Protocol (BCP), and the Boogie playfield visual reference.

[`BoogiePlayfield.gd`](./Boogie/boogie-gmc/BoogiePlayfield.gd) draws a
photo-based playfield layout with approximate, selectable markers for major
areas. [`BoogieSlide.gd`](./Boogie/boogie-gmc/BoogieSlide.gd) displays the MPF
connection state. The playfield scene also contains an MPF variable widget for
the score.

The playfield scene is a visual reference, not a ball-physics simulation. Its
markers are approximate, and the scene is not yet wired to playfield inputs or
machine hardware.

## Project layout

```text
Boogie/
  config/                  MPF machine, switch, coil, light, ball-device, and playfield config
  data/                    MPF machine variables and audit data
  modes/
    base/                  Main scoring and playfield event logic
    drop_target_scoring/   Python drop-target scoring mode
    score_milestones/      Per-player score chimes and extra-ball thresholds
    playfield_lights/      Per-ball playfield LED control
  boogie-gmc/              Godot front end and MPF-GMC integration
```

## Tests and development

Run the tests from the `Boogie/` directory using the same Python environment
that has MPF installed:

```bash
cd Boogie
python -m unittest discover -s tests -v
```

The current tests are:

- [`test_playfield_lights.py`](./Boogie/tests/test_playfield_lights.py):
  rollover scoring and one-ball rollover selection; per-ball state reset;
  bonus accumulation, 10k+ light display, end-of-ball countdown, and double
  bonus; raised-then-hit drop-target behavior; special-light prerequisites and
  repeatable extra-ball sequence; drop-target scoring; coil/switch references
  and MPF mode loading.
- [`test_score_milestones.py`](./Boogie/tests/test_score_milestones.py):
  verifies the once-per-player 10k chimes and the one-time extra-ball awards
  when score crosses 75k and 125k.

Run an individual test module while iterating:

```bash
python -m unittest discover -s tests -p test_playfield_lights.py -v
python -m unittest discover -s tests -p test_score_milestones.py -v
```

The switch, coil, and light mappings are operational on the playable machine.
Tilt handling remains disabled until a physical tilt switch is configured.
NFC-selected game modes are not implemented. Godot/GMC remains a separate
front end; the Raspberry Pi launcher above starts MPF without a BCP connection.
