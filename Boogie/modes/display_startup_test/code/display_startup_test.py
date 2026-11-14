from mpf.core.mode import Mode
from mpf.core.rgb_color import RGBColor
from mpf.platforms.interfaces.segment_display_platform_interface import FlashingType


class DisplayStartupTest(Mode):

    DISPLAY_NAMES = (
        "player1_display",
        "player2_display",
        "player3_display",
        "player4_display",
        "ball_display",
    )
    STEP_DURATION_MS = 1000
    BOOGIE_DURATION_MS = 5000

    def mode_start(self, **kwargs):
        del kwargs
        self._digit = 0
        self._set_display_text("BOOGIE")
        self.delay.add(
            ms=self.BOOGIE_DURATION_MS,
            callback=self._start_digit_test,
            name="start_digit_test",
        )

    def _start_digit_test(self):
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
            self._show_flashing_zeros()
            return

        self._digit += 1
        self._show_digit()
        self.delay.add(
            ms=self.STEP_DURATION_MS,
            callback=self._advance_digit,
            name="advance_digit",
        )

    def _show_digit(self):
        self._set_display_text(str(self._digit))

    def _show_flashing_zeros(self):
        self._set_display_text("0", FlashingType.FLASH_ALL)

    def _set_display_text(self, text, flashing=FlashingType.NO_FLASH):
        for display_name in self.DISPLAY_NAMES:
            display = self.machine.segment_displays[display_name]
            if len(text) == 1 and text.isdigit():
                display_text = text * display.size
            elif display.size == 2 and text == "BOOGIE":
                display_text = "bL"
            else:
                display_text = text
            display.add_text_entry(
                text=display_text,
                color=[RGBColor("white")],
                flashing=flashing,
                flash_mask="",
                transition=None,
                transition_out=None,
                priority=100,
                key="display_startup_test",
            )
