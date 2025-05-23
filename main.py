#from agent import lynis ,Lynis, scanLynis,UserLogger,setup_logger,Rule,SystemRules
from agent import Lynis, UserLogger,setup_logger,Rule,SystemRules
#from logging.handlers import RotatingFileHandler
from typing import List
#from urllib.parse import urlparse, parse_qs
from urllib.parse import urlparse
import http.server
import json
import socketserver
import subprocess
import platform as pt;

actual_username="Unknown"
main_logger = setup_logger(log_file_path='application.log')
rules = []
logger = UserLogger(main_logger,"Giggino", {})

def read_json():
    with open('./data/config.json', 'r') as file:
        local_data = json.load(file)
    return local_data

def get_local_info():
    command_ip = 'hostname -I'
    ip = subprocess.run(
        command_ip,
        shell=True,  
        capture_output=True,  
        text=True  
    )
    os = pt.uname().system
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
        with open('./application.log', 'r', encoding='utf-8') as file:
            # Legge tutte le righe del file
            for line in file:
                # Rimuove spazi bianchi extra e caratteri newline
                line = line.strip()
                if line:  # Ignora righe vuote
                    logs.append(line)
        
        print(f"Lette {len(logs)} righe di log")
    except FileNotFoundError:
        print("Il file application.log non è stato trovato.")
    except Exception as e:
        print(f"Si è verificato un errore durante la lettura del file: {str(e)}")
    
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
    lynis = Lynis()
    if len(rules) > 0:
        lynis.add_rules(rules)
    else:
        lynis.delete_all_rules()
        

class AgentRequest (http.server.BaseHTTPRequestHandler):
    

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
            #ip = "192.168.1.1"

            #logger.user = self.actual_username             
            print(f" utente attule {actual_username}")
            if actual_username !='Unknown':
                logger.info(f"ping from {ip}")
                print(f"utente loggato come {logger.user}\t ip sender={ip}")

            response = {"status": "success", "message": "Agent is running"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        if path == '/get_status':
            # read local data 
            # extract other info services
            logger.info("get request status")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status = get_local_info()
            response = {"status": "success", "message": status}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        if path == '/get_rules':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            logger.info("required security rules")

            actual_rules = get_system_rules()
            json_rules = []
            for rule in actual_rules.rules :
                json_rules.append(json.dumps(rule.to_dict('192.168.1.1')))

            response = {"status": "success", "message": json_rules}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        if path == '/get_logs':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            logger.info("required logs")
            logs = get_logs()
            response = {"status": "success", "message": logs}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return 

        if path == '/get_lynis':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            lynis = get_lynis()
            logger.info("required lynis rules")
            response = {"status": "success", "message": lynis}
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
                    print(f"ecco il dato ricevuto {data}")
                    
                    logger.info(f"added the folloing rules = {data} as the lynis skipped rules")
                    replace_rules(data)
                    
                    # Rispondiamo con successo
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
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {"status": "success", "message": f"registrato utente {data}"}
                    logger.info(f"set user {data} as active user")
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    self.process_command(data)
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

    def process_command(self, data):
        """Elabora i comandi ricevuti"""
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


if __name__ == "__main__":


    json_data=read_json()
     #print(json.dumps(json_data, indent=4))
    port = json_data["port"]
    host = '0.0.0.0'
    print(f"config attula {port},host{host}")
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
    except Exception as e:
        print(f"Errore nell'avvio del server: {e}")
        
