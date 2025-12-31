#!/usr/bin/env python3
"""
Research Paper Summary PDF Generator v2.0

Features:
- Automatic figure detection and extraction from source PDFs
- Brand-compliant styling (Oligon Scientific Brand v4.0)
- Professional layout matching publication standards

Usage:
    # With automatic figure extraction:
    python generate_summary_pdf_v2.py --yaml summary.yaml --source paper.pdf --output summary.pdf
    
    # With pre-extracted figures:
    python generate_summary_pdf_v2.py --yaml summary.yaml --figures figures/ --output summary.pdf

Dependencies:
    pip install reportlab pyyaml Pillow pymupdf pdfplumber --break-system-packages
"""

import argparse
import yaml
import os
import re
import io
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# PDF libraries
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Image handling
from PIL import Image as PILImage

# PDF reading for figure extraction
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


# =============================================================================
# BRAND COLOR PALETTE (Oligon Scientific Brand v4.0)
# =============================================================================
BRAND_COLORS = {
    # Primary Brand Color
    'brand_blue': HexColor('#2DB2E8'),
    
    # Neutral Data Colors
    'dark_gray': HexColor('#222222'),
    'medium_gray': HexColor('#666666'),
    'muted_gray': HexColor('#999999'),
    'light_gray': HexColor('#BDBDBD'),
    
    # Scientific Contrast Colors
    'contrast_orange': HexColor('#E8622D'),
    'dark_warm': HexColor('#7D250F'),
    
    # Supporting Blues
    'medium_blue': HexColor('#158BBB'),
    'dark_teal': HexColor('#0F5D7D'),
    
    # Structure Colors
    'black': HexColor('#000000'),
    'white': HexColor('#FFFFFF'),
    'gridline': HexColor('#E5E5E5'),
}

# Semantic color mapping for PDF sections
PDF_COLORS = {
    'primary': BRAND_COLORS['dark_gray'],        # Headers, main text
    'secondary': BRAND_COLORS['medium_gray'],    # Subheaders
    'accent': BRAND_COLORS['brand_blue'],        # Highlights, key findings
    'success': BRAND_COLORS['brand_blue'],       # Overview box (using brand blue)
    'warning': BRAND_COLORS['contrast_orange'],  # Limitations
    'text': BRAND_COLORS['dark_gray'],
    'text_muted': BRAND_COLORS['medium_gray'],
    'border': BRAND_COLORS['light_gray'],
    'light_bg': HexColor('#F8F9FA'),
}


# =============================================================================
# AUTOMATIC FIGURE EXTRACTION
# =============================================================================
class FigureExtractor:
    """Extract figures from PDF with automatic detection and caption matching."""
    
    def __init__(self, pdf_path: str, output_dir: str = None):
        self.pdf_path = pdf_path
        self.output_dir = output_dir or Path(pdf_path).stem + "_figures"
        self.figures: Dict[str, dict] = {}
        
    def extract_figures(self) -> Dict[str, dict]:
        """
        Extract all figures from the PDF.
        
        Returns dict mapping figure identifiers to:
        {
            'path': str,           # Path to extracted image
            'page': int,           # Page number
            'caption': str,        # Detected caption (if any)
            'bbox': tuple,         # Bounding box
            'width': int,
            'height': int
        }
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        if PYMUPDF_AVAILABLE:
            return self._extract_with_pymupdf()
        elif PDFPLUMBER_AVAILABLE:
            return self._extract_with_pdfplumber()
        else:
            print("⚠️ No PDF extraction library available. Install pymupdf or pdfplumber.")
            return {}
    
    def _extract_with_pymupdf(self) -> Dict[str, dict]:
        """Extract figures using PyMuPDF (fitz) - preferred method."""
        doc = fitz.open(self.pdf_path)
        figures = {}
        image_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get all images on the page
            image_list = page.get_images(full=True)
            
            # Get text blocks for caption detection
            text_blocks = page.get_text("blocks")
            
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                
                try:
                    # Extract image
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Get image dimensions
                    width = base_image.get("width", 0)
                    height = base_image.get("height", 0)
                    
                    # Skip very small images (likely icons/logos)
                    if width < 100 or height < 100:
                        continue
                    
                    # Skip very large aspect ratio images (likely decorative)
                    aspect = max(width, height) / max(min(width, height), 1)
                    if aspect > 10:
                        continue
                    
                    image_count += 1
                    
                    # Save image
                    image_filename = f"figure_{image_count:03d}.{image_ext}"
                    image_path = os.path.join(self.output_dir, image_filename)
                    
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                    
                    # Try to find figure number from nearby text
                    figure_id = self._detect_figure_label(page, xref, text_blocks)
                    
                    # Try to extract caption
                    caption = self._extract_caption(page, xref, text_blocks)
                    
                    figures[figure_id or f"img_{image_count}"] = {
                        'path': image_path,
                        'page': page_num + 1,
                        'caption': caption,
                        'width': width,
                        'height': height,
                        'sequence': image_count,
                    }
                    
                except Exception as e:
                    print(f"  Warning: Could not extract image {xref}: {e}")
        
        doc.close()
        print(f"✅ Extracted {len(figures)} figures from {self.pdf_path}")
        return figures
    
    def _extract_with_pdfplumber(self) -> Dict[str, dict]:
        """Fallback extraction using pdfplumber."""
        figures = {}
        image_count = 0
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # pdfplumber's image extraction is more limited
                if hasattr(page, 'images'):
                    for img in page.images:
                        image_count += 1
                        
                        # pdfplumber doesn't directly extract image bytes
                        # We'd need additional processing here
                        figures[f"img_{image_count}"] = {
                            'path': None,
                            'page': page_num + 1,
                            'caption': '',
                            'width': img.get('width', 0),
                            'height': img.get('height', 0),
                            'sequence': image_count,
                        }
        
        print(f"⚠️ pdfplumber extraction limited. Found {len(figures)} image references.")
        return figures
    
    def _detect_figure_label(self, page, xref, text_blocks) -> Optional[str]:
        """
        Detect figure label (e.g., 'Figure 1', 'Fig. 2A') from nearby text.
        """
        # Common figure label patterns
        patterns = [
            r'(?:Figure|Fig\.?|FIG\.?)\s*(\d+[A-Za-z]?)',
            r'(?:Table|Tab\.?)\s*(\d+[A-Za-z]?)',
            r'(?:Scheme|Sch\.?)\s*(\d+[A-Za-z]?)',
        ]
        
        for block in text_blocks:
            if len(block) >= 5:
                text = block[4]
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        # Normalize the label
                        full_match = match.group(0)
                        if 'table' in full_match.lower():
                            return f"Table {match.group(1)}"
                        elif 'scheme' in full_match.lower():
                            return f"Scheme {match.group(1)}"
                        else:
                            return f"Figure {match.group(1)}"
        
        return None
    
    def _extract_caption(self, page, xref, text_blocks) -> str:
        """
        Extract figure caption from nearby text blocks.
        """
        caption_patterns = [
            r'(?:Figure|Fig\.?|FIG\.?)\s*\d+[A-Za-z]?[.:\s]+(.+?)(?:\n\n|$)',
            r'(?:Table|Tab\.?)\s*\d+[A-Za-z]?[.:\s]+(.+?)(?:\n\n|$)',
        ]
        
        for block in text_blocks:
            if len(block) >= 5:
                text = block[4]
                for pattern in caption_patterns:
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        caption = match.group(1).strip()
                        # Limit caption length
                        if len(caption) > 500:
                            caption = caption[:500] + "..."
                        return caption
        
        return ""


def extract_figures_from_pdf(pdf_path: str, output_dir: str = None) -> Dict[str, dict]:
    """
    Convenience function to extract figures from a PDF.
    
    Args:
        pdf_path: Path to source PDF
        output_dir: Directory to save extracted images
        
    Returns:
        Dictionary mapping figure IDs to metadata
    """
    extractor = FigureExtractor(pdf_path, output_dir)
    return extractor.extract_figures()


# =============================================================================
# PDF STYLES (Brand-Compliant)
# =============================================================================
def get_brand_styles():
    """Create brand-compliant paragraph styles."""
    styles = getSampleStyleSheet()
    
    # Base font - prefer Arial/Helvetica
    base_font = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    
    # Document title
    styles.add(ParagraphStyle(
        name='DocTitle',
        parent=styles['Title'],
        fontSize=16,
        textColor=PDF_COLORS['primary'],
        fontName=bold_font,
        spaceAfter=6,
        alignment=TA_CENTER,
    ))
    
    # Paper title
    styles.add(ParagraphStyle(
        name='PaperTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=PDF_COLORS['primary'],
        fontName=bold_font,
        spaceAfter=4,
        alignment=TA_CENTER,
    ))
    
    # Section header (brand blue accent line)
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=PDF_COLORS['primary'],
        fontName=bold_font,
        spaceBefore=14,
        spaceAfter=6,
    ))
    
    # Update existing BodyText style
    styles['BodyText'].fontSize = 9
    styles['BodyText'].textColor = PDF_COLORS['text']
    styles['BodyText'].fontName = base_font
    styles['BodyText'].alignment = TA_JUSTIFY
    styles['BodyText'].spaceAfter = 6
    styles['BodyText'].leading = 12
    
    # Statistics text (monospace)
    styles.add(ParagraphStyle(
        name='StatText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=PDF_COLORS['text_muted'],
        fontName='Courier',
        spaceAfter=4,
    ))
    
    # Caption style
    styles.add(ParagraphStyle(
        name='Caption',
        parent=styles['Normal'],
        fontSize=8,
        textColor=PDF_COLORS['text_muted'],
        fontName=base_font,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=10,
    ))
    
    # Metadata style
    styles.add(ParagraphStyle(
        name='Metadata',
        parent=styles['Normal'],
        fontSize=8,
        textColor=PDF_COLORS['text_muted'],
        fontName=base_font,
        alignment=TA_CENTER,
    ))
    
    # Bullet item
    styles.add(ParagraphStyle(
        name='BulletItem',
        parent=styles['Normal'],
        fontSize=9,
        textColor=PDF_COLORS['text'],
        fontName=base_font,
        leftIndent=12,
        spaceAfter=4,
        leading=12,
    ))
    
    return styles


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def create_section_header(text: str, styles, icon: str = "") -> Table:
    """Create a brand-styled section header with accent line."""
    header_text = f"{icon} {text}".strip() if icon else text
    
    # Create header with blue accent underline
    header_table = Table(
        [[Paragraph(header_text, styles['SectionHeader'])]],
        colWidths=[6.5*inch]
    )
    header_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, PDF_COLORS['accent']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return header_table


def create_hr():
    """Create a subtle horizontal rule."""
    return HRFlowable(
        width="100%",
        thickness=0.5,
        color=PDF_COLORS['border'],
        spaceBefore=8,
        spaceAfter=8
    )


def create_highlight_box(text: str, styles, box_type: str = 'default') -> Table:
    """
    Create a highlighted text box with brand colors.
    
    box_type: 'default' (blue), 'warning' (orange), 'neutral' (gray)
    """
    colors_map = {
        'default': (HexColor('#E8F4FC'), PDF_COLORS['accent']),      # Light blue bg
        'warning': (HexColor('#FEF3E8'), PDF_COLORS['warning']),     # Light orange bg
        'neutral': (PDF_COLORS['light_bg'], PDF_COLORS['border']),  # Gray bg
    }
    
    bg_color, border_color = colors_map.get(box_type, colors_map['default'])
    
    table = Table(
        [[Paragraph(text, styles['BodyText'])]],
        colWidths=[6.5*inch]
    )
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BOX', (0, 0), (-1, -1), 1.5, border_color),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return table


def find_figure_image(figures_data: Dict, figure_ref: str, figures_dir: str = None) -> Optional[str]:
    """
    Find the image file for a figure reference.
    
    Checks both extracted figures (from automatic detection) and manual figures directory.
    """
    # Normalize the reference
    ref_lower = figure_ref.lower().strip()
    ref_nums = ''.join(filter(str.isdigit, ref_lower))
    
    # Check extracted figures first
    if figures_data:
        for fig_id, fig_info in figures_data.items():
            fig_id_lower = fig_id.lower()
            
            # Direct match
            if ref_lower in fig_id_lower or fig_id_lower in ref_lower:
                if fig_info.get('path') and os.path.exists(fig_info['path']):
                    return fig_info['path']
            
            # Number match
            fig_nums = ''.join(filter(str.isdigit, fig_id_lower))
            if ref_nums and fig_nums and ref_nums == fig_nums:
                if fig_info.get('path') and os.path.exists(fig_info['path']):
                    return fig_info['path']
    
    # Check manual figures directory
    if figures_dir and os.path.exists(figures_dir):
        figures_path = Path(figures_dir)
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']:
            for img_file in figures_path.glob(ext):
                stem_lower = img_file.stem.lower()
                if ref_nums and ref_nums in stem_lower:
                    return str(img_file)
                if ref_lower.replace(' ', '') in stem_lower.replace('_', '').replace('-', ''):
                    return str(img_file)
    
    return None


def add_figure(story: list, figure_path: str, caption: str, styles,
               max_width: float = 5.5*inch, max_height: float = 3.5*inch):
    """Add a figure with caption to the document."""
    if figure_path and os.path.exists(figure_path):
        try:
            img = Image(figure_path)
            
            # Scale to fit
            if img.imageWidth > 0 and img.imageHeight > 0:
                aspect = img.imageWidth / img.imageHeight
                
                img.drawWidth = min(img.imageWidth, max_width)
                img.drawHeight = img.drawWidth / aspect
                
                if img.drawHeight > max_height:
                    img.drawHeight = max_height
                    img.drawWidth = max_height * aspect
                
                story.append(img)
            
            story.append(Paragraph(caption, styles['Caption']))
            
        except Exception as e:
            story.append(Paragraph(
                f"<i>[Figure could not be loaded: {os.path.basename(figure_path)}]</i>",
                styles['Caption']
            ))
    else:
        story.append(Paragraph(f"<i>{caption}</i>", styles['Caption']))


# =============================================================================
# MAIN PDF GENERATION
# =============================================================================
def generate_summary_pdf(
    yaml_path: str,
    output_path: str,
    source_pdf: str = None,
    figures_dir: str = None,
    auto_extract: bool = True
) -> str:
    """
    Generate the summary PDF from YAML data.
    
    Args:
        yaml_path: Path to YAML summary file
        output_path: Output PDF path
        source_pdf: Path to original paper PDF (for figure extraction)
        figures_dir: Directory with pre-extracted figures
        auto_extract: Whether to automatically extract figures from source PDF
        
    Returns:
        Path to generated PDF
    """
    
    # Load YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Extract figures if source PDF provided
    extracted_figures = {}
    if source_pdf and auto_extract and os.path.exists(source_pdf):
        print(f"📄 Extracting figures from {source_pdf}...")
        extracted_figures = extract_figures_from_pdf(
            source_pdf,
            output_dir=figures_dir or (Path(source_pdf).stem + "_figures")
        )
        # Update figures_dir to point to extracted location
        if extracted_figures:
            figures_dir = figures_dir or (Path(source_pdf).stem + "_figures")
    
    # Setup document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = get_brand_styles()
    story = []
    
    # =========================================================================
    # HEADER
    # =========================================================================
    story.append(Paragraph("Research Paper Summary", styles['DocTitle']))
    story.append(Spacer(1, 4))
    
    meta = data.get('metadata', {})
    story.append(Paragraph(meta.get('title', 'Untitled'), styles['PaperTitle']))
    
    # Author and journal line
    meta_parts = [meta.get('authors', 'Unknown')]
    if meta.get('journal'):
        meta_parts.append(meta['journal'])
    if meta.get('year'):
        meta_parts.append(f"({meta['year']})")
    story.append(Paragraph(" • ".join(meta_parts), styles['Metadata']))
    
    # DOI and PMID
    ids = []
    if meta.get('doi'):
        ids.append(f"DOI: {meta['doi']}")
    if meta.get('pmid'):
        ids.append(f"PMID: {meta['pmid']}")
    if ids:
        story.append(Paragraph(" | ".join(ids), styles['Metadata']))
    
    story.append(Spacer(1, 8))
    story.append(create_hr())
    
    # =========================================================================
    # OVERVIEW
    # =========================================================================
    story.append(create_section_header("Overview", styles, "🎯"))
    story.append(Spacer(1, 4))
    story.append(create_highlight_box(
        data.get('overview', 'No overview provided.'),
        styles,
        'default'
    ))
    story.append(Spacer(1, 8))
    
    # =========================================================================
    # KEY FINDINGS
    # =========================================================================
    story.append(create_section_header("Key Findings", styles, "📊"))
    story.append(Spacer(1, 4))
    
    findings = data.get('key_findings', [])
    for i, finding in enumerate(findings, 1):
        finding_text = finding.get('finding', '') if isinstance(finding, dict) else str(finding)
        
        # Finding with brand blue number
        story.append(Paragraph(
            f"<font color='#2DB2E8'><b>{i}.</b></font> {finding_text}",
            styles['BodyText']
        ))
        
        if isinstance(finding, dict):
            stats = finding.get('statistics', '')
            fig_ref = finding.get('figure_ref', '')
            
            if stats or fig_ref:
                stat_parts = []
                if stats:
                    stat_parts.append(f"<font face='Courier' size='8'>{stats}</font>")
                if fig_ref:
                    stat_parts.append(f"<i>[{fig_ref}]</i>")
                story.append(Paragraph(" • ".join(stat_parts), styles['StatText']))
        
        story.append(Spacer(1, 2))
    
    # =========================================================================
    # KEY FIGURES
    # =========================================================================
    key_figures = data.get('key_figures', [])
    if key_figures:
        story.append(create_section_header("Key Figures", styles, "🖼️"))
        story.append(Spacer(1, 4))
        
        for fig in key_figures:
            fig_num = fig.get('number', 'Figure')
            fig_title = fig.get('title', '')
            fig_findings = fig.get('key_findings', '')
            
            # Find the figure image
            fig_path = find_figure_image(extracted_figures, fig_num, figures_dir)
            
            # Build caption
            caption = f"<b>{fig_num}</b>"
            if fig_title:
                caption += f": {fig_title}"
            if fig_findings:
                caption += f"<br/><i>{fig_findings}</i>"
            
            add_figure(story, fig_path, caption, styles)
    
    # =========================================================================
    # METHODS SUMMARY
    # =========================================================================
    story.append(create_section_header("Methods Summary", styles, "🔬"))
    story.append(Spacer(1, 4))
    
    methods = data.get('methods', {})
    methods_rows = [
        ('Study Design', methods.get('study_design')),
        ('Model System', methods.get('model_system')),
        ('Sample Size', methods.get('sample_size')),
        ('Key Techniques', methods.get('key_techniques')),
        ('Statistical Analysis', methods.get('statistical_analysis')),
        ('Key Parameters', methods.get('key_parameters')),
    ]
    
    # Filter out empty rows
    methods_data = [[label, value] for label, value in methods_rows if value]
    
    if methods_data:
        methods_table = Table(methods_data, colWidths=[1.4*inch, 5.1*inch])
        methods_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), PDF_COLORS['light_bg']),
            ('TEXTCOLOR', (0, 0), (0, -1), PDF_COLORS['text_muted']),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, PDF_COLORS['border']),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(methods_table)
    else:
        story.append(Paragraph("<i>Methods details not provided.</i>", styles['BodyText']))
    
    story.append(Spacer(1, 8))
    
    # =========================================================================
    # LIMITATIONS
    # =========================================================================
    story.append(create_section_header("Limitations & Caveats", styles, "⚠️"))
    story.append(Spacer(1, 4))
    
    limitations = data.get('limitations', {})
    has_limitations = False
    
    author_lims = limitations.get('author_stated', [])
    if author_lims:
        has_limitations = True
        story.append(Paragraph("<b>Author-stated:</b>", styles['BodyText']))
        for lim in author_lims:
            story.append(Paragraph(f"• {lim}", styles['BulletItem']))
    
    additional_lims = limitations.get('additional', [])
    if additional_lims:
        has_limitations = True
        if author_lims:
            story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Additional considerations:</b>", styles['BodyText']))
        for lim in additional_lims:
            story.append(Paragraph(f"• {lim}", styles['BulletItem']))
    
    if not has_limitations:
        story.append(Paragraph("<i>No limitations noted.</i>", styles['BodyText']))
    
    story.append(Spacer(1, 8))
    
    # =========================================================================
    # IMPLICATIONS
    # =========================================================================
    story.append(create_section_header("Implications & Future Directions", styles, "💡"))
    story.append(Spacer(1, 4))
    
    implications = data.get('implications', '')
    if implications:
        story.append(Paragraph(implications, styles['BodyText']))
    else:
        story.append(Paragraph("<i>Not specified.</i>", styles['BodyText']))
    
    # =========================================================================
    # RELEVANCE NOTES (optional)
    # =========================================================================
    relevance = data.get('relevance_notes', '')
    if relevance and str(relevance).strip():
        story.append(create_section_header("Relevance to Current Work", styles, "🔗"))
        story.append(Spacer(1, 4))
        story.append(create_highlight_box(relevance, styles, 'neutral'))
    
    # =========================================================================
    # FOOTER
    # =========================================================================
    story.append(Spacer(1, 16))
    story.append(create_hr())
    story.append(Paragraph(
        f"Summary generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles['Metadata']
    ))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF generated successfully: {output_path}")
    return output_path


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description='Generate brand-compliant research summary PDFs with automatic figure extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With automatic figure extraction from source paper:
  %(prog)s --yaml summary.yaml --source paper.pdf --output summary.pdf
  
  # With pre-extracted figures directory:
  %(prog)s --yaml summary.yaml --figures figures/ --output summary.pdf
  
  # YAML only (no figures):
  %(prog)s --yaml summary.yaml --output summary.pdf

Workflow:
  1. Use Claude to analyze paper and generate YAML summary
  2. Run this script with --source pointing to original PDF
  3. Figures are automatically extracted and matched to references
        """
    )
    parser.add_argument(
        '--yaml', '-y',
        required=True,
        help='Path to YAML summary file (from Claude)'
    )
    parser.add_argument(
        '--source', '-s',
        default=None,
        help='Source PDF to extract figures from (optional)'
    )
    parser.add_argument(
        '--figures', '-f',
        default=None,
        help='Directory with pre-extracted figures (optional)'
    )
    parser.add_argument(
        '--output', '-o',
        default='summary.pdf',
        help='Output PDF path (default: summary.pdf)'
    )
    parser.add_argument(
        '--no-auto-extract',
        action='store_true',
        help='Disable automatic figure extraction'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.yaml):
        print(f"❌ Error: YAML file not found: {args.yaml}")
        return 1
    
    if args.source and not os.path.exists(args.source):
        print(f"⚠️ Warning: Source PDF not found: {args.source}")
        args.source = None
    
    if args.figures and not os.path.exists(args.figures):
        print(f"⚠️ Warning: Figures directory not found: {args.figures}")
        args.figures = None
    
    # Check for extraction libraries
    if args.source and not args.no_auto_extract:
        if not PYMUPDF_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            print("⚠️ No PDF extraction library available.")
            print("   Install with: pip install pymupdf --break-system-packages")
            print("   Continuing without figure extraction...")
    
    # Generate PDF
    try:
        generate_summary_pdf(
            yaml_path=args.yaml,
            output_path=args.output,
            source_pdf=args.source,
            figures_dir=args.figures,
            auto_extract=not args.no_auto_extract
        )
        return 0
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
