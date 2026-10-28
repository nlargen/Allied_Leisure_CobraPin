import random

from mpf.core.mode import Mode


class PlayfieldLights(Mode):

    BONUS_ROLLOVER_SWITCHES = (
        "s_50_rollover_1",
        "s_50_rollover_2",
        "s_50_rollover_3",
    )
    DROP_TARGETS = tuple(f"drop_target_{number}" for number in range(1, 5))

    def mode_start(self, **kwargs):
        del kwargs
        self._reset_ball_lights()
        self._register_switch_handlers()

    def mode_stop(self, **kwargs):
        del kwargs
        for light in self.machine.lights.values():
            light.off()

    def _reset_ball_lights(self):
        for light in self.machine.lights.values():
            light.off()

        self._bonus_value = 1000
        self._bonus_awarded = False
        self._double_bonus_active = False
        self._completed_drop_targets = set()
        self._raised_drop_targets = {
            target
            for target in self.DROP_TARGETS
            if self.machine.switch_controller.is_active(
                self.machine.switches[f"s_{target}"]
            )
        }
        self._open_gates = {"left": False, "right": False}
        self._selected_500_rollover = random.choice((1, 2, 3))

        self.machine.lights["l_bonus_1000"].on()
        self.machine.lights[
            f"l_500_when_lit_{self._selected_500_rollover}"
        ].on()

    def _register_switch_handlers(self):
        self.add_mode_event_handler(
            "ball_will_end",
            self._award_bonus,
        )

        for number, switch in enumerate(self.BONUS_ROLLOVER_SWITCHES, start=1):
            self.add_mode_event_handler(
                f"{switch}_active",
                self._rollover_hit,
                rollover_number=number,
            )

        for number in range(1, 9):
            self.add_mode_event_handler(
                f"s_500_ab_{number}_active",
                self._bonus_advance_target_hit,
                target_number=number,
            )

        for number, target in enumerate(self.DROP_TARGETS, start=1):
            switch = f"s_{target}"
            self.add_mode_event_handler(
                f"{switch}_active",
                self._drop_target_raised,
                target=target,
            )
            self.add_mode_event_handler(
                f"{switch}_inactive",
                self._drop_target_hit,
                target=target,
            )

        # Gate A / close-gate 1 are the left gate; gate D / close-gate 2 are
        # the right gate. Change these event bindings if the installed wiring
        # uses the opposite side assignment.
        self.add_mode_event_handler(
            "open_gate_a", self._gate_opened, gate="left"
        )
        self.add_mode_event_handler(
            "open_gate_d", self._gate_opened, gate="right"
        )
        self.add_mode_event_handler(
            "s_close_gate_1_active", self._gate_closed, gate="left"
        )
        self.add_mode_event_handler(
            "s_close_gate_2_active", self._gate_closed, gate="right"
        )

    def _rollover_hit(self, rollover_number, **kwargs):
        del kwargs
        self._advance_bonus()
        if rollover_number == self._selected_500_rollover:
            self.player.score += 500
            self.machine.lights[
                f"l_500_when_lit_{rollover_number}"
            ].off()
            self._selected_500_rollover = None
        else:
            self.player.score += 50

    def _bonus_advance_target_hit(self, target_number, **kwargs):
        del kwargs
        self.machine.lights[f"l_bonus_advance_{target_number}"].on()
        self._advance_bonus()

    def _advance_bonus(self):
        if self._bonus_value < 10000:
            self._bonus_value += 1000

        for value in range(1000, 11000, 1000):
            light = self.machine.lights[f"l_bonus_{value}"]
            if value == self._bonus_value:
                light.on()
            else:
                light.off()

    def _award_bonus(self, **kwargs):
        del kwargs
        if self._bonus_awarded:
            return

        multiplier = 2 if self._double_bonus_active else 1
        self.player.score += self._bonus_value * multiplier
        self._bonus_awarded = True
        self.info_log(
            "Awarded %s bonus points (%s x %s)",
            self._bonus_value * multiplier,
            self._bonus_value,
            multiplier,
        )

    def _drop_target_raised(self, target, **kwargs):
        del kwargs
        self._raised_drop_targets.add(target)

    def _drop_target_hit(self, target, **kwargs):
        del kwargs
        if target not in self._raised_drop_targets:
            return

        self._raised_drop_targets.remove(target)
        if target in self._completed_drop_targets:
            return

        self._completed_drop_targets.add(target)

        if len(self._completed_drop_targets) == len(self.DROP_TARGETS):
            self._double_bonus_active = True
            self.machine.lights["l_double_bonus"].on()

    def _gate_opened(self, gate, **kwargs):
        del kwargs
        self._open_gates[gate] = True
        self._update_gate_lights()

    def _gate_closed(self, gate, **kwargs):
        del kwargs
        self._open_gates[gate] = False
        self._update_gate_lights()

    def _update_gate_lights(self):
        if all(self._open_gates.values()):
            self.machine.lights["l_gates_open"].on()
        else:
            self.machine.lights["l_gates_open"].off()

        self._update_special_lights()

    def _update_special_lights(self):
        for gate, light_name in (
            ("left", "l_special_left"),
            ("right", "l_special_right"),
        ):
            light = self.machine.lights[light_name]
            if self._open_gates[gate]:
                light.on()
            else:
                light.off()
