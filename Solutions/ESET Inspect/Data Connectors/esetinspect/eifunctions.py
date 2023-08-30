import logging


def exit_error(err: str, exception: bool = True) -> None:

    logging.error(err)
    if exception:
        raise Exception(err)
