from datetime import datetime
from typing import Dict, Optional, Union
from zipfile import Path as ZipPath
from zipfile import ZipFile

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
RESULT_FILE = "result"

NUM_PROBLEMS = 24098
NUM_FILES = len(SOLVERS) * NUM_PROBLEMS
PROCESSED_FILES = 0

###############


def evaluate_archive(path: ZipPath):
    for job_folder in path.iterdir():
        for user_folder in job_folder.iterdir():
            for sub_space_folder in user_folder.iterdir():
                evaluate_problems(sub_space_folder)


def evaluate_problems(problems_folder: ZipPath):
    for problem_category_folder in problems_folder.iterdir():
        evaluate_problem_category_all_solvers(problem_category_folder)


def analyze_problem_category_all_solvers(problem_category_folder: ZipPath):
    evaluation = evaluate_problem_category_all_solvers(problem_category_folder)
    pass


def evaluate_problem_category_all_solvers(problem_category_folder: ZipPath):
    """ returns a dictionary with the results of all problems of a category for all solvers
    e.g. evaluation = {
        "PyRes_v1.5_test1": {
            PUZ001+1.p = {
                "SZS Status": "Theorem",
                "User Timer": "3.5",
                ...
            },
            PUZ001+2.p = {
                "SZS Status": "ResourceOut",
                "User Time": "",
                ...
            },
            ...
        }
        "PyRes_v1.5_test2": { ... },
        ...
    }
    """
    evaluation: Dict[str, Dict[str, Dict[str, Union[str, float]]]] = {}

    for solver_folder in problem_category_folder.iterdir():
        print_status()
        solver = solver_folder.name
        if solver in SOLVERS:
            evaluation[solver] = evaluate_problem_category_single_solver(solver_folder)
    return evaluation


def evaluate_problem_category_single_solver(solver_folder: ZipPath) -> Dict[str, Dict[str, Union[str, float]]]:
    """ returns a dictionary with the results of a problems of a category for on solver
    e.g. evaluation = {
        PUZ001+1.p = {
            "SZS Status": "Theorem",
            "User Timer": "3.5",
            ...
        },
        PUZ001+2.p = {
            "SZS Status": "ResourceOut",
            "User Time": "",
            ...
        },
        ...
    }
    """
    evaluation = {}
    for problem_folder in solver_folder.iterdir():
        evaluation[problem_folder.name] = evaluate_single_problem(problem_folder)
    return evaluation


def evaluate_single_problem(problem_folder: ZipPath) -> Dict[str, Union[str, float]]:
    """ returns a dictionary with the results of a single file
    e.g. evaluation = {
        "SZS Status": "Theorem",
        "Resolvents computed": "256",
        "User time": "3.5"
        ...
    }
    """
    for problem_file in problem_folder.iterdir():
        evaluation = {}
        text = problem_file.read_text()
        result_type = extract_status(text)
        evaluation[STATUS_TOPIC] = result_type

        if result_type != "" and result_type not in ["ResourceOut", "Inappropriate"]:
            for topic in EVAL_TOPICS:
                evaluation[topic] = extract_result(topic, text)
        else:
            for topic in EVAL_TOPICS:
                evaluation[topic] = ""
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
        return None

    value_start = text.find(":", topic_start)
    value_end = text.find("\n", value_start)
    value_string = text[value_start+1:value_end].replace("s", "")
    return float(value_string)


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

zip_file = ZipFile(ZIP_NAME, 'r')
zip_path = ZipPath(zip_file, at='')
evaluate_archive(zip_path)

for solver in SOLVERS:
    FILES[solver].close()
