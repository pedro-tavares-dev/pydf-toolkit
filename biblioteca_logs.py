import logging
import sys
import os

# Códigos de cor ANSI para o terminal
RESET = "\033[0m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CINZA = "\033[90m"

class ColoredFormatter(logging.Formatter):
    """Formata os logs com cores baseadas no nível (INFO, ERROR, etc)"""
    
    FORMATO = "%(asctime)s | %(levelname)s | %(message)s"
    DATE_FMT = "%H:%M:%S"

    FORMATS = {
        logging.DEBUG: CINZA + FORMATO + RESET,
        logging.INFO: VERDE + FORMATO + RESET,
        logging.WARNING: AMARELO + FORMATO + RESET,
        logging.ERROR: VERMELHO + FORMATO + RESET,
        logging.CRITICAL: VERMELHO + "\033[1m" + FORMATO + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.DATE_FMT)
        return formatter.format(record)

def configurar_logger(nome_logger="PyDF"):
    """Configura e retorna um logger pronto para uso"""
    logger = logging.getLogger(nome_logger)
    logger.setLevel(logging.INFO)

    # Evita duplicidade de logs se chamar a função mais de uma vez
    if not logger.handlers:
        # Handler para o Console (Terminal)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        # Aplica o formatador colorido
        ch.setFormatter(ColoredFormatter())
        
        logger.addHandler(ch)
    
    return logger