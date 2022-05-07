from zipfile import ZipFile

PROBLEMS_ZIP_NAME = "Problems_Hierarchy"
ACTUAL_STATUS_TOPIC = "Status"


def eval_actual_results() -> dict:
    zip_file = ZipFile(f"{PROBLEMS_ZIP_NAME}.zip", "r")
    result = {}
    info_list = zip_file.infolist()
    for single_file in info_list:
        file = zip_file.open(single_file, "r")
        text = file.read().decode("utf-8")
        topic_start = text.find(ACTUAL_STATUS_TOPIC)
        if topic_start != -1:
            value_start = topic_start + len(ACTUAL_STATUS_TOPIC)
            value_end = text.find("\n", value_start)
            actual_status = text[value_start: value_end]\
                .replace(" ", "")\
                .replace(":", "")
            result[single_file.filename.split("/")[-1]] = actual_status
    zip_file.close()
    return result
