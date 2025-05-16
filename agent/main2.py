from lynis_audit import scanLynis
from user_logger import UserLogger
import logging

if __name__ == "__main__":

    logger = UserLogger(logging.getLogger(__name__), {})
    logger.info("Start scan")
    scanLynis("Mariolone bubbarello")
