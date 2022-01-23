
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

urlBase = "https://aim.asecna.aero/html/eAIP/"

mydb = mysql.connector.connect(
  host=os.getenv("host"),
  user=os.getenv("user"),
  password=os.getenv("password"),
  database=os.getenv("database"),
  port=os.getenv("port")
)
mycursor = mydb.cursor()
sql = "INSERT INTO Chart_of_airport(ICAO_AIRPORT,Chart_type,Chart_name,Chart_url) VALUES (%s,%s,%s,%s)"
values = []



def inAirportPage(pageUrl):
    response = requests.get(pageUrl)
    if response.ok:
        airportPage = BeautifulSoup(response.text, "html.parser")
        # TODO : REFACTOR
        # Parsing title of page to get just the ICAO Code
        airportICAO = (str(airportPage.find("h3", {"class": "TitleAD"}).text.encode('utf-8')).split("\\")[0].split("+")[0])[2:]
        charts = airportPage.findAll("div",{"class":"Figure"})
        for chart in charts:
            link = chart.find('a')
            chartName = link.text #TODO: If chart name contains VAC, it is a VFR charts
            chartUrl = urlBase + quote(link['href'])
            charType = "IFR"

            # print(tuple((airportICAO,charType,chartName,chartUrl)))
            values.append(tuple((airportICAO,charType,chartName,chartUrl)))




if __name__ == '__main__':

    urlMenu = urlBase + "FR-menu-fr-FR.html"

    response = requests.get(urlMenu);

    if response.ok:
        menuFr = BeautifulSoup(response.text, 'html.parser')
        zoneChart = menuFr.find("div", {"id": "AD-2.24details"})
        listOfCountrieDiv = zoneChart.findAll("div", {"class": "H3"})
        # print(len(listOfCountrieDiv))

        for div in listOfCountrieDiv:
            links = div.findAll("a")
            for link in links:
                airpotPageUrl = urlBase + link['href']
                inAirportPage(airpotPageUrl)

        mycursor.execute("SET FOREIGN_KEY_CHECKS=0")

        mycursor.executemany(sql, values)
        mycursor.execute("SET FOREIGN_KEY_CHECKS=1")

        mydb.commit()