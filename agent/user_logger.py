import logging
import os
import platform as pt;

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(utente)s] %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)

class UserLogger(logging.LoggerAdapter):

    sistema_operativo = pt.uname().system
    #user = os.popen('whoami').read() if sistema_operativo=='Linux' else os.getlogin( )
    user = os.system('whoami') if sistema_operativo=='Linux' else os.getlogin( )
    def process(self, msg, kwargs):
        return msg, {**kwargs, "extra": {"utente": self.user}}


if __name__ == "__main__":
    logger = UserLogger(logging.getLogger(__name__), {})
    logger.info("test logger")
