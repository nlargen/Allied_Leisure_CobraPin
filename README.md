# Allied_Leisure_CobraPin
repository for MPF code for modernization of Allied Leisure pinball machines to include Boogie, Rock-on, TNT, and Dyn o mite. 

Boogie coil configuration — 3 ms commissioning draft
Target: MPF 0.80.1 and CobraPin.

Contents:
- coils.yaml: initial 3 ms pulses, 5 ms software maximum, coil names and placeholders.
- flippers.yaml: dual-wound flippers using MPF EOS-based changeover.

Before energizing:
1. Replace driver placeholders with verified CobraPin output numbers.
2. Verify coil resistance, winding identity, 24 V wiring, common ground, diode polarity,
   and suppression arrangement.
3. Confirm the actual CobraPin driver and bank current/thermal limits.
4. Test one output at a time starting at 3 ms, increasing only as needed.

Important:
- max_pulse_ms limits software pulse duration; it does not limit peak current.
- The flipper hold-power setting of 25% is not validated for this hardware. Confirm that
  the controller supports the requested hold behavior and that the flipper holds safely
  without overheating before using it in normal play.
- The original 8 A fuse does not by itself prove an individual driver can handle every coil.
- These are commissioning starting points, not verified factory settings.
