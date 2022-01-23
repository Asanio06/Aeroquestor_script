import xml.etree.ElementTree as ET

from urllib.request import urlopen
import mysql.connector

import os


from dotenv import load_dotenv
load_dotenv()


mydb = mysql.connector.connect(
  host=os.getenv("host"),
  user=os.getenv("user"),
  password=os.getenv("password"),
  database=os.getenv("database"),
  port=os.getenv("port")
)
mycursor = mydb.cursor()
sql = "insert into Metar(station_id, raw_text, temp_c, wind_dir_degrees, wind_speed_kt, altim_in_hg, sea_level_pressure_mb, flight_category, metar_type, elevation_m) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
sqlDeleteContent = " delete  from Metar"
values = []
if __name__ == '__main__':
    var_url = urlopen('https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.xml')
    root = ET.parse(var_url).getroot()
    data = root.find("data")
    metars = data.findall("METAR")

    for metar in metars:
        raw_text =   metar.find('raw_text').text if metar.find('raw_text') != None else ""
        station_id = metar.find('station_id').text if metar.find('station_id') != None else ""
        temp_c = metar.find('temp_c').text if metar.find('temp_c') != None  else ""
        wind_dir_degrees = metar.find('wind_dir_degrees').text if metar.find('wind_dir_degrees') != None else ""
        wind_speed_kt = int(metar.find('wind_speed_kt').text) if metar.find('wind_speed_kt') != None else None
        altim_in_hg = metar.find('altim_in_hg').text  if metar.find('altim_in_hg') != None else ""
        sea_level_pressure_mb = metar.find('sea_level_pressure_mb').text if metar.find('sea_level_pressure_mb') != None else ""
        flight_category = metar.find('flight_category').text   if metar.find('flight_category')!= None else ""
        metar_type = metar.find('metar_type').text  if metar.find('metar_type') != None else ""
        elevation_m = metar.find('elevation_m').text  if metar.find('elevation_m') != None else ""
        result = tuple((station_id,raw_text,temp_c,wind_dir_degrees,wind_speed_kt,altim_in_hg,sea_level_pressure_mb,flight_category,metar_type,elevation_m))
        values.append(result)

    # print(len(values))
    mycursor.execute("SET FOREIGN_KEY_CHECKS=0")

    mycursor.execute(sqlDeleteContent)
    mycursor.executemany(sql, values)
    mycursor.execute("SET FOREIGN_KEY_CHECKS=1")

    mydb.commit()