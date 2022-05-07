import json
from datetime import datetime
from typing import Dict, Optional, Union
from zipfile import ZipInfo, ZipFile

from Conclusion import Conclusion

from eval_actual_results import eval_actual_results

#############

ZIP_NAME = "Job50840_output"
RESULT_FILE_SUFFIX = ""

SOLVERS = [
    "PyRes_v2.0.8___PyRes_sos0",
    "PyRes_v2.0.8___PyRes_sos1",
    "PyRes_v2.0.8___PyRes_sos2",
    "PyRes_v2.0.8___PyRes_sos3",
    "PyRes_v2.0.8___PyRes_sos1r1",
    "PyRes_v2.0.8___PyRes_sos1r2",
    "PyRes_v2.0.8___PyRes_sos1r3",
    "PyRes_v2.0.8___PyRes_sos1r4",
    "PyRes_v2.0.8___PyRes_sos1r5",
    "PyRes_v2.0.8___PyRes_sos1r6",
    #"PyRes_2.0.10___PyRes_sos0_lit"
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


def evaluate_archive(zip_file: ZipFile) -> (dict, dict):
    info_list = zip_file.infolist()
    evaluation_all = init_evaluation()

    for single_file in info_list:
        solver, problem = get_solver_and_problem(single_file)
        if solver in SOLVERS:
            evaluation_single = evaluate_problem(zip_file, single_file)
            evaluation_all[solver][problem] = evaluation_single
            if PROCESSED_FILES % 5000 == 0:
                print_status()
    conclusion = Conclusion.conclude(evaluation_all, EVAL_TOPICS, SOLVERS)
    return evaluation_all, conclusion


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


def print_status():
    percentage = PROCESSED_FILES / NUM_FILES
    if percentage == 0:
        return
    print(f"{PROCESSED_FILES}/{NUM_FILES} files, {round(percentage * 100, 2)}% finished")

###############


start_time = datetime.now()

zip_file = ZipFile(f"{ZIP_NAME}.zip", "r")
evaluation, conclusion = evaluate_archive(zip_file)
zip_file.close()
actual_evaluation = eval_actual_results()


contradictions = Conclusion.contradictions_between_solvers(evaluation, actual_evaluation, SOLVERS)
if contradictions is not None:
    print(contradictions)
else:
    print("no contradictions")
file = open(f"{RESULT_FOLDER}/{ZIP_NAME}_{RESULT_FILE_SUFFIX}.json", "w+")
file.write(json.dumps(conclusion, indent=4))
file.close()
