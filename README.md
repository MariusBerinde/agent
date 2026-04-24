# 🐦‍⬛ Corvo — Agent

> Componente di acquisizione dati e auditing del sistema [Corvo](https://github.com/), sviluppato come progetto di tesi magistrale in collaborazione con **Sinelec S.p.A.**

---

## 📋 Descrizione

`corvo_agent` è il modulo daemon installato sugli host Linux da monitorare. Il suo compito è raccogliere informazioni sullo stato del sistema, gestire i servizi attivi, eseguire scansioni di sicurezza tramite **Lynis** e rendere disponibili i dati al backend centrale (`corvo_back`) tramite API REST.

> **Nota:** Questo repository contiene esclusivamente il codice dell'agent. Gli altri componenti del sistema si trovano nei repository [`corvo_back`](#) e [`corvo_front`](#).

---

## ✨ Funzionalità

- **Registrazione automatica** al backend all'avvio, con invio delle informazioni del nodo (IP, porta, nome, descrizione)
- **Server REST locale** che espone le API per ricevere comandi dal backend
- **Monitoraggio servizi di sistema** tramite `systemctl`
- **Integrazione Lynis** — avvio scansioni di sicurezza in background, gestione regole da escludere, esposizione dei report
- **Logging strutturato** con rotazione automatica dei file (max 10 MB)
- **Sessione single-user** con autenticazione richiesta su tutte le route (eccetto `/ping` e `/set_user`)
- **Resilienza ai riavvii** — le regole di auditing attive vengono persistite su file e ricaricate all'avvio

---

## 🏗️ Architettura interna

```
corvo_agent/
├── main.py                  # Entrypoint: avvio e inizializzazione
├── data/
│   ├── config.json          # Configurazione dell'agent (endpoint backend, nome, porta...)
│   ├── deb.prt              # Profilo Lynis (regole da escludere)
│   └── application.log      # Log dell'agent (generato a runtime)
└── agent/
    ├── lynis_audit.py        # Generazione ed esposizione dei report Lynis
    ├── lynis.py              # Gestione delle regole da disabilitare nelle scansioni
    ├── rules.py              # Gestione delle regole di auditing attive
    └── user_logger.py        # Sistema di logging centralizzato (UserLogger)
```

### Layer logici

| Layer | Classe/Modulo | Responsabilità |
|---|---|---|
| Comunicazione e controllo | `AgentController` | Server HTTP locale, dispatch delle richieste REST |
| Auditing e persistenza | `SystemRules`, `Rule` | Gestione e persistenza delle regole di sicurezza |
| Integrazione tooling | `Lynis` | Esecuzione asincrona delle scansioni, gestione profili |
| Diagnostica | `UserLogger` | Logging strutturato, audit trail locale |

---

## 🔌 API REST esposte

Tutte le route (eccetto `/ping` e `/set_user`) richiedono che l'utente sia autenticato tramite `/set_user`.

| Route | Descrizione |
|---|---|
| `GET /ping` | Verifica disponibilità dell'agent |
| `POST /set_user` | Imposta l'utente attivo per la sessione |
| `GET /get_status` | Restituisce lo stato dell'agent e dei servizi monitorati |
| `GET /get_logs` | Ritorna i log locali dell'agent |
| `GET /get_lynis` | Restituisce le regole attualmente escluse dalla scansione |
| `GET /get_lynis_report` | Restituisce il report dell'ultima scansione Lynis (UTF-8, fallback Latin-1) |
| `POST /add_rules` | Aggiorna la lista delle regole da saltare o effettua un reset completo |
| `POST /start_lynis_scan` | Avvia una scansione Lynis in thread separato |

---

## ⚙️ Configurazione

L'agent viene configurato tramite il file `data/config.json`. Esempio:

```json
{
  "name": "nome-del-server",
  "descr": "Descrizione opzionale dell'host",
  "port": 8080,
  "backend_url": "http://<IP_BACKEND>:<PORTA>/api/agent/connect"
}
```

| Campo | Descrizione |
|---|---|
| `name` | Nome identificativo del nodo |
| `descr` | Descrizione testuale dell'host |
| `port` | Porta su cui l'agent espone il proprio server REST |
| `backend_url` | URL completo dell'endpoint di registrazione su `corvo_back` |

---

## 🚀 Avvio locale

### Prerequisiti

- Python 3.8+
- [Lynis](https://cisofy.com/lynis/) installato sull'host
- `corvo_back` raggiungibile in rete

> L'agent utilizza **esclusivamente la Standard Library di Python**: non è necessario installare dipendenze esterne né usare `pip`.

### Avvio

```bash
# 1. Clona il repository
git clone https://github.com/<tuo-utente>/corvo_agent.git
cd corvo_agent

# 2. Configura l'agent
cp data/config.json.example data/config.json
# Modifica data/config.json con i parametri del tuo ambiente

# 3. Avvia l'agent
python3 main.py
```

All'avvio, l'agent:
1. Legge la configurazione da `data/config.json`
2. Invia una richiesta POST al backend per registrarsi
3. Rimane in attesa delle richieste del backend sul proprio server REST locale

In caso di errore nella lettura del file di configurazione o di mancata risposta dal backend (HTTP 200), l'agent si ferma e registra l'errore nel log.

---

## 🔒 Note di sicurezza

- L'agent è progettato per operare in **reti aziendali isolate (intranet)**; non deve essere esposto su reti pubbliche
- La comunicazione avviene in **HTTP non cifrato**: la protezione è delegata ai controlli fisici e logici dell'infrastruttura di rete
- Le scansioni Lynis vengono eseguite **senza privilegi di root** ove possibile, nel rispetto del principio del minimo privilegio
- I log vengono salvati in `./data/application.log` con **rotazione automatica** al raggiungimento dei 10 MB

### Compatibilità verificata

| Sistema operativo | Note |
|---|---|
| Debian 11 | Ambiente di produzione — operatività con privilegi limitati |
| Ubuntu 24.04 | Ambiente di sviluppo — supporto elevazione privilegi per controlli su risorse di sistema protette |

---

## 📄 Contesto del progetto

`corvo_agent` fa parte del sistema **Corvo**, sviluppato come progetto di tesi magistrale presso **Sinelec S.p.A.** Il sistema completo comprende anche il backend Java Spring Boot (`corvo_back`) e il frontend Angular (`corvo_front`).

---

## 📜 Licenza

Tutti i diritti riservati. Progetto sviluppato nell'ambito di un tirocinio magistrale presso Sinelec S.p.A.
