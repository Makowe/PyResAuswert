from typing import Dict, Union, List

import statistics
import math

import numpy as np


class Conclusion:
    """ class that holds a comparison of multiple solvers on a single problem category (e.g. PUZ)"""

    STATUSES = ["solved", "unsatisfiable", "satisfiable", "not_solved"]
    STATUS_KEY = "SZS status"

    STATUS_GROUPS = {
        "solved": ["Unsatisfiable", "Theorem", "Satisfiable"],
        "unsatisfiable": ["Unsatisfiable", "Theorem"],
        "satisfiable": ["Satisfiable"],
        "not_solved": ["ResourceOut"],
    }

    SUB_GROUPS = ["all", "shared"]

    @staticmethod
    def init_dict(topics: List[str]) -> Dict:
        emtpy_conclusion = {}
        for status in Conclusion.STATUSES:
            emtpy_conclusion[status] = {}
            for sub_group in Conclusion.SUB_GROUPS:
                emtpy_conclusion[status][sub_group] = {}
                for topic in topics:
                    emtpy_conclusion[status][sub_group][topic] = {}
                emtpy_conclusion[status][sub_group]["problems"] = {}
        return emtpy_conclusion

    @staticmethod
    def conclude(evaluation, topics, solvers) -> dict:
        conclusion: dict = Conclusion.init_dict(topics)
        for status in Conclusion.STATUSES:
            for solver in solvers:
                Conclusion.conclude_single_solver(conclusion, evaluation, status,
                                                  "all", topics, solver)

        Conclusion.filter_shared_evaluation(evaluation, solvers)
        for status in Conclusion.STATUSES:
            for solver in solvers:
                Conclusion.conclude_single_solver(conclusion, evaluation, status,
                                                  "shared", topics, solver)
        return conclusion

    @staticmethod
    def conclude_single_solver(conclusion: dict, evaluation: dict, status: str,
                               sub_type: str, topics: List[str], solver: str):
        result_list = {}
        num_problems = 0

        for topic in topics:
            result_list[topic] = []

        for problem in evaluation[solver].keys():
            if evaluation[solver][problem][Conclusion.STATUS_KEY] in Conclusion.STATUS_GROUPS[status]:
                num_problems += 1
                for topic in topics:
                    result_list[topic].append(evaluation[solver][problem][topic])

        conclusion[status][sub_type]["problems"][solver] = num_problems
        for topic in result_list.keys():
            mean = np.nanmean(result_list[topic])
            conclusion[status][sub_type][topic][solver] = mean

    @staticmethod
    def check_contradiction(evaluation: dict):
        pass

    @staticmethod
    def filter_shared_evaluation(evaluation: dict, solvers: List[str]):
        """ returns a new filtered dictionary of evaluations that only includes problems where
        every solver has the same status result """
        if len(solvers) <= 1:
            return
        problems_to_delete: List[str] = []

        solver0 = solvers[0]
        for problem in evaluation[solver0].keys():
            status_0 = evaluation[solver0][problem][Conclusion.STATUS_KEY]
            for solver_i in solvers[1:]:
                status_i = evaluation[solver_i][problem][Conclusion.STATUS_KEY]
                if status_i != status_0:
                    problems_to_delete.append(problem)
                    break

        for solver in solvers:
            for problem in problems_to_delete:
                del evaluation[solver][problem]
