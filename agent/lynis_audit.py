import subprocess
import datetime
import os
import re

def scanLynis(auditor: str="Altair"):
    """
    Esegue un audit di sistema con Lynis e salva l'output in un file timestampato.
    
    Args:
        auditor (str): Nome dell'auditor da inserire nel report.
    """
    # Timestamp per il nome file
    timestamp = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    output_filename = f"../data/lynis_audit_{timestamp}.txt"
    output_filename1 = f"./data/lynis_audit_{timestamp}.txt"

    # (Facoltativo) profilo personalizzato
    profile = "../data/deb.prt"
    use_profile = os.path.isfile(profile)

    # Intestazione
    print("== Avvio dell'audit system con Lynis ==")
    print(f"Data: {timestamp}")
    print(f"Auditor: {auditor}")
    print(f"Output: {output_filename}")
    print("----------------------------------------")

    # Costruzione del comando
    cmd = ["lynis", "audit", "system", "--quick", "--auditor", auditor]
    if use_profile:
        cmd.extend(["--profile", profile])

    try:
        # Esecuzione del comando con cattura output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Rimozione codici ANSI (colori terminale)
        clean_output = re.sub(r'\x1B\[[0-9;?]*[ -/]*[@-~]', '', result.stdout)

        # Salvataggio su file
        with open(output_filename1, "w") as f:
            f.write(clean_output)

        # Stato finale
        if result.returncode == 0:
            print("✅ Audit completato con successo.")
            print(f"📄 Report salvato in: {output_filename}")
        else:
            print("❌ Errore durante l'esecuzione di Lynis.")
            print(f"📄 Output salvato in: {output_filename}")
            raise subprocess.CalledProcessError(result.returncode, cmd)

    except FileNotFoundError:
        print(f"FileNotFound error{{FileNotFoundError}}")
    except Exception as e:
        print(f" Errore imprevisto: {e}")

if __name__ == "__main__":
#    scanLynis("Marius Berinde")
    print("PATH usato da Python:", os.environ["PATH"])
