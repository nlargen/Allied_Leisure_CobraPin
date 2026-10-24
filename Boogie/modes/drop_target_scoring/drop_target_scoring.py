
from mpf.core.mode import Mode

class DropTargetScoring(Mode):

    def mode_start(self, **kwargs):
        self.armed = {}

        for number in range(1, 5):
            target = f"drop_target_{number}"
            switch_name = f"s_{target}"

            # NC switch: active means the target is raised.
            is_raised = self.machine.switch_controller.is_active(
                self.machine.switches[switch_name]
            )
            self.armed[target] = is_raised

            self.add_mode_event_handler(
                f"{switch_name}_active",
                self.target_raised,
                target=target
            )

            self.add_mode_event_handler(
                f"{switch_name}_inactive",
                self.target_dropped,
                target=target
            )

    def target_raised(self, target, **kwargs):
        self.armed[target] = True

    def target_dropped(self, target, **kwargs):
        if not self.armed[target]:
            return

        self.armed[target] = False
        self.player.score += 1000

        self.machine.log.info(
            "Drop target %s scored 1000 points", target
        )
