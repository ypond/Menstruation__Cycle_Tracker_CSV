from project import track_and_save, analyse_data, validate_action, Track, Greetings
from datetime import date
import unittest
from unittest.mock import patch



def test_Track():
    track = Track()
    assert track.date_today == ""
    assert track.bleeding == 0
    assert track.physical_wellbeing == 0
    assert track.pain == 0
    assert track.mood == 0
    assert track.physical_activity == 0
    assert track.stress == 0
    assert track.fieldnames == [
            "Date",
            "Bleeding",
            "Physical",
            "Pain",
            "Mood",
            "Activity",
            "Stress",
        ]
    track.get_date_today()
    assert track.date_today == str(date.today())
    track.get_bleeding("10")
    assert track.bleeding == 10
    track.get_physical_wellbeing("5")
    assert track.physical_wellbeing == 5
    track.get_pain("2")
    assert track.pain == 2
    track.get_mood("7")
    assert track.mood == 7
    track.get_physical_activity("5")
    assert track.physical_activity == 5
    track.get_stress("9")
    assert track.stress == 9


class TestTrackValidate(unittest.TestCase):
    def test_track_invalidate(self):
        inputs = ["-5", "11", "1", "Q"]
        with patch('builtins.input', side_effect=inputs):
            track = Track()
            Greetings.create_figlet()
            result = track.validate("-1", pattern=r"^(?:\d|10)$")
            self.assertEqual(result, "1")
            with self.assertRaises(SystemExit):
                track.validate("-1", pattern=r"^(?:\d|10)$")

    def test_track_validate(self):
        track = Track()
        Greetings.create_figlet()
        self.assertEqual(track.validate("1", pattern=r"^(?:\d|10)$"), "1")
        self.assertEqual(track.validate("9", pattern=r"^(?:\d|10)$"), "9")


class TestTrackAndSave(unittest.TestCase):
    def test_track_and_save(self):
        with patch("project.Track.save") as mock_save:
            inputs = ["4", "5", "6", "8", "9", "4", "Y", "Q"]
            with patch("builtins.input", side_effect=inputs):
                Greetings.create_figlet()
                track_and_save()
                with self.assertRaises(SystemExit):
                    track_and_save()


class TestAnalysis(unittest.TestCase):
    def test_analyse_data(self):
        inputs = ["tracking.csv"]
        with patch('builtins.input', side_effect=inputs):
            Greetings.create_figlet()
            analyse_data()

class TestValidateAction(unittest.TestCase):
    def test_invalidate_action(self):
        inputs = ["YN", "QY"]
        with patch('builtins.input', side_effect=inputs):
            result = validate_action("23", pattern=r"^(?:Y|N|Q)$")
            self.assertEqual(result, None)

    def validate_action(self):
        self.assertEqual(validate_action("Y", pattern=r"^(?:Y|N|Q)$"), True)
        self.assertEqual(validate_action("N", pattern=r"^(?:Y|N|Q)$"), True)
        self.assertEqual(validate_action("Q", pattern=r"^(?:Y|N|Q)$"), True)

class TestValidateActionVariation(unittest.TestCase):
    def test_invalidate_action_var(self):
        inputs = ["AT", "QA"]
        with patch('builtins.input', side_effect=inputs):
            result = validate_action("23", pattern=r"^(?:T|A|Q)$")
            self.assertEqual(result, None)

    def test_validate_action(self):
        self.assertEqual(validate_action("T", pattern=r"^(?:T|A|Q)$"), True)
        self.assertEqual(validate_action("A", pattern=r"^(?:T|A|Q)$"), True)
        self.assertEqual(validate_action("Q", pattern=r"^(?:T|A|Q)$"), True)

