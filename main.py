import json

import pyres_conclusion
import pyres_evaluation

JOB_ZIP_NAME = "Job50840_output"
TPTP_ZIP_NAME = "Problems_Hierarchy"

RESULT_FOLDER = "results"
RESULT_FILE = f"{RESULT_FOLDER}/{JOB_ZIP_NAME}_test.json"

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


def main():
    # evaluate
    evaluation = pyres_evaluation.evaluate_archive(JOB_ZIP_NAME, SOLVERS, EVAL_TOPICS)
    conclusion = pyres_conclusion.conclude(evaluation, SOLVERS, EVAL_TOPICS)

    # check for contradictions
    actual_evaluation = pyres_evaluation.eval_actual_results(TPTP_ZIP_NAME)
    contradictions = pyres_conclusion.find_contradictions(evaluation, actual_evaluation)
    if contradictions is not None:
        print(contradictions)
    else:
        print("no contradictions")

    # export
    file = open(RESULT_FILE, "w+")
    file.write(json.dumps(conclusion, indent=4))
    file.close()


if __name__ == "__main__":
    main()
