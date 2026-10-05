import subprocess
import sys
import time

def main():
    print("=========================================================")
    print("      INITIALIZING SOS DISPATCH SYSTEM PROTOCOL...       ")
    print("=========================================================")
    
    processes = []
    
    try:
        # 1. Start the Flask Web Server
        print("[1/3] Booting Central Command Server (app.py)...")
        p1 = subprocess.Popen([sys.executable, "app.py"])
        processes.append(p1)
        time.sleep(2) # Give the server a moment to bind to the port
        
        # 2. Start the Cleanup Worker
        print("[2/3] Booting Auto-Cleanup Worker (cleanup_reports.py)...")
        p2 = subprocess.Popen([sys.executable, "-u", "cleanup_reports.py"])
        processes.append(p2)
        
        # 3. Start the Simulation Engine
        print("[3/3] Booting Live Simulation Engine (simulator.py)...")
        p3 = subprocess.Popen([sys.executable, "-u", "simulator.py"])
        processes.append(p3)
        
        print("\n=========================================================")
        print("   ALL SYSTEMS ONLINE. READY FOR DEMONSTRATION.          ")
        print("   Access the Web Interface at: http://127.0.0.1:5000    ")
        print("   (Press Ctrl+C to shut down all systems safely)        ")
        print("=========================================================\n")
        
        # Wait indefinitely to keep the main thread alive
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\n[!] Shutting down all systems gracefully...")
        for p in processes:
            p.terminate()
        print("[!] All systems offline. Goodbye.")
        sys.exit(0)

if __name__ == "__main__":
    main()
