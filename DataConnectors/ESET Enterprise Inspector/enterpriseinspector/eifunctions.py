import logging

def exit_error(err, exception=True):

    logging.error(err)
    if exception:
        raise Exception(err)
