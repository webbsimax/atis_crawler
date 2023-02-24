# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 21:35:08 2023

@author: adam
"""

def transfer_detail():
    import mysql.connector
    from atis import Atis
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD 
    from datetime import datetime

    mydb = mysql.connector.connect(
        host=SQL_HOST,
        user=SQL_USER,
        password=SQL_PASSWORD
        )
    
    
    mycursor = mydb.cursor()
    
    sql = "SELECT id, atis, datetime_utc FROM adamw780_atis_log.atis_log ORDER BY datetime_utc ASC"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    
    for r in result:
        try:
            atis = Atis(r[1],_got_time = datetime.strptime(r[2], "%Y-%m-%d %H:%M:%S"))
        except:
            print("Error parsing: "+r[1])
        # Create the detailed record
        sql = """INSERT INTO adamw780_atis_log.atis_log_detailed (id, airport, dt_start, dt_end, information, 
                                                                runway_mode, qnh, wind_direction, wind_speed, 
                                                                cloud, visibility, lvo, atis_text, notes) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        
        #try:
        val = (r[0], atis.airport, r[2], "", atis.information, atis.runway, atis.qnh, atis.wind_direction ,atis.wind_speed ,atis.cloud,atis.visibility,atis.lvo,atis.atis_text,"")
        
        mycursor.execute(sql, val)
        #except:
        #    print(r)
    mydb.commit()
        
transfer_detail()
