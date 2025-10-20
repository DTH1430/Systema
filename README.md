# SystemScanner

A professional Windows system security scanner with a modern GUI interface. SystemScanner performs comprehensive security audits, network analysis, and generates detailed PDF reports.

## Features

### System Information
- Computer name and user information
- Windows OS version and edition detection
- BIOS version and release date
- System architecture (x64/x86)
- Real-time scan timestamp

### Security Analysis
- **VPN Detection**: Identifies VPN software (NordVPN, ExpressVPN, ProtonVPN, etc.)
- **Communication Apps**: Detects messaging applications (Telegram, Discord, Slack, etc.)
- **Remote Access Tools**: Scans for remote desktop and access software
- **Antivirus Detection**: Checks for installed security software including Kaspersky
- **Firewall Rules**: Analyzes Windows Firewall configuration
- **Network Security**: Monitors open ports and network interfaces

### Report Generation
- **Text Reports**: Plain text export (.txt)
- **CSV Reports**: Spreadsheet-compatible format
- **PDF Reports**: Professional PDF documents with charts and visualizations
- Color-coded security status indicators
- Comprehensive scan summaries with timestamps

### User Interface
- Modern, responsive GUI built with Tkinter
- Real-time scan progress updates
- Color-coded results (success/warning/danger)
- Easy-to-navigate sections
- One-click export functionality

## Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
```
tkinter (usually included with Python)
reportlab (for PDF export)
pillow (for PDF charts)
```

## Installation

### Option 1: Using the Pre-built Executable
1. Download the latest release from the releases page
2. Run `SystemScanner.exe`
3. Grant administrator privileges when prompted

### Option 2: Running from Source
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd SystemScanner
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv scanner_env
   scanner_env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install reportlab pillow
   ```

4. Run the application:
   ```bash
   python check.py
   ```

## Building the Executable

To build your own executable using PyInstaller:

1. Install PyInstaller and dependencies:
   ```bash
   pip install pyinstaller reportlab pillow
   ```

2. Run the build script:
   ```bash
   build.bat
   ```
   Or manually:
   ```bash
   pyinstaller SystemScanner.spec
   ```

3. The executable will be created in the `dist` folder

## Usage

1. **Launch the Application**
   - Double-click `SystemScanner.exe` or run `python check.py`
   - Accept UAC prompt to grant administrator privileges

2. **Run a Scan**
   - Click the "Start Scan" button
   - Wait for the scan to complete (usually 10-30 seconds)
   - Review results in the GUI

3. **Export Reports**
   - Click "Export TXT" for plain text format
   - Click "Export CSV" for spreadsheet format
   - Click "Export PDF" for professional reports (requires reportlab)

4. **Review Results**
   - Green indicators: No issues detected
   - Orange indicators: Items detected (informational)
   - Red indicators: Security concerns found

## Security Checks Performed

### Network Security
- Open network ports
- Listening services
- Port ranges (1-65535)
- Network interface configuration

### Software Detection
- VPN clients (10+ popular VPNs)
- Communication apps (Telegram, Discord, Teams, etc.)
- Remote access tools (TeamViewer, AnyDesk, etc.)
- Antivirus software

### Firewall Analysis
- Active firewall rules
- Inbound/outbound rule configurations
- Rule profiles and actions

### System Information
- Operating system details
- BIOS information
- System architecture
- User account information

## File Structure

```
SystemScanner/
├── check.py                 # Main GUI application
├── system_info.py          # System information collector
├── pdf_reporter.py         # PDF report generator
├── SystemScanner.spec      # PyInstaller build configuration
├── build.bat              # Build script for Windows
├── version_info.txt       # Version information for executable
├── app.manifest           # Windows manifest for UAC
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Antivirus False Positives

Some antivirus software may flag the executable as suspicious. This is a common false positive for PyInstaller-built applications. See [ANTIVIRUS_FIX_SUMMARY.md](ANTIVIRUS_FIX_SUMMARY.md) for details.

**To minimize false positives:**
- UPX compression is disabled
- Digital signing recommended (requires code signing certificate)
- Version information and manifest included
- Console mode enabled for transparency

## Troubleshooting

### PDF Export Not Working
If the PDF export button is disabled:
1. Ensure reportlab is installed: `pip install reportlab pillow`
2. Rebuild the executable if using the .exe version
3. Check console output for error messages

### Scan Hangs or Fails
- Ensure you have administrator privileges
- Check Windows Defender or antivirus isn't blocking the scan
- Verify network connectivity for network scans

### Permission Errors
- Run as Administrator
- Check UAC settings
- Verify firewall isn't blocking the application

## Development

### Running Tests
```bash
# Run test files (multiple test scripts available)
python test_full_workflow.py
python test_pdf_export.py
```

### Code Style
- PEP 8 compliant
- Type hints where applicable
- Comprehensive docstrings

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Wish I had one

## Acknowledgments

- Built with Python and Tkinter
- PDF generation powered by ReportLab
- Network scanning using Windows built-in tools

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation in the repository

## Changelog

See individual documentation files for detailed change history:
- [PDF_FIX_SUMMARY.md](PDF_FIX_SUMMARY.md)
- [ANTIVIRUS_FIX_SUMMARY.md](ANTIVIRUS_FIX_SUMMARY.md)
- [GITIGNORE_UPDATE.md](GITIGNORE_UPDATE.md)

## Author

You already know

---

**Note**: This tool is designed for legitimate security auditing purposes only. Use responsibly and in accordance with applicable laws and regulations.
