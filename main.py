from typing import Dict, List
from zipfile import ZipFile
from zipfile import Path as ZipPath

#############

ZIP_NAME = "Job2748_output.zip"

SOLVERS = [
    "PyRes---1.3___PyRes---1.3"
]

TOPICS = [
    "Initial clauses",
    "Processed clauses",
    "Factors computed",
    "Resolvents computed",
    "Tautologies deleted",
    "Forward subsumed",
    "Backward subsumed",
    "User time",
    "System time",
    "Total time"
]

###############

from zipfile import Path as ZipPath


def iterate_directory(path, depth=0, name=""):
    sub_path: ZipPath
    if depth <= 3:
        print(path)
        for sub_path in path.iterdir():
            iterate_directory(sub_path, depth+1)

    elif depth == 4:
        # solver depth
        print(path)
        for sub_path in path.iterdir():
            if sub_path.name in SOLVERS:
                iterate_directory(sub_path, depth+1)

    elif depth == 5:
        # single problem
        for sub_path in path.iterdir():
            iterate_directory(sub_path, depth+1, sub_path.name)

    elif depth == 6:
        for sub_path in path.iterdir():
            print(f"{name}; {evaluate_file(sub_path)}")


def evaluate_file(sub_path) -> str:
    text = sub_path.read_text()
    results = [(extract_topic(topic, text)) for topic in TOPICS]
    result_str = "; ".join(results)
    return result_str


def extract_topic(topic: str, text) -> str:
    index_topic = text.find(topic)
    if index_topic == -1:
        return "#NV"

    text_content = text[index_topic:index_topic+50]
    text_content = text_content.replace("s", "")

    index_colon = text_content.find(":")
    index_newline = text_content.find("\n")
    result = float(text_content[index_colon+1: index_newline])
    return str(result).replace(".", ",")


###############

zip_file = ZipFile(ZIP_NAME, 'r')
zip_path = ZipPath(zip_file, at='')

iterate_directory(zip_path)