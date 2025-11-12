"""
Export utilities for conversations
"""
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from config.settings import Settings


class ConversationExporter:
    """Handles exporting conversations to various formats"""

    def __init__(self, export_dir: str = None):
        """
        Initialize exporter

        Args:
            export_dir: Directory for exports (defaults to Settings.EXPORT_DIR)
        """
        self.export_dir = Path(export_dir or Settings.EXPORT_DIR)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_to_text(
        self,
        messages: List[Dict],
        metadata: Dict,
        filename: str = None
    ) -> str:
        """
        Export conversation to text file

        Args:
            messages: List of message dictionaries
            metadata: Conversation metadata (oncologist type, patient type, etc.)
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.txt"

        filepath = self.export_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("MEDICAL VISIT SIMULATION\n")
            f.write("=" * 80 + "\n\n")

            # Metadata
            f.write(f"Date: {metadata.get('timestamp', datetime.now().isoformat())}\n")
            f.write(f"Oncologist: {metadata.get('oncologist_name', 'N/A')} ({metadata.get('oncologist_type', 'N/A')})\n")
            f.write(f"Patient: {metadata.get('patient_name', 'N/A')} ({metadata.get('patient_type', 'N/A')})\n")
            f.write(f"Oncologist Model: {metadata.get('oncologist_model', 'N/A')}\n")
            f.write(f"Patient Model: {metadata.get('patient_model', 'N/A')}\n")

            if metadata.get('case_title'):
                f.write(f"Case: {metadata.get('case_title')}\n")

            f.write(f"Total Messages: {len(messages)}\n")
            f.write("\n" + "=" * 80 + "\n\n")

            # Conversation
            for i, msg in enumerate(messages, 1):
                speaker = msg.get('speaker', 'Unknown')
                content = msg.get('content', '')

                f.write(f"[Message {i}] {speaker}:\n")
                f.write("-" * 40 + "\n")
                f.write(content + "\n\n")

            # Footer
            f.write("=" * 80 + "\n")
            f.write("End of Conversation\n")
            f.write("=" * 80 + "\n")

        return str(filepath)

    def export_to_pdf(
        self,
        messages: List[Dict],
        metadata: Dict,
        filename: str = None
    ) -> str:
        """
        Export conversation to PDF file

        Args:
            messages: List of message dictionaries
            metadata: Conversation metadata
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.pdf"

        filepath = self.export_dir / filename

        # Create PDF
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Styles
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#1f4788',
            spaceAfter=12,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor='#2c5aa0',
            spaceAfter=6,
            spaceBefore=6
        )

        meta_style = ParagraphStyle(
            'MetaStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor='#666666'
        )

        speaker_style = ParagraphStyle(
            'SpeakerStyle',
            parent=styles['Heading3'],
            fontSize=11,
            textColor='#1f4788',
            spaceAfter=4,
            spaceBefore=8
        )

        content_style = ParagraphStyle(
            'ContentStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=8
        )

        # Build document content
        story = []

        # Title
        story.append(Paragraph("Medical Visit Simulation", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Metadata
        story.append(Paragraph("Simulation Details", heading_style))
        story.append(Paragraph(f"<b>Date:</b> {metadata.get('timestamp', datetime.now().isoformat())}", meta_style))
        story.append(Paragraph(f"<b>Oncologist:</b> {metadata.get('oncologist_name', 'N/A')} ({metadata.get('oncologist_type', 'N/A')})", meta_style))
        story.append(Paragraph(f"<b>Patient:</b> {metadata.get('patient_name', 'N/A')} ({metadata.get('patient_type', 'N/A')})", meta_style))
        story.append(Paragraph(f"<b>Oncologist Model:</b> {metadata.get('oncologist_model', 'N/A')}", meta_style))
        story.append(Paragraph(f"<b>Patient Model:</b> {metadata.get('patient_model', 'N/A')}", meta_style))

        if metadata.get('case_title'):
            story.append(Paragraph(f"<b>Case:</b> {metadata.get('case_title')}", meta_style))

        story.append(Paragraph(f"<b>Total Messages:</b> {len(messages)}", meta_style))
        story.append(Spacer(1, 0.3*inch))

        # Conversation
        story.append(Paragraph("Conversation Transcript", heading_style))
        story.append(Spacer(1, 0.1*inch))

        for i, msg in enumerate(messages, 1):
            speaker = msg.get('speaker', 'Unknown')
            content = msg.get('content', '')

            # Clean content for PDF
            content_clean = content.replace('<', '&lt;').replace('>', '&gt;')
            # Convert line breaks to paragraphs
            paragraphs = content_clean.split('\n')

            story.append(Paragraph(f"<b>{speaker}:</b>", speaker_style))

            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, content_style))

            story.append(Spacer(1, 0.1*inch))

        # Build PDF
        doc.build(story)

        return str(filepath)

    def export_to_json(
        self,
        messages: List[Dict],
        metadata: Dict,
        filename: str = None
    ) -> str:
        """
        Export conversation to JSON file

        Args:
            messages: List of message dictionaries
            metadata: Conversation metadata
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        import json

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"

        filepath = self.export_dir / filename

        data = {
            "metadata": metadata,
            "messages": messages,
            "exported_at": datetime.now().isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)


# Create singleton instance
exporter = ConversationExporter()
