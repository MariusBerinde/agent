import subprocess
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
    def __init__(self, name:str,command:str,expected_result:str,status:bool=False,description:str=None):
        self.name  = name
        self.command = command
        self.description = description 
        self.expected_result = expected_result
        self.status = status
    def __str__(self):
        return f"nome={self.name},comando={self.command},valore aspettato per risultato={self.expected_result}"

    def check(self)->bool:
        """
        Lancia command sul sistema e verifica se contiene il risultato di expected_result
        """ 
        result = subprocess.run(
            self.command,
            shell=True,  # Necessario per comandi con pipe o redirezioni
            capture_output=True,  # Cattura sia stdout che stderr
            text=True  # Converte l'output in stringa
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
    def addRule(self,rule:Rule):
        """
        aggiunge rule alle regole da controllare nel sistema 
        """
        self.rules.append(rule)
    def deleteRule(self,rule:Rule):
        """
        cancella la regola dalla lista di regole che rappresentano il sistema(rules)
        """
        self.rules.remove(rule)
    def checkAll(self):
        for rule in self.rules:
            rule.check()


if __name__ == "__main__":
    regola_shadow = Rule(
        name="Regola shadow",
        command='''awk -F: '($2 == "" ) { print $1 " does not have a password "}' /etc/shadow''',
        expected_result = "")
    ris_regola = regola_shadow.check()
    print("Dettagli regola con  implementato metodo di stampa oggetto",regola_shadow)
    print("risultato check",ris_regola)

