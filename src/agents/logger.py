import logging

class ServicePrefixFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, service_name=""):
        super().__init__(fmt, datefmt)
        self.service_name = service_name

    def format(self, record):
        record.service_name = self.service_name
        return super().format(record)


def get_logger(service_name):
    logger = logging.getLogger(service_name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = ServicePrefixFormatter(
            fmt=f"%(asctime)s - %(service_name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            service_name=service_name
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger