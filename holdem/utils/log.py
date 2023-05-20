from io import TextIOWrapper
import os
import csv
from typing import List
import matplotlib.pyplot as plt


class Logger:
    def __init__(self, log_dir: str, verbose: bool = False) -> None:
        self.log_dir: str = log_dir
        self.verbose: bool = verbose

    def __enter__(self) -> "Logger":
        self.txt_path: str = os.path.join(self.log_dir, "log.txt")
        self.csv_path: str = os.path.join(self.log_dir, "perf.csv")
        self.fig_path: str = os.path.join(self.log_dir, "fig.png")

        os.makedirs(self.log_dir, exist_ok=True)

        self.txt_file: TextIOWrapper = open(self.txt_path, "w")
        self.csv_file: TextIOWrapper = open(self.csv_path, "w")
        fieldnames: List[str] = ["episode", "reward"]
        self.writer: csv.DictWriter = csv.DictWriter(
            self.csv_file, fieldnames=fieldnames
        )
        self.writer.writeheader()

        return self

    def log(self, text: str) -> None:
        self.txt_file.write(f"{text}\n")
        self.txt_file.flush()
        if self.verbose:
            print(text)

    def log_perf(self, episode, reward) -> None:
        if self.verbose:
            print("")

        self.writer.writerow({"episode": episode, "reward": reward})
        self.log("----------------------------------------")
        self.log(f"  episode      |  {episode}")
        self.log(f"  reward       |  {reward}")
        self.log("----------------------------------------")

    def __exit__(self, type, value, traceback) -> None:
        if self.txt_path is not None:
            self.txt_file.close()
        if self.csv_path is not None:
            self.csv_file.close()

        if self.verbose:
            print("")
            print("Logs saved in", self.log_dir)
