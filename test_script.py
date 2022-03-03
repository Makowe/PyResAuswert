from datetime import datetime
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


def evaluate_problem_category_all_solvers(problem_category_folder: ZipPath):
    for solver_folder in problem_category_folder.iterdir():
        solver = solver_folder.name
        if solver in SOLVERS:
            evaluate_problem_category_single_solver(solver_folder)
    print_status(problem_category_folder.name)


def evaluate_problem_category_single_solver(solver_folder: ZipPath):
    for problem_folder in solver_folder.iterdir():
        evaluate_single_problem(problem_folder)


def evaluate_single_problem(problem_folder: ZipPath):
    global PROCESSED_FILES
    for problem_file in problem_folder.iterdir():

        PROCESSED_FILES += 1
        return


def print_status(message: str):
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
zip_path = ZipPath(zip_file, at='')
evaluate_archive(zip_path)
