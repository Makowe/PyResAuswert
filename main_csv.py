from datetime import datetime
from typing import Dict, List, Optional
from zipfile import ZipFile
from zipfile import Path as ZipPath
import csv

#############

ZIP_NAMES = [
    "Job50527_output.zip",
    "Job50604_output.zip"
]
""" SOLVERS = [
    "PyRes_v2_0_sos0___PyRes_sos0",
]
"""
SOLVERS = [
    "PyRes_v2_0_sos0___PyRes_sos0",
    # "PyRes_v2_0_sos1___PyRes_sos1",
    # "PyRes_v2_0_sos2___PyRes_sos2",
    # "PyRes_v2_0_sos3___PyRes_sos3",
    "PyRes_v2.0.4_all___PyRes_sos1r1",
    "PyRes_v2.0.4_all___PyRes_sos1r2",
    "PyRes_v2.0.4_all___PyRes_sos1r3",
    "PyRes_v2.0.4_all___PyRes_sos1r4"
]

EVAL_TOPICS = [
    # "Initial clauses",
    # "Processed clauses",
    # "Factors computed",
    "Resolvents computed",
    # "Tautologies deleted",
    # "Forward subsumed",
    # "Backward subsumed",
    "User time",
    # "System time",
    # "Total time"
]

FILES = {}

RESULT_TOPIC = "SZS status"

RESULT_FILE = "result"

NUM_PROBLEMS = 24098
NUM_FILES = len(SOLVERS) * NUM_PROBLEMS
PROCESSED_FILES = 0

###############


def evaluate_archive(path):
    for job_folder in path.iterdir():
        for user_folder in job_folder.iterdir():
            for sub_space_folder in user_folder.iterdir():
                evaluate_problems(sub_space_folder)


def evaluate_problems(path):
    for category_folder in path.iterdir():
        for solver_folder in category_folder.iterdir():
            print_status()
            solver = solver_folder.name
            if solver in SOLVERS:
                evaluate_problem_category(solver_folder, FILES[solver])


def evaluate_problem_category(path, file):
    file.write("\n".join([evaluate_problem_folder(x, x.name) for x in path.iterdir()]))


def evaluate_problem_folder(path, problem_name) -> str:
    for problem_file in path.iterdir():
        text = problem_file.read_text()
        result_type = extract_result(RESULT_TOPIC, text)
        evaluation = [problem_name, result_type]

        if result_type != "" and result_type not in ["ResourceOut", "Inappropriate"]:
            evaluation.extend([extract_topic(topic, text) for topic in EVAL_TOPICS])
        else:
            evaluation.extend("" for topic in EVAL_TOPICS)
        global PROCESSED_FILES
        PROCESSED_FILES += 1
        return ",".join(evaluation)


def extract_result(topic: str, text) -> str:
    topic_start = text.find(topic)
    if topic_start == -1:
        return ""

    value_start = topic_start + len(topic)
    value_end = text.find("\n", value_start)
    text_content = text[value_start+1:value_end]
    return text_content


def extract_topic(topic: str, text) -> str:
    topic_start = text.find(topic)
    if topic_start == -1:
        return ""

    value_start = text.find(":", topic_start)
    value_end = text.find("\n", value_start)
    value_string = text[value_start+1:value_end].replace("s", "")
    return value_string


def print_status():
    percentage = PROCESSED_FILES / NUM_FILES
    if percentage == 0:
        return
    current_time = datetime.now()
    running = current_time - start_time
    time_left = (running / percentage) * (1-percentage)
    print(f"{round(percentage * 100, 2)}% finished \t expected time: {current_time+time_left}")

###############

start_time = datetime.now()

for solver in SOLVERS:
    FILES[solver] = open(f"{RESULT_FILE}_{solver}.csv", "w+", newline="")

for zip_name in ZIP_NAMES:
    zip_file = ZipFile(zip_name, 'r')
    zip_path = ZipPath(zip_file, at='')
    evaluate_archive(zip_path)

for solver in SOLVERS:
    FILES[solver].close()
