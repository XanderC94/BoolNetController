import logging, os
from pathlib import Path
from bncontroller.file.utils import iso8106

class FileLogger:

    def __init__(self, name:str, path = Path(f"{os.getcwd()}/{iso8106()}.log"), buffer_length = 50):

        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(message)s')
        fh = logging.FileHandler(path, mode='w', encoding="UTF-8")
        fh.setLevel(logging.ERROR)
        fh.setFormatter(formatter)
        self.__logger.addHandler(fh)

        self.__buffer_length = buffer_length
        
        self.__log_buffer = []

    def info(self, message: str):
        if not self.__logger.disabled:
            self.__log_buffer.append(message)
            if len(self.__log_buffer) > self.__buffer_length:
                self.__log()        

    def __log(self):
        m = '\n'.join([ f'{s}' for s in self.__log_buffer])
        self.__logger.info(m)
        self.__log_buffer.clear()

    def flush(self):
        if not self.__logger.disabled:
            self.__log()

    def suppress(self, boolean:bool):
        self.__logger.disabled = boolean

    @property
    def logger(self):
        return logger
    
    @property
    def buffer_length(self):
        return self.__buffer_length

    @buffer_length.setter
    def buffer_length(self, new_length):
        self.__buffer_length = new_length