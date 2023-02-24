from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

TESTING = True

def login():
    import mysql.connector
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD 
    print (SQL_USER)
    mydb = mysql.connector.connect(
        host=SQL_HOST,
        user=SQL_USER,
        password=SQL_PASSWORD
        )
   
    driver.get("https://www.airservicesaustralia.com/naips/Account/LogOn")
    assert "Login" in driver.title
    mycursor = mydb.cursor()
    sql = "SELECT username, password FROM adamw780_atis_log.user_details ORDER BY created_at DESC"
    mycursor.execute(sql)
    NAIPS_USER, NAIPS_PASSWORD =  mycursor.fetchone()
    print(NAIPS_USER, NAIPS_PASSWORD)
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

def read_atis(b, airport):
    import re
    from atis import Atis
    
    atis_text = re.findall(r'ATIS.*$',b[0],flags=re.DOTALL)[0]
    atis = Atis(atis_text)
    return atis 
    

def makeFile(atis,airport):
    import os
    from datetime import datetime, timezone
    
    filename = "ATIS_" + airport + "_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + ".txt" 
    
    with open(filename,'w') as f:
        f.write(atis)
    logging.debug("File written to " + filename)
    logging.debug(os.curdir)

def save_sql(atis):
    import mysql.connector
    from datetime import datetime, timezone
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD 
    print (SQL_USER)
    mydb = mysql.connector.connect(
        host=SQL_HOST,
        user=SQL_USER,
        password=SQL_PASSWORD
        )
    
    
    mycursor = mydb.cursor()
    
    sql = "SELECT id, atis, datetime_utc FROM adamw780_atis_log.{} WHERE airport = %s ORDER BY datetime_utc DESC".format("atis_log" + ("_test" if TESTING else ""))
    val = ((atis.airport,))
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    
    if result == None or result[1] != atis.atis_text:
        # We have a new atis
        
        # Update the basic table
        sql = "INSERT INTO adamw780_atis_log.{} (datetime_utc, airport, atis) VALUES (%s, %s, %s)".format("atis_log" + ("_test" if TESTING else ""))
        val = (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), atis.airport,atis.atis_text)
        mycursor.execute(sql, val)
        mydb.commit()
        
        # Get the ID created so that it matches the detail table
        sql = "SELECT id FROM adamw780_atis_log.{} WHERE atis = %s".format("atis_log" + ("_test" if TESTING else ""))
        val = (atis.atis_text,)
        mycursor.execute(sql, val)
        atis_id =  mycursor.fetchone()[0]
        
        # Create the detailed record
        sql = """INSERT INTO adamw780_atis_log.{} (id, airport, dt_start, dt_end, information,
                                                                runway_mode, qnh, wind, wind_direction, wind_speed, wind_notes,
                                                                cloud, visibility, lvo, atis_text, notes) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""".format("atis_log_detailed" + ("_test" if TESTING else ""))
        val = (atis_id, atis.airport, atis.dt_start.strftime("%Y-%m-%d %H:%M:%S"), "", atis.information, atis.runway, 
               atis.qnh, atis.wind, atis.wind_direction, atis.wind_speed, atis.wind_notes, 
               "","","", atis.atis_text, atis.note)
        print(val)
        mycursor.execute(sql, val)
        mydb.commit()
    else:
        print("Already in db")
  
    
#options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
#driver = webdriver.Chrome('C:/Users/adam/Downloads/chromedriver_win32/chromedriver.exe',options=chrome_options)


logging.basicConfig(filename='atis_errors.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
("App Started")
logging.debug

airports = ["YMML" , "YMEN"]
for AIRPORT in airports:  
    options = Options()
    options.add_argument("--headless")
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    
    driver = webdriver.Firefox(executable_path=r'C:\Users\adam\Documents\Development\GetAtis\geckodriver.exe',options=options)

    #driver = webdriver.Firefox(options=options)
    login()
    b = get_briefing(AIRPORT)
    
    atis = read_atis(b,"YMML")
    
    
    #makeFile('.'.join([findATIS(x) for x in b if len(x) > 0]),AIRPORT)
    save_sql(atis)



driver.close()
print("All done")



