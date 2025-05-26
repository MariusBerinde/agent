import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs
import subprocess
import os
import glob
from pathlib import Path

def read_json():
    with open('./data/config.json', 'r') as file:
        local_data = json.load(file)

    print(local_data)
    return local_data

def get_last_report():
    '''
    return the last lynis report 
    Aggiornata per gestire il formato lynis_audit_DD-MM-YYYY_HH-MM-SS.txt
    '''
    cmd = "ls -t ./data/lynis_audit_*.txt | head -n 1"
    last_lynis_report = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.replace("\n","")
    content_file = ""
    with open(last_lynis_report) as file:
        content_file = file.read()
    print(f"nome ultimo report lynis: {last_lynis_report}")
    print(f"contenuto ultimo report {content_file}")
    return content_file

def get_last_report_alternative():
    '''
    Versione alternativa usando solo pathlib (più moderna)
    Gestisce il formato lynis_audit_DD-MM-YYYY_HH-MM-SS.txt
    '''
    try:
        data_dir = Path("./data")
        
        if not data_dir.exists():
            raise FileNotFoundError("La directory ./data/ non esiste")
        
        # Trova tutti i file lynis usando il pattern corretto
        lynis_files = list(data_dir.glob("lynis_audit_*.txt"))
        
        if not lynis_files:
            raise FileNotFoundError("Nessun file lynis trovato nella directory ./data/")
        
        # Trova il file più recente basandosi sulla data di modifica del file
        last_lynis_report = max(lynis_files, key=lambda f: f.stat().st_mtime)
        
        # Legge il contenuto
        content_file = last_lynis_report.read_text(encoding='utf-8')
        
        print(f"Nome ultimo report lynis: {last_lynis_report}")
        print(f"Contenuto ultimo report: {content_file[:100]}...")
        
        return content_file
        
    except FileNotFoundError as e:
        print(f"Errore: {e}")
        raise
    except IOError as e:
        print(f"Errore nella lettura del file: {e}")
        raise

def get_last_report_file_info():
    '''
    Restituisce informazioni sul file dell'ultimo report lynis
    Gestisce il formato lynis_audit_DD-MM-YYYY_HH-MM-SS.txt
    '''
    try:
        data_dir = Path("./data")
        
        if not data_dir.exists():
            raise FileNotFoundError("La directory ./data/ non esiste")
        
        # Trova tutti i file lynis usando il pattern corretto
        lynis_files = list(data_dir.glob("lynis_audit_*.txt"))
        
        if not lynis_files:
            raise FileNotFoundError("Nessun file lynis trovato nella directory ./data/")
        
        # Trova il file più recente basandosi sulla data di modifica del file
        last_lynis_report = max(lynis_files, key=lambda f: f.stat().st_mtime)
        
        # Restituisce info sul file
        file_info = {
            "filename": last_lynis_report.name,
            "filepath": str(last_lynis_report),
            "size": last_lynis_report.stat().st_size,
            "modified_time": last_lynis_report.stat().st_mtime,
            "size_mb": round(last_lynis_report.stat().st_size / 1024 / 1024, 2)
        }
        
        print(f"Info ultimo report lynis: {file_info}")
        
        return file_info
        
    except FileNotFoundError as e:
        print(f"Errore: {e}")
        raise
    except IOError as e:
        print(f"Errore nell'accesso al file: {e}")
        raise

class AgentRequest (http.server.BaseHTTPRequestHandler):
    """
    gestione richieste http
    """

    def do_GET(self):
        """
        Per le richieste get
        """
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/ping':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "success", "message": "Agent is running"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        if path == '/lol': 
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "success", "message": "lol msg from server"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        # NUOVA ROUTE: get_report_content - restituisce il contenuto dell'ultimo report
        if path == '/get_report_content':
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Ottiene il contenuto dell'ultimo report
                report_content = get_last_report_alternative()
                
                response = {
                    "status": "success", 
                    "message": "Report content retrieved successfully",
                    "content": report_content
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    "status": "error", 
                    "message": f"Errore nel recupero del contenuto del report: {str(e)}"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

        # NUOVA ROUTE: get_report - restituisce informazioni sull'ultimo report
        if path == '/get_report':
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Ottiene informazioni sul file dell'ultimo report
                report_info = get_last_report_file_info()
                
                response = {
                    "status": "success", 
                    "message": "Report info retrieved successfully",
                    "report_info": report_info
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    "status": "error", 
                    "message": f"Errore nel recupero delle informazioni del report: {str(e)}"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

        if path == '/report': 
            self.send_response(200)
            self.send_header('Content-Type', 'text')
            self.end_headers()
            report = get_last_report()
            report_alt = get_last_report_alternative()

            response = {"status": "success", "message": get_last_report}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        if path == '/obj': 
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            json_data = read_json()

            response = {"status": "success", "message": json_data}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

    def do_POST(self):
        """
        Per le richieste POST
        """
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        # Leggiamo la lunghezza del contenuto
        content_length = int(self.headers.get('Content-Length', 0))
        
        if content_length > 0:
            # Leggiamo il corpo della richiesta
            post_data = self.rfile.read(content_length)
            
            try:
                # Convertiamo il JSON in un dizionario Python
                data = json.loads(post_data.decode('utf-8'))
                
                # Gestiamo i diversi endpoint
                if path == "/add_data":
                    # Elaboriamo i dati ricevuti
                    # Esempio: salviamo in un file o in un database
                    print(f"ecco il dato ricevuto {data}")
                    
                    # Rispondiamo con successo
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {"status": "success", "message": "Messaggio ricevuto"}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                elif path == "/load_user":

                    print(f"Nome utente ricevuto {data}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {"status": "success", "message": "Messaggio ricevuto"}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    # Endpoint non riconosciuto
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {"status": "error", "message": "Endpoint not found"}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    
            except json.JSONDecodeError:
                # Gestiamo l'errore se i dati ricevuti non sono JSON valido
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "Invalid JSON data"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # Nessun dato ricevuto
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "No data provided"}
            self.wfile.write(json.dumps(response).encode('utf-8'))

def main():
    print("dentro main") 
    port =  5000
    host =  '0.0.0.0'
    print(f"config attula {port},host{host}")
    try:
        with socketserver.TCPServer((host, port), AgentRequest ) as httpd:
            print(f"Server avviato su {host}:{port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server fermato")
    except Exception as e:
        print(f"Errore nell'avvio del server: {e}")

if __name__ == "__main__":
    main()
    #get_last_report()
