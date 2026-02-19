from pyfiglet import Figlet
import re
import csv
from datetime import date
import sys
import pandas as pd
import tabulate


class Greetings:
    """
    Class methods for using Figlet on Greetings messages
    """

    @classmethod
    def create_figlet(cls):
        figlet = Figlet(font="contessa")
        cls.figlet = figlet

    @classmethod
    def welcome(cls):
        print(cls.figlet.renderText("\nmenstruation cycle tracker"))
        print(
            "+ + + Welcome! + + + \n\nThis is your personal menstruation cycle tracker.\n\nTo quit the program type 'Q'\n"
        )

    @classmethod
    def tracking(cls):
        print(cls.figlet.renderText("\ntracking"))

    @classmethod
    def analysis(cls):
        print(cls.figlet.renderText("\nanalysis"))

    @classmethod
    def goodbye(cls):
        print(cls.figlet.renderText("\nsee you tomorrow!"))
        sys.exit()


class Track:
    """
    A class for a daily tracking entry for the menstruation cycle tracker. Gets data, validates it and saves it to a cvs file
    """

    def __init__(
        self,
        date_today="",
        bleeding=0,
        physical_wellbeing=0,
        pain=0,
        mood=0,
        physical_activity=0,
        stress=0,
    ):
        self.date_today = date_today
        self.bleeding = bleeding
        self.physical_wellbeing = physical_wellbeing
        self.pain = pain
        self.mood = mood
        self.physical_activity = physical_activity
        self.stress = stress
        self.fieldnames = [
            "Date",
            "Bleeding",
            "Physical",
            "Pain",
            "Mood",
            "Activity",
            "Stress",
        ]

    def __str__(self):
        return "\nThe questions for the tracking use a scale from 0 to 10. As 0 being the lowest (for example 0 = no bleeding) and 10 the highest.\nIf you would like to exit type 'Q'\n"

    def validate(self, amount, pattern):
        """
        Verifies if input is valid, depending on regex pattern
        """
        while True:
            match = re.search(pattern, amount)
            if match is not None:
                return amount
            elif amount.upper() == "Q":
                Greetings.goodbye()
            else:
                amount = input("Please enter valid input. ").strip().upper()


    def get_date_today(self):
        """
        Check if today's data is already in CSV file. If it is, ask user if they want to overwrite data.
        """
        self.date_today = str(date.today())
        with open("tracking.csv", "r") as file:
            reader = csv.DictReader(file)
            list_dict = list(reader)
        for row in list_dict:
            if self.date_today == row["Date"]:
                print("\n+++You have already tracked your cycle today.+++\n")
                action = self.validate(
                    input(
                        "Would you like to overwrite (O) today's data or go back (B)? O/B "
                    )
                    .strip()
                    .upper(),
                    pattern=r"^(?:O|B)$",
                )
                if action == "B":
                    Greetings.welcome()
                    return False
                elif action == "O":
                    updated_list = []
                    for dict in list_dict:
                        if self.date_today != dict["Date"]:
                            updated_list.append(dict)
                    with open("tracking.csv", "w", newline="") as new_data:
                        writer = csv.DictWriter(new_data, fieldnames=self.fieldnames)
                        writer.writeheader()
                        for dict in updated_list:
                            writer.writerow(dict)
                    return True
        return True

    def get_bleeding(self, amount):
        self.bleeding = self.validate(amount, pattern=r"^(?:\d|10)$")
        self.bleeding = int(self.bleeding)

    def get_physical_wellbeing(self, amount):
        self.physical_wellbeing = self.validate(amount, pattern=r"^(?:\d|10)$")
        self.physical_wellbeing = int(self.physical_wellbeing)

    def get_pain(self, amount):
        self.pain = self.validate(amount, pattern=r"^(?:\d|10)$")
        self.pain = int(self.pain)

    def get_mood(self, amount):
        self.mood = self.validate(amount, pattern=r"^(?:\d|10)$")
        self.mood = int(self.mood)

    def get_physical_activity(self, amount):
        self.physical_activity = self.validate(amount, pattern=r"^(?:\d|10)$")
        self.physical_activity = int(self.physical_activity)

    def get_stress(self, amount):
        self.stress = self.validate(amount, pattern=r"^(?:\d|10)$")
        self.stress = int(self.stress)

    def save(self, data):
        with open("tracking.csv", "a") as tracking_file:
            writer = csv.DictWriter(
                tracking_file,
                fieldnames=self.fieldnames,
            )
            writer.writerow(data)


class Analysis:

    @classmethod
    def read_and_analyse(cls, csv_file):
        """
        class method that uses pandas to read data from csv-file and uses pandas dataFrame structure to analyse.
        """
        cycle_data = pd.read_csv(csv_file, parse_dates=["Date"])
        cycle_data = cycle_data.sort_values("Date").reset_index(drop=True)
        cycle_data = cycle_data.set_index("Date").resample("D").asfreq().reset_index()
        cycle_data["is_day_one"] = (cycle_data["Bleeding"] > 0) & (
            (cycle_data["Bleeding"].shift(1) == 0) | (cycle_data.index == 0)
        )
        cycle_data["cycle_id"] = cycle_data["is_day_one"].cumsum()
        cycle_data["cycle_id"] = cycle_data["cycle_id"].ffill()
        cycle_data["cycle_day"] = cycle_data.groupby("cycle_id").cumcount() + 1
        cycle_data["is_bleeding"] = cycle_data["Bleeding"] > 0
        cycle_data["Day"] = (
            cycle_data[cycle_data["is_bleeding"]]
            .groupby("cycle_id")
            .cumcount()
            .astype(int)
            + 1
        )
        cycle_data = cycle_data[cycle_data["cycle_id"] > 0]
        completed_cycles_data = cycle_data[
            cycle_data["cycle_id"] < cycle_data["cycle_id"].max()
        ]
        cycle_lengths = completed_cycles_data.groupby("cycle_id")["cycle_day"].max()
        average_duration = cycle_lengths.mean().astype(int)
        bleeding_max = completed_cycles_data.groupby("cycle_id")["Day"].max()
        average_bleeding = bleeding_max.mean().astype(int)
        max_pain = (
            completed_cycles_data.groupby("Pain")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Pain", ascending=False)
            .head()
        )
        max_pain.to_csv("max_pain.csv")
        max_pain = cls.get_dict("max_pain.csv")
        min_pain = (
            completed_cycles_data.groupby("Pain")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Pain")
            .head()
        )
        min_pain.to_csv("min_pain.csv")
        min_pain = cls.get_dict("min_pain.csv")
        max_mood = (
            completed_cycles_data.groupby("Mood")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Mood", ascending=False)
            .head()
        )
        max_mood.to_csv("max_mood.csv")
        max_mood = cls.get_dict("max_mood.csv")
        min_mood = (
            completed_cycles_data.groupby("Mood")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Mood")
            .head()
        )
        min_mood.to_csv("min_mood.csv")
        min_mood = cls.get_dict("min_mood.csv")
        max_physical = (
            completed_cycles_data.groupby("Physical")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Physical", ascending=False)
            .head()
        )
        max_physical.to_csv("max_physical.csv")
        max_physical = cls.get_dict("max_physical.csv")
        min_physical = (
            completed_cycles_data.groupby("Physical")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Physical")
            .head()
        )
        min_physical.to_csv("min_physical.csv")
        min_physical = cls.get_dict("min_physical.csv")
        max_stress = (
            completed_cycles_data.groupby("Stress")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Stress", ascending=False)
            .head()
        )
        max_stress.to_csv("max_stress.csv")
        max_stress = cls.get_dict("max_stress.csv")
        min_stress = (
            completed_cycles_data.groupby("Stress")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Stress")
            .head()
        )
        min_stress.to_csv("min_stress.csv")
        min_stress = cls.get_dict("min_stress.csv")
        max_active = (
            completed_cycles_data.groupby("Activity")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Activity", ascending=False)
            .head()
        )
        max_active.to_csv("max_active.csv")
        max_active = cls.get_dict("max_active.csv")
        min_active = (
            completed_cycles_data.groupby("Activity")[["cycle_day", "Bleeding"]]
            .mean()
            .astype(int)
            .sort_values(by="Activity", ascending=False)
            .head()
        )
        min_active.to_csv("min_active.csv")
        min_active = cls.get_dict("min_active.csv")
        print(
            "Average duration of one cycle: ",
            average_duration,
            " days\n",
            "Average length of menstruation: ",
            average_bleeding,
            " days\n\n",
            "Most pain in cycle:\n",
            tabulate.tabulate(max_pain, headers="keys", tablefmt="grid"),
            "\n\n\nLeast pain in cycle:\n",
            tabulate.tabulate(min_pain, headers="keys", tablefmt="grid"),
            "\n\n\nBest mood in cycle:\n",
            tabulate.tabulate(max_mood, headers="keys", tablefmt="grid"),
            "\n\n\nWorst mood in cycle:\n",
            tabulate.tabulate(min_mood, headers="keys", tablefmt="grid"),
            "\n\n\nMost physical activity in cycle:\n",
            tabulate.tabulate(max_active, headers="keys", tablefmt="grid"),
            "\n\n\nLeast physical activity in cycle:\n",
            tabulate.tabulate(min_active, headers="keys", tablefmt="grid"),
            "\n\n\nBest physical wellbeing in cycle:\n",
            tabulate.tabulate(max_physical, headers="keys", tablefmt="grid"),
            "\n\n\nWorst physical wellbeing in cycle:\n",
            tabulate.tabulate(min_physical, headers="keys", tablefmt="grid"),
            "\n\n\nMost stressful days in cycle:\n",
            tabulate.tabulate(max_stress, headers="keys", tablefmt="grid"),
            "\n\n\nLeast stress-full days in cycle:\n",
            tabulate.tabulate(min_stress, headers="keys", tablefmt="grid"),
            end="\n\n",
            sep="",
        )

    @classmethod
    def get_dict(cls, f):
        text = []
        with open(f) as file:
            reader = csv.DictReader(file)
            for row in reader:
                text.append(row)
            return text


def main():
    Greetings.create_figlet()
    Greetings.welcome()
    while True:
        action = (
            input(
                "Would you like to track (T) data, analyse (A) your cycle or quit (Q) the program? T/A/Q "
            )
            .strip()
            .upper()
        )
        if validate_action(action, pattern=r"^(?:T|A|Q)$"):
            if action == "T":
                track_and_save()
            elif action == "A":
                analyse_data()
            elif action == "Q":
                Greetings.goodbye()


def track_and_save():
    """
    Create an instance and ask for user input to get data. Save data by user's permission.
    """
    Greetings.tracking()
    track = Track()
    if track.get_date_today():
        date_today = date.today()
        formatted_date = date_today.strftime("%A, %B %d %Y")
        print(f"\n+++Let's track your data for today: {formatted_date}+++\n")
    else:
        return False
    print(track)
    track.get_bleeding(
        input("On a scale 0-10: How strong is your bleeding today? ").strip()
    )
    track.get_physical_wellbeing(
        input("On a scale 0-10: How well do you feel physically today? ").strip()
    )
    track.get_pain(
        input("On a scale 0-10: How much pain do you experience today? ").strip()
    )
    track.get_mood(input("On a scale 0-10: How is your mood today? ").strip())
    track.get_physical_activity(
        input("On a scale 0-10: How active were you physically today? ").strip()
    )
    track.get_stress(
        input("On a scale 0-10: How much stress did you experience today? ").strip()
    )
    print(
        f"\nWell done! this is your data of today, {formatted_date}. Bleeding: {track.bleeding}, physical wellbeing: {track.physical_wellbeing}, pain: {track.pain}, mood: {track.mood}, physical activity: {track.physical_activity}, stress: {track.stress}.\n"
    )
    while True:
        save = (
            input("Would you like to save the data? Yes (Y) or No (N)? Y/N ")
            .strip()
            .upper()
        )
        if validate_action(save, pattern=r"^(?:Y|N|Q)$"):
            if save == "Y":
                tracking_list = {
                    "Date": track.date_today,
                    "Bleeding": track.bleeding,
                    "Physical": track.physical_wellbeing,
                    "Pain": track.pain,
                    "Mood": track.mood,
                    "Activity": track.physical_activity,
                    "Stress": track.stress,
                }
                track.save(tracking_list)
                print("\n+++Data saved+++\n")
                return True
            elif save == "N":
                print("\n+++Data discarded+++\n")
                return True
            elif save == "Q":
                Greetings.goodbye()


def analyse_data():
    Greetings.analysis()
    Analysis.read_and_analyse("tracking.csv")


def validate_action(user_input, pattern):
    """
    Validate user input by regex pattern
    """
    match = re.search(pattern, user_input)
    if match is not None:
        return True
    else:
        print("Invalid Input.")
        return False


if __name__ == "__main__":
    main()
