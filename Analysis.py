from typing import Dict, Union

class Analyis:
    STATUS_UNSATISFIABLE = ["Unsatisfiable", "Theorem"]
    STATUS_SATISFIABLE = ["Satisfiable"]
    STATUS_NOT_SOLVED = ["ResourceOut"]

    """ class that holds a comparison of multiple solvers on a single problem category (e.g. PUZ)"""

    def __init__(self, evaluation: Dict[str, Dict[str, Union[str, float]]]):
        self.problem_category: str = ""
        """ name of the problem category (e.g. "PUZ")"""

        self.solvers_contradict: bool = False
        """ boolean states whether solvers get contradicting results on the same problem
        (e.g. solver1: satisfiable, solver2: unsatisfiable)
        """

        self.conclusion: dict = {
            "solved": {},
            "unsatisfiable": {},
            "satisfiable": {},
            "not_solved": {}
        }
        """ dictionary that includes the average values for the problems """

        self.read_evaluation(evaluation)

    def read_evaluation(self, evaluation: Dict[str, Dict[str, Union[str, float]]]):
        pass

    def check_contradiction(self, evaluation: Dict[str, Dict[str, Union[str, float]]]):
        pass