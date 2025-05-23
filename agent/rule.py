import subprocess
import json
from typing import  List
class Rule:
    """
    This class aims to verify the security rules of the Debian system
    the attributes are :
    - name : how we identify the rule
    - command : what bash command can i use to check the status of the rule
    - description what the rule does
    - status true or false
    """
    def __init__(self, name:str,command:str,expected_result:str,status:bool=False,description:str= None):
        self.name  = name
        self.command = command
        self.description = description 
        self.expected_result = expected_result
        self.status = status
    def __str__(self):
        return f"nome={self.name}\tcomando={self.command}\nvalore aspettato per risultato={self.expected_result}"

    def __eq__ (self,o):
        if(type(o)=="Rule"):
            eq_name = self.name == o.name 
            eq_command = self.command == o.command 
            eq_descr = self.description == o.description 
            eq_exp = self.expected_result == o.expected_result 
            eq_status = self.status == o.status 
            return eq_name and eq_command and eq_descr and eq_exp and eq_status
        else:
            return False
    def to_dict(self,ip:str):
        return {'name':self.name,'description':self.description,'status':self.status,'ip':ip}



    def check(self)->bool:
        """
        Lancia command sul sistema e verifica se contiene il risultato di expected_result
        """ 
        result = subprocess.run(
            self.command,
            shell=True,  
            capture_output=True,  
            text=True  
        )
        print(f"prova subprocess valore stdout {result.stdout}\t stderr {result.stderr} ")
        self.status = result.stdout == self.expected_result 
        return self.status


class SystemRules:
    """
    Classe che rappresenta le regole di sicurezza che vogliamo testare sulla nostra configurazione
    """
    def __init__(self,name:str,descr:str):
        self.name = name 
        self.descr = descr
        self.rules: List[Rule] = []
    def add_rule(self,rule:Rule):
        """
        aggiunge rule alle regole da controllare nel sistema 
        """
        self.rules.append(rule)
    def delete_rule(self,rule:Rule):
        """
        cancella la regola dalla lista di regole che rappresentano il sistema(rules)
        """
        self.rules.remove(rule)
    def checkAll(self):
        for rule in self.rules:
            rule.check()


def test_rule():

    regola_shadow = Rule(
        name="Regola shadow",
        command='''awk -F: '($2 == "" ) { print $1 " does not have a password "}' /etc/shadow''',
        expected_result = "")
    ris_regola = regola_shadow.check()
    print("Dettagli regola con  implementato metodo di stampa oggetto",regola_shadow)
    print("risultato check",ris_regola)
    print("Test conversione in json")
    obj_json=json.dumps(regola_shadow.to_dict('192.168.1.1'))
    print(f"oggetto json {obj_json}")
def test_system():
    sys = SystemRules("Test","Test regole")

    regola_shadow = Rule(
        name="Regola shadow",
        command='''awk -F: '($2 == "" ) { print $1 " does not have a password "}' /etc/shadow''',
        expected_result = "")
    sys.add_rule(regola_shadow)
    print(f"regola shadow\n {regola_shadow} ")

  #  regola_shadow = Rule( name="2.2.12 Ensure HTTP Proxy Server is not installed", command='''dpkg-query -W -f='${binary:Package} ${Status}\t${db:Status-Status} squid''', expected_result = "squid unknown ok not-installed not-installed")
  # sys.add_rule(regola_shadow)
    print("controllo tutto")
    #sys.checkAll()
if __name__ == "__main__":

    #test_rule()
    test_system()

