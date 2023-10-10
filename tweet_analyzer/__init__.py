import logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(module)s:%(lineno)d]: %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

