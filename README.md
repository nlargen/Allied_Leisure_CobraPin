# Allied Leisure Boogie Modernization

This repository contains Mission Pinball Framework (MPF) and Godot-based
modernization work for Allied Leisure pinball machines, including Boogie,
Rock-On, T.N.T., and Dyn-O-Mite. The Boogie project is the active example
documented here.

## Boogie hardware design

The Boogie is a hybrid electromechanical/solid-state machine. The modernization
is intended to replace its original control electronics with a CobraPin
controller while retaining the original playfield mechanisms and coils.

The planned electrical arrangement uses:

- A 24 V supply for the original playfield coils and mechanisms.
- A 24 V-to-5 V DC-DC converter to supply the GI lights.
- A CobraPin controller, hosted by a raspberry pi 3 b+ running MPF.
- The original playfield mechanisms and coils, controlled by CobraPin outputs
  and MPF rules.

This is the intended system architecture, not a wiring diagram. Confirm the
power, grounding, fusing, driver ratings, coil suppression, and lamp
requirements against the machine and controller documentation before connecting
or energizing hardware.

Switch matrix and coil mapping to be provided later. 

## Software overview

### Mission Pinball Framework

The MPF machine configuration is in [`Boogie/config/`](./Boogie/config/), with
game modes in [`Boogie/modes/`](./Boogie/modes/).

- [`config.yaml`](./Boogie/config/config.yaml) sets up a five-ball game for up
  to two players, loads the base, tilt, and drop-target-scoring modes, and
  currently selects MPF's `smart_virtual` platform for development.
- [`switches.yaml`](./Boogie/config/switches.yaml) maps the playfield and
  cabinet switches to logical switch names. CobraPin switch addresses still
  need to be entered for the physical installation.
- [`balldevices.yaml`](./Boogie/config/balldevices.yaml) and
  [`playfields.yaml`](./Boogie/config/playfields.yaml) describe Boogie's
  documented EM-style, no-trough ball flow. Preserve this machine-specific
  arrangement rather than assuming a modern trough and shooter-lane layout.
- [`base.yaml`](./Boogie/modes/base/config/base.yaml) contains the main
  switch-driven scoring and playfield logic. It awards points for configured
  targets, rollovers, pop bumper, and slingshots, tracks completion of target
  banks, and applies the current -5000-point tilt penalty.
- The built-in MPF `tilt` mode is enabled. The physical tilt switch is tagged
  as `tilt`, allowing MPF to handle tilt behavior and ball ending.
- [`drop_target_scoring.py`](./Boogie/modes/drop_target_scoring/drop_target_scoring.py)
  scores 1000 points when one of the four drop targets falls after being
  detected in its raised state.
- [`coils.yaml`](./Boogie/config/coils.yaml) and
  [`flippers.yaml`](./Boogie/config/flippers.yaml) describe draft coil and
  dual-wound flipper configurations. The coil addresses are placeholders, and
  the current pulse/hold values are unvalidated commissioning drafts, not
  factory specifications or confirmed safe settings.

The physical CobraPin platform and the coil/flipper files are not currently
enabled in the machine config. The checked-in machine config remains on
`smart_virtual`; the coil config include is commented out, and the flipper
config is not included. Complete and verify the hardware mappings and driver
settings before switching to CobraPin or energizing coils. The current
configuration should not be treated as a ready-to-run physical machine setup.

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
  config/                  MPF machine, switch, coil, ball-device, and playfield config
  data/                    MPF machine variables and audit data
  modes/
    base/                  Main scoring and playfield event logic
    drop_target_scoring/   Python drop-target scoring mode
  boogie-gmc/              Godot front end and MPF-GMC integration
```

## Development and next steps

The current setup is for virtual development. Before physical play:

1. Confirm the Boogie wiring and the CobraPin output limits, including the
   flipper EOS behavior and the two windings of Allied coil 264-1-155.
2. Replace the placeholder coil and switch addresses with verified CobraPin
   assignments; validate all pulse, hold, fuse, and driver settings against
   reliable hardware documentation.
3. Enable the appropriate coil and flipper configuration files and change the
   platform from `smart_virtual` to CobraPin's OPP platform configuration.
4. Validate the documented no-trough ball flow, tilt handling, switches,
   actuators, scoring, and game lifecycle on the machine.
5. Connect Godot/GMC to MPF and implement any desired interactive display or
   game-selection features. NFC-selected game modes are not implemented yet.

The 3 ms coil pulse, 5 ms software maximum, and 25% flipper hold-power entries
currently in `coils.yaml` are tentative software limits only. They have not
been validated against the original coils or CobraPin hardware. A software
limit does not establish a safe current or make incorrect wiring safe; do not
energize the coils based on these draft values alone.
