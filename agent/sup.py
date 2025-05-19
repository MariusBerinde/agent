import os
import re
from typing import Tuple, List, Set


class Lynis:
    """
    Classe che contiene metodi di supporto per l'uso di Lynis,
    uno strumento di auditing per la sicurezza dei sistemi.
    """
    def __init__(self, profile_path="../data/deb.prt"):
        """
        Inizializza un'istanza della classe Lynis.

        Args:
            profile_path: Percorso al file di profilo Lynis da utilizzare
        """
        self.profile = profile_path
        self._validate_profile()
        self.skipped_list = self._read_skipped_list()
    
    def _validate_profile(self) -> None:
        """
        Verifica che il file di profilo esista e sia accessibile.
        
        Raises:
            FileNotFoundError: Se il file di profilo non esiste
            PermissionError: Se il file di profilo non è accessibile
        """
        if not os.path.exists(self.profile):
            raise FileNotFoundError(f"Il file di profilo '{self.profile}' non esiste")
        if not os.access(self.profile, os.R_OK | os.W_OK):
            raise PermissionError(f"Permessi insufficienti per accedere al file '{self.profile}'")
    
    def _read_skipped_list(self) -> Set[str]:
        """
        Legge dal file di profilo tutte le regole che vengono saltate durante il controllo di Lynis.
        
        Returns:
            Set[str]: Set di regole saltate
        """
        skipped_rules = set()
        try:
            with open(self.profile, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('skip-test='):
                        rule = line.split('=', 1)[1]
                        if rule:  # Assicuriamoci che la regola non sia vuota
                            skipped_rules.add(rule)
        except Exception as e:
            print(f"Errore durante la lettura delle regole saltate: {e}")
        
        return skipped_rules
    
    def get_skipped_rules(self) -> Set[str]:
        """
        Restituisce la lista delle regole attualmente saltate.
        
        Returns:
            Set[str]: Set delle regole saltate
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
                self.skipped_list.discard(rule)
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
        rules_to_remove = list(self.skipped_list)  # Crea una copia per evitare modifiche durante l'iterazione
        
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
                - bool: True se tutte le regole sono state aggiunte con successo, False altrimenti
                - List[str]: Lista delle regole che non è stato possibile aggiungere
        """
        not_added = []
        added = False
        
        try:
            with open(self.profile, "a") as f:
                for rule in rules:
                    # Verifica se la regola è già presente
                    if rule in self.skipped_list:
                        continue
                    
                    rule = rule.strip()  # Rimuove spazi iniziali e finali
                    if not rule:  # Salta regole vuote
                        continue
                        
                    line = f"skip-test={rule}\n"
                    f.write(line)
                    self.skipped_list.add(rule)
                    added = True
            
            return added, not_added
        except Exception as e:
            print(f"Errore durante l'aggiunta delle regole: {e}")
            return False, rules
    
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
        self.skipped_list = self._read_skipped_list()

