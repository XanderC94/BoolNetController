import logging, os, sys
from pathlib import Path
from singleton_decorator import singleton
from bncontroller.file.utils import iso8106

class Logger(object):

    def __init__(self, name, 
                output_stream = sys.stdout,
                log_level=logging.INFO, 
                message_format='%(message)s', 
                buffer_length=0):

        self._logger = logging.getLogger(name)
        self._logger.setLevel(log_level)

        self._formatter = logging.Formatter(message_format)
        self._sh = logging.StreamHandler(output_stream)
        self._sh.setFormatter(self._formatter)
        
        self._logger.addHandler(self._sh)
        self._buffer_length = buffer_length
        self._log_buffer = []
    
    def __call__(self, *items):
        self.info(*items)

    def info(self, *items):
        if not self._logger.disabled:
            msg = ' '.join(map(str, items))
            self._log_buffer.append(msg)
            if len(self._log_buffer) > self._buffer_length:
                self.__log()        

    def __log(self):
        m = '\n'.join([ f'{s}' for s in self._log_buffer])
        self._logger.info(m)
        self._log_buffer.clear()

    def flush(self):
        if not self._logger.disabled:
            self.__log()

    def suppress(self, boolean:bool):
        self._logger.disabled = boolean
    
    @property
    def buffer_length(self):
        return self._buffer_length

    def set_file_logger(self, path):
        self._logger.removeHandler(self._sh)

        fh = logging.FileHandler(path, mode='w', encoding="UTF-8")
        fh.setLevel(self._logger.level)
        fh.setFormatter(self._formatter)
        self._logger.addHandler(fh)

class FileLogger(Logger):

    def __init__(self, name, 
                path = Path(f"./{iso8106()}.log"),
                log_level=logging.INFO, 
                message_format='%(message)s', 
                buffer_length = 50):

        super().__init__(
            name, 
            log_level=log_level,
            output_stream=None,
            message_format=message_format, 
            buffer_length=buffer_length
        )

        super().set_file_logger(path)
        
class LoggerFactory(object):
    
    @staticmethod
    def filelogger(path, buffer=2):
        return FileLogger('FileLogger', path=path, buffer_length=buffer)
    
    @staticmethod
    def streamlogger():
        return Logger('StreamLogger')

@singleton
class StaticLogger(object):
    instance = LoggerFactory.streamlogger()

    def info(self, *items):
        self.instance.info(*items)

    def flush(self):
        self.instance.flush()

staticlogger = StaticLogger()