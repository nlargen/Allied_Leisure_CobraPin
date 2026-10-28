import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from mpf.file_interfaces.yaml_interface import YamlInterface
from mpf.tests.MpfTestCase import MpfTestCase
from modes.playfield_lights.code.playfield_lights import PlayfieldLights


BOOGIE_ROOT = Path(__file__).resolve().parents[1]


class FakeLight:

    def __init__(self):
        self.is_on = False

    def on(self):
        self.is_on = True

    def off(self):
        self.is_on = False


class PlayfieldLightsTest(unittest.TestCase):

    def setUp(self):
        self.active_switches = set()
        self.lights = {
            f"l_bonus_{value}": FakeLight()
            for value in range(1000, 11000, 1000)
        }
        self.lights.update({
            f"l_bonus_advance_{number}": FakeLight()
            for number in range(1, 9)
        })
        self.lights.update({
            f"l_500_when_lit_{number}": FakeLight()
            for number in range(1, 4)
        })
        self.lights.update({
            name: FakeLight()
            for name in (
                "l_special_left",
                "l_special_right",
                "l_double_bonus",
                "l_gates_open",
            )
        })

        self.mode = PlayfieldLights.__new__(PlayfieldLights)
        self.mode.machine = SimpleNamespace(
            lights=self.lights,
            switches={
                f"s_drop_target_{number}": f"s_drop_target_{number}"
                for number in range(1, 5)
            },
            switch_controller=SimpleNamespace(
                is_active=lambda switch: switch in self.active_switches
            ),
        )
        self.mode.player = SimpleNamespace(score=0)
        self.mode.info_log = Mock()
        self.mode.handlers = []
        self.mode.add_mode_event_handler = (
            lambda event, handler, **kwargs:
            self.mode.handlers.append((event, handler, kwargs))
        )

    def start_mode(self, selected_rollover=1):
        with patch(
            "modes.playfield_lights.code.playfield_lights.random.choice",
            return_value=selected_rollover,
        ):
            self.mode.mode_start()

    def post(self, event):
        for registered_event, handler, kwargs in self.mode.handlers:
            if registered_event == event:
                handler(**kwargs)

    def test_selected_rollover_scores_500_once(self):
        self.start_mode(selected_rollover=2)

        self.assertTrue(self.lights["l_500_when_lit_2"].is_on)
        self.assertEqual(
            1,
            sum(
                self.lights[f"l_500_when_lit_{number}"].is_on
                for number in range(1, 4)
            ),
        )
        self.post("s_50_rollover_1_active")
        self.assertEqual(50, self.mode.player.score)
        self.assertEqual(2000, self.mode._bonus_value)

        self.post("s_50_rollover_2_active")
        self.assertEqual(550, self.mode.player.score)
        self.assertFalse(self.lights["l_500_when_lit_2"].is_on)
        self.assertEqual(3000, self.mode._bonus_value)

        self.post("s_50_rollover_2_active")
        self.assertEqual(600, self.mode.player.score)

    def test_base_mode_does_not_add_duplicate_rollover_scoring(self):
        base_config = YamlInterface.process(
            (
                BOOGIE_ROOT
                / "modes"
                / "base"
                / "config"
                / "base.yaml"
            ).read_text(encoding="utf-8")
        )

        for number in range(1, 4):
            event = f"s_50_rollover_{number}_active"
            self.assertNotIn(
                "score",
                base_config["variable_player"][event],
            )

    def test_ball_reset_restores_bonus_and_selects_one_rollover(self):
        self.start_mode(selected_rollover=3)
        self.post("s_500_ab_1_active")
        self.post("s_drop_target_1_active")
        self.post("s_drop_target_1_inactive")
        self.mode._gate_opened("left")

        with patch(
            "modes.playfield_lights.code.playfield_lights.random.choice",
            return_value=1,
        ):
            self.mode._reset_ball_lights()

        self.assertEqual(1000, self.mode._bonus_value)
        self.assertFalse(self.mode._double_bonus_active)
        self.assertFalse(self.mode._open_gates["left"])
        self.assertEqual(set(), self.mode._completed_drop_targets)
        self.assertTrue(self.lights["l_bonus_1000"].is_on)
        self.assertTrue(self.lights["l_500_when_lit_1"].is_on)
        self.assertEqual(
            1,
            sum(
                self.lights[f"l_500_when_lit_{number}"].is_on
                for number in range(1, 4)
            ),
        )
        self.assertFalse(self.lights["l_bonus_advance_1"].is_on)
        self.assertFalse(self.lights["l_special_left"].is_on)

    def test_ball_will_end_awards_accumulated_bonus_once(self):
        self.start_mode(selected_rollover=3)
        self.post("s_50_rollover_1_active")
        self.post("s_500_ab_1_active")
        self.assertEqual(50, self.mode.player.score)
        self.assertEqual(3000, self.mode._bonus_value)

        self.post("ball_will_end")
        self.assertEqual(3050, self.mode.player.score)
        self.post("ball_will_end")
        self.assertEqual(3050, self.mode.player.score)

    def test_ball_will_end_doubles_bonus_when_double_bonus_is_lit(self):
        self.start_mode()
        self.mode._bonus_value = 7000
        self.mode._double_bonus_active = True

        self.post("ball_will_end")

        self.assertEqual(14000, self.mode.player.score)
        self.assertTrue(self.mode._bonus_awarded)

    def test_bonus_advances_from_rollovers_and_500_targets_and_caps(self):
        self.start_mode()

        self.post("s_50_rollover_1_active")
        self.assertEqual(2000, self.mode._bonus_value)
        self.post("s_500_ab_4_active")
        self.assertEqual(3000, self.mode._bonus_value)
        self.assertTrue(self.lights["l_bonus_advance_4"].is_on)

        for _ in range(20):
            self.post("s_50_rollover_1_active")

        self.assertEqual(10000, self.mode._bonus_value)
        self.assertTrue(self.lights["l_bonus_10000"].is_on)

    def test_drop_target_must_be_raised_before_it_counts(self):
        self.start_mode()

        self.post("s_drop_target_1_inactive")
        self.assertNotIn("drop_target_1", self.mode._completed_drop_targets)

        for number in range(1, 5):
            target = f"drop_target_{number}"
            self.post(f"s_{target}_active")
            self.post(f"s_{target}_inactive")

        self.assertEqual(4, len(self.mode._completed_drop_targets))
        self.assertTrue(self.mode._double_bonus_active)
        self.assertTrue(self.lights["l_double_bonus"].is_on)

    def test_gate_and_special_lights_follow_gate_states(self):
        self.start_mode()

        self.post("open_gate_a")
        self.assertTrue(self.lights["l_special_left"].is_on)
        self.assertFalse(self.lights["l_special_right"].is_on)
        self.assertFalse(self.lights["l_gates_open"].is_on)

        self.post("open_gate_d")
        self.assertTrue(self.lights["l_gates_open"].is_on)
        self.assertTrue(self.lights["l_special_right"].is_on)

        self.post("s_close_gate_1_active")
        self.assertFalse(self.lights["l_gates_open"].is_on)
        self.assertFalse(self.lights["l_special_left"].is_on)
        self.assertTrue(self.lights["l_special_right"].is_on)

    def test_coil_player_and_autofire_coils_are_declared(self):
        machine_config = YamlInterface.process(
            (BOOGIE_ROOT / "config" / "config.yaml").read_text(
                encoding="utf-8"
            )
        )
        switch_config = YamlInterface.process(
            (BOOGIE_ROOT / "config" / "switches.yaml").read_text(
                encoding="utf-8"
            )
        )
        flipper_config = YamlInterface.process(
            (BOOGIE_ROOT / "config" / "flippers.yaml").read_text(
                encoding="utf-8"
            )
        )
        coil_config = YamlInterface.process(
            (BOOGIE_ROOT / "config" / "coils.yaml").read_text(
                encoding="utf-8"
            )
        )
        base_config = YamlInterface.process(
            (
                BOOGIE_ROOT
                / "modes"
                / "base"
                / "config"
                / "base.yaml"
            ).read_text(encoding="utf-8")
        )
        declared_coils = set(coil_config["coils"])
        referenced_coils = set(base_config["coil_player"].values())
        referenced_coils.update(
            settings["coil"]
            for settings in machine_config["autofire_coils"].values()
        )
        referenced_switches = {
            settings["switch"]
            for settings in machine_config["autofire_coils"].values()
        }
        for flipper in flipper_config["flippers"].values():
            referenced_coils.update(
                (flipper["main_coil"], flipper["hold_coil"])
            )
            referenced_switches.update(
                (flipper["activation_switch"], flipper["eos_switch"])
            )
        declared_switches = set(switch_config["switches"])

        self.assertEqual(set(), referenced_coils - declared_coils)
        self.assertEqual(set(), referenced_switches - declared_switches)


class BoogieMachineStartupTest(MpfTestCase):

    def get_machine_path(self):
        return str(BOOGIE_ROOT)

    def get_config_file(self):
        return "config.yaml"

    def test_all_configured_modes_load(self):
        self.assertIn("drop_target_scoring", self.machine.modes)
        self.assertIn("playfield_lights", self.machine.modes)


if __name__ == "__main__":
    unittest.main()
