from mpf.core.mode import Mode


class ScoreMilestones(Mode):

    EXTRA_BALL_SCORE_MILESTONES = (75000, 125000)

    def mode_start(self, **kwargs):
        del kwargs
        self.add_mode_event_handler(
            "player_score",
            self._check_score_milestone,
        )

    def _check_score_milestone(self, value, prev_value, **kwargs):
        del kwargs
        for milestone in self.EXTRA_BALL_SCORE_MILESTONES:
            player_var = f"extra_ball_{milestone}_awarded"
            if (
                prev_value < milestone <= value
                and not getattr(self.player, player_var, False)
            ):
                setattr(self.player, player_var, True)
                self.player.extra_balls += 1

        if (
            prev_value < 10000 <= value
            and not self.player.chime_10000_played
        ):
            self.player.chime_10000_played = True
            self.machine.coils["c_chime_50"].pulse()
            self.machine.coils["c_chime_100"].pulse()
