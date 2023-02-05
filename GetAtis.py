from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

def login():
    from secrets import NAIPS_USER, NAIPS_PASSWORD
    driver.get("https://www.airservicesaustralia.com/naips/Account/LogOn")
    assert "Login" in driver.title
    
    elem = driver.find_element(By.NAME, "UserName")
    elem.clear()
    elem.send_keys(NAIPS_USER)
    
    elem = driver.find_element(By.NAME, "Password")
    elem.clear()
    elem.send_keys(NAIPS_PASSWORD)
    
    elem.send_keys(Keys.RETURN)
    
    delay = 10 # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'clocklbltxt')))
        logging.debug( "Logged in successfully")
    except:
        logging.debug("Unable to log in")

    
    
    
def get_briefing(airport):
    

    driver.get("https://www.airservicesaustralia.com/naips/Briefing/Location")
    
    elem = driver.find_element(By.ID,"Locations_0_")
    elem.clear()
    elem.send_keys(airport)
    
    elem = driver.find_element(By.ID,"ChartsChkBox")
    elem.click()
    
    elem = driver.find_element(By.ID,"NOTAM")
    elem.click()
    
    elem = driver.find_element(By.ID,"Validity")
    elem.clear()
    elem.send_keys("24")
    
    elem.send_keys(Keys.RETURN)
    delay = 10 # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'briefing')))
        logging.debug("Briefing in successfully")
    except:
        logging.debug("Unable to find briefing")

    brief_text = driver.find_elements(By.CLASS_NAME,"briefing")
    
    return [b.text for b in brief_text]

def findATIS(b):
    import re
    return re.findall(r'ATIS.*$',b,flags=re.DOTALL)[0]
    

def makeFile(atis,airport):
    import os
    from datetime import datetime, timezone
    
    filename = "ATIS_" + airport + "_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + ".txt" 
    
    with open(filename,'w') as f:
        f.write(atis)
    logging.debug("File written to " + filename)
    logging.debug(os.curdir)

def save_sql(atis,airport):
    import os, mysql.connector
    from datetime import datetime, timezone
    from secrets import SQL_HOST, SQL_USER, SQL_PASSWORD 
    
    mydb = mysql.connector.connect(
        host=SQL_HOST,
        user=SQL_USER,
        password=SQL_PASSWORD
        )
    
    mycursor = mydb.cursor()
    sql = "INSERT INTO adamw780_atis_log.atis_log (datetime_utc, airport, atis) VALUES (%s, %s, %s)"
    val = (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), airport,atis)
    mycursor.execute(sql, val)
    mydb.commit()

#options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
#driver = webdriver.Chrome('C:/Users/adam/Downloads/chromedriver_win32/chromedriver.exe',options=chrome_options)


logging.basicConfig(filename='atis_errors.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
("App Started")
logging.debug

airports = ["YMML" , "YMEN"]
for AIRPORT in airports:  
    options = Options()
    options.add_argument("--headless")
    #options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    
    #driver = webdriver.Firefox(executable_path=r'C:\Users\adam\Documents\Development\GetAtis\geckodriver.exe',options=options)

    driver = webdriver.Firefox(options=options)
    login()
    b = get_briefing(AIRPORT)
    
    #makeFile('.'.join([findATIS(x) for x in b if len(x) > 0]),AIRPORT)
    save_sql('.'.join([findATIS(x) for x in b if len(x) > 0]),AIRPORT)



driver.close()
print("All done")



