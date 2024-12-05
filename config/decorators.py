from filelock import FileLock, Timeout
import logging
import time
from functools import wraps
import random

# Configure logging
logging.basicConfig(filename='./tmp/cronjob.log', level=logging.INFO)

def single_instance(timeout=1, retry_interval=5, max_retries=30):
    """
    Decorator to ensure that only one instance of the decorated function runs at a time.
    Uses a file lock to manage concurrency with retry logic and fixed retry interval.
    """
    lock_file_path = './tmp/sim_restock.lock'

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Random sleep between 1 and 2 seconds before acquiring the lock
            sleep_time = random.uniform(1.0, 2.0)
            time.sleep(sleep_time)
            lock = FileLock(lock_file_path)
            retries = 0
            while retries < max_retries:
                try:
                    with lock.acquire(timeout=timeout):
                        return func(*args, **kwargs)
                except Timeout:
                    retries += 1
                    logging.info(f"Retrying ({retries}/{max_retries}) - Another instance is already running. Sleeping for {retry_interval} seconds.")
                    time.sleep(retry_interval)
                except Exception as e:
                    logging.error(f"Error while executing command: {e}")
                    break

            logging.error(f"Failed to acquire lock after {max_retries} retries.")

        return wrapper
    return decorator
