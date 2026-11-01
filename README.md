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
  to two players, loads the base, tilt, drop-target-scoring, and playfield
  lights modes, and selects the OPP platform with Gen2 driver boards for
  CobraPin. The `opp.ports` entry is OS-specific: use the COM ports Windows
  assigns to the boards when MPF runs on Windows (currently `COM7, COM8` as
  temporary values), or the verified `/dev/ttyACM*` paths when MPF runs on a
  Raspberry Pi/Linux. Update this one setting when changing hosts; the example
  port values must be confirmed on the machine that runs MPF.
- [`switches.yaml`](./Boogie/config/switches.yaml) maps the playfield and
  cabinet switches to logical switch names. Hardware address values follow the
  requested `0-0-N` pattern, with dedicated `1-0-N` addresses for the start,
  flipper, tilt, and credit switches; verify and replace these placeholders
  with the actual CobraPin addresses.
- [`balldevices.yaml`](./Boogie/config/balldevices.yaml) and
  [`playfields.yaml`](./Boogie/config/playfields.yaml) describe Boogie's
  documented EM-style, no-trough ball flow. Preserve this machine-specific
  arrangement rather than assuming a modern trough and shooter-lane layout.
- [`base.yaml`](./Boogie/modes/base/config/base.yaml) contains the main
  switch-driven scoring and playfield logic. It awards points for configured
  targets, rollovers, pop bumper, and slingshots, tracks completion of target
  banks, and applies the current -5000-point tilt penalty.
- [`lights.yaml`](./Boogie/config/lights.yaml) defines 25 sequential logical
  playfield lights. The `playfield_lights` mode controls the bonus ladder,
  target-progress indicators, random 500-when-lit rollover indicator, double
  bonus, gate-open, and special lamps per ball. Each special lamp follows its
  corresponding gate independently of double bonus; the gates-open lamp is on
  only while both gates are open. Each of the three 50-point
  rollover switches scores an additional 500 points once per ball when its
  matching randomly selected 500-when-lit lamp is lit. Accumulated bonus is
  awarded at ball end and doubled when double bonus is active. These logical
  light numbers are currently virtual; the CobraPin WS2812 output mapping
  still needs commissioning.
- The built-in MPF `tilt` mode is enabled. The physical tilt switch is tagged
  as `tilt`, allowing MPF to handle tilt behavior and ball ending.
- [`drop_target_scoring.py`](./Boogie/modes/drop_target_scoring/code/drop_target_scoring.py)
  scores 1000 points when one of the four drop targets falls after being
  detected in its raised state.
- [`coils.yaml`](./Boogie/config/coils.yaml) and
  [`flippers.yaml`](./Boogie/config/flippers.yaml) describe draft coil and
  dual-wound flipper configurations. Coil hardware addresses follow the
  requested `0-0-N` placeholder pattern. The current pulse/hold values are
  unvalidated commissioning drafts, not factory specifications or confirmed
  safe settings.

The checked-in machine config selects the physical OPP platform, but this
configuration is not ready to energize hardware until the switch and coil
addresses and coil settings have been verified against the actual CobraPin
boards and machine wiring. The dual-wound flipper config is loaded; its
activation/EOS switches, main/hold coil addresses, and pulse/hold settings must
be verified before testing flippers. Playfield light hardware mappings still
need commissioning.

MPF does not automatically choose between Windows COM names and Linux
`/dev/tty*` paths from a single static `opp.ports` value. For now, set that
value for the computer running MPF before startup. To avoid editing the
shared config when switching hosts, use separate Windows/Linux OPP config
overrides and a platform-specific launcher that selects the appropriate
override. OPP also supports identifying CobraPin boards by their configured
serial numbers to avoid dependence on which port each board is assigned; this
does not remove the need to use the appropriate OS-specific connection setup.

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
    playfield_lights/      Per-ball playfield LED control
  boogie-gmc/              Godot front end and MPF-GMC integration
```

## Development and next steps

The current setup is for virtual development. Before physical play:

Run the playfield light and device-reference regression tests from `Boogie/`
with the project's MPF Python environment:
`python -m unittest discover -s tests -v`.

1. Verify the OPP serial port names on the host running MPF: Windows COM ports
   on the development PC, or `/dev/ttyACM*` paths on the Raspberry Pi.
2. Replace the placeholder coil and switch addresses with verified CobraPin
   assignments; validate all pulse, hold, fuse, and driver settings against
   reliable hardware documentation.
3. Confirm the Boogie wiring and CobraPin output limits, including flipper EOS
   behavior and both windings of Allied coil 264-1-155. The flipper config is
   loaded; test it only after verifying its coil and switch mappings.
4. Validate the documented no-trough ball flow, tilt handling, switches,
   actuators, scoring, and game lifecycle on the machine.
5. Connect Godot/GMC to MPF and implement any desired interactive display or
   game-selection features. NFC-selected game modes are not implemented yet.

The 3 ms coil pulse, 5 ms software maximum, and 25% flipper hold-power entries
currently in `coils.yaml` are tentative software limits only. They have not
been validated against the original coils or CobraPin hardware. A software
limit does not establish a safe current or make incorrect wiring safe; do not
energize the coils based on these draft values alone.
