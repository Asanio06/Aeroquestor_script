import glob, os
import time
import logging
import threading
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
load_dotenv()


log_name = 'logs/scripts.log'
logging.basicConfig(filename=log_name,
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

handler = RotatingFileHandler(log_name, maxBytes=20000, backupCount=1)
logger.addHandler(handler)



WAIT_FOR_NEXT_SCRAPING = int(os.getenv("WAIT_FOR_NEXT_SCRAPING"))
WAIT_FOR_NEXT_METAR_UPDATE = int(os.getenv("WAIT_FOR_NEXT_METAR_UPDATE"))

class myThread(threading.Thread):
    def __init__(self, threadID, name, running):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.running = running

    def run(self):
        self.running()


def scrapingOfAirportCharts():
    spyder_script = glob.glob("*_spyder.py")
    while True:
        for file in spyder_script:
            try:
                logger.info(f"${file} begin")

                exec(open(file).read(), globals())
                logger.info(f"${file} runned correctly")

            except Exception as e:
                logging.warning(f"Scraping of charts failed - ${e}")

        logger.info("\n************ Scraping of charts finished *******************")
        time.sleep(WAIT_FOR_NEXT_SCRAPING)


def updateMetarInformation():
    while True:
        try:
            logger.info("Updating metar")
            exec(open("metar_parsing.py").read())
            logger.info("Update of metar complete")
        except Exception as e:
            logging.warning(f"Updating of metar failed - ${e}")

        time.sleep(WAIT_FOR_NEXT_METAR_UPDATE)


if __name__ == '__main__':

    # Creating thread
    scrapingOfAirportChartsThread = myThread(1, "Thread-1 for scrapingOfAirportCharts", scrapingOfAirportCharts)
    updateMetarInformationThread = myThread(2, "Thread-2 for updateMetarInformation", updateMetarInformation)
    try:
        updateMetarInformationThread.start()
        time.sleep(5)
        scrapingOfAirportChartsThread.start()


    except:
        logger.warning("Error: unable to start thread")
