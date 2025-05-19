from lynis_audit import scanLynis
from user_logger import UserLogger
import logging
import os
import re

if __name__ == "__main__":

    """
    logger = UserLogger(logging.getLogger(__name__), {})
    logger.info("Start scan")
    scanLynis("Mariolone bubbarello")
"""
    profile = "../data/deb.prt"
    comand=f'grep -e ^skip-test {profile}'
    skipped_elements = os.popen(comand).read()
    lines=re.split("\n",skipped_elements)
    sigle = []
    for e in lines:
        if "=" in e:
            iE = e.index("=")
            sigla=""
            if iE>0:
                sigla = e[iE+1:]
                sigle.append(sigla)
            #print("elemento = ",e)
            print("regola = ",sigla)
    
    print(skipped_elements)
    print("lista elementi skippati")
    print("tipo di sigle = ",type(sigle))
    if len(sigle):
        print (sigle)

