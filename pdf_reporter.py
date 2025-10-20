#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Report Generator for System Scanner
Professional PDF export with charts and formatting
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus import Frame, PageTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.pdfgen import canvas
import datetime
from io import BytesIO


class PDFReporter:
    """Generate professional PDF reports for security scans"""

    def __init__(self, scan_results, filename):
        """
        Initialize PDF reporter

        Args:
            scan_results: Dictionary containing scan results
            filename: Output PDF filename
        """
        self.scan_results = scan_results
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.story = []

        # Custom color scheme (matching app theme)
        self.colors = {
            'primary': colors.HexColor('#2563eb'),
            'success': colors.HexColor('#10b981'),
            'warning': colors.HexColor('#f59e0b'),
            'danger': colors.HexColor('#ef4444'),
            'gray': colors.HexColor('#64748b'),
            'light_gray': colors.HexColor('#f8fafc')
        }

        # Define custom styles
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=self.colors['primary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Heading 1 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.colors['primary'],
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Heading 2 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.colors['gray'],
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Normal text with custom color
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=6
        ))

        # Status text (for success/warning/danger)
        self.styles.add(ParagraphStyle(
            name='StatusSuccess',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.colors['success'],
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='StatusWarning',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.colors['warning'],
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='StatusDanger',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.colors['danger'],
            fontName='Helvetica-Bold'
        ))

    def generate(self):
        """Generate the complete PDF report"""
        # Cover page
        self._add_cover_page()

        # Executive summary
        self._add_executive_summary()

        # Statistics with charts
        self._add_statistics_section()

        # Detailed findings
        self._add_detailed_findings()

        # Security assessment
        self._add_security_assessment()

        # System information
        self._add_system_information()

        # Recommendations
        self._add_recommendations()

        # Build PDF
        self.doc.build(self.story, onFirstPage=self._add_page_number,
                      onLaterPages=self._add_page_number)

    def _add_cover_page(self):
        """Add professional cover page"""
        # Title
        title = Paragraph("System Security Scan Report", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))

        # Scan date
        scan_time = self.scan_results.get('system', {}).get('scan_time',
                                                            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        date_text = Paragraph(f"<b>Scan Date:</b> {scan_time}", self.styles['CustomNormal'])
        self.story.append(date_text)
        self.story.append(Spacer(1, 0.3*inch))

        # Computer info
        system = self.scan_results.get('system', {})
        computer_name = system.get('computer_name', 'Unknown')
        username = system.get('username', 'Unknown')

        info_text = Paragraph(f"<b>Computer:</b> {computer_name}<br/><b>User:</b> {username}",
                             self.styles['CustomNormal'])
        self.story.append(info_text)
        self.story.append(Spacer(1, 0.5*inch))

        # Summary statistics box
        vpn_count = len(self.scan_results.get('vpn', []))
        chat_count = len(self.scan_results.get('chat', []))
        remote_count = len(self.scan_results.get('remote', []))
        total_count = vpn_count + chat_count + remote_count

        summary_data = [
            ['Category', 'Count'],
            ['VPN Applications', str(vpn_count)],
            ['Chat Applications', str(chat_count)],
            ['Remote Control Apps', str(remote_count)],
            ['Total Detections', str(total_count)]
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']])
        ]))

        self.story.append(summary_table)
        self.story.append(PageBreak())

    def _add_executive_summary(self):
        """Add executive summary section"""
        self.story.append(Paragraph("Executive Summary", self.styles['CustomHeading1']))
        self.story.append(Spacer(1, 0.2*inch))

        # Calculate statistics
        vpn_count = len(self.scan_results.get('vpn', []))
        chat_count = len(self.scan_results.get('chat', []))
        remote_count = len(self.scan_results.get('remote', []))
        total_count = vpn_count + chat_count + remote_count

        # Risk assessment
        risk_level = "Low"
        risk_style = 'StatusSuccess'

        if total_count > 20:
            risk_level = "High"
            risk_style = 'StatusDanger'
        elif total_count > 10:
            risk_level = "Medium"
            risk_style = 'StatusWarning'

        summary_text = f"""
        This report provides a comprehensive security assessment of the system.
        A total of <b>{total_count}</b> applications were detected across VPN, Chat, and Remote Control categories.
        <br/><br/>
        <b>Risk Level:</b> {risk_level}<br/>
        <b>VPN Applications:</b> {vpn_count}<br/>
        <b>Chat Applications:</b> {chat_count}<br/>
        <b>Remote Control Applications:</b> {remote_count}
        """

        self.story.append(Paragraph(summary_text, self.styles['CustomNormal']))
        self.story.append(Spacer(1, 0.3*inch))

    def _add_statistics_section(self):
        """Add statistics section with charts"""
        self.story.append(Paragraph("Application Statistics", self.styles['CustomHeading1']))
        self.story.append(Spacer(1, 0.2*inch))

        # Create pie chart
        vpn_count = len(self.scan_results.get('vpn', []))
        chat_count = len(self.scan_results.get('chat', []))
        remote_count = len(self.scan_results.get('remote', []))

        if vpn_count + chat_count + remote_count > 0:
            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 100
            pie.height = 100
            pie.data = [vpn_count, chat_count, remote_count]
            pie.labels = ['VPN', 'Chat', 'Remote']
            pie.slices.strokeWidth = 0.5
            pie.slices[0].fillColor = colors.HexColor('#6366f1')
            pie.slices[1].fillColor = colors.HexColor('#8b5cf6')
            pie.slices[2].fillColor = colors.HexColor('#ec4899')

            drawing.add(pie)
            self.story.append(drawing)

        self.story.append(Spacer(1, 0.3*inch))

    def _add_detailed_findings(self):
        """Add detailed findings section"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Detailed Findings", self.styles['CustomHeading1']))
        self.story.append(Spacer(1, 0.2*inch))

        # VPN Applications
        self._add_category_findings("VPN Applications", self.scan_results.get('vpn', []))

        # Chat Applications
        self._add_category_findings("Chat Applications", self.scan_results.get('chat', []))

        # Remote Control Applications
        self._add_category_findings("Remote Control Applications", self.scan_results.get('remote', []))

    def _add_category_findings(self, category_name, apps):
        """Add findings for a specific category"""
        self.story.append(Paragraph(category_name, self.styles['CustomHeading2']))

        if not apps:
            self.story.append(Paragraph(f"No {category_name.lower()} detected.",
                                       self.styles['CustomNormal']))
            self.story.append(Spacer(1, 0.2*inch))
            return

        self.story.append(Paragraph(f"Found {len(apps)} application(s):",
                                   self.styles['CustomNormal']))
        self.story.append(Spacer(1, 0.1*inch))

        # Create table for applications
        table_data = [['Application Name', 'Installation Path']]

        for app in apps[:20]:  # Limit to 20 for readability
            name = app.get('name', 'Unknown')
            path = app.get('path', 'Unknown')
            # Truncate long paths
            if len(path) > 60:
                path = path[:57] + "..."
            table_data.append([name, path])

        if len(apps) > 20:
            table_data.append(['...', f'and {len(apps) - 20} more'])

        findings_table = Table(table_data, colWidths=[2*inch, 4*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['gray']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']])
        ]))

        self.story.append(findings_table)
        self.story.append(Spacer(1, 0.3*inch))

    def _add_security_assessment(self):
        """Add security configuration assessment"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Security Configuration", self.styles['CustomHeading1']))
        self.story.append(Spacer(1, 0.2*inch))

        security = self.scan_results.get('security', {})

        # Security settings table
        security_data = [['Security Item', 'Status', 'Assessment']]

        # File extensions
        ext_status = security.get('file_extensions', 'Unknown')
        ext_assessment = '✓ Good' if ext_status == 'Visible' else '✗ Needs Attention'
        security_data.append(['File Extensions Visibility', ext_status, ext_assessment])

        # Guest account
        guest_status = security.get('guest_account', 'Unknown')
        guest_assessment = '✓ Good' if guest_status == 'Disabled' else '✗ Security Risk'
        security_data.append(['Guest Account', guest_status, guest_assessment])

        # AutoPlay
        autoplay_status = security.get('autoplay', 'Unknown')
        autoplay_assessment = '✓ Good' if autoplay_status == 'Disabled' else '✗ Needs Attention'
        security_data.append(['AutoPlay', autoplay_status, autoplay_assessment])

        # Firewall
        firewall = security.get('firewall_status', {})
        firewall_status = firewall.get('overall', 'Unknown')
        firewall_assessment = '✓ Good' if 'Enabled' in firewall_status else '✗ Critical'
        security_data.append(['Windows Firewall', firewall_status, firewall_assessment])

        security_table = Table(security_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        security_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']])
        ]))

        self.story.append(security_table)
        self.story.append(Spacer(1, 0.3*inch))

        # Add Port Blocking section
        self._add_port_blocking_section(security)

        # Add Network Interfaces section
        self._add_network_interfaces_section(security)

    def _add_port_blocking_section(self, security):
        """Add port blocking check results"""
        self.story.append(Paragraph("Port Blocking Status", self.styles['CustomHeading2']))
        self.story.append(Spacer(1, 0.1*inch))

        port_blocking = security.get('port_blocking', {})

        if not port_blocking:
            self.story.append(Paragraph("Port blocking check not performed or data unavailable.",
                                       self.styles['CustomNormal']))
            self.story.append(Spacer(1, 0.2*inch))
            return

        # Port blocking table
        port_data = [['Port', 'Status', 'Details']]

        # Ports to check: 135, 136, 137, 138, 139, 445
        for port in sorted(port_blocking.keys()):
            port_info = port_blocking[port]
            blocked_status = port_info.get('blocked', 'Unknown')
            details = port_info.get('details', 'No details available')

            # Determine status display
            if blocked_status == 'Yes':
                status_display = '✓ Blocked'
            elif blocked_status == 'No':
                status_display = '✗ Not Blocked'
            elif blocked_status == 'Not listening':
                status_display = '○ Not Listening'
            else:
                status_display = '? Unknown'

            port_data.append([str(port), status_display, details])

        port_table = Table(port_data, colWidths=[0.8*inch, 1.5*inch, 3.7*inch])
        port_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['gray']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        self.story.append(port_table)
        self.story.append(Spacer(1, 0.2*inch))

        # Add explanation
        explanation = Paragraph(
            "<b>Note:</b> Ports 135-139 and 445 are commonly targeted by network attacks. "
            "These ports should be blocked by your firewall for inbound connections when not needed. "
            "'Blocked' status is recommended for enhanced security.",
            self.styles['CustomNormal']
        )
        self.story.append(explanation)
        self.story.append(Spacer(1, 0.3*inch))

    def _add_network_interfaces_section(self, security):
        """Add network interfaces check results"""
        self.story.append(Paragraph("Network Interfaces Status", self.styles['CustomHeading2']))
        self.story.append(Spacer(1, 0.1*inch))

        network_interfaces = security.get('network_interfaces', {})

        if not network_interfaces or not network_interfaces.get('all_interfaces'):
            self.story.append(Paragraph("Network interfaces check not performed or data unavailable.",
                                       self.styles['CustomNormal']))
            self.story.append(Spacer(1, 0.2*inch))
            return

        # Summary paragraph
        total_count = network_interfaces.get('total_count', 0)
        enabled_count = network_interfaces.get('enabled_count', 0)
        disabled_count = network_interfaces.get('disabled_count', 0)
        unused_enabled_count = network_interfaces.get('unused_enabled_count', 0)
        summary = network_interfaces.get('summary', 'Unknown')

        summary_text = (
            f"<b>Summary:</b> {summary}<br/>"
            f"Total Interfaces: {total_count} | "
            f"Enabled: {enabled_count} | "
            f"Disabled: {disabled_count} | "
            f"<font color='#ef4444'>Unused but Enabled: {unused_enabled_count}</font>"
        )
        self.story.append(Paragraph(summary_text, self.styles['CustomNormal']))
        self.story.append(Spacer(1, 0.15*inch))

        # Network interfaces table
        interface_data = [['Interface Name', 'Status', 'Description']]

        all_interfaces = network_interfaces.get('all_interfaces', [])
        for interface in all_interfaces:
            name = interface.get('name', 'Unknown')
            status = interface.get('status', 'Unknown')
            description = interface.get('description', 'No description')

            # Truncate long descriptions
            if len(description) > 50:
                description = description[:47] + '...'

            interface_data.append([name, status, description])

        interface_table = Table(interface_data, colWidths=[1.8*inch, 1.2*inch, 3*inch])
        interface_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['gray']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        self.story.append(interface_table)
        self.story.append(Spacer(1, 0.2*inch))

        # Add explanation
        if unused_enabled_count > 0:
            warning = Paragraph(
                "<b>Security Warning:</b> Some network interfaces are enabled but not in use (status: Disconnected). "
                "Unused interfaces should be disabled to reduce potential attack surface. "
                "You can disable unused interfaces in Network Connections settings.",
                self.styles['StatusWarning']
            )
            self.story.append(warning)
        else:
            success = Paragraph(
                "<b>Good:</b> All unused network interfaces are properly disabled.",
                self.styles['StatusSuccess']
            )
            self.story.append(success)

        self.story.append(Spacer(1, 0.3*inch))

    def _add_system_information(self):
        """Add system information section"""
        self.story.append(Paragraph("System Information", self.styles['CustomHeading1']))
        self.story.append(Spacer(1, 0.2*inch))

        system = self.scan_results.get('system', {})

        system_data = [
            ['Property', 'Value'],
            ['Computer Name', system.get('computer_name', 'Unknown')],
            ['Username', system.get('username', 'Unknown')],
            ['OS Name', system.get('os_name', 'Unknown')],
            ['OS Version', system.get('os_version', 'Unknown')],
            ['BIOS Version', system.get('bios_version', 'Unknown')],
            ['System Type', system.get('system_type', 'Unknown')],
            ['Scan Time', system.get('scan_time', 'Unknown')]
        ]

        system_table = Table(system_data, colWidths=[2*inch, 4*inch])
        system_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['gray']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']])
        ]))

        self.story.append(system_table)

    def _add_recommendations(self):
        """Add security recommendations"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Security Recommendations", self.styles['CustomHeading1']))
        self.story.append(Spacer(1, 0.2*inch))

        recommendations = []

        # Check security settings and add recommendations
        security = self.scan_results.get('security', {})

        if security.get('file_extensions') == 'Hidden':
            recommendations.append("Enable file extension visibility to identify potentially malicious files.")

        if security.get('guest_account') == 'Enabled':
            recommendations.append("Disable the Guest account to prevent unauthorized access.")

        if security.get('autoplay') != 'Disabled':
            recommendations.append("Disable AutoPlay to prevent automatic execution of malicious content from USB devices.")

        firewall = security.get('firewall_status', {})
        if 'Disabled' in firewall.get('overall', ''):
            recommendations.append("Enable Windows Firewall on all network profiles immediately.")

        # Check port blocking
        port_blocking = security.get('port_blocking', {})
        unblocked_ports = []
        for port, status in port_blocking.items():
            if status.get('blocked') == 'No' or (status.get('listening') and not status.get('firewall_blocked')):
                unblocked_ports.append(str(port))

        if unblocked_ports:
            ports_str = ', '.join(unblocked_ports)
            recommendations.append(f"Block vulnerable ports ({ports_str}) using Windows Firewall inbound rules to prevent network attacks.")

        # Check network interfaces
        network_interfaces = security.get('network_interfaces', {})
        unused_enabled_count = network_interfaces.get('unused_enabled_count', 0)
        if unused_enabled_count > 0:
            recommendations.append(
                f"Disable {unused_enabled_count} unused network interface(s) to reduce attack surface. "
                "Go to Network Connections and disable interfaces that are not in use."
            )

        # Check for too many applications
        total_apps = len(self.scan_results.get('vpn', [])) + len(self.scan_results.get('chat', [])) + len(self.scan_results.get('remote', []))
        if total_apps > 15:
            recommendations.append("Review and uninstall unnecessary applications to reduce attack surface.")

        if not recommendations:
            recommendations.append("✓ No critical security issues found. Continue monitoring system regularly.")

        # Add recommendations as numbered list
        for i, rec in enumerate(recommendations, 1):
            rec_text = Paragraph(f"<b>{i}.</b> {rec}", self.styles['CustomNormal'])
            self.story.append(rec_text)
            self.story.append(Spacer(1, 0.1*inch))

    def _add_page_number(self, canvas, doc):
        """Add page numbers to footer"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(letter[0] - 0.75*inch, 0.5*inch, text)

        # Add footer text
        canvas.drawString(0.75*inch, 0.5*inch, "System Security Scanner Report")
        canvas.restoreState()
