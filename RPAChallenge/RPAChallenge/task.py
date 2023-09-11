from RPA.Robocorp.WorkItems import WorkItems

from logger import logger
from process_run import Process


def workitems() -> dict:
    """ Returns:
            workitems.
    """
    # work_item = WorkItems()
    # work_item.get_input_work_item()
    # workitem = work_item.get_work_item_variables()
    workitem = {
        "phrase": "India",
        "section": "World",
        "months": 2
    }

    return workitem


def task():
    """
    Initilize the process.
    """
    w_items = workitems()
    process = Process(workitems=w_items)
    process.start()


if __name__ == "__main__":
    logger.info('Initializing the Process')
    task()
    logger.info("Done.")
    logger.info("Done.")
