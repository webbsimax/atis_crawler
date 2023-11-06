# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 19:51:03 2023

@author: adam
"""


class Notam:
    """
    Attempt to parse a NOTAM with airspcae opening/closing times
    NOTAMs are free text so we'll just give it our best go
    
    """
    
    def __init__(self,notam_text):
        import re
        self.notam_text = notam_text
        try:
            self.airspace_id = re.findall(r'[RD]\d{3}[A-Z]', notam_text)[0]
        except:
            self.airspace_id = "N/A"
            
        self.airspace_name = ""
        
        try:
            self.notam_id = self._get_notam_id(notam_text)
        except:
            self.notam_id = "N/A"
            
        try:    
            self.notam_review_id = self._get_notam_review_id(notam_text)
        except:
            self.notam_review_id = "N/A"
            
        try:
            self.list_open_close = self._get_open_close(notam_text)
        except:
            self.list_open_close = ["N/A"]
            
        try:
            self.valid_from, self.valid_to = self._get_notam_period(notam_text)
        except:
            self.valid_from, self.valid_to = ("N/A","N/A")
        #for n in notam_text.split('\n'):
        #    print(n + ",")
            
        #print(airspace_code)
        
    def _get_notam_id(self,notam_text):
        import re
        return re.findall(r'[A-Z]\d{1,4}/\d{2}',notam_text)[0]
    
    def  _get_notam_review_id(self,notam_text):
        import re
        if "REVIEW" in notam_text:
            return re.findall(r'[A-Z]\d{1,4}/\d{2}',notam_text)[1]
        else:
            return "N/A"
    
    def _get_notam_period(self,notam_text):
        '''
        Try and get the valitiy period of the NOTAM. This is going to be messy
        as Airservices do not use standard (10 digit) DTGs in their NOTAMs
        
        Parameters
        ----------
        notam_text : STRING
            The string of the entire NOTAM

        Returns
        -------
            A tuple (start,end)

        '''
        from datetime import datetime, timedelta
        import re
        # First assumption - the valid period is the first line that looks like
        # mm ddHHMM TO mm ddHHMM
        
        valid_line = re.findall('\d{2}\s\d{6}\sTO\s\d{2}\s\d{6}',notam_text)[0]
        
        fr = datetime.strptime(valid_line[:9], "%m %d%H%M")
        to = datetime.strptime(valid_line[13:], "%m %d%H%M")    
        
        # Next assumption - due to Airservices using non-standard format for dates
        # we'll assume that the NOTAM is valid for a period starting and finishing
        # in the current (utc) year. 
        
        fr = fr.replace(year=datetime.utcnow().year)
        to = to.replace(year=datetime.utcnow().year)
        
        # If the validity period starts more than two days from now, then we'll 
        # assume that it actually started in the previous year (because we should
        # only ever extract for a 24hr period)
        
        if fr > datetime.utcnow() + timedelta(days=2):
            fr = fr.replace(year=fr.year-1)
            
        # If the validity period finishes more than two days ago then we'll 
        # we'll assume that is actually finishes next year
        
        if to < datetime.utcnow() - timedelta(days=2):
            fr = fr.replace(year=fr.year+1)
        
        return (fr,to)        
    
    def _get_open_close(self,notam_text):
        import re
        from datetime import datetime

        return [(datetime.strptime(line[:10], "%y%m%d%H%M"),datetime.strptime(line[14:], "%y%m%d%H%M")) for line in re.findall('\d{10}\sTO\s\d{10}',notam_text)]
      
            