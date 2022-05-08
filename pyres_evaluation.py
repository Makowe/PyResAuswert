from typing import Dict, Optional, Union
from zipfile import ZipInfo, ZipFile

STATUS_TOPIC = "SZS status"


def init_evaluation(solvers: list) -> dict:
    evaluation_all = {}
    for solver in solvers:
        evaluation_all[solver] = {}
    return evaluation_all


def get_solver_and_problem(single_file: ZipInfo) -> (str, str):
    folders = single_file.filename.split("/")
    solver = folders[4]
    problem = folders[5]
    return solver, problem


def evaluate_archive(zip_name: str, solvers: list, eval_topics: list) -> dict:
    zip_file = ZipFile(f"{zip_name}.zip", "r")
    info_list = zip_file.infolist()
    evaluation_all = init_evaluation(solvers)

    for single_file in info_list:
        solver, problem = get_solver_and_problem(single_file)
        if solver in solvers:
            evaluation_single = evaluate_problem(zip_file, single_file, eval_topics)
            evaluation_all[solver][problem] = evaluation_single

    zip_file.close()
    return evaluation_all


def evaluate_problem(zip_file: ZipFile, file_info: ZipInfo, eval_topics: list) -> Dict[str, Union[str, float]]:
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
        for topic in eval_topics:
            evaluation[topic] = extract_result(topic, text)
    else:
        for topic in eval_topics:
            evaluation[topic] = float("nan")
    return evaluation


def extract_status(text) -> str:
    """ returns the string of the result, e.g. "Theorem" or "Satisfiable" """
    topic_start = text.find(STATUS_TOPIC)
    if topic_start == -1:
        return ""

    value_start = topic_start + len(STATUS_TOPIC)
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


def eval_actual_results(problem_zip_name: str) -> dict:
    zip_file = ZipFile(f"{problem_zip_name}.zip", "r")
    result = {}
    info_list = zip_file.infolist()
    for single_file in info_list:
        file = zip_file.open(single_file, "r")
        text = file.read().decode("utf-8")
        topic_start = text.find("Status")
        if topic_start != -1:
            value_start = topic_start + len("Status")
            value_end = text.find("\n", value_start)
            actual_status = text[value_start: value_end]\
                .replace(" ", "")\
                .replace(":", "")
            result[single_file.filename.split("/")[-1]] = actual_status
    zip_file.close()
    return result