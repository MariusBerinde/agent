import logging
import os
import platform as pt
from logging.handlers import RotatingFileHandler

# Configura logging per console e file
def setup_logger(log_file_path='app.log', max_size_mb=10, backup_count=3):
    # Crea il logger principale
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Formattazione dei log
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(utente)s] %(message)s', 
                                 datefmt='%d-%m-%Y %H:%M:%S')
    
    # Handler per console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Handler per file con rotazione
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=max_size_mb * 1024 * 1024,  # Converti MB in bytes
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    
    # Aggiungi handlers al logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

class UserLogger(logging.LoggerAdapter):
    
    def __init__(self, logger,username, extra):
        super().__init__(logger, extra)
        self.user = username

    def process(self, msg, kwargs):
        kwargs_copy = kwargs.copy()
        extra = kwargs_copy.get('extra', {})

        extra['utente'] = self.user
        kwargs_copy['extra'] = extra
        return msg, kwargs_copy

if __name__ == "__main__":
    # Configurazione del logger
    main_logger = setup_logger(log_file_path='application.log')
    
    # Creazione dell'adapter
    logger = UserLogger(main_logger,"Giggino", {})
    
    # Test di logging
    logger.info("test logger")
