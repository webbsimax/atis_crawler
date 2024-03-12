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
    
    import psycopg2
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD, SQL_DB, SQL_PORT
    
    print("Logging into NAIPS")

    connection_String = 'postgresql://{}:{}@{}:{}/atis-log-13694.{}?sslmode=verify-full'.format(
        SQL_USER,SQL_PASSWORD,SQL_HOST,SQL_PORT,SQL_DB)
    mydb = psycopg2.connect(connection_String)
   
    driver.get("https://www.airservicesaustralia.com/naips/Account/LogOn")
    assert "Login" in driver.title
    mycursor = mydb.cursor()
    sql = "SELECT username, password FROM user_details ORDER BY created_at DESC"
    mycursor.execute(sql)
    NAIPS_USER, NAIPS_PASSWORD =  mycursor.fetchone()
    elem = driver.find_element(By.NAME, "UserName")
    elem.clear()
    elem.send_keys(NAIPS_USER)
    
    elem = driver.find_element(By.NAME, "Password")
    elem.clear()
    elem.send_keys(NAIPS_PASSWORD)
    
    elem.send_keys(Keys.RETURN)
    print("Attempting log in")
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
    
    #elem = driver.find_element(By.ID,"NOTAM")
    #elem.click()
    
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

    return " ".join([a.text for a in driver.find_elements(By.CLASS_NAME,"briefing")])
    


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
    
def read_notams(b):
    """
    Find the airspace NOTAMs within the briefing
    
    Return a list of NOTAM objects
    """
    
    import re
    from notam import Notam
    
    # Get rid of anything after the below text
    if "THE FOLLOWING REQUESTED LOCATIONS HAVE NO CURRENT NOTAM:" in b:
        b = b.split("THE FOLLOWING REQUESTED LOCATIONS HAVE NO CURRENT NOTAM:")[0]
        
    notam_texts = re.findall(r'[RD]\d{3}?.*(?:\r?\n(?!\r?\n).*)*',b)
    if len(notam_texts) > 0:
        return [Notam(notam_text) for notam_text in notam_texts]
    else:
        return []

def save_sql_atis(atis):
    import psycopg2
    from datetime import datetime, timezone, timedelta
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD, SQL_DB, SQL_PORT


    connection_String = 'postgresql://{}:{}@{}:{}/atis-log-13694.{}?sslmode=verify-full'.format(
        SQL_USER,SQL_PASSWORD,SQL_HOST,SQL_PORT,SQL_DB)
    mydb = psycopg2.connect(connection_String)
   
    
    
    mycursor = mydb.cursor()
    
    sql = "SELECT id, atis, datetime_utc FROM {} WHERE airport = %s ORDER BY datetime_utc DESC LIMIT 1".format("atis_log" + ("_test" if TESTING else ""))
    val = ((atis.airport,))
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    
    if result == None or result[1] != atis.atis_text:
        # We have a new atis
        # None is for the first entry in the table
        # Update the basic table
        sql = "INSERT INTO {} (datetime_utc, airport, atis) VALUES (%s, %s, %s)".format("atis_log" + ("_test" if TESTING else ""))
        val = (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), atis.airport,atis.atis_text)
        mycursor.execute(sql, val)
        
        # Update the previous entry's end time
        if result != None:
            sql = "UPDATE {} SET dt_end = %s WHERE id = %s".format("atis_log_detailed" + ("_test" if TESTING else ""))
            dt_end = atis.dt_start - timedelta(minutes=1)
            val = (dt_end.strftime("%Y-%m-%d %H:%M:%S") ,result[0],)
            mycursor.execute(sql, val) 
        mydb.commit()
        
        # Get the ID created so that it matches the detail table
        sql = "SELECT id FROM {} WHERE airport = %s ORDER BY datetime_utc DESC LIMIT 1".format("atis_log" + ("_test" if TESTING else ""))
        val = (atis.airport,)
        mycursor.execute(sql, val)
        atis_id =  mycursor.fetchone()[0]
        
        # Create the detailed record
        sql = """INSERT INTO {} (id, airport, dt_start, information,
                                                                runway_mode, qnh, wind, wind_direction, wind_speed, wind_notes,
                                                                cloud, visibility, lvo, atis_text, notes) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""".format("atis_log_detailed" + ("_test" if TESTING else ""))
        val = (atis_id, atis.airport, atis.dt_start.strftime("%Y-%m-%d %H:%M:%S"), atis.information, atis.runway, 
               atis.qnh, atis.wind, atis.wind_direction, atis.wind_speed, atis.wind_notes, 
               atis.cloud,atis.visibility, atis.lvo, atis.atis_text, atis.note)
        print(val)
        mycursor.execute(sql, val)
        mydb.commit()
    else:
        print("Already in db")
  



def save_sql_notam(notam):
    import psycopg2
    from datetime import datetime
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD, SQL_DB, SQL_PORT

    connection_String = 'postgresql://{}:{}@{}:{}/atis-log-13694.{}?sslmode=verify-full'.format(
        SQL_USER,SQL_PASSWORD,SQL_HOST,SQL_PORT,SQL_DB)
    mydb = psycopg2.connect(connection_String)
   
    
    mycursor = mydb.cursor()
    
    sql = "SELECT id, notam_id FROM {} WHERE notam_id = %s and airspace_id = %s".format("notam_log" + ("_test" if TESTING else ""))
    val = ((notam.notam_id,notam.airspace_id))
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    
    if result == None:
        
        # We have a new notam!
        
        # Update the basic table
        sql = "INSERT INTO {} (notam_id, notam_text, first_seen, airspace_id) VALUES (%s, %s, %s, %s)".format("notam_log" + ("_test" if TESTING else ""))
        val = (notam.notam_id,notam.notam_text, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),notam.airspace_id)
        mycursor.execute(sql, val)
        
        mydb.commit()
        
        # Get the ID created so that it matches the detail table
        sql = "SELECT id FROM {} WHERE notam_id = %s AND airspace_id = %s".format("notam_log" + ("_test" if TESTING else ""))
        val = (notam.notam_id,notam.airspace_id)
        mycursor.execute(sql, val)
        notam_pk =  mycursor.fetchone()[0]
        
      
        # Create records of open/close
        for opening in notam.list_open_close:
            sql = """INSERT INTO {} (notam_log_id, opening_dtg, closing_dtg) 
                    VALUES (%s,%s,%s)""".format("notam_airspace_open" + ("_test" if TESTING else ""))
            val = (notam_pk, opening[0].strftime("%Y-%m-%d %H:%M:%S"), opening[1].strftime("%Y-%m-%d %H:%M:%S"))
        
            mycursor.execute(sql, val)
        mydb.commit()

    else:
        print("Already in db")



def breifing(locations):
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
   
    if len(locations) > 10:
        print("Only 10 airports or airspace allowed - taking the first 10")
        airports = airports[:10]
    
    b = get_briefing(locations, driver) 
    
    list_atis = read_atis(b)
    list_notams = read_notams(b)
    
    for atis in list_atis:
        print("Saving " + atis.airport + "...")
        save_sql_atis(atis)
    
    for notam in list_notams:
        print("Saving " + notam.airspace_id + "...")
        save_sql_notam(notam)
        
    driver.close()
    print("All done")



def main():
    # Here we do airports first, then airspace locations next
    # This isn't nesseary, but it will help if the airspace 
    # causes a crash, and we won't drop the ATIS data. 
    locations = [
                ["YMML", "YMEN", "YSSY", "YBBN", "YMAV", 
                 "YPPH", "YPAD"],
                ["R330A", "R330B", "D399", "D383A","D383B",
                "D342","D322A","D322B"]
                ]
    
    for l in locations:
        breifing(l)
    
    
    
def test():
    from text_notam import b
    print(read_airspace(b)[0].list_open_close)

if __name__ == "__main__":
    #test()
    main()
    

