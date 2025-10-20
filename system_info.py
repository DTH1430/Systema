#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows System Information Script
Displays system information in a specific format
"""

import os
import sys
import platform
import subprocess
import datetime
import getpass

def safe_subprocess_run(cmd, timeout=10):
    """Run subprocess safely with timeout"""
    try:
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True,
                timeout=timeout,
                startupinfo=startupinfo
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True,
                timeout=timeout
            )
        return result
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None

def map_edition_sku_to_friendly_name(sku_name):
    """Map Windows internal SKU names to user-friendly edition names"""
    if not sku_name:
        return ""

    sku_lower = sku_name.lower()

    # Windows SKU to Edition mapping
    sku_mappings = {
        # Windows 11/10 Home variants
        'coresinglelanguage': 'Home',
        'core': 'Home',
        'corecountryspecific': 'Home',
        'coren': 'Home N',
        'home': 'Home',
        'homesinglelan': 'Home',

        # Windows 11/10 Pro variants
        'professional': 'Pro',
        'pro': 'Pro',
        'professionaln': 'Pro N',
        'pron': 'Pro N',
        'professionalworkstation': 'Pro for Workstations',
        'professionalworkstationn': 'Pro for Workstations N',
        'proworkstation': 'Pro for Workstations',

        # Windows 11/10 Enterprise variants
        'enterprise': 'Enterprise',
        'enterprisen': 'Enterprise N',
        'enterpriseg': 'Enterprise G',
        'enterprisegn': 'Enterprise G N',
        'enterprises': 'Enterprise S',
        'enterprisesn': 'Enterprise S N',
        'enterpriseltsc': 'Enterprise LTSC',
        'enterpriseltsbn': 'Enterprise LTSB N',

        # Windows 11/10 Education variants
        'education': 'Education',
        'educationn': 'Education N',
        'professionalstudent': 'Education',
        'professionalstudentn': 'Education N',

        # Other variants
        'serverrdsh': 'Enterprise for Virtual Desktops',
        'iotuap': 'IoT Core',
        'ppipro': 'Team',
        'embedded': 'Embedded',
        'mobile': 'Mobile',
        'mobilenterprise': 'Mobile Enterprise'
    }

    # Direct mapping check
    if sku_lower in sku_mappings:
        return sku_mappings[sku_lower]

    # Partial matching for complex names
    for sku_key, friendly_name in sku_mappings.items():
        if sku_key in sku_lower:
            return friendly_name

    # Check if the input string contains recognizable edition names
    if 'coresinglelanguage' in sku_lower or 'single language' in sku_lower:
        return 'Home'
    elif 'professional' in sku_lower or 'pro' in sku_lower:
        return 'Pro'
    elif 'enterprise' in sku_lower:
        return 'Enterprise'
    elif 'education' in sku_lower:
        return 'Education'
    elif 'home' in sku_lower or 'core' in sku_lower:
        return 'Home'

    return ""

def get_windows_edition():
    """Get Windows edition (Home, Pro, Enterprise, etc.)"""
    edition = ""

    # Method 1: Registry ProductName with SKU mapping
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")

        # Try to get EditionID first (more reliable)
        try:
            edition_id, _ = winreg.QueryValueEx(key, "EditionID")
            if edition_id:
                edition = map_edition_sku_to_friendly_name(str(edition_id))
                if edition:
                    winreg.CloseKey(key)
                    return edition
        except:
            pass

        # Fallback to ProductName
        try:
            product_name, _ = winreg.QueryValueEx(key, "ProductName")
            if product_name:
                product_name_str = str(product_name)
                # Check for internal SKU names first
                edition = map_edition_sku_to_friendly_name(product_name_str)
                if not edition:
                    # Extract edition from ProductName (e.g., "Windows 11 Pro" -> "Pro")
                    product_parts = product_name_str.split()
                    for part in reversed(product_parts):
                        if part.lower() in ['home', 'pro', 'enterprise', 'education', 'professional']:
                            edition = part.capitalize()
                            break
        except:
            pass
        winreg.CloseKey(key)
    except:
        pass

    # Method 2: PowerShell Get-WindowsEdition (Windows 10/11)
    if not edition:
        try:
            ps_cmd = 'powershell -Command "Get-WindowsEdition -Online | Select-Object Edition | ConvertTo-Csv -NoTypeInformation"'
            result = safe_subprocess_run(ps_cmd, timeout=10)
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    edition_line = lines[1].strip().strip('"')
                    if edition_line and edition_line != "Edition":
                        raw_edition = edition_line.replace('Edition', '').strip()
                        edition = map_edition_sku_to_friendly_name(raw_edition)
                        if not edition:
                            edition = raw_edition
        except:
            pass

    # Method 3: WMIC OS Caption
    if not edition:
        try:
            result = safe_subprocess_run(['wmic', 'os', 'get', 'caption', '/value'], timeout=10)
            if result and result.stdout:
                for line in result.stdout.split('\n'):
                    if line.startswith('Caption='):
                        caption = line.split('=', 1)[1].strip()
                        # Check for internal SKU names first
                        edition = map_edition_sku_to_friendly_name(caption)
                        if not edition:
                            # Extract edition from caption
                            caption_lower = caption.lower()
                            if 'home' in caption_lower:
                                edition = 'Home'
                            elif 'pro' in caption_lower or 'professional' in caption_lower:
                                edition = 'Pro'
                            elif 'enterprise' in caption_lower:
                                edition = 'Enterprise'
                            elif 'education' in caption_lower:
                                edition = 'Education'
                        break
        except:
            pass

    return edition

def get_windows_version():
    """Get Windows OS name and version using multiple methods"""
    os_name = "Unknown"
    os_version = "Unknown"

    try:
        # Method 1: Use sys.getwindowsversion() if available
        if hasattr(sys, 'getwindowsversion'):
            win_ver = sys.getwindowsversion()
            major, minor, build = win_ver.major, win_ver.minor, win_ver.build

            # Map version numbers to Windows names
            if major == 10:
                if build >= 22000:
                    base_name = "Microsoft Windows 11"
                else:
                    base_name = "Microsoft Windows 10"
                os_version = f"{major}.{minor}.{build}"
            elif major == 6:
                if minor == 3:
                    base_name = "Microsoft Windows 8.1"
                elif minor == 2:
                    base_name = "Microsoft Windows 8"
                elif minor == 1:
                    base_name = "Microsoft Windows 7"
                elif minor == 0:
                    base_name = "Microsoft Windows Vista"
                else:
                    base_name = f"Microsoft Windows {major}.{minor}"
                os_version = f"{major}.{minor}.{build}"
            else:
                base_name = f"Microsoft Windows {major}.{minor}"
                os_version = f"{major}.{minor}.{build}"

            # Get Windows edition and append to base name
            if major >= 6:  # Vista and later support editions
                edition = get_windows_edition()
                if edition:
                    os_name = f"{base_name} {edition}"
                else:
                    os_name = base_name
            else:
                os_name = base_name
    except:
        pass

    # Method 2: Registry method for detailed info
    if os_name == "Unknown":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            try:
                product_name, _ = winreg.QueryValueEx(key, "ProductName")
                if product_name:
                    os_name = str(product_name)
            except:
                pass

            try:
                current_version, _ = winreg.QueryValueEx(key, "CurrentVersion")
                build_number, _ = winreg.QueryValueEx(key, "CurrentBuildNumber")
                if current_version and build_number:
                    os_version = f"{current_version}.{build_number}"
            except:
                pass

            winreg.CloseKey(key)
        except:
            pass

    # Method 3: Use platform module as fallback
    if os_name == "Unknown":
        try:
            os_name = platform.system()
            if os_name == "Windows":
                release = platform.release()
                version = platform.version()
                os_name = f"Microsoft Windows {release}"
                os_version = version
        except:
            pass

    # Method 4: Try systeminfo command
    if os_name == "Unknown" or os_version == "Unknown":
        try:
            result = safe_subprocess_run(['systeminfo'], timeout=15)
            if result and result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'OS Name:' in line and os_name == "Unknown":
                        os_name = line.split(':', 1)[1].strip()
                    elif 'OS Version:' in line and os_version == "Unknown":
                        os_version = line.split(':', 1)[1].strip()
                        break
        except:
            pass

    return os_name, os_version

def get_bios_info():
    """Get BIOS version and release date using multiple methods"""
    bios_version = "Unknown"

    # Method 1: PowerShell Get-WmiObject Win32_BIOS
    try:
        ps_cmd = 'powershell -Command "Get-WmiObject -Class Win32_BIOS | Select-Object SMBIOSBIOSVersion, ReleaseDate | ConvertTo-Csv -NoTypeInformation"'
        result = safe_subprocess_run(ps_cmd, timeout=15)
        if result and result.stdout:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:  # Header + data line
                data_line = lines[1].strip('"')
                parts = [p.strip('"') for p in data_line.split('","')]
                if len(parts) >= 2:
                    version = parts[0]
                    release_date = parts[1]

                    # Parse PowerShell date format
                    if version and version != '':
                        if release_date and release_date != '' and len(release_date) >= 8:
                            try:
                                year = release_date[:4]
                                month = release_date[4:6]
                                day = release_date[6:8]
                                formatted_date = f"{day}/{month}/{year}"
                                bios_version = f"{version} (Release Date: {formatted_date})"
                            except:
                                bios_version = version
                        else:
                            bios_version = version
    except:
        pass

    # Method 2: PowerShell Get-CimInstance Win32_BIOS (newer method)
    if bios_version == "Unknown":
        try:
            ps_cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_BIOS | Select-Object SMBIOSBIOSVersion, ReleaseDate | ConvertTo-Csv -NoTypeInformation"'
            result = safe_subprocess_run(ps_cmd, timeout=15)
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    data_line = lines[1].strip('"')
                    parts = [p.strip('"') for p in data_line.split('","')]
                    if len(parts) >= 1 and parts[0]:
                        bios_version = parts[0]
        except:
            pass

    # Method 3: Registry method
    if bios_version == "Unknown":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS")
            try:
                version, _ = winreg.QueryValueEx(key, "BIOSVersion")
                if version:
                    bios_version = str(version)
            except:
                try:
                    version, _ = winreg.QueryValueEx(key, "SystemBiosVersion")
                    if version:
                        bios_version = str(version)
                except:
                    pass
            winreg.CloseKey(key)
        except:
            pass

    # Method 4: WMIC with different timeout and retry
    if bios_version == "Unknown":
        try:
            result = safe_subprocess_run(['wmic', 'bios', 'get', 'smbiosbiosversion,releasedate', '/format:list'], timeout=15)
            if result and result.stdout:
                lines = result.stdout.split('\n')
                version = None
                release_date = None

                for line in lines:
                    line = line.strip()
                    if line.startswith('SMBIOSBIOSVersion=') and '=' in line:
                        version_part = line.split('=', 1)[1].strip()
                        if version_part:
                            version = version_part
                    elif line.startswith('ReleaseDate=') and '=' in line:
                        date_part = line.split('=', 1)[1].strip()
                        if date_part and len(date_part) >= 8:
                            try:
                                year = date_part[:4]
                                month = date_part[4:6]
                                day = date_part[6:8]
                                release_date = f"{day}/{month}/{year}"
                            except:
                                release_date = date_part[:8]

                if version:
                    if release_date:
                        bios_version = f"{version} (Release Date: {release_date})"
                    else:
                        bios_version = version
        except:
            pass

    # Method 5: Alternative WMIC formats
    if bios_version == "Unknown":
        wmic_commands = [
            ['wmic', 'bios', 'get', 'version', '/value'],
            ['wmic', 'bios', 'get', 'smbiosbiosversion'],
            ['wmic', 'bios', 'get', 'name,version']
        ]

        for cmd in wmic_commands:
            try:
                result = safe_subprocess_run(cmd, timeout=10)
                if result and result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        line = line.strip()
                        if 'Version=' in line and '=' in line:
                            version_part = line.split('=', 1)[1].strip()
                            if version_part:
                                bios_version = version_part
                                break
                        elif line and line not in ['SMBIOSBIOSVersion', 'Version', 'Name']:
                            if len(line) > 3:  # Avoid empty or very short lines
                                bios_version = line
                                break
                    if bios_version != "Unknown":
                        break
            except:
                continue

    return bios_version

def get_system_type():
    """Get system architecture (x64 or x86)"""
    try:
        # Method 1: Check PROCESSOR_ARCHITECTURE environment variable
        arch = os.environ.get('PROCESSOR_ARCHITECTURE', '').upper()
        if arch == 'AMD64':
            return "x64-based PC"
        elif arch == 'X86':
            return "x86-based PC"

        # Method 2: Use platform.machine()
        machine = platform.machine().upper()
        if machine in ['AMD64', 'X86_64']:
            return "x64-based PC"
        elif machine in ['I386', 'I686', 'X86']:
            return "x86-based PC"

        # Method 3: Check if running on 64-bit Python
        import struct
        bits = struct.calcsize("P") * 8
        if bits == 64:
            return "x64-based PC"
        else:
            return "x86-based PC"
    except:
        return "Unknown"

def display_system_info():
    """Display system information in the required format"""

    # Get system information
    computer_name = os.environ.get('COMPUTERNAME', 'Unknown')
    username = getpass.getuser() or os.environ.get('USERNAME', 'Unknown')

    os_name, os_version = get_windows_version()
    bios_version = get_bios_info()
    system_type = get_system_type()
    scan_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Display formatted output
    print("=========================================================")
    print("SYSTEM INFORMATION")
    print("=========================================================")
    print(f"Computer Name: {computer_name}")
    print(f"Username: {username}")
    print(f"OS Name: {os_name}")
    print(f"OS Version: {os_version}")
    print(f"BIOS Version: {bios_version}")
    print(f"System Type: {system_type}")
    print(f"Scan Time: {scan_time}")
    print("=======================================================")

def main():
    """Main function"""
    try:
        display_system_info()
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()