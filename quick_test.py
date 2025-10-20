"""Quick test of the enhanced export_pdf with debug output"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test by importing and calling the function
from tkinter import Tk, filedialog, messagebox

# Mock file dialog
def mock_save(*args, **kwargs):
    return "test_debug.pdf"

filedialog.asksaveasfilename = mock_save

# Mock message boxes
def mock_info(title, msg):
    print(f"[MSGBOX INFO] {title}: {msg}")

def mock_yesno(title, msg):
    print(f"[MSGBOX YESNO] {title}: {msg}")
    return False

messagebox.showinfo = mock_info
messagebox.askyesno = mock_yesno
messagebox.showerror = lambda t, m: print(f"[MSGBOX ERROR] {t}: {m}")

# Import after mocking
from check import SystemScannerGUI

print("\n" + "="*70)
print("QUICK TEST WITH DEBUG OUTPUT")
print("="*70 + "\n")

root = Tk()
root.withdraw()

# Check startup messages
app = SystemScannerGUI(root)

# Set scan results
app.scan_results = {
    'timestamp': '2025-10-19 12:00:00',
    'computer_name': 'TEST-PC',
    'username': 'TestUser',
    'os_name': 'Windows 11',
    'os_version': '10.0',
    'bios_version': 'BIOS',
    'system_type': 'x64',
    'vpn_apps': [{'name': 'VPN', 'path': 'C:\\vpn.exe'}],
    'chat_apps': [],
    'remote_apps': [],
    'kaspersky': False,
    'security_checks': {}
}

print("\n" + "-"*70)
print("Calling scan_complete()...")
print("-"*70 + "\n")

app.scan_complete()

print("\n" + "-"*70)
print("Calling export_pdf()...")
print("-"*70 + "\n")

app.export_pdf()

print("\n" + "="*70)
print("TEST COMPLETE - Check debug output above")
print("="*70)

root.destroy()
