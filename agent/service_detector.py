#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import os


class ServiceDetector:
    """
    Classe per rilevare i servizi di sistema e il loro stato su Debian 11.
    Utilizza systemctl per ottenere l'elenco e lo stato dei servizi.
    """
    
    def __init__(self):
        """
        Inizializza la classe ServiceDetector.
        Verifica che l'utente abbia i permessi necessari per eseguire i comandi.
        """
        if os.geteuid() != 0:
            print("Attenzione: Alcuni servizi potrebbero non essere visibili senza permessi di root.")
            print("Si consiglia di eseguire lo script con sudo per risultati completi.")
    
    def get_services(self):
        """
        Ottiene l'elenco di tutti i servizi sul sistema.
        
        Returns:
            list: Lista di dizionari, ognuno contenente 'nome' e 'stato' di un servizio.
        """
        try:
            # Esegue il comando systemctl per ottenere l'elenco dei servizi
            cmd = ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--plain"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Elabora l'output per estrarre nome e stato dei servizi
            services = []
            for line in result.stdout.split('\n'):
                # Ignora le linee vuote o le intestazioni
                if not line.strip() or "UNIT" in line and "LOAD" in line:
                    continue
                
                # Usa regex per estrarre nome e stato del servizio
                match = re.match(r'(\S+\.service)\s+\S+\s+\S+\s+(\S+)\s+.*', line)
                if match:
                    service_name = match.group(1)
                    service_status = match.group(2)
                    services.append({
                        'nome': service_name,
                        'stato': service_status
                    })
            
            return services
        
        except subprocess.SubprocessError as e:
            print(f"Errore nell'esecuzione del comando systemctl: {e}")
            return []
        except Exception as e:
            print(f"Errore imprevisto: {e}")
            return []
    
    def get_service_details(self, service_name):
        """
        Ottiene informazioni dettagliate su un servizio specifico.
        
        Args:
            service_name (str): Il nome del servizio da controllare.
            
        Returns:
            dict: Dizionario con informazioni dettagliate sul servizio.
        """
        try:
            # Verifica che il nome del servizio termini con .service
            if not service_name.endswith('.service'):
                service_name += '.service'
            
            # Esegue il comando systemctl per ottenere i dettagli del servizio
            cmd = ["systemctl", "show", service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Elabora l'output per creare un dizionario di proprietà
            details = {}
            for line in result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    details[key] = value
            
            return details
        
        except subprocess.SubprocessError as e:
            print(f"Errore nell'ottenere i dettagli per il servizio {service_name}: {e}")
            return {}
        except Exception as e:
            print(f"Errore imprevisto: {e}")
            return {}


# Esempio di utilizzo
if __name__ == "__main__":
    detector = ServiceDetector()
    
    print("Rilevamento dei servizi di sistema...")
    services = detector.get_services()
    
    if services:
        print(f"\nTrovati {len(services)} servizi sul sistema:\n")
        print(f"{'NOME SERVIZIO':<50} {'STATO':<15}")
        print("-" * 65)
        
        for service in services:
            print(f"{service['nome']:<50} {service['stato']:<15}")
        
        # Esempio di come ottenere dettagli su un servizio specifico
        print("\nPer ottenere dettagli su un servizio specifico:")
        print("detector.get_service_details('nome_servizio.service')")
    else:
        print("Nessun servizio trovato o errore nell'esecuzione.")
