from datetime import datetime
from typing import Dict, List, Optional
from zipfile import ZipFile
from zipfile import Path as ZipPath
import json


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
    "PyRes_v2_0_sos1___PyRes_sos1",
    "PyRes_v2_0_sos2___PyRes_sos2",
    "PyRes_v2_0_sos3___PyRes_sos3",
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

RESULT_TOPIC = "SZS status"

RESULT_FILE = "result.json"

NUM_PROBLEMS = 24098
NUM_FILES = len(SOLVERS) * NUM_PROBLEMS

###############


def evaluate_archive(path, result: Dict[str, List[dict]]):
    for solver in SOLVERS:
        result[solver] = []
    for job_folder in path.iterdir():
        for user_folder in job_folder.iterdir():
            for sub_space_folder in user_folder.iterdir():
                evaluate_problems(sub_space_folder, result)


def evaluate_problems(path, result: Dict[str, List[dict]]):
    for category_folder in path.iterdir():
        for solver_folder in category_folder.iterdir():
            solver = solver_folder.name
            if solver in SOLVERS:
                evaluate_problem_category(solver_folder, result[solver])
        print_status()


def evaluate_problem_category(path, result: List[dict]):
    result.extend([evaluate_problem_folder(x, x.name) for x in path.iterdir()])


def evaluate_problem_folder(path, problem_name) -> dict:
    for problem_file in path.iterdir():
        return evaluate_problem_file(problem_file, problem_name)


def evaluate_problem_file(problem_file, problem_name) -> dict:
    evaluation: dict = {}

    text = problem_file.read_text()
    result_type = extract_result(RESULT_TOPIC, text)

    evaluation["Result"] = result_type
    evaluation["Name"] = problem_name
    if result_type is not None and result_type not in ["ResourceOut", "Inappropriate"]:
        for topic in EVAL_TOPICS:
            evaluation[topic] = extract_topic(topic, text)
    return evaluation


def extract_result(topic: str, text) -> Optional[str]:
    topic_start = text.find(topic)
    if topic_start == -1:
        return None

    value_start = topic_start + len(topic)
    value_end = text.find("\n", value_start)
    text_content = text[value_start+1:value_end]
    return text_content


def extract_topic(topic: str, text) -> Optional[float]:
    topic_start = text.find(topic)
    if topic_start == -1:
        return None

    value_start = text.find(":", topic_start)
    value_end = text.find("\n", value_start)
    value_string = text[value_start+1:value_end].replace("s", "")
    return float(value_string)


def print_status():
    processed = 0
    for solver in SOLVERS:
        processed += len(result_dict[solver])
    percentage = processed / NUM_FILES

    current_time = datetime.now()
    running = current_time - start_time
    time_left = (running / percentage) * (1-percentage)
    print(f"{round(percentage * 100, 2)}% finished \t expected time: {current_time+time_left}")

###############

start_time = datetime.now()
result_dict = {}

for zip_name in ZIP_NAMES:
    zip_file = ZipFile(zip_name, 'r')
    zip_path = ZipPath(zip_file, at='')
    evaluate_archive(zip_path, result_dict)

json_object = json.dumps(result_dict, indent=4)
result_file = open(RESULT_FILE, "w+")
result_file.write(json_object)
result_file.close()
