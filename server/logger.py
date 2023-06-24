import logging
import os


class RobotLogger(object):
    app_log_file = None
    message_log_file = None
    message_logger = None

    @staticmethod
    def setup_logger(app_log_file, message_log_file, level):
        if app_log_file is not None:
            RobotLogger.app_log_file = os.path.expanduser(app_log_file)
            log_format = "%(asctime)s %(name)s %(levelname)s %(message)s"
            logging.basicConfig(filename=RobotLogger.app_log_file, format=log_format, level=level)

        if message_log_file is not None:
            RobotLogger.message_log_file = os.path.expanduser(message_log_file)
            RobotLogger.message_logger = logging.getLogger("message")
            handler = logging.FileHandler(RobotLogger.message_log_file)
            log_format = "%(asctime)s %(message)s"
            handler.setFormatter(logging.Formatter(log_format))

            RobotLogger.message_logger.setLevel(logging.INFO)
            RobotLogger.message_logger.addHandler(handler)

    @staticmethod
    def log_message(message_type, message_direction, message):
        if RobotLogger.message_logger is not None:
            RobotLogger.message_logger.info(f"{message_type} {message_direction} {message}")


