from mpf.core.mode import Mode
from mpf.platforms.interfaces.segment_display_platform_interface import FlashingType


class DisplayStartupTest(Mode):

    DISPLAY_NAMES = ("player1_display", "player2_display")
    STEP_DURATION_MS = 1000

    def mode_start(self, **kwargs):
        del kwargs
        self._digit = 0
        self._show_digit()
        self.delay.add(
            ms=self.STEP_DURATION_MS,
            callback=self._advance_digit,
            name="advance_digit",
        )

    def mode_stop(self, **kwargs):
        del kwargs
        self._set_display_text("")

    def _advance_digit(self):
        if self._digit == 9:
            self.stop()
            return

        self._digit += 1
        self._show_digit()
        self.delay.add(
            ms=self.STEP_DURATION_MS,
            callback=self._advance_digit,
            name="advance_digit",
        )

    def _show_digit(self):
        self._set_display_text(str(self._digit) * 8)

    def _set_display_text(self, text):
        for display_name in self.DISPLAY_NAMES:
            self.machine.segment_displays[display_name].add_text_entry(
                text=text,
                color=None,
                flashing=FlashingType.NO_FLASH,
                flash_mask="",
                transition=None,
                transition_out=None,
                priority=100,
                key="display_startup_test",
            )
