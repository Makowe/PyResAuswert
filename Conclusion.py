from typing import Dict, Union, List

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


    def __init__(self, problem_category: str, evaluation: Dict[str, Dict[str, Dict[str, Union[str, float]]]],
                 topics: List[str], solvers: List[str]):
        self.problem_category: str = problem_category
        """ name of the problem category (e.g. "PUZ")"""

        self.evaluation = evaluation
        """ reference to the evaluation dict """

        self.solvers = solvers
        self.topics = topics

        self.solvers_contradict: bool = False
        """ boolean states whether solvers get contradicting results on the same problem
        (e.g. solver1: satisfiable, solver2: unsatisfiable)
        """

        self.conclusion: dict = {}
        """ dictionary that includes the average values for the problems """

        self.conclude()
        del self.evaluation

    def init_dict(self):
        for status in Conclusion.STATUSES:
            self.conclusion[status] = {}
            for sub_group in Conclusion.SUB_GROUPS:
                self.conclusion[status][sub_group] = {}
                for topic in self.topics:
                    self.conclusion[status][sub_group][topic] = {}
                self.conclusion[status][sub_group]["problems"] = {}

    def conclude(self):
        self.init_dict()
        for status in Conclusion.STATUSES:
            for solver in self.solvers:
                self.conclude_single_solver(status, "all", solver)

        self.filter_shared_evaluation()
        for status in Conclusion.STATUSES:
            for solver in self.solvers:
                self.conclude_single_solver(status, "shared", solver)

    def conclude_single_solver(self, status: str, sub_type: str, solver: str):
        result_list = {}
        num_problems = 0

        for topic in self.topics:
            result_list[topic] = []

        for problem in self.evaluation[solver].keys():
            if self.evaluation[solver][problem][Conclusion.STATUS_KEY] in Conclusion.STATUS_GROUPS[status]:
                num_problems += 1
                for topic in self.topics:
                    result_list[topic].append(self.evaluation[solver][problem][topic])

        self.conclusion[status][sub_type]["problems"][solver] = num_problems
        for topic in result_list.keys():
            self.conclusion[status][sub_type][topic][solver] \
                 = np.nanmean(result_list[topic])

    def check_contradiction(self, evaluation: Dict[str, Dict[str, Union[str, float]]]):
        pass

    def filter_shared_evaluation(self):
        """ returns a new filtered dictionary of evaluations that only includes problems where
        every solver has the same status result """
        if len(self.solvers) <= 1:
            return
        problems_to_delete: List[str] = []

        solver0 = self.solvers[0]
        for problem in self.evaluation[solver0].keys():
            status_0 = self.evaluation[solver0][problem][Conclusion.STATUS_KEY]
            for solver_i in self.solvers[1:]:
                status_i = self.evaluation[solver_i][problem][Conclusion.STATUS_KEY]
                if status_i != status_0:
                    problems_to_delete.append(problem)
                    break

        for solver in self.solvers:
            for problem in problems_to_delete:
                del self.evaluation[solver][problem]
