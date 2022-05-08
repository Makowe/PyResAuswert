from typing import Dict, List, Tuple, Optional

import numpy as np

STATUS_KEY = "SZS status"

STATUS_CATEGORIES = {
    "solved": ["Unsatisfiable", "Theorem", "Satisfiable", "CounterSatisfiable"],
    "unsatisfiable": ["Unsatisfiable", "Theorem"],
    "satisfiable": ["Satisfiable", "CounterSatisfiable"],
    "not_solved": ["ResourceOut"],
}
""" list of the four categories to which the problems are assigned. 
Problems with status Inappropiate are not assigned to any category.
Problems can be assigned to multiple categories (e.g. solved, and unsatisfiable)
"""

SUB_CATEGORY = ["all", "shared"]
""" Every of the four categories is seperated in two sub categories.
all: considers all problems within the category
shared: considers only problems within the category where all solvers have the same status. This
    is useful to compare the performance of two solvers (e.g. the user time)
"""


def conclude(evaluation: dict, solvers: list, topics: list) -> dict:
    """
    concludes an evaluation by summarizing the relevant information
    :param evaluation: dictionary of the starexec computation
    :param topics: relevant information (e.g. user time and resolvents computed
    :param solvers: list of the solvers
    :return: a dictionary representing the conclusion
    """
    evaluation = evaluation.copy()
    conclusion: dict = init_dict(topics)
    for status in STATUS_CATEGORIES.keys():
        for solver in solvers:
            conclude_single_solver(conclusion, evaluation, status,
                                   "all", topics, solver)

    filter_shared_evaluation(evaluation, solvers)
    for status in STATUS_CATEGORIES.keys():
        for solver in solvers:
            conclude_single_solver(conclusion, evaluation, status,
                                   "shared", topics, solver)
    return conclusion


def init_dict(topics: List[str]) -> Dict:
    """ Initializes the conclusion dictionary """
    conclusion = {}
    for status in STATUS_CATEGORIES.keys():
        conclusion[status] = {}
        for sub_group in SUB_CATEGORY:
            conclusion[status][sub_group] = {}
            for topic in topics:
                conclusion[status][sub_group][topic] = {}
            conclusion[status][sub_group]["problems"] = {}
    return conclusion


def conclude_single_solver(conclusion: dict, evaluation: dict, status: str,
                           sub_type: str, topics: List[str], solver: str):
    """ Find all problems in the evaluation where a given solver has found a given status (e.g. satisfiable).
    Summarize the information and add it to the conclusion dictionary.
    """
    result_list = {}
    num_problems = 0

    for topic in topics:
        result_list[topic] = []

    for problem in evaluation[solver].keys():
        if evaluation[solver][problem][STATUS_KEY] in STATUS_CATEGORIES[status]:
            num_problems += 1
            for topic in topics:
                result_list[topic].append(evaluation[solver][problem][topic])

    conclusion[status][sub_type]["problems"][solver] = num_problems
    for topic in result_list.keys():
        mean = np.nanmean(result_list[topic])
        conclusion[status][sub_type][topic][solver] = mean


def filter_shared_evaluation(evaluation: dict, solvers: List[str]) -> None:
    """ Eeletes all entries from the evaluation where the solvers find different solutions
     (e.g. solver1: Unsatisfiable, solver2: ResourceOut)
     The resulting evaluation contains only problems where all solvers have the same status
     """
    if len(solvers) <= 1:
        return
    problems_to_delete: List[str] = []

    solver0 = solvers[0]
    for problem in evaluation[solver0].keys():
        status_0 = evaluation[solver0][problem][STATUS_KEY]
        for solver_i in solvers[1:]:
            status_i = evaluation[solver_i][problem][STATUS_KEY]
            if status_i != status_0:
                problems_to_delete.append(problem)
                break

    for solver in solvers:
        for problem in problems_to_delete:
            del evaluation[solver][problem]


def find_contradictions(resolved_eval: dict, actual_eval: dict) \
        -> Optional[List[Tuple[str, str]]]:
    """
    Checks whether contradictions between the solver results and the actual results exist.
    :param resolved_eval: dictionary containing the results computed by starexec
    :param actual_eval: dictionary containing the actual status of each problem
    :return: a list of the found contradictions
        each contradiction is a tuple of problem and solver. Returns None if no contradictions
        have been found.
    """
    contradictions: List[Tuple[str, str]] = []
    for solver in resolved_eval.keys():
        for problem in resolved_eval[solver].keys():
            resolved_status = resolved_eval[solver][problem]
            actual_status = actual_eval[problem]
            if resolved_status in STATUS_CATEGORIES["satisfiable"] \
                    and actual_status in STATUS_CATEGORIES["unsatisfiable"] \
                    or resolved_status in STATUS_CATEGORIES["unsatisfiable"] \
                    and actual_status in STATUS_CATEGORIES["satisfiable"]:
                contradictions.append((problem, solver))
    if len(contradictions):
        return contradictions
    else:
        return None
