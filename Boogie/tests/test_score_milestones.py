import unittest
from types import SimpleNamespace

from modes.score_milestones.code.score_milestones import ScoreMilestones


class FakeCoil:

    def __init__(self):
        self.pulse_count = 0

    def pulse(self):
        self.pulse_count += 1


class ScoreMilestonesTest(unittest.TestCase):

    def setUp(self):
        self.coils = {
            name: FakeCoil()
            for name in ("c_chime_50", "c_chime_100")
        }
        self.handlers = []
        self.mode = ScoreMilestones.__new__(ScoreMilestones)
        self.mode.machine = SimpleNamespace(coils=self.coils)
        self.mode.player = SimpleNamespace(
            score=0,
            extra_balls=0,
            chime_10000_played=False,
        )
        self.mode.add_mode_event_handler = (
            lambda event, handler, **kwargs:
            self.handlers.append((event, handler, kwargs))
        )
        self.mode.mode_start()

    def post_score(self, value, prev_value):
        for event, handler, kwargs in self.handlers:
            if event == "player_score":
                handler(value=value, prev_value=prev_value, **kwargs)

    def test_score_milestones_award_each_extra_ball_once(self):
        self.post_score(value=74999, prev_value=74000)
        self.assertEqual(0, self.mode.player.extra_balls)

        self.post_score(value=75000, prev_value=74999)
        self.assertEqual(1, self.mode.player.extra_balls)

        self.post_score(value=80000, prev_value=75000)
        self.assertEqual(1, self.mode.player.extra_balls)

        self.post_score(value=125000, prev_value=124500)
        self.assertEqual(2, self.mode.player.extra_balls)

        self.post_score(value=130000, prev_value=125000)
        self.assertEqual(2, self.mode.player.extra_balls)

    def test_ten_thousand_score_milestone_plays_both_chimes_once(self):
        self.post_score(value=9999, prev_value=9000)
        self.assertEqual(0, self.coils["c_chime_50"].pulse_count)
        self.assertEqual(0, self.coils["c_chime_100"].pulse_count)

        self.post_score(value=10000, prev_value=9999)
        self.assertEqual(1, self.coils["c_chime_50"].pulse_count)
        self.assertEqual(1, self.coils["c_chime_100"].pulse_count)

        self.post_score(value=20000, prev_value=10000)
        self.assertEqual(1, self.coils["c_chime_50"].pulse_count)
        self.assertEqual(1, self.coils["c_chime_100"].pulse_count)
