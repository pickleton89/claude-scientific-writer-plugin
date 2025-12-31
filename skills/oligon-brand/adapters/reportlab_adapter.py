"""
Oligon Brand Adapter for ReportLab PDF Generation

This module provides constants, styles, and helper functions for creating
PDFs with Oligon scientific brand identity using ReportLab.

Usage:
    from oligon_brand.adapters.reportlab_adapter import (
        BRAND_COLORS,
        get_brand_styles,
        create_brand_document,
        BrandParagraphStyle
    )

    # Create a branded PDF
    doc = create_brand_document("output.pdf")
    styles = get_brand_styles()
    # ... add content
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, pt
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from typing import Optional, List, Dict, Any

# =============================================================================
# BRAND COLORS
# =============================================================================

BRAND_COLORS = {
    # Primary highlight
    'brand_blue': HexColor('#2DB2E8'),

    # Neutrals
    'dark_gray': HexColor('#222222'),
    'medium_gray': HexColor('#666666'),
    'muted_gray': HexColor('#999999'),
    'light_gray': HexColor('#BDBDBD'),

    # Contrast
    'contrast_orange': HexColor('#E8622D'),
    'dark_warm': HexColor('#7D250F'),

    # Supporting blues
    'medium_blue': HexColor('#158BBB'),
    'dark_teal': HexColor('#0F5D7D'),

    # Structure
    'black': black,
    'white': white,
    'gridline': HexColor('#E5E5E5'),
}

# Hex strings for convenience
BRAND_HEX = {
    'brand_blue': '#2DB2E8',
    'dark_gray': '#222222',
    'medium_gray': '#666666',
    'muted_gray': '#999999',
    'light_gray': '#BDBDBD',
    'contrast_orange': '#E8622D',
    'dark_warm': '#7D250F',
    'medium_blue': '#158BBB',
    'dark_teal': '#0F5D7D',
    'black': '#000000',
    'white': '#FFFFFF',
    'gridline': '#E5E5E5',
}

# =============================================================================
# TYPOGRAPHY SETTINGS
# =============================================================================

FONT_FAMILY = 'Helvetica'  # Arial not available in ReportLab by default
FONT_FAMILY_BOLD = 'Helvetica-Bold'
FONT_FAMILY_ITALIC = 'Helvetica-Oblique'

FONT_SIZES = {
    'body': 11,
    'heading1': 14,
    'heading2': 12,
    'heading3': 11,
    'caption': 10,
    'footnote': 9,
    'small': 8,
}

# =============================================================================
# PARAGRAPH STYLES
# =============================================================================

def get_brand_styles() -> Dict[str, ParagraphStyle]:
    """
    Get a dictionary of brand-compliant paragraph styles.

    Returns
    -------
    dict
        Dictionary mapping style names to ParagraphStyle objects.

    Examples
    --------
    >>> styles = get_brand_styles()
    >>> para = Paragraph("Hello World", styles['body'])
    """
    styles = {}

    # Body text
    styles['body'] = ParagraphStyle(
        'BrandBody',
        fontName=FONT_FAMILY,
        fontSize=FONT_SIZES['body'],
        leading=14,
        textColor=BRAND_COLORS['black'],
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )

    # Heading 1
    styles['heading1'] = ParagraphStyle(
        'BrandHeading1',
        fontName=FONT_FAMILY_BOLD,
        fontSize=FONT_SIZES['heading1'],
        leading=18,
        textColor=BRAND_COLORS['black'],
        spaceBefore=12,
        spaceAfter=6,
    )

    # Heading 2
    styles['heading2'] = ParagraphStyle(
        'BrandHeading2',
        fontName=FONT_FAMILY_BOLD,
        fontSize=FONT_SIZES['heading2'],
        leading=15,
        textColor=BRAND_COLORS['black'],
        spaceBefore=10,
        spaceAfter=4,
    )

    # Heading 3
    styles['heading3'] = ParagraphStyle(
        'BrandHeading3',
        fontName=FONT_FAMILY_BOLD,
        fontSize=FONT_SIZES['heading3'],
        leading=14,
        textColor=BRAND_COLORS['black'],
        spaceBefore=8,
        spaceAfter=4,
    )

    # Figure caption
    styles['caption'] = ParagraphStyle(
        'BrandCaption',
        fontName=FONT_FAMILY_ITALIC,
        fontSize=FONT_SIZES['caption'],
        leading=12,
        textColor=BRAND_COLORS['dark_gray'],
        alignment=TA_LEFT,
        spaceAfter=8,
    )

    # Table header
    styles['table_header'] = ParagraphStyle(
        'BrandTableHeader',
        fontName=FONT_FAMILY_BOLD,
        fontSize=FONT_SIZES['small'],
        leading=10,
        textColor=BRAND_COLORS['black'],
        alignment=TA_CENTER,
    )

    # Table cell
    styles['table_cell'] = ParagraphStyle(
        'BrandTableCell',
        fontName=FONT_FAMILY,
        fontSize=FONT_SIZES['small'],
        leading=10,
        textColor=BRAND_COLORS['black'],
        alignment=TA_LEFT,
    )

    # Footnote
    styles['footnote'] = ParagraphStyle(
        'BrandFootnote',
        fontName=FONT_FAMILY,
        fontSize=FONT_SIZES['footnote'],
        leading=11,
        textColor=BRAND_COLORS['medium_gray'],
    )

    # Title
    styles['title'] = ParagraphStyle(
        'BrandTitle',
        fontName=FONT_FAMILY_BOLD,
        fontSize=18,
        leading=22,
        textColor=BRAND_COLORS['black'],
        alignment=TA_LEFT,
        spaceAfter=12,
    )

    # Subtitle
    styles['subtitle'] = ParagraphStyle(
        'BrandSubtitle',
        fontName=FONT_FAMILY,
        fontSize=12,
        leading=14,
        textColor=BRAND_COLORS['medium_gray'],
        alignment=TA_LEFT,
        spaceAfter=20,
    )

    return styles


# =============================================================================
# TABLE STYLES
# =============================================================================

def get_brand_table_style(
    header_bg: str = 'light_gray',
    alt_row_bg: Optional[str] = None
) -> TableStyle:
    """
    Get a brand-compliant table style.

    Parameters
    ----------
    header_bg : str
        Background color name for header row
    alt_row_bg : str, optional
        Background color for alternating rows (zebra striping)

    Returns
    -------
    TableStyle
        ReportLab TableStyle object

    Examples
    --------
    >>> style = get_brand_table_style()
    >>> table = Table(data)
    >>> table.setStyle(style)
    """
    commands = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLORS.get(header_bg, BRAND_COLORS['light_gray'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), BRAND_COLORS['black']),
        ('FONTNAME', (0, 0), (-1, 0), FONT_FAMILY_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Body rows
        ('FONTNAME', (0, 1), (-1, -1), FONT_FAMILY),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), BRAND_COLORS['black']),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),

        # Alignment
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, BRAND_COLORS['gridline']),
        ('LINEBELOW', (0, 0), (-1, 0), 1, BRAND_COLORS['black']),
    ]

    return TableStyle(commands)


def get_brand_table_style_minimal() -> TableStyle:
    """
    Get a minimal table style (no vertical lines, only horizontal separators).

    Returns
    -------
    TableStyle
        Minimal ReportLab TableStyle object
    """
    return TableStyle([
        # Header
        ('FONTNAME', (0, 0), (-1, 0), FONT_FAMILY_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), BRAND_COLORS['black']),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1, BRAND_COLORS['black']),

        # Body
        ('FONTNAME', (0, 1), (-1, -1), FONT_FAMILY),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), BRAND_COLORS['black']),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, BRAND_COLORS['gridline']),

        # Alignment
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])


# =============================================================================
# DOCUMENT CREATION
# =============================================================================

def create_brand_document(
    filename: str,
    pagesize: tuple = letter,
    margins: tuple = (0.75*inch, 0.75*inch, 0.75*inch, 0.75*inch)
) -> SimpleDocTemplate:
    """
    Create a SimpleDocTemplate with brand-compliant settings.

    Parameters
    ----------
    filename : str
        Output PDF filename
    pagesize : tuple
        Page size (default: letter)
    margins : tuple
        (left, right, top, bottom) margins in points

    Returns
    -------
    SimpleDocTemplate
        Configured document template

    Examples
    --------
    >>> doc = create_brand_document("report.pdf")
    >>> styles = get_brand_styles()
    >>> story = [Paragraph("Hello", styles['heading1'])]
    >>> doc.build(story)
    """
    left, right, top, bottom = margins

    return SimpleDocTemplate(
        filename,
        pagesize=pagesize,
        leftMargin=left,
        rightMargin=right,
        topMargin=top,
        bottomMargin=bottom,
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def brand_spacer(height: float = 0.25*inch) -> Spacer:
    """Create a spacer with brand-appropriate height."""
    return Spacer(1, height)


def brand_page_break() -> PageBreak:
    """Create a page break."""
    return PageBreak()


def highlight_text(text: str, color: str = 'brand_blue') -> str:
    """
    Wrap text in a font tag with brand color.

    Parameters
    ----------
    text : str
        Text to highlight
    color : str
        Brand color name

    Returns
    -------
    str
        HTML-formatted string for ReportLab Paragraph
    """
    hex_color = BRAND_HEX.get(color, '#2DB2E8')
    return f'<font color="{hex_color}">{text}</font>'


def bold_text(text: str) -> str:
    """Wrap text in bold tags."""
    return f'<b>{text}</b>'


def italic_text(text: str) -> str:
    """Wrap text in italic tags."""
    return f'<i>{text}</i>'


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def create_example_report():
    """Create an example report demonstrating brand styles."""
    doc = create_brand_document("example_brand_report.pdf")
    styles = get_brand_styles()
    story = []

    # Title
    story.append(Paragraph("Oligon Scientific Report", styles['title']))
    story.append(Paragraph("Demonstrating Brand-Compliant PDF Generation", styles['subtitle']))

    # Section 1
    story.append(Paragraph("Introduction", styles['heading1']))
    story.append(Paragraph(
        "This document demonstrates the use of Oligon brand guidelines "
        "in PDF generation using ReportLab. All colors, fonts, and spacing "
        "follow the brand specification.",
        styles['body']
    ))

    story.append(brand_spacer())

    # Section 2 with highlighted text
    story.append(Paragraph("Key Findings", styles['heading2']))
    story.append(Paragraph(
        f"The {highlight_text('treatment group')} showed significant improvement "
        f"compared to the {bold_text('control group')} (p < 0.05).",
        styles['body']
    ))

    # Table
    story.append(brand_spacer())
    story.append(Paragraph("Results Summary", styles['heading2']))

    data = [
        ['Group', 'N', 'Mean', 'SD', 'p-value'],
        ['Control', '25', '4.2', '1.1', '-'],
        ['Treatment', '25', '6.8', '0.9', '<0.001'],
    ]

    table = Table(data, colWidths=[1.5*inch, 0.75*inch, 1*inch, 0.75*inch, 1*inch])
    table.setStyle(get_brand_table_style())
    story.append(table)

    story.append(brand_spacer())
    story.append(Paragraph(
        "Table 1. Summary statistics for treatment comparison.",
        styles['caption']
    ))

    # Build document
    doc.build(story)
    print("Example report created: example_brand_report.pdf")


if __name__ == "__main__":
    create_example_report()
