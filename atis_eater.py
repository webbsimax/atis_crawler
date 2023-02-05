# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#X=[]

class ATIS:
    def __init__(self,atis_dict):
        from datetime import datetime
        
        # First we get the text from the dictionary provided
        self.id = atis_dict['Record No']
        self.station = atis_dict['Station ID']
        self.start_time_text = atis_dict['Start Time (local)']
        self.duration_sec = float(atis_dict['Duration (sec)']) if len(atis_dict['Duration (sec)'])>0 else ""
        self.end_time_text = atis_dict['End Time (local)']
        self.atis_text = atis_dict['CATIS']
        
        self.start_time = datetime.strptime(self.start_time_text, '%Y-%m-%d %H:%M') 
        self.end_time = datetime.strptime(self.end_time_text, '%Y-%m-%d %H:%M') if len(self.end_time_text) > 0 else datetime(2000,1,1,0,0,0)
        self.dictionary = self.parse_atis()
        self.runway = self._clean_runway(self.dictionary['RWY']) if 'RWY' in self.dictionary.keys()  else "n/a"
        
        self.cavok = "TRUE" if "CAVOK" in self.atis_text else "FALSE"
        self.visibility = "CAVOK" if self.cavok == "TRUE" else '|'.join([self.dictionary[i] for i in ["VIS","RWY VIS","RVR"] if i in self.dictionary.keys()])
        
        self.wind = '|'.join([self.dictionary[i] for i in ["WND", "WIND"] if i in self.dictionary.keys()])
        self.cloud = '|'.join([self.dictionary[i] for i in ["CLD", "CLOUD"] if i in self.dictionary.keys()])
        self.dictionary['RVR'] if 'RVR' in self.dictionary.keys()  else "n/a"
        
        self.lvo = "TRUE" if "LVO" in self.atis_text or "LOW VIS" in self.atis_text else "FALSE"
    def line(self):
        return '"' + '","'.join([self.id,
                                 self.station,
                                 self.start_time.strftime("%y-%m-%d %H:%M"),
                                 self.end_time.strftime("%y-%m-%d %H:%M"),
                                 self.runway,
                                 self.visibility.strip(),
                                 self._attempt_min_vis(self.visibility),
                                 self.cloud.strip(),
                                 self.wind.strip(),
                                 self.lvo,
                                 self.atis_text
                                 ])+'"\n'
    
    def _attempt_min_vis(self, vis):
        import re
        if vis == "CAVOK" or vis.replace(" ","") == "GREATERTHAN10KM":
            return "10000"
        else:
            # here things get a bit messy - basically ad-hoc fixing of issues I've found in the free-text. At some point I'll 
            # come back and fix things up here
            
            
            vis = vis.replace(" ","") #spaces are causing too much of an issue
            
            vis = vis.replace("THOUSAND","000")
            
            vis = vis.replace("METRES","M").replace("KM","000M")
            
            vis = re.sub("TIME\d\d\d\d","",vis)
            
            list_dist = re.findall(r"\d+", vis)  # a list of all numbers in string
            list_dist = [l for l in list_dist if l not in ("16","09","34","27")] #assume that any mention of 16,34,09,27 is a runway name
            
            if len(list_dist) > 0: 
                return str(min([int(m) for m in list_dist]))
            else:
                if len(vis.strip())>0: print (vis)
                return "N/A"
    def _clean_runway(self, runway):
        
        rep = {"ARRIVALS"   :"A",
               "ARRIVAL"    :"A",
               "ARRS"       :"A",
               "ARR"        :"A",
               "DEPARTURES" :"D",
               "DEPARTURE"  :"D",
               "DEPS"       :"D",
               "DEP"        :"D",
               "NORTH"      :"N",
               "EAST"       :"E",
               "SOUTH"      :"S",
               "WEST"       :"W"}
        rem = ["EXPECT","TO","AND","FOR","RWY","RUNWAY",".",","," "]
        
        runway = self.replace_all(runway,rep)
        runway = self.remove_all(runway,rem)
        runway = runway.split("FROMTIME")[0]
        
        modes = {"16A27D"   :"16A / 27D",
                  "34"      :"34 SRO",
                  "16"      :"16 SRO",
                  "27"      :"27 SRO",
                  "9"       :"09 SRO",
                  "09"      :"09 SRO",
                  "2734A27D":"LAHSO",
                  "27A34DNE27ALLOTHERD":"27A / 27 34 D",
                  "09A16D"  : "09A / 16D"
                  }
                  
        runway = modes[runway] if runway in modes.keys() else runway
        
        return runway
    
    
    
    def replace_all(self,text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text
    
    def remove_all(self,text,lis):
        for i in lis:
            text = text.replace(i,"")
        return text
    
    
    def parse_atis(self,atis_text=None):      
        
        parts = ["WND","WIND","VIS","OPR INFO","CLD","SFC COND","RWY","WX","QNH","APCH","TMP","RWY VIS","RVR","SIGWX"]
        
        if atis_text == None:
            atis_text = self.atis_text
        d = {}
        k = None
        for line in atis_text.splitlines():
            line = line.strip()
            '''
            if ':' in line:
                item = line.split(':')[0].strip(' +')
                if not(item in X):
                    X.append(item)
            '''
            if line.strip()[:4] == "ATIS":
                self.information = line[10]
                self.airport = line[5:9]
            
            elif ':' in line and line.split(":")[0].strip(' +') in parts: 
                k = line.split(':')[0].strip(' +')
                v = ":".join(line.split(':')[1:]).strip()
                d[k]=v
            
            elif k != None:
                d[k]+=(" " + line)
            
            elif len(line) >0:
                print ("XX: "+line)
        return d
            
     
        
def foo():    
    import csv
    
    filename = r"C:\Users\awebb\OneDrive - Australia Pacific Airports Corporation LTD\Capacity Modelling and Planning\02 Reference & Tools\Weather Data\ATIS\APAM_ATIS_Jan2012_Mar22.csv"
    outfile  = filename.split(".csv")[0] + "_output.csv"
    
    for i in range(2) :print()
    print("Loading file:")
    print(filename)   
    for i in range(2) :print()
  
    with open(filename,'r') as f, open (outfile,'w') as o:
        reader = csv.DictReader(f)
        o.write(','.join(["id","station_id","start dtg","end dtg","runway mode","visibility","min vis","cloud","wind","lvo","atis"])+"\n")
        for row in reader:
            #print(reader.line_num)
            #try:
            a = ATIS(row)
            o.write(a.line())
            #except:
            #    print("Unable to parse line: " + row['Record No'])
            
            #if reader.line_num > 10: break
    print ("Done!")
    for i in range(2) :print()
    #print(X)
if __name__ == "__main__":
    foo()
    
    
    
    
