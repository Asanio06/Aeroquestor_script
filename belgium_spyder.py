import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()


mydb = mysql.connector.connect(
  host=os.getenv("host"),
  user=os.getenv("user"),
  password=os.getenv("password"),
  database=os.getenv("database"),
  port=os.getenv("port"),
)
mycursor = mydb.cursor()
sql = "INSERT INTO Chart_of_airport(ICAO_AIRPORT,Chart_type,Chart_name,Chart_url) VALUES (%s,%s,%s,%s)"
queryToRemoveBelgiumAndLuxembourgAirportCharts = "DELETE FROM Chart_of_airport WHERE Chart_of_airport.ICAO_AIRPORT LIKE 'EB%' OR Chart_of_airport.ICAO_AIRPORT LIKE 'EL%'"

values = []



urlBase = "https://ops.skeyes.be/html/belgocontrol_static/eaip/eAIP_Main/html/eAIP/"





def inAirportPage(pageUrl):
    response = requests.get(pageUrl)
    if response.ok:
        airportPage = BeautifulSoup(response.text, "html.parser")
        # TODO : REFACTOR
        # Parsing title of page to get just the ICAO Code
        airportICAO = (str(airportPage.find("h3", {"class": "TitleAD"}).text.encode('utf-8')).split("\\")[0].split("+")[0])[2:]
        # print(airportICAO)
        table = airportPage.findAll("table")[-1]
        trs = table.findAll("tr")
        for i in range(0,len(trs)):
            if i%2 ==0:

                trWithChartName =  trs[i] # TODO : GET TRUE NAME OF CHARTS
                trWithChartLink = trWithChartName.nextSibling("td")[0]
                chartName = trWithChartName.findAll("td")[1].text
                chartUrl = urlBase+ quote(trWithChartLink.find("a")["href"])
                if "VAC" in chartName:
                    charType = "VFR"
                else:
                    charType = "IFR"

                # print(tuple((airportICAO, charType, chartName, chartUrl)))
                values.append(tuple((airportICAO, charType, chartName, chartUrl)))


if __name__ == '__main__':

    urlMenu = urlBase + "EB-menu-en-GB.html"

    response = requests.get(urlMenu)

    if response.ok:
        menuFr = BeautifulSoup(response.text, 'html.parser')
        zoneChart = menuFr.find("div", {"id": "ADdetails"})
        publicAerodromeDiv = zoneChart.findAll("div", {"class": "H2"})[2].findNext("div").findAll("div",
                                                                                                  {"class": "H3"})


        for div in publicAerodromeDiv:
            links = div.findAll("a")
            for link in links:
                if link['href'] != "#":
                    airpotPageUrl = urlBase + link['href']
                    inAirportPage(airpotPageUrl)

        mycursor.execute("SET FOREIGN_KEY_CHECKS=0")

        mycursor.execute(queryToRemoveBelgiumAndLuxembourgAirportCharts)
        mycursor.executemany(sql, values)
        mycursor.execute("SET FOREIGN_KEY_CHECKS=1")

        mydb.commit()
