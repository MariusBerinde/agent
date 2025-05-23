import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

def read_json():
    with open('./data/config.json', 'r') as file:
        local_data = json.load(file)

    print(local_data)
    return local_data


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
