import requests                   # import all these libraries
import pandas as pd               # don't forget to pip install!!
from bs4 import BeautifulSoup
from splinter import Browser      # also sorry there are so many
import time                       # I should've been more efficient
import argparse                   # but I didn't have enough time
from ConfigParser import SafeConfigParser
import os
from os import path
from twilio.rest import Client

# "pip install -r requirements.txt" for packages

# example: to skip the temperature, type into console:
#     runwebscraper.py --skiptemp 5 40 minutes "San Francisco"
# you have to type an interval, time length, and city in the command

account_sid = 'ACf4c0b57408f916faa17aef730562cb61'
auth_token = 'f323736f3adaf0a8984364ec9131eb92'
twilio_numb = '+19718034237'
my_numb = '+15037043189'

client = Client(account_sid, auth_token)

def scrape():

   # check if the INI file exists
   # if not, create the file and set the variables to "none"
   if path.exists("weatherconfig.ini") == False:
      f = open("weatherconfig.ini","w+")
      f.write("[forecast]\n")
      f.write("periods=none\n")
      f.write("short_descs=none\n")
      f.write("temps=none\n")
      f.write("descs=none\n")
      f.close()

   # parse user inputs into arguments for program
   parser = argparse.ArgumentParser(description='Process some intervals.')
   parser.add_argument('--skipperiod', action='store_true')     # --skipperiod to skip time perioid
   parser.add_argument('--skipshort_desc', action='store_true') # --skipshort_desc to skip short description
   parser.add_argument('--skipdesc', action='store_true')       # --skipdesc to skip long description
   parser.add_argument('--skiptemp', action='store_true')       # --skiptemp to skip temperature
   parser.add_argument('interval', type=int)   # specify the interval in seconds between each cycle
   parser.add_argument('numoftimes', type=int) # set to negative number for infinite scraping
   parser.add_argument('timetype', type=str)   # specify hours, minutes, seconds
   parser.add_argument('location', type=str)   # specify the US city

   args = parser.parse_args()

   print(args)   # print all arguments to show the user their input

   # if hours were specified, do some math to make the loop run on hours
   if args.timetype == "hour" or args.timetype == "hours":
      numberOfScrapes = (args.numoftimes * 3600) / args.interval
      numberOfScrapes = int(round(numberOfScrapes))

   # if minutes were specified, do some math to make the loop run on minutes
   elif args.timetype == "minute" or args.timetype == "minutes":
      numberOfScrapes = (args.numoftimes * 60) / args.interval
      numberOfScrapes = int(round(numberOfScrapes))

   # if seconds were specified, make the loop run on default settings (which are seconds)
   elif args.timetype == "second" or args.timetype == "seconds":
      numberOfScrapes = args.numoftimes / args.interval
      numberOfScrapes = int(round(numberOfScrapes))

   # if the type of time is unrecognized, default to one cycle
   else:
      numberOfScrapes = 0
      print "UNIT OF TIME UNSPECIFIED; DEFAULT TO 1 FETCH"


   scrapeCounter = 0   # this number goes up by 1 each time a cycle is completed


   browser = Browser('chrome')                # choose Chrome as the browser
   #browser.driver.set_window_size(640, 480)  # Ignore, I decided I didn't want to open a specific browser size
   browser.visit('http://www.weather.gov/')   # go to http://www.weather.gov/

   search_bar_xpath = '//*[@id="inputstring"]'              # set this variable to the XPath of the search bar
   search_bar = browser.find_by_xpath(search_bar_xpath)[0]  # find the search bar with that XPath
   search_bar.fill(args.location)                           # put the city into the search bar

   # Set up code to click the search button
   search_button_xpath = '//*[@id="btnSearch"]'                   # set this variable to the XPath of the search button
   search_button = browser.find_by_xpath(search_button_xpath)[0]  # find the search button with that XPath
   time.sleep(1)                    # delay to let button load
   search_button.click()            # click the button
   time.sleep(1)                    # delay to let new page load
   url = browser.driver.current_url # get the current url
   time.sleep(1)                    # delay to get current url

   

   while True:   # loop that scrapes the website until the loop breaks

      # set up forecast variables
      page = requests.get(url)   # put the site into "page" using the current url
      soup = BeautifulSoup(page.content, 'html.parser')   # set up BeutifulSoup to parse the page
      seven_day = soup.find(id="seven-day-forecast")      # find the HTML with the forecast
      forecast_items = seven_day.find_all(class_="tombstone-container")   # find the individual sections in the forecast
    
      # find the name of the city in the html
      city = soup.find('h2', attrs={'class': 'panel-title'})
      city_text = city.text
      print("Monitoring weather for " + city_text)  # tell the user the city
      
      parser = SafeConfigParser()
      parser.read('weatherconfig.ini')    # use SafeConfigParser to read the file

      # set the comparison variables to the previous values in the INI file
      periodChange = parser.get('forecast', 'periods')
      short_descChange = parser.get('forecast', 'short_descs')
      tempChange = parser.get('forecast', 'temps')
      descChange = parser.get('forecast', 'descs')
      
      # get the time period, short description, temperature (Farenheight), and long description
      period_tags = seven_day.select(".tombstone-container .period-name")
      periods = [pt.get_text() for pt in period_tags]
      short_descs = [sd.get_text() for sd in seven_day.select(".tombstone-container .short-desc")]
      temps = [t.get_text() for t in seven_day.select(".tombstone-container .temp")]
      descs = [d["title"] for d in seven_day.select(".tombstone-container img")]

      f = open("weatherconfig.ini","w+")  # open the INI file
      # write in those new values in the INI
      f.write("[forecast]\n")
      f.write("periods=" + str(periods) + "\n")
      f.write("short_descs=" + str(short_descs) + "\n")
      f.write("temps=" + str(temps) + "\n")
      descsstring = str(descs).replace("%","")  # little trick to get rid of "%" sign bc it screws up the data

      f.write("descs=" + str(descsstring) + "\n")

      f.close()  # close the file

      # check if change is detected and if the parameter is not skipped
      # then notify via printing in console


      if periodChange != str(periods) and args.skipperiod == False:
         print("TIME PERIOD CHANGE")
         periodChange = str(periods)
      
      if tempChange != str(temps) and args.skiptemp == False:
         print("TEMPERATURE CHANGE")
         tempChange = str(temps)

      if descChange != str(descsstring) and args.skipdesc == False:
         print("LONG DESCRIPTION CHANGE")
         descChange = str(descs)

      if short_descChange != str(short_descs) and args.skipshort_desc == False:
         print("SHORT DESCRIPTION CHANGE")
         short_descChange = str(short_descs)


      # check if any parameters were skipped
      # sneakily change skipped parameters to "none" while still grabbing them
      
      if args.skipperiod == True:
         periods = "none"

      if args.skipshort_desc == True:
         short_descs = "none"

      if args.skiptemp == True:
         temps = "none"

      if args.skipdesc == True:
         descs = "none"

      # arrange data into panda table
      weather = pd.DataFrame({
              "desc":descs, 
              "short_desc": short_descs, 
              "temp": temps,
              "period": periods
          })
      print(weather)  # print the table
      
      client.messages.create(
         body=str(weather),
         to=my_numb,
         from_=twilio_numb
      )


      # add 1 to the total cycles completed
      scrapeCounter += 1

      # check if the specified amount of cycles has been reached
      # if so, break the loop
      # if numberOfScrapes was set to a negative number, this will keep going until you press ctrl + c
      if (scrapeCounter >=  numberOfScrapes and numberOfScrapes >= 0):
         print(scrapeCounter) # print number  of times the loop ran
         break                # break the loop

      # minimum intervals of 2 seconds
      # else set intervals to the specified value
      if args.interval < 2:
         time.sleep(2)
      else:
         time.sleep(args.interval)

# if the file is in a command line interface, run the function
if __name__=="__main__":
   scrape()
