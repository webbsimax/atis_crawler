# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 21:35:08 2023

@author: adam
"""




def fix_csv():
    from atis import Atis
    import csv
    from datetime import datetime
    CSV = r"C:/Users/adam/Documents/GitHub/MainXCSoar/atis_crawler/data/atis_log.csv"
    CSV_OUT = r"C:/Users/adam/Documents/GitHub/MainXCSoar/atis_crawler/data/atis_log_out.csv"
    CSV_DETAILED = r"C:/Users/adam/Documents/GitHub/MainXCSoar/atis_crawler/data/atis_log_detailed.csv"
    with open(CSV,"r") as f_in, open(CSV_OUT,"w") as f_out, open(CSV_DETAILED,"r") as f_detailed:
        reader = csv.DictReader(f_in)
        writer_out = csv.DictWriter(f_out,fieldnames = ["id","datetime_utc","airport","atis"])
        sortedlist = sorted(reader, key=lambda row:(row["datetime_utc"]), reverse=False)
        
        previous_atis = {}
        for i in sortedlist:
            atis = Atis(i["atis"],datetime.strptime(i["datetime_utc"],"%Y-%m-%d %H:%M:%S"))
            if atis.airport not in previous_atis.keys() or atis.atis_text != previous_atis[atis.airport].atis_text:
                writer_out.writerow(i)
                
                


def transfer_detail():
    import mysql.connector
    import get_atis
    from atis import Atis
    from adams_secrets import SQL_HOST, SQL_USER, SQL_PASSWORD 
    #from datetime import datetime


    mydb = mysql.connector.connect(
        host=SQL_HOST,
        user=SQL_USER,
        password=SQL_PASSWORD
        )
    
    
    mycursor = mydb.cursor()

    sql = "SELECT id, airport, atis, datetime_utc FROM adamw780_atis_log.atis_log ORDER BY datetime_utc ASC"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    
    for r in result:
        try:
        #if True:
            atis = Atis(r[2],_got_time = r[3]) #datetime.strptime(r[3], "%Y-%m-%d %H:%M:%S"))
            get_atis.save_sql(atis)
            print (r[3])
        #if False:
        except:
            print("Error parsing: " + str(r[0]) + r[2] )
 
    
if __name__ == "__main__":
    #transfer_detail()
    fix_csv()