import os
import sys
import threading
import time
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# 1. 🏛️ Hub ALIGNMENT
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UNSCCDC.settings')

# 2. Hub Hub Hub START THE Hub Hub Hub Hub ENGINE
application = get_wsgi_application()
print("--- 🏛️ NATIONAL Hub ENGINE: ONLINE ---")

# 3. 🚀 THE Hub Hub Hub Hub Hub Hub Hub REAL-TIME Hub Hub Hub Hub Hub Hub Hub WORKER
def start_sovereign_worker():
    """
    Independent thread that monitors National Treasury Settlments 24/7.
    """
    def run():
        # Wait for database to warm up
        time.sleep(10)
        print("--- 💰 TREASURY Hub Hub Hub Hub Hub Hub WORKER: Hub Hub Hub Hub Hub Hub ACTIVE ---")
        
        while True:
            try:
                from schoolpay_worker import fetch_all_school_transactions
                fetch_all_school_transactions()
            except Exception as e:
                print(f"--- ⚠️ WORKER Hub Hub Hub Hub Hub Hub ERROR: {e} ---")
            
            # Real-time enough for polling: Check every 30 seconds
            time.sleep(30)

    # Start the worker in the background
    worker_thread = threading.Thread(target=run, daemon=True)
    worker_thread.start()

# Initialize the worker
start_sovereign_worker()