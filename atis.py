class Atis:
    #d, airport, dt_start, dt_end, information, 
    #runway_mode, qnh, wind_direction, wind_speed, 
    #cloud, visibility, lvo, atis_text, notes
    
    def __init__(self,atis_text,_got_time=None):    
    
        self.atis_text = atis_text
        self.note = "" # We'll use this if any possible warnings come up
     
        self.dictionary = self.parse_atis(got_time=_got_time)
        self.runway = self._clean_runway(self.dictionary['RWY']) if 'RWY' in self.dictionary.keys()  else "n/a"
        
        self.cavok = True if "CAVOK" in self.atis_text else "FALSE"
        
        self.visibility = "9999" if "CAVOK" in self.atis_text else self.dictionary["VIS"] if "VIS" in self.dictionary.keys() else "n/a"
        
        self.wind = '|'.join([self.dictionary[i] for i in ["WND", "WIND"] if i in self.dictionary.keys()])
        self._clean_wind(self.wind)
        self.cloud = '|'.join([self.dictionary[i] for i in ["CLD", "CLOUD"] if i in self.dictionary.keys()])
        self.rvr = self.dictionary['RVR'] if 'RVR' in self.dictionary.keys()  else "n/a"
        self.lvo = "TRUE" if "LVO" in self.atis_text or "LOW VIS" in self.atis_text else "FALSE"
        
        self.qnh = self.dictionary['QNH'] if 'QNH' in self.dictionary.keys() else "n/a"
        self.cloud = self.dictionary['CLD'] if 'CLD' in self.dictionary.keys() else "n/a"
        
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
    
    
    def _clean_wind(self,wind):
        ''' 
            Clean up the "WND:" section of ATIS, we consider the formats:
                DIR/SP 
                DIR-DIR/SP
            and store anything after the DIR/SP as a note (e.g. crosswind remarks etc)
        '''
                                                       
        import re
        if re.match("^(\d+|VRB)/(\d+)",wind):
            # then wind is of format 180/20 or VRB/20
            self.wind_direction,self.wind_speed,self.wind_notes  = re.findall("^(\d+|VRB)/(\d+)(.*)",self.wind)[0]
        elif re.match("^(\d+)-(\d+)/(\d+)",wind):
            # then wind is of the format 180-190/20
            self.wind_direction,self.wind_speed, self.wind_notes  = re.findall("^(\d+-\d+)/(\d+)(.*)",self.wind)[0]
            self.wind_notes + " VRB_DIR"
        elif re.match("^(VRB) (\d+)",wind):
            # sometimes wind is reported VBR without the "/"
            self.wind_direction,self.wind_speed, self.wind_notes = re.findall("^(VRB) (\d+)(.*)",self.wind)[0]
        else:
            self.wind_direction ="n/a"
            self.wind_speed = "n/a"
            self.wind_notes = "Wind unable to be parsed: " + wind
    
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
    
    
    def parse_atis(self,atis_text=None,got_time=None):      
        import re 
        from datetime import datetime, timedelta
        parts = ["WND","WIND","VIS","OPR INFO","CLD","SFC COND","RWY","WX","QNH","APCH","TMP","RWY VIS","RVR","SIGWX"]
        
        if atis_text == None:
            atis_text = self.atis_text
        d = {}
        k = None
        
        for line in atis_text.splitlines():
            line = line.strip()

            if line.strip()[:4] == "ATIS": # Deal with the fist line
            
                self.information = line[10]
                self.airport = line[5:9]
                
                # Get a start day/time
                
                now = datetime.utcnow() if got_time == None else got_time
                yesterday = now - timedelta(days = 1)
                
                _dtg = re.findall('\d+',line)[0]
                self.dt_start = datetime.strptime(_dtg, "%d%H%M")
                                
                if self.dt_start.day == now.day - 1:
                    # The DTG is from the previous day (e.g. ATIS at 2359, retrieved at 0001)
                    self.dt_start = self.dt_start.replace(month=yesterday.month,year=yesterday.year)
                    
                elif self.dt_start.day == now.day:
                    # Today
                    self.dt_start = self.dt_start.replace(month=now.month,year=now.year)
                    
                else:
                    # Something weird is going on
                    self.note += "Warning: Possible date issue\n" + line
                    self.dt_start = self.dt_start.replace(month=now.month,year=now.year)
                    
                                                  
                                                  
                                                  
            elif ':' in line and line.split(":")[0].strip(' +') in parts: 
                k = line.split(':')[0].strip(' +')
                v = ":".join(line.split(':')[1:]).strip()
                d[k]=v
            
            elif k != None:
                d[k]+=(" " + line)
            
            elif len(line) >0:
                print ("Unable to parse line: "+line)
        return d
            
     
        
#def foo():    
#    a = ATIS(" ")
#if __name__ == "__main__":
#    foo()
    
    
    
    
