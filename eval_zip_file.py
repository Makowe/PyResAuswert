import json
from datetime import datetime
from typing import Dict, Optional, Union
from zipfile import Path as ZipPath, ZipInfo, ZipFile

from Conclusion import Conclusion

#############

ZIP_NAME = "Job50527_output.zip"

SOLVERS = [
    "PyRes_v2_0_sos0___PyRes_sos0",
    "PyRes_v2_0_sos1___PyRes_sos1",
    "PyRes_v2_0_sos2___PyRes_sos2",
    "PyRes_v2_0_sos3___PyRes_sos3",
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

STATUS_TOPIC = "SZS status"
STATUS_TOPIC_LEN = len(STATUS_TOPIC)

ALL_TOPICS = EVAL_TOPICS.copy()
ALL_TOPICS.append(STATUS_TOPIC)

FILES = {}
RESULT_FOLDER = "results"

NUM_PROBLEMS = 24098
NUM_FILES = len(SOLVERS) * NUM_PROBLEMS
PROCESSED_FILES = 0

###############


def init_evaluation() -> dict:
    evaluation_all = {}
    for solver in SOLVERS:
        evaluation_all[solver] = {}
    return evaluation_all


def get_solver_and_problem(single_file: ZipInfo) -> (str, str):
    folders = single_file.filename.split("/")
    solver = folders[4]
    problem = folders[5]
    return solver, problem


def evaluate_archive(zip_file: ZipFile) -> dict:
    info_list = zip_file.infolist()
    evaluation_all = init_evaluation()

    for single_file in info_list:
        solver, problem = get_solver_and_problem(single_file)
        if solver in SOLVERS:
            evaluation_single = evaluate_problem(zip_file, single_file)
            evaluation_all[solver][problem] = evaluation_single
            if not PROCESSED_FILES % 100:
                print_status(PROCESSED_FILES)
    conclusion = Conclusion.conclude(evaluation_all, EVAL_TOPICS, SOLVERS)
    return conclusion


def evaluate_problem(zip_file: ZipFile, file_info: ZipInfo) -> Dict[str, Union[str, float]]:
    """ returns a dictionary with the results of a single file
    e.g. evaluation = {
        "SZS Status": "Theorem",
        "Resolvents computed": "256",
        "User time": "3.5"
        ...
    }
    """
    evaluation = {}
    file = zip_file.open(file_info.filename, "r")
    text = file.read().decode("utf-8")

    result_type = extract_status(text)
    evaluation[STATUS_TOPIC] = result_type

    if result_type != "" and result_type not in ["ResourceOut", "Inappropriate"]:
        for topic in EVAL_TOPICS:
            evaluation[topic] = extract_result(topic, text)
    else:
        for topic in EVAL_TOPICS:
            evaluation[topic] = float("nan")
    global PROCESSED_FILES
    PROCESSED_FILES += 1
    return evaluation


def extract_status(text) -> str:
    """ returns the string of the result, e.g. "Theorem" or "Satisfiable" """
    topic_start = text.find(STATUS_TOPIC)
    if topic_start == -1:
        return ""

    value_start = topic_start + STATUS_TOPIC_LEN
    value_end = text.find("\n", value_start)
    text_content = text[value_start+1:value_end]
    return text_content


def extract_result(topic: str, text) -> Optional[float]:
    """ returns the value of a given topic
    e.g. input: "User Timer", output: 2.6
    """
    topic_start = text.find(topic)
    if topic_start == -1:
        return float("nan")

    value_start = text.find(":", topic_start)
    value_end = text.find("\n", value_start)
    value_string = text[value_start+1:value_end].replace("s", "")
    return float(value_string)

#####################


def export_conclusion(problem_category, conclusion):
    file = open(f"{RESULT_FOLDER}/{problem_category}.json", "w+")
    output = json.dumps(conclusion, sort_keys=True, indent=4)
    file.write(output)
    file.close()


def print_status(message):
    percentage = PROCESSED_FILES / NUM_FILES
    if percentage == 0:
        return
    current_time = datetime.now()
    running = current_time - start_time
    time_left = (running / percentage) * (1-percentage)
    print(f"{message} {round(percentage * 100, 2)}% finished \t expected time: {current_time+time_left}")

###############


start_time = datetime.now()

zip_file = ZipFile(ZIP_NAME, 'r')
conclusion = evaluate_archive(zip_file)
