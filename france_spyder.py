import time

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import os
import mysql.connector
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

mydb = mysql.connector.connect(
  host=os.getenv("host"),
  user=os.getenv("user"),
  password=os.getenv("password"),
  database=os.getenv("database"),
  port=os.getenv("port"),
    auth_plugin = 'mysql_native_password'
)


mycursor = mydb.cursor()
sql = "INSERT INTO Chart_of_airport(ICAO_AIRPORT,Chart_type,Chart_name,Chart_url) VALUES (%s,%s,%s,%s)"
queryToRemoveFrenchAirportCharts = "DELETE FROM Chart_of_airport WHERE Chart_of_airport.ICAO_AIRPORT LIKE 'LF%'"
values = []


urlBase = "https://www.sia.aviation-civile.gouv.fr/dvd/"

service = Service(executable_path=ChromeDriverManager().install())
chrome_options = Options()
chrome_options.add_argument("--headless")  # Opens the browser up in background
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def inAirportPage(pageUrl):
    response = requests.get(pageUrl)
    if response.ok:
        airportPage = BeautifulSoup(response.text, "html.parser")
        # TODO : REFACTOR
        # Parsing title of page to get just the ICAO Code
        airportICAO = (str(airportPage.find("h3", {"class": "TitleAD"}).text.encode('utf-8')).split("\\")[0].split("+")[0])[2:]
        # print(airportICAO)
        charts = airportPage.findAll("div", {"class": "Figure"})
        for chart in charts:

            link = chart.find('a')
            if link:
                chartName = link.text  # TODO: If chart name contains VAC, it is a VFR charts
                chartUrl = '/'.join(pageUrl.split("/")[0:-1]) + "/" + quote(link['href'])
                charType = "IFR"
                # print(tuple((airportICAO,charType,chartName,chartUrl)))
                values.append(tuple((airportICAO, charType, chartName, chartUrl)))



def inEAipMenuFr(menuZoneUrl):

    with Chrome(service=service,options=chrome_options) as browser:
        browser.get(menuZoneUrl)
        html = browser.page_source

    menuFrZone = BeautifulSoup(html, 'html.parser')
    menuFrLinks = '/'.join(menuZoneUrl.split("/")[0:-1]) + "/" + menuFrZone.find("frame",{"name":"eAISNavigation"})["src"]
    response = requests.get(menuFrLinks)

    if response.ok:
        menuFr = BeautifulSoup(response.text, 'html.parser')
        aerodromeList = menuFr.find("div", {"id": "ADdetails"}).find("div", {"id": "AD-2-IFRdetails"}).findAll("div", {"class": "H3"})
    for aerodrome in aerodromeList:

        aerodromeLink = '/'.join(menuFrLinks.split("/")[0:-1]) + "/" + aerodrome.find("a",{"title":"Aerodrome"})["href"]
        inAirportPage(aerodromeLink)


def inEaipSection(eAipUrl):

    with Chrome(service=service,options=chrome_options) as browser:
        browser.get(eAipUrl)
        html = browser.page_source

    eAipSection = BeautifulSoup(html, 'html.parser')
    table = eAipSection.findAll("table")[0]
    eAipPageLink = eAipUrl.split("home.html")[0] + table.find(("a"))['href']
    response = requests.get(eAipPageLink)

    if response.ok:
        eAipPage = BeautifulSoup(response.text, 'html.parser')
        menuZoneUrl = eAipPageLink.split("index-fr-FR.html")[0] + eAipPage.find("frame",{"name":"eAISNavigationBase"})['src']
        inEAipMenuFr(menuZoneUrl)


if __name__ == '__main__':

    aisUrl = "https://www.sia.aviation-civile.gouv.fr/"




    with Chrome(service=service,options=chrome_options) as browser:
        browser.get(aisUrl)
        browser.implicitly_wait(1000)

        time.sleep(5)
        html = browser.page_source
        aisPage = BeautifulSoup(html, 'html.parser')
        navBar = aisPage.find("nav")
        eAipLink = navBar.find("a",string="eAIP FRANCE")["href"]
        eAipLink = "https://www.sia.aviation-civile.gouv.fr/dvd/" + eAipLink.split("dvd/")[1]
        inEaipSection(eAipLink)

        mycursor.execute("SET FOREIGN_KEY_CHECKS=0")
        mycursor.execute(queryToRemoveFrenchAirportCharts)

        mycursor.executemany(sql, values)
        mycursor.execute("SET FOREIGN_KEY_CHECKS=1")

        mydb.commit()