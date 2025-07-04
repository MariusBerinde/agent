import os
import re
import unittest
from pathlib import Path
from typing import Tuple, List


class Lynis:
    """
    Classe che contiene metodi di supporto per l'uso di Lynis,
    uno strumento di auditing per la sicurezza dei sistemi.
    """
    def __init__(self, profile_path=None):
        """
        Inizializza un'istanza della classe Lynis.

        Args:
            profile_path: Percorso al file di profilo Lynis da utilizzare.
                          Se None, verrà usato il percorso predefinito.
        """
        self.profile = profile_path or "./data/deb.prt"
        self._validate_profile()
        self.skipped_list = self.read_skipped_list()

    def to_dict(self,ip:str):
        return {"profilo":self.profile,"ip":ip}


    def _validate_profile(self) -> None:
        """
        Verifica che il file di profilo esista e sia accessibile.
        
        Raises:
            FileNotFoundError: Se il file di profilo non esiste
            PermissionError: Se il file di profilo non è accessibile
        """
        profile_path = Path(self.profile)
        if not profile_path.exists():
            raise FileNotFoundError(f"Il file di profilo '{self.profile}' non esiste")
        if not os.access(self.profile, os.R_OK | os.W_OK):
            raise PermissionError(f"Permessi insufficienti per accedere al file '{self.profile}'")
    
    def read_skipped_list(self) -> List[str]:
        """
        Legge dal file di profilo tutte le regole che vengono saltate durante il controllo di Lynis.
        
        Returns:
            List[str]: Lista di regole saltate
        """
        skipped_rules = []
        try:
            # Metodo sicuro che usa file handling invece di os.popen
            with open(self.profile, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('skip-test='):
                        rule = line.split('=', 1)[1]
                        if rule:  # Assicuriamoci che la regola non sia vuota
                            skipped_rules.append(rule)
        except Exception as e:
            print(f"Errore durante la lettura delle regole saltate: {e}")
        
        return skipped_rules
    
    def get_skipped_rules(self) -> List[str]:
        """
        Restituisce la lista delle regole attualmente saltate.
        
        Returns:
            List[str]: Lista delle regole saltate
        """
        return self.skipped_list.copy()
    
    def delete_rule(self, rule: str) -> bool:
        """
        Tenta di cancellare una regola presente nel file di profilo.
        
        Args:
            rule: La regola da cancellare
            
        Returns:
            bool: True se la regola è stata cancellata con successo, False altrimenti
        """
        try:
            with open(self.profile, "r") as f:
                lines = f.readlines()
            
            new_lines = []
            found = False
            for line in lines:
                if line.strip() == f"skip-test={rule}":
                    found = True
                    continue  # salta la riga con la regola
                new_lines.append(line)
            
            if found:
                with open(self.profile, "w") as f:
                    f.writelines(new_lines)
                # Aggiorniamo la lista locale
                if rule in self.skipped_list:
                    self.skipped_list.remove(rule)
                return True
            return False
        except Exception as e:
            print(f"Errore durante la cancellazione della regola '{rule}': {e}")
            return False
    
    def delete_all_rules(self) -> Tuple[bool, List[str]]:
        """
        Cancella tutte le regole presenti in self.skipped_list dal file di profilo Lynis.
        
        Returns:
            Tuple[bool, List[str]]: Una tupla contenente:
                - bool: True se tutte le regole sono state cancellate, False altrimenti
                - List[str]: Lista delle regole che non è stato possibile cancellare
        """
        not_removed = []
        rules_to_remove = self.skipped_list.copy()  # Crea una copia per evitare modifiche durante l'iterazione
        
        for rule in rules_to_remove:
            cancellation_result = self.delete_rule(rule)
            if not cancellation_result:
                not_removed.append(rule)
        
        all_removed = len(not_removed) == 0
        return all_removed, not_removed
    
    def add_rules(self, rules: List[str]) -> Tuple[bool, List[str]]:
        """
        Aggiunge regole da saltare durante l'esecuzione di Lynis.
        
        Args:
            rules: Lista di regole da aggiungere
            
        Returns:
            Tuple[bool, List[str]]: Una tupla contenente:
                - bool: True se alcune regole sono state aggiunte con successo
                - List[str]: Lista delle regole aggiunte con successo
        """
        added_rules = []
        
        try:
            with open(self.profile, "a") as f:
                for rule in rules:
                    rule = rule.strip()  # Rimuove spazi iniziali e finali
                    if not rule or rule in self.skipped_list:  # Salta regole vuote o già presenti
                        continue
                        
                    line = f"skip-test={rule}\n"
                    f.write(line)
                    self.skipped_list.append(rule)
                    added_rules.append(rule)
            
            success = len(added_rules) > 0
            return success, added_rules
        except Exception as e:
            print(f"Errore durante l'aggiunta delle regole: {e}")
            return False, []
    
    def is_rule_skipped(self, rule: str) -> bool:
        """
        Controlla se una regola è attualmente saltata.
        
        Args:
            rule: La regola da controllare
            
        Returns:
            bool: True se la regola è saltata, False altrimenti
        """
        return rule in self.skipped_list
    
    def reload_skipped_list(self) -> None:
        """
        Ricarica la lista delle regole saltate dal file di profilo.
        Utile dopo modifiche esterne al file.
        """
        self.skipped_list = self.read_skipped_list()
        
    def find_rules_by_pattern(self, pattern: str) -> List[str]:
        """
        Cerca regole che corrispondono a un pattern specifico.
        
        Args:
            pattern: Il pattern regex da cercare
            
        Returns:
            List[str]: Lista delle regole che corrispondono al pattern
        """
        regex = re.compile(pattern, re.IGNORECASE)
        return [rule for rule in self.skipped_list if regex.search(rule)]



if __name__ == "__main__":
    # Esempio di utilizzo della classe
    try:
        print("=== Esempio di utilizzo della classe Lynis ===")
        lynis = Lynis()
        print(f"Regole attualmente saltate: {lynis.get_skipped_rules()}")
        
        # Prova ad aggiungere una regola
        test_rule = "PHP-2211"
        success, added = lynis.add_rules([test_rule])
        if success:
            print(f"Regole aggiunte con successo: {added}")
        else:
            print("Impossibile aggiungere le regole")
        
        # Prova a eliminare una regola
        if lynis.delete_rule(test_rule):
            print(f"Regola {test_rule} eliminata con successo")
        else:
            print(f"Impossibile eliminare la regola {test_rule}")
        
        # Cerca regole per pattern
        php_rules = lynis.find_rules_by_pattern("PHP")
        if php_rules:
            print(f"Regole PHP trovate: {php_rules}")
        else:
            print("Nessuna regola PHP trovata")
            
        print("\n=== Esecuzione dei test unitari ===")
        unittest.main()
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")
