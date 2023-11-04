from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

TESTING = True

def login(driver):
    """
        Log in to naips using the headless browser
        Get the username and password from the SQL database
    """
    
    import mysql.connector
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD 
    
    print("Logging into NAIPS")
    
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
        print("- Logged in successfully")
        logging.debug( "- Logged in successfully")
    except:
        logging.debug("- Unable to log in")
        print("- Unable to log in")

    
    
    
def get_briefing(airports,driver):
    """
    Use the headless browser (driver) to collect a breifing for the airport sent
    
    Returns a long strong containing the whole briefing.
    """

    driver.get("https://www.airservicesaustralia.com/naips/Briefing/Location")
    
    for i in range(len(airports)):
        elem = driver.find_element(By.ID,"Locations_{}_".format(i))
        elem.clear()
        elem.send_keys(airports[i])
    
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
        print("Got breifing")
    except:
        logging.debug("Unable to find briefing")
        print("unable to get briefing")

    return driver.find_elements(By.CLASS_NAME,"briefing")[0].text
    


def read_atis(b):
    """
    Find the ATISes within the briefing
    Then create the Atis 
    
    Return a list of ATIS objects
    """
    
    import re
    from atis import Atis
    atis_texts = re.findall(r'ATIS.*(?:\r?\n(?!\r?\n).*)*',b) #find everything between ATIS and double newline
    return [Atis(atis_text) for atis_text in atis_texts] 
    

def save_sql(atis):
    """
    Save the ATIS to the SQL database
    """
    import mysql.connector
    from datetime import datetime, timezone, timedelta
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD 

    mydb = mysql.connector.connect(
        host=SQL_HOST,
        user=SQL_USER,
        password=SQL_PASSWORD
        )
    
    
    mycursor = mydb.cursor()
    
    sql = "SELECT id, atis, datetime_utc FROM adamw780_atis_log.{} WHERE airport = %s ORDER BY datetime_utc DESC LIMIT 1".format("atis_log" + ("_test" if TESTING else ""))
    val = ((atis.airport,))
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    
    if result == None or result[1] != atis.atis_text:
        # We have a new atis
        
        # Update the basic table
        sql = "INSERT INTO adamw780_atis_log.{} (datetime_utc, airport, atis) VALUES (%s, %s, %s)".format("atis_log" + ("_test" if TESTING else ""))
        val = (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), atis.airport,atis.atis_text)
        mycursor.execute(sql, val)
        
        # Update the previous entry's end time
        if result != None:
            sql = "UPDATE adamw780_atis_log.{} SET dt_end = %s WHERE id = %s".format("atis_log_detailed" + ("_test" if TESTING else ""))
            dt_end = atis.dt_start - timedelta(minutes=1)
            val = (dt_end.strftime("%Y-%m-%d %H:%M:%S") ,result[0],)
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
               atis.cloud,atis.visibility, atis.lvo, atis.atis_text, atis.note)
        
        mycursor.execute(sql, val)
        mydb.commit()
    else:
        print("Already in db")
  


def main():
    #options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    #driver = webdriver.Chrome('C:/Users/adam/Downloads/chromedriver_win32/chromedriver.exe',options=chrome_options)
    import os
    
    logging.basicConfig(filename='atis_errors.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    ("App Started")
    logging.debug
    options = Options()
    
    
    options.add_argument("--headless")
    
    if os.name == 'nt':
        options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        driver = webdriver.Firefox(options = options)
        #driver = webdriver.Firefox(executable_path=r'C:\Users\adam\Documents\Development\GetAtis\geckodriver.exe',options=options)
    else:
        driver = webdriver.Firefox(options=options)
        
        
    login(driver)
   
    airports = ["YMML" , "YMEN", "YSSY", "YBBN", "YPPH", "YPAD"]
    
    b = get_briefing(airports, driver)
    #print(b)    
    
    list_atis = read_atis(b)
    for atis in list_atis:
        save_sql(atis)
    
    
    
    driver.close()
    print("All done")

if __name__ == "__main__":
    main()
    

