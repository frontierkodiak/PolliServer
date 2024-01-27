import logging
import os
import sys
from datetime import datetime
from threading import Timer

class LoggerSingleton:
    _instance = None

    @classmethod
    def get_logger(cls, log_dir='logs', run_name=None, log_buffer=5):
        if cls._instance is None:
            cls._instance = Logger(log_dir, run_name, log_buffer)
        return cls._instance
    
class StreamWriter:
    def __init__(self, buffer, log_file):
        if log_file is None:
            raise ValueError("Logger.StreamWriter: stdout/stderr log_file must be provided")
        self.buffer = buffer
        self.log_file = log_file

    def write(self, message):
        self.buffer.append(message)

    def flush(self):
        with open(self.log_file, 'a') as file:
            file.writelines(self.buffer)
        self.buffer.clear()


class Logger:
    def __init__(self, log_dir='logs', run_name=None, log_buffer=5):
        os.makedirs(log_dir, exist_ok=True)
        
        run_name = run_name + datetime.now().strftime("_%Y-%m-%d_%H-%M") if run_name else datetime.now().strftime("%Y-%m-%d_%H-%M")

        if run_name is None:
            run_name = datetime.now().strftime("%Y-%m-%d_%H-%M")
            if os.path.isfile(os.path.join(log_dir, f'{run_name}.log')):
                existing_files = [f for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]
                matching_files = [f for f in existing_files if f.startswith(run_name)]
                run_name = f'{run_name}_{len(matching_files)}'

        self.log_file = os.path.join(log_dir, f'{run_name}.log')
        self.profile_log_file = os.path.join(log_dir, f'{run_name}_profile.log')
        self.stdout_log_file = os.path.join(log_dir, f'{run_name}_stdout.log')
        self.stderr_log_file = os.path.join(log_dir, f'{run_name}_stderr.log')
        self.buffered_logs = []
        self.profile_buffered_logs = []
        self.stdout_buffered_logs = []
        self.stderr_buffered_logs = []
        self.buffer_limit = log_buffer  # Adjust as needed

        self.logger = logging.getLogger(run_name)
        self.logger.setLevel(logging.INFO)
        
        self.stdout_writer = StreamWriter(self.stdout_buffered_logs, self.stdout_log_file)
        self.stderr_writer = StreamWriter(self.stderr_buffered_logs, self.stderr_log_file)

        file_handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        self.profile_logger = logging.getLogger(f"{run_name}_profile")
        self.profile_logger.setLevel(logging.INFO)

        profile_file_handler = logging.FileHandler(self.profile_log_file)
        profile_file_handler.setFormatter(formatter)

        self.profile_logger.addHandler(profile_file_handler)
        
        self.server_log_file = os.path.join(log_dir, f'{run_name}_server.log')  # New attribute for server log file
        self.server_buffered_logs = []  # New buffer for server logs

        self.server_logger = logging.getLogger(f"{run_name}_server")  # New logger instance for server
        self.server_logger.setLevel(logging.INFO)

        server_file_handler = logging.FileHandler(self.server_log_file)
        server_file_handler.setFormatter(formatter)

        self.server_logger.addHandler(server_file_handler)

        self.flush_timer = Timer(5, self.flush_logs)
        self.flush_timer.start()
        
    def redirect_stdout(self):
        sys.stdout = self.stdout_writer

    def redirect_stderr(self):
        sys.stderr = self.stderr_writer

    def info(self, message):
        self.buffered_logs.append(f'{datetime.now()} : INFO : {message}\n')
        if len(self.buffered_logs) >= self.buffer_limit:
            self.flush_logs()

    def warning(self, message):
        self.buffered_logs.append(f'{datetime.now()} : WARNING : {message}\n')
        if len(self.buffered_logs) >= self.buffer_limit:
            self.flush_logs()

    def error(self, message):
        self.buffered_logs.append(f'{datetime.now()} : ERROR : {message}\n')
        self.flush_logs()  # You might want to flush immediately on errors

    def debug(self, message):
        self.buffered_logs.append(f'{datetime.now()} : DEBUG : {message}\n')
        if len(self.buffered_logs) >= self.buffer_limit:
            self.flush_logs()

    def profile(self, message):
        self.profile_buffered_logs.append(f'{datetime.now()} : PROFILE : {message}\n')
        if len(self.profile_buffered_logs) >= self.buffer_limit:
            self.flush_profile_logs()
            
    def server_info(self, message):
        self.server_buffered_logs.append(f'{datetime.now()} : INFO : {message}\n')
        if len(self.server_buffered_logs) >= self.buffer_limit:
            self.flush_server_logs()

    def server_warning(self, message):
        self.server_buffered_logs.append(f'{datetime.now()} : WARNING : {message}\n')
        if len(self.server_buffered_logs) >= self.buffer_limit:
            self.flush_server_logs()

    def server_error(self, message):
        self.server_buffered_logs.append(f'{datetime.now()} : ERROR : {message}\n')
        self.flush_server_logs()  # Flush immediately on server errors

    def server_debug(self, message):
        self.server_buffered_logs.append(f'{datetime.now()} : DEBUG : {message}\n')
        if len(self.server_buffered_logs) >= self.buffer_limit:
            self.flush_server_logs()

    def flush_logs(self):
        with open(self.log_file, 'a') as log_file:
            log_file.writelines(self.buffered_logs)
        self.buffered_logs = []
        
        with open(self.stdout_log_file, 'a') as stdout_log_file:
            stdout_log_file.writelines(self.stdout_buffered_logs)
        self.stdout_buffered_logs = []

        with open(self.stderr_log_file, 'a') as stderr_log_file:
            stderr_log_file.writelines(self.stderr_buffered_logs)
        self.stderr_buffered_logs = []
        
        self.flush_timer = Timer(5, self.flush_logs)
        self.flush_timer.start()
        self.flush_profile_logs()

    def flush_profile_logs(self):
        with open(self.profile_log_file, 'a') as profile_log_file:
            profile_log_file.writelines(self.profile_buffered_logs)
        self.profile_buffered_logs = []

    def flush_server_logs(self):
        with open(self.server_log_file, 'a') as server_log_file:
            server_log_file.writelines(self.server_buffered_logs)
        self.server_buffered_logs = []
        
    def close_logs(self):
        # Called on program exit
        self.flush_logs()
        self.flush_profile_logs()
        self.flush_server_logs()
        self.logger.removeHandler(self.logger.handlers[0])
        if self.profile_logger is not None:
            self.profile_logger.removeHandler(self.profile_logger.handlers[0])
        if self.server_logger is not None:
            self.server_logger.removeHandler(self.server_logger.handlers[0])
        self.logger = None
        self.profile_logger = None
        self.server_logger = None