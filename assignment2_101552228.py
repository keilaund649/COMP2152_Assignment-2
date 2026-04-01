"""
Author: <KEILAUND SAUNDERS>
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""


import socket
import threading
import sqlite3
import os
import platform
import datetime

print(f"Python Version: {platform.python_version()}")
print(f"Operating System: {os.name}")


#This dictionary stores common port numbers to their associated service names

common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}
class NetworkTool:
    def __init__(self, target):
        self.__target = target
        

# Q3: What is the benefit of using @property and @target.setter?
# TODO: Your 2-4 sentence answer here... (Part 2, Q3)

# Using @property and @target.setter provides controlled access to the private
# __target attribute instead of exposing it directly. The setter can validate

    @property
    def target(self):
        return self.__target
 
    @target.setter
    def target(self, value):
        if value:
            self.__target = value
 
    def __del__(self):
        print("NetworkTool instance destroyed")

# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)

# PortScanner inherits from NetworkTool using class PortScanner(NetworkTool),
# which means it automatically gets the __init__ constructor, the target

class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()
 
    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()
 
    def scan_port(self, port):
        # Q4: What would happen without try-except here?

        # A failed connection would raise an unhandled exception and crash the program.
        # try-except catches socket errors so the scan keeps running on other ports.
        # The finally block ensures the socket always closes, even if an error occurs.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            status = "Open" if result == 0 else "Closed"
            service = common_ports.get(port, "Unknown")
            with self.lock:
                self.scan_results.append((port, status, service))
        except socket.error as e:
            print(f"Socket error on port {port}: {e}")
        finally:
            sock.close()
 
    def get_open_ports(self):
        return [(port, status, service)
                for port, status, service in self.scan_results
                if status == "Open"]
#
# - get_open_ports(self):
#     - Use list comprehension to return only "Open" results
#
#     Q2: Why do we use threading instead of scanning one port at a time?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q2)

 # Each port has a 1-second timeout, so scanning 1024 ports sequentially takes 17+ minutes.
    # Threading runs all port scans at the same time, finishing in about 1 second total.
    # Without threads, the program would be too slow to be useful.
#
    def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

# TODO: Create save_results(target, results) function (Step vii)

def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            port INTEGER,
            status TEXT,
            service TEXT,
            scan_date TEXT
        )""")
        scan_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for port, status, service in results:
            cursor.execute(
                "INSERT INTO scans (target, port, status, service, scan_date) VALUES (?, ?, ?, ?, ?)",
                (target, port, status, service, scan_date)
            )
        conn.commit()
        conn.close()
        print("Results saved to database.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# TODO: Create load_past_scans() function (Step viii)

def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT target, port, status, service, scan_date FROM scans ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        if rows:
            print("\n--- Past Scan History ---")
            for row in rows:
                print(f"[{row[4]}] {row[0]} - Port {row[1]} ({row[3]}): {row[2]}")
        else:
            print("No past scans found.")
    except sqlite3.Error:
        print("No past scans found.")

# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    pass
    try:
        target_ip = input("Enter target IP address (press Enter for 127.0.0.1): ").strip()
        if not target_ip:
            target_ip = "127.0.0.1"
 
        start_port = int(input("Enter start port (1-1024): "))
        end_port = int(input("Enter end port (1-1024): "))
 
        if not (1 <= start_port <= 1024) or not (1 <= end_port <= 1024) or end_port < start_port:
            print("Port must be between 1 and 1024.")
        else:
            scanner = PortScanner(target_ip)
            print(f"Scanning {target_ip} from port {start_port} to {end_port}...")
            scanner.scan_range(start_port, end_port)
 
            open_ports = scanner.get_open_ports()
            print(f"\n--- Scan Results: {target_ip} ---")
            for port, status, service in open_ports:
                print(f"Port {port} ({service}): {status}")
            print("------")
            print(f"Total open ports found: {len(open_ports)}")
 
            save_results(target_ip, scanner.scan_results)
 
            history = input("Would you like to see past scan history? (yes/no): ").strip().lower()
            if history == "yes":
                load_past_scans()
 
    except ValueError:
        print("Invalid input. Please enter a valid integer.")

# Q5: New Feature Proposal
# I would add a results exporter that writes all open ports to a .txt report file.
# It uses a list comprehension to filter only open ports and format each line as a string.
# This lets users save and share scan results without needing to access the database.
# Diagram: See diagram_101552228.png in the repository root

