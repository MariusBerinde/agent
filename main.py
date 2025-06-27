from agent import Lynis, UserLogger,setup_logger,Rule,SystemRules,scanLynis
from typing import List
from urllib.parse import urlparse
import http.server
import json
import subprocess
import platform as pt;
import sys 
import socketserver
from pathlib import Path

actual_username="Unknown"
LOG_FILE = './data/application.log'
CONFIG_FILE = './data/config.json'
main_logger = setup_logger(log_file_path=LOG_FILE)
rules = []
logger = UserLogger(main_logger,"Unknown", {})

def read_json():
    try:
        with open( CONFIG_FILE, 'r') as file:
            local_data = json.load(file)
    except FileNotFoundError:
        logger.error(f"file {CONFIG_FILE} non trovato")
        sys.exit(1)
    except Exception as e:
        logger.error(f"errore {e} con il file {CONFIG_FILE}")
        sys.exit(1)

    return local_data

def get_local_info():
    command_ip = 'hostname -I'
    try:
        ip = subprocess.run(
            command_ip,
            shell=True,  
            capture_output=True,  
            text=True  
        )
        os = pt.uname().system
    except subprocess.CalledProcessError as e:
        logger.error(f"errore nel recuperare l'IP con il comando {command_ip} :{e}")
        sys.exit(1)
    except Exception as e:

        logger.error(f"errore generico in get_local_info {e}")
        sys.exit(1)
    return [ip.stdout,os]

def get_logs() -> List[str]:
    """
    Legge il file di log e restituisce una lista di righe.
    
    Returns:
        List[str]: Lista contenente tutte le righe del file di log
    """
    logs = []
    print("Lettura del file di log in corso...")
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as file:
            # Legge tutte le righe del file
            for line in file:
                # Rimuove spazi bianchi extra e caratteri newline
                line = line.strip()
                if line:  # Ignora righe vuote
                    logs.append(line)
        #print(f"Lette {len(logs)} righe di log")
    except FileNotFoundError:
        logger.error(f"file {LOG_FILE} non trovato")
        sys.exit(1)
    except Exception as e:
        logger.error(f"errore {e} con il file {LOG_FILE}")
        sys.exit(1)
    
    return logs

def get_lynis():
    lynis = Lynis()
    return lynis.get_skipped_rules()

def get_system_rules()->SystemRules:
    system_rules = SystemRules("Linux","Sistema di prova")
    local_config = read_json() 
    for line in local_config["rules"]:
        tmp_rule = Rule( name=line['name'], command=line['command'], expected_result= line['expected_ris'],description=line['desc'] )
        system_rules.add_rule(tmp_rule) 
    system_rules.checkAll()
    return system_rules

def replace_rules(rules):

    print(f" REPLACE_RULES parameters {rules}")
    lynis = Lynis()
    print(f" REPLACE_RULES:list of skipped rules before the use of param: {lynis.get_skipped_rules()}")
    if len(rules) > 0:
        lynis.add_rules(rules)
        print(f" REPLACE_RULES list of skipped rules after the add after the use of param: {lynis.get_skipped_rules()}")
    else:
        lynis.delete_all_rules()
        print(f" REPLACE_RULES list of skipped rules after the reset  {lynis.get_skipped_rules()}")

        

def get_last_report():
    '''
    Versione usando solo pathlib (più moderna)
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
        logger.error(f"file non trovato in get_last_report {e}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"Errore nella lettura del file: {e}")
        sys.exit(1)

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
        logger.error(f"Errore in : {e}")
        raise
    except IOError as e:
        logger.error(f"Errore nell'accesso al file: {e}")
        raise
def is_service_active(service_name):
    """
    Verifica se un servizio systemd è attivo.
    
    Args:
        service_name (str): Nome del servizio da verificare
        
    Returns:
        bool: True se il servizio è attivo, False altrimenti
    """
    try:
        # Usa systemctl per verificare lo stato del servizio
        # L'opzione --quiet sopprime l'output
        # is-active restituisce 0 se il servizio è attivo, non-zero altrimenti
        result = subprocess.run(
            ['systemctl', 'is-active', '--quiet', service_name],
            capture_output=True,
            timeout=10
        )
        
        # Se il codice di ritorno è 0, il servizio è attivo
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        # Timeout - considera il servizio non attivo
        return False
    except FileNotFoundError as f:
        # systemctl non trovato - prova con il metodo alternativo
        logger.error("is_service_active : systemctl non trovato")
        return False
        return _check_service_alternative(service_name)
    except Exception as e:
        # Qualsiasi altro errore
        logger.error(f" lanciata eccezzione durante l'esecuzione della funzione is_service_active:{e}")
        return False

class AgentRequest (http.server.BaseHTTPRequestHandler):
    #    protocol_version = "HTTP/1.1"

    def get_client_ip(self):
        """
        Restituisce l'indirizzo IP del client.
        
        Returns:
            str: Indirizzo IP del client
        """
        # Controlla prima gli header per proxy/load balancer
        forwarded_for = self.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Se ci sono più IP separati da virgole, prende il primo
            return forwarded_for.split(',')[0].strip()
        
        # Controlla X-Real-IP (CORREZIONE: ora è raggiungibile)
        real_ip = self.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()
        
        # Usa l'indirizzo diretto del client
        return self.client_address[0]

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
            ip = self.get_client_ip()
            print(f" utente attule {actual_username}")
            logger.info(f"ping from {ip}")
            print(f"utente loggato come {logger.user}\t ip sender={ip}")
            response = {"status": "success", "message": "Agent is running"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        if path == '/get_status':
            if logger.user == "Unknown":
                self.send_response(401)
                logger.error("rischiesta di stato da parte di utente non riconosciuto")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "utente non riconosciuto"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                logger.info("get request status")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                status = get_local_info()
                response = {"status": "success", "message": status}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        if path == '/get_rules':
            if logger.user == "Unknown":
                self.send_response(401)
                logger.info("tentativo di ricevimento info da utente non riconosciuto")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "utente non riconosciuto operazione non permessa"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                logger.info("required security rules")
                actual_rules = get_system_rules()
                json_rules = []
                ip = self.get_client_ip()
                for rule in actual_rules.rules :
                    json_rules.append(json.dumps(rule.to_dict(ip)))
                response = {"status": "success", "message": json_rules}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        if path == '/get_logs':
            if logger.user == "Unknown":
                self.send_response(401)
                logger.info("richiesta di logs da parte di utente non riconosciuto")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "utente non riconosciuto operazione non permessa"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                logger.info("required logs")
                logs = get_logs()
                response = {"status": "success", "message": logs}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            return 

        if path == '/get_lynis':
            if logger.user == "Unknown":
                self.send_response(401)
                logger.info("richiesta di regole lynis da parte di un utente non riconosciuto")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "utente non riconosciuto operazione non permessa"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                lynis = get_lynis()
                logger.info("required lynis rules")
                response = {"status": "success", "message": lynis}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            return 

        if path == '/get_lynis_report':
            if logger.user == "Unknown":
                self.send_response(401)
                logger.info("richiesta di report lynis  da parte di un utente non riconosciuto")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "utente non riconosciuto operazione non permessa"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'html/txt')
                self.end_headers()
                lynis =  read_last_report()
                logger.info("required last lynis report")
                response = {"status": "success", "message": lynis}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            return 
    
        if path == '/start_lynis_scan':
            if logger.user == "Unknown":
                self.send_response(401)
                logger.info("tentativo di lancio di scan lynis da parte di utente non riconosciuto")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "utente non riconosciuto operazione non permessa"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else: 
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                lynis = scanLynis(logger.user)
                logger.info("lancio lynis scan")
                response = {"status": "success", "message": lynis}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            return 
    
        if path == '/get_report_content':
            if logger.user == "Unknown":
                self.send_response(401)
                logger.error("richiesta del report lynis da parte di un utente sconosciuto")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "utente non riconosciuto"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:

                try:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    report_content = get_last_report()
                    
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
                    logger.error(f"Errore nel recupero delle informazioni del report: {str(e)}")
                    return

        if path == '/get_report':
            if logger.user == "Unknown":
                self.send_response(401)
                logger.error("richiesta del report lynis da parte di un utente sconosciuto")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "utente non riconosciuto"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
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
                    logger.error(f"Errore nel recupero delle informazioni del report: {str(e)}")
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
                
                if path == "/add_rules":
                    # per sostituire file di configurazione  
                    if logger.user == 'Unknown':
                        self.send_response(401)
                        logger.info("tentativo di inserimento regole da saltare da utente non riconosciuto")
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {"status": "success", "message": "utente non riconosciuto operazione non permessa"}
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                    else:
                        rules =  data["rules"]
                        print(f"ecco il dato ricevuto {rules}")
                        replace_rules(rules)
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {"status": "success", "message": "Regole aggiornate"}
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                elif path == "/set_user":
                    print("dato ricevuto =",data["name"])
                    logger.user = data["name"]
                    actual_username =  data["name"]
                    print(f"acutal user modificato {actual_username}")

                    '''

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    '''
                    #response = {"status": "success", "message": "registrato utente {data}"}
                    response = {"status": "success", "message": "registrato utente "}
                    response_bytes = json.dumps(response).encode('utf-8')

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(response_bytes)))
                    self.send_header('Connection', 'close')  # <--- IMPORTANTE
                    self.end_headers()
                    self.wfile.write(response_bytes)
                    #self.process_command(data)
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
                logger.error("Invalid JSON data")
                response = {"status": "error", "message": "Invalid JSON data"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # Nessun dato ricevuto
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "No data provided"}
            self.wfile.write(json.dumps(response).encode('utf-8'))

            """

    def process_command(self, data):
        ->Elabora i comandi ricevuti <- da commentare 
        # Verifica che la struttura del comando sia valida
        if 'command' not in data:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Missing command field"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        command = data['command']
        params = data.get('params', {})
        
        # Comandi disponibili
        commands = {
            'get_service_status': self.get_service_status,
            'start_service': self.start_service,
            'stop_service': self.stop_service,
            'restart_service': self.restart_service,
            # Altri comandi che hai già implementato
        }
        
        # Esegue il comando se disponibile
        if command in commands:
            commands[command](params)
        else:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": f"Unknown command: {command}"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    # Implementa i vari metodi per i comandi
    def get_service_status(self, params):
        # Implementazione
        pass
        
    def start_service(self, params):
        # Implementazione
        pass
        
    def stop_service(self, params):
        # Implementazione
        pass
        
    def restart_service(self, params):
        # Implementazione
        pass

            """


def test_read_json():
    json_data=read_json()
    print(json.dumps(json_data, indent=4))
    port = json_data["port"]
    print(f"test isolamento parti:\n porta di funzionamento ={port}")
    for r in json_data["rules"]:
        print(f"nome:{r['name']}\ncommand:{r['command']}\ndesc:{r['desc']}\nex:{r['expected_ris']}")
        print("------")
def test_log():
    logger.user = "Mariolone Bubbarello"
    logger.info("Test from main")
def test_read_logs():
    logs = get_logs()
    for l in logs:
        print(l)
def test_load_rules():
    system_rules = SystemRules("Linux","Sistema di prova")
    local_config = read_json() 
    for line in local_config["rules"]:
        print(f"riga attuale {line}")
        tmp_rule = Rule( name=line['name'], command=line['command'], expected_result= line['expected_ris'],description=line['desc'] )
        print(f"stampo anche la regola creata\n{tmp_rule}")
        system_rules.add_rule(tmp_rule) 
    print("Ecco le regole caricate:")
    system_rules.checkAll()

    for r in system_rules.rules:
        #stato_locale = r.check()
        valore_status =r.status 
        #print(f"{r}\t stato_locale={stato_locale}\t valore status={valore_status}")
        print(f"{r}\t  valore status={valore_status}")
def test_get_local_info():
    [ip,os] = get_local_info()
    print(f"ip attuale {ip}\nsistema operativo{os}")

def test_set_new_lynis_rules(path_config_lynis):
    print("test add rules with empty array")
    replace_rules(path_config_lynis,[])
    print("------")
    print("test replace rules with obljet like from the client")
    replace_rules(path_config_lynis,["ACCT-2754","ACCT-2760"])




if __name__ == "__main__":
    json_data=read_json()
    print(json.dumps(json_data, indent=4))
    port = json_data["port"]
    host = '0.0.0.0'
    logger.info("Avvio server")
    servizi = json_data["services"]
    print(f"config attuale {port},host{host}")


    ''' 
    print(f"lettura servizi da controllare: {servizi}")
    for e in servizi:
        print(e)
    '''
   # test_set_new_lynis_rules(json_data["lynis_profile"]);
    #test_log()
    #test_read_logs()
    #test_load_rules()
    #test_get_local_info()


    try:
        with socketserver.TCPServer((host, port), AgentRequest ) as httpd:
            print(f"Server avviato su {host}:{port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server fermato")
        logger.info("server locale fermato correttamente")
        sys.exit(0)
    except Exception as e:
        print(f"Errore nell'avvio del server: {e}")
        logger.error(f"server locale fermato con errore {e}")
        sys.exit(1)
        

