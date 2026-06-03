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

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from typing import Optional, Dict

# =============================================================================
# BRAND COLORS (v5.0 — Style Guide v2.3: Oklch tonal ramps)
# =============================================================================

BRAND_HEX = {
    # Brand anchor
    "brand_blue": "#2DB2E8",
    # Blue ramp
    "blue_50": "#EFFBFF",
    "blue_100": "#DBF3FF",
    "blue_200": "#B3E3FC",
    "blue_300": "#76CAF3",
    "blue_400": "#1FACE3",
    "blue_500": "#008ECB",
    "blue_600": "#006EA6",
    "blue_700": "#00507E",
    "blue_800": "#003454",
    "blue_900": "#001A2E",
    # Orange ramp
    "orange_50": "#FFF5F1",
    "orange_100": "#FFE8E0",
    "orange_200": "#FFCEBD",
    "orange_300": "#F0AA92",
    "orange_400": "#DD8363",
    "orange_500": "#C45E39",
    "orange_600": "#A0421D",
    "orange_700": "#772E11",
    "orange_800": "#4F1B06",
    "orange_900": "#2B0901",
    # Neutral ramp
    "neutral_50": "#F3FAFD",
    "neutral_100": "#E9F0F3",
    "neutral_200": "#D6DCDF",
    "neutral_300": "#B9BFC2",
    "neutral_400": "#9A9FA2",
    "neutral_500": "#7C8184",
    "neutral_600": "#5F6467",
    "neutral_700": "#44494B",
    "neutral_800": "#2A2F31",
    "neutral_900": "#121719",
    # Structure
    "black": "#000000",
    "white": "#FFFFFF",
    "gridline": "#D6DCDF",  # neutral.200
    # Deprecated v4 aliases (route to closest v2.3 equivalent)
    "dark_gray": "#121719",
    "medium_gray": "#44494B",
    "muted_gray": "#7C8184",
    "light_gray": "#B9BFC2",
    "contrast_orange": "#A0421D",
    "dark_warm": "#4F1B06",
    "medium_blue": "#008ECB",
    "dark_teal": "#003454",
}

BRAND_COLORS = {
    name: (black if hx == "#000000" else white if hx == "#FFFFFF" else HexColor(hx))
    for name, hx in BRAND_HEX.items()
}

# =============================================================================
# TYPOGRAPHY SETTINGS
# =============================================================================

FONT_FAMILY = "Helvetica"  # Arial not available in ReportLab by default
FONT_FAMILY_BOLD = "Helvetica-Bold"
FONT_FAMILY_ITALIC = "Helvetica-Oblique"

FONT_SIZES = {
    "body": 11,
    "heading1": 14,
    "heading2": 12,
    "heading3": 11,
    "caption": 10,
    "footnote": 9,
    "small": 8,
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
    styles["body"] = ParagraphStyle(
        "BrandBody",
        fontName=FONT_FAMILY,
        fontSize=FONT_SIZES["body"],
        leading=14,
        textColor=BRAND_COLORS["black"],
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )

    # Heading 1
    styles["heading1"] = ParagraphStyle(
        "BrandHeading1",
        fontName=FONT_FAMILY_BOLD,
        fontSize=FONT_SIZES["heading1"],
        leading=18,
        textColor=BRAND_COLORS["black"],
        spaceBefore=12,
        spaceAfter=6,
    )

    # Heading 2
    styles["heading2"] = ParagraphStyle(
        "BrandHeading2",
        fontName=FONT_FAMILY_BOLD,
        fontSize=FONT_SIZES["heading2"],
        leading=15,
        textColor=BRAND_COLORS["black"],
        spaceBefore=10,
        spaceAfter=4,
    )

    # Heading 3
    styles["heading3"] = ParagraphStyle(
        "BrandHeading3",
        fontName=FONT_FAMILY_BOLD,
        fontSize=FONT_SIZES["heading3"],
        leading=14,
        textColor=BRAND_COLORS["black"],
        spaceBefore=8,
        spaceAfter=4,
    )

    # Figure caption
    styles["caption"] = ParagraphStyle(
        "BrandCaption",
        fontName=FONT_FAMILY_ITALIC,
        fontSize=FONT_SIZES["caption"],
        leading=12,
        textColor=BRAND_COLORS["dark_gray"],
        alignment=TA_LEFT,
        spaceAfter=8,
    )

    # Table header
    styles["table_header"] = ParagraphStyle(
        "BrandTableHeader",
        fontName=FONT_FAMILY_BOLD,
        fontSize=FONT_SIZES["small"],
        leading=10,
        textColor=BRAND_COLORS["black"],
        alignment=TA_CENTER,
    )

    # Table cell
    styles["table_cell"] = ParagraphStyle(
        "BrandTableCell",
        fontName=FONT_FAMILY,
        fontSize=FONT_SIZES["small"],
        leading=10,
        textColor=BRAND_COLORS["black"],
        alignment=TA_LEFT,
    )

    # Footnote
    styles["footnote"] = ParagraphStyle(
        "BrandFootnote",
        fontName=FONT_FAMILY,
        fontSize=FONT_SIZES["footnote"],
        leading=11,
        textColor=BRAND_COLORS["medium_gray"],
    )

    # Title
    styles["title"] = ParagraphStyle(
        "BrandTitle",
        fontName=FONT_FAMILY_BOLD,
        fontSize=18,
        leading=22,
        textColor=BRAND_COLORS["black"],
        alignment=TA_LEFT,
        spaceAfter=12,
    )

    # Subtitle
    styles["subtitle"] = ParagraphStyle(
        "BrandSubtitle",
        fontName=FONT_FAMILY,
        fontSize=12,
        leading=14,
        textColor=BRAND_COLORS["medium_gray"],
        alignment=TA_LEFT,
        spaceAfter=20,
    )

    return styles


# =============================================================================
# TABLE STYLES
# =============================================================================


def get_brand_table_style(
    header_bg: str = "light_gray", alt_row_bg: Optional[str] = None
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
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            BRAND_COLORS.get(header_bg, BRAND_COLORS["light_gray"]),
        ),
        ("TEXTCOLOR", (0, 0), (-1, 0), BRAND_COLORS["black"]),
        ("FONTNAME", (0, 0), (-1, 0), FONT_FAMILY_BOLD),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        # Body rows
        ("FONTNAME", (0, 1), (-1, -1), FONT_FAMILY),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TEXTCOLOR", (0, 1), (-1, -1), BRAND_COLORS["black"]),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        # Alignment
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, BRAND_COLORS["gridline"]),
        ("LINEBELOW", (0, 0), (-1, 0), 1, BRAND_COLORS["black"]),
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
    return TableStyle(
        [
            # Header
            ("FONTNAME", (0, 0), (-1, 0), FONT_FAMILY_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("TEXTCOLOR", (0, 0), (-1, 0), BRAND_COLORS["black"]),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("LINEBELOW", (0, 0), (-1, 0), 1, BRAND_COLORS["black"]),
            # Body
            ("FONTNAME", (0, 1), (-1, -1), FONT_FAMILY),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (-1, -1), BRAND_COLORS["black"]),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("LINEBELOW", (0, 1), (-1, -1), 0.5, BRAND_COLORS["gridline"]),
            # Alignment
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
    )


# =============================================================================
# DOCUMENT CREATION
# =============================================================================


def create_brand_document(
    filename: str,
    pagesize: tuple = letter,
    margins: tuple = (0.75 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch),
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


def brand_spacer(height: float = 0.25 * inch) -> Spacer:
    """Create a spacer with brand-appropriate height."""
    return Spacer(1, height)


def brand_page_break() -> PageBreak:
    """Create a page break."""
    return PageBreak()


def highlight_text(text: str, color: str = "brand_blue") -> str:
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
    hex_color = BRAND_HEX.get(color, "#2DB2E8")
    return f'<font color="{hex_color}">{text}</font>'


def bold_text(text: str) -> str:
    """Wrap text in bold tags."""
    return f"<b>{text}</b>"


def italic_text(text: str) -> str:
    """Wrap text in italic tags."""
    return f"<i>{text}</i>"


# =============================================================================
# LOGO & HEADER HELPERS
# =============================================================================

# Default location for skill-bundled logos. Resolved relative to this file so
# the adapter works regardless of the consumer's CWD.
import os as _os

_ADAPTER_DIR = _os.path.dirname(_os.path.abspath(__file__))
DEFAULT_LOGO_DIR = _os.path.normpath(
    _os.path.join(_ADAPTER_DIR, "..", "assets", "logos")
)
DEFAULT_LOGO_PATH = _os.path.join(DEFAULT_LOGO_DIR, "Oligon_Logo_BrandBlue.svg")


def brand_logo(
    path: Optional[str] = None,
    width_inches: float = 1.2,
    prefer: str = "vector",
):
    """
    Return a flowable Oligon logo for a ReportLab story.

    Embeds the SVG as true vector geometry via svglib + svg2rlg (prints at any
    size without pixelation). Falls back to a high-DPI raster (4x target, via
    cairosvg) if svglib is not available. Raises RuntimeError if neither is
    installed.

    Parameters
    ----------
    path : str, optional
        Path to an SVG logo. Defaults to the skill-bundled
        `Oligon_Logo_BrandBlue.svg`. Any logo under `assets/logos/` is valid.
    width_inches : float
        Target rendered width in inches. Height scales proportionally from the
        source SVG's aspect ratio.
    prefer : {'vector', 'raster'}
        'vector' (default) uses svglib; 'raster' forces high-DPI PNG via
        cairosvg. Raster fallback runs automatically if svglib is unavailable.

    Returns
    -------
    flowable
        A ReportLab `Drawing` (vector) or `Image` (raster) flowable, ready to
        drop into a story list or Table cell.

    Examples
    --------
    >>> story.append(brand_logo(width_inches=1.5))
    >>> story.append(brand_logo(path='assets/logos/Oligon_Icon_White.svg',
    ...                         width_inches=0.5))
    """
    logo_path = path or DEFAULT_LOGO_PATH
    if not _os.path.exists(logo_path):
        raise FileNotFoundError(
            f"Logo not found: {logo_path}. "
            f"Check `oligon-brand-core/assets/logos/` or pass an explicit path."
        )

    target_width_pt = width_inches * inch

    # Try vector first (the right answer — never pixelates)
    if prefer == "vector":
        try:
            from svglib.svglib import svg2rlg

            drawing = svg2rlg(logo_path)
            if drawing is None:
                raise RuntimeError(f"svg2rlg returned None for {logo_path}")
            scale = target_width_pt / drawing.width
            drawing.width *= scale
            drawing.height *= scale
            drawing.scale(scale, scale)
            return drawing
        except ImportError:
            pass  # fall through to raster

    # Raster fallback — render at 4x target width for print-quality density
    try:
        import cairosvg
        from io import BytesIO

        # 4x for retina + print headroom; ReportLab will downscale in layout
        render_px = int(target_width_pt * 4)
        png_bytes = cairosvg.svg2png(url=logo_path, output_width=render_px)
        img = Image(BytesIO(png_bytes), width=target_width_pt)
        # Preserve aspect ratio by letting ReportLab compute height from image
        img._restrictSize(target_width_pt, 10 * inch)
        return img
    except ImportError as e:
        raise RuntimeError(
            "brand_logo() needs either `svglib` (preferred, vector) or "
            "`cairosvg` (raster fallback). Install one: "
            "`pip install svglib` or `pip install cairosvg`."
        ) from e


def brand_header(
    title: str,
    subtitle: Optional[str] = None,
    logo_path: Optional[str] = None,
    logo_width_inches: float = 1.2,
    page_width_inches: float = 7.0,
    divider: bool = True,
):
    """
    A branded header strip: logo on the left, title (and optional subtitle)
    on the right, optional brand-blue divider rule underneath.

    Enforces generous padding so the logo and title never collide — the
    failure mode from iteration-1's ad-hoc header. Use this instead of
    hand-rolling a Table([logo, title]).

    Parameters
    ----------
    title : str
        Main document title. Rendered in brand.blue, 18 pt, bold.
    subtitle : str, optional
        Eyebrow or subtitle, rendered in neutral.700, 11 pt, uppercase
        letter-spacing. Sits above the title if provided.
    logo_path : str, optional
        SVG logo path. Defaults to `Oligon_Logo_BrandBlue.svg`.
    logo_width_inches : float
        Logo render width. Default 1.2 in.
    page_width_inches : float
        Usable page width (letter minus default 0.75" margins = 7.0 in).
    divider : bool
        If True, append a 1 pt brand.blue horizontal rule below the header.

    Returns
    -------
    list of flowables
        A list you can extend into your story: `story.extend(brand_header(...))`.
    """
    from reportlab.platypus import HRFlowable

    styles = get_brand_styles()
    logo_flowable = brand_logo(path=logo_path, width_inches=logo_width_inches)

    # Right-side text stack (subtitle + title)
    text_parts = []
    if subtitle:
        subtitle_html = (
            f'<font color="{BRAND_HEX["neutral_700"]}" size="10">'
            f"<b>{subtitle.upper()}</b></font>"
        )
        text_parts.append(Paragraph(subtitle_html, styles["body"]))
    title_html = (
        f'<font color="{BRAND_HEX["brand_blue"]}" size="18"><b>{title}</b></font>'
    )
    text_parts.append(Paragraph(title_html, styles["body"]))

    # Two-column table: logo | text. Fixed-width logo column with 24pt right-
    # padding means the title can never visually collide with the mark.
    logo_col_width = (logo_width_inches + 0.35) * inch  # logo + gap
    title_col_width = page_width_inches * inch - logo_col_width

    header_tbl = Table(
        [[logo_flowable, text_parts]],
        colWidths=[logo_col_width, title_col_width],
    )
    header_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 24),  # generous gap after logo
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    out = [header_tbl, brand_spacer(0.12 * inch)]
    if divider:
        out.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=HexColor(BRAND_HEX["brand_blue"]),
            )
        )
        out.append(brand_spacer(0.18 * inch))
    return out


# =============================================================================
# EXAMPLE USAGE
# =============================================================================


def create_example_report():
    """Create an example report demonstrating brand styles."""
    doc = create_brand_document("example_brand_report.pdf")
    styles = get_brand_styles()
    story = []

    # Title
    story.append(Paragraph("Oligon Scientific Report", styles["title"]))
    story.append(
        Paragraph("Demonstrating Brand-Compliant PDF Generation", styles["subtitle"])
    )

    # Section 1
    story.append(Paragraph("Introduction", styles["heading1"]))
    story.append(
        Paragraph(
            "This document demonstrates the use of Oligon brand guidelines "
            "in PDF generation using ReportLab. All colors, fonts, and spacing "
            "follow the brand specification.",
            styles["body"],
        )
    )

    story.append(brand_spacer())

    # Section 2 with highlighted text
    story.append(Paragraph("Key Findings", styles["heading2"]))
    story.append(
        Paragraph(
            f"The {highlight_text('treatment group')} showed significant improvement "
            f"compared to the {bold_text('control group')} (p < 0.05).",
            styles["body"],
        )
    )

    # Table
    story.append(brand_spacer())
    story.append(Paragraph("Results Summary", styles["heading2"]))

    data = [
        ["Group", "N", "Mean", "SD", "p-value"],
        ["Control", "25", "4.2", "1.1", "-"],
        ["Treatment", "25", "6.8", "0.9", "<0.001"],
    ]

    table = Table(
        data, colWidths=[1.5 * inch, 0.75 * inch, 1 * inch, 0.75 * inch, 1 * inch]
    )
    table.setStyle(get_brand_table_style())
    story.append(table)

    story.append(brand_spacer())
    story.append(
        Paragraph(
            "Table 1. Summary statistics for treatment comparison.", styles["caption"]
        )
    )

    # Build document
    doc.build(story)
    print("Example report created: example_brand_report.pdf")


if __name__ == "__main__":
    create_example_report()
