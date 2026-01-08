"""
Type stubs for brand adapter interface.

Brand adapters MUST implement the required protocol to be compatible
with the skill library. Use this file for static type checking.

Usage:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from brand_interface.type_stubs.adapter_interface import BrandAdapterProtocol

    def validate_adapter(adapter: BrandAdapterProtocol) -> bool:
        ...
"""

from typing import Protocol, Literal, Optional, runtime_checkable
from matplotlib.axes import Axes
from matplotlib.colors import Colormap
from matplotlib.lines import Line2D
from numpy.typing import ArrayLike


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

CycleType = Literal[
    'default',
    'treatment_control',
    'neutrals_only',
    'opposing',
    'multi_category'
]

BrandType = Literal['organizational', 'personal', 'institutional', 'journal', 'generic']


# =============================================================================
# REQUIRED PROTOCOL
# =============================================================================

@runtime_checkable
class BrandAdapterProtocol(Protocol):
    """
    Protocol defining the required interface for matplotlib brand adapters.

    All brand adapters MUST implement these members to be compatible
    with the skill library (e.g., plotting-libraries skill).
    """

    # Required constant: color name -> hex mapping
    BRAND_COLORS: dict[str, str]

    def set_brand_style(self, cycle: str = 'default') -> None:
        """
        Apply brand rcParams to matplotlib.

        Parameters
        ----------
        cycle : str
            Name of the color cycle to use as default.
            Must match a key in the brand's color_cycles.
        """
        ...

    def get_cycle(self, name: str) -> list[str]:
        """
        Return color cycle by name.

        Parameters
        ----------
        name : str
            Cycle name (e.g., 'treatment_control', 'opposing')

        Returns
        -------
        list[str]
            List of hex color strings in cycle order.
        """
        ...

    def get_color(self, name: str) -> str:
        """
        Return single color hex value by name.

        Parameters
        ----------
        name : str
            Color name (e.g., 'brand_blue', 'dark_gray')

        Returns
        -------
        str
            Hex color string (e.g., '#2DB2E8')
        """
        ...


# =============================================================================
# OPTIONAL EXTENSIONS
# =============================================================================

class BrandAdapterOptionalProtocol(BrandAdapterProtocol, Protocol):
    """
    Extended protocol with optional functions that brand adapters MAY implement.

    These provide additional functionality for specialized visualizations.
    """

    def get_divergent_cmap(self, name: str = 'default') -> Colormap:
        """
        Return divergent colormap for heatmaps.

        Parameters
        ----------
        name : str
            Colormap name (typically just 'default')

        Returns
        -------
        matplotlib.colors.Colormap
            LinearSegmentedColormap suitable for data centered at zero.
        """
        ...

    def add_panel_label(
        self,
        ax: Axes,
        label: str,
        offset: tuple[float, float] = (-0.12, 1.05),
        fontsize: int = 10,
        fontweight: str = 'bold'
    ) -> None:
        """
        Add panel label (A, B, C...) to axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to label
        label : str
            Label text (e.g., 'A', 'B')
        offset : tuple
            (x, y) offset in axes coordinates
        fontsize : int
            Font size in points
        fontweight : str
            Font weight
        """
        ...

    def add_error_band(
        self,
        ax: Axes,
        x: ArrayLike,
        y: ArrayLike,
        yerr: ArrayLike | tuple[ArrayLike, ArrayLike],
        color: str,
        alpha: float = 0.25,
        label: Optional[str] = None
    ) -> Line2D:
        """
        Add semi-transparent error band around a line.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to plot on
        x : array-like
            X values
        y : array-like
            Y values (center line)
        yerr : array-like or tuple
            Error values. If tuple, (lower, upper) errors.
        color : str
            Hex color for line and band
        alpha : float
            Band opacity
        label : str, optional
            Legend label

        Returns
        -------
        matplotlib.lines.Line2D
            The line object
        """
        ...


# =============================================================================
# R ADAPTER INTERFACE (DOCUMENTATION)
# =============================================================================

# R adapters should export these functions (cannot be type-checked from Python):
#
# theme_<brand>() -> ggplot2::theme
#     Returns theme object with brand styling
#
# scale_color_<brand>(cycle = 'default') -> ggplot2::scale_color_manual
#     Returns color scale with brand colors
#
# scale_fill_<brand>(cycle = 'default') -> ggplot2::scale_fill_manual
#     Returns fill scale with brand colors
#
# BRAND_COLORS <- c(primary = "#XXXXXX", ...)
#     Named vector of brand colors


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

# Note: These functions are type stubs for future implementation.
# For current validation, use validate_brand.py which performs AST-based checking.

def is_valid_adapter(adapter: object) -> bool:
    """
    Check if an object implements the required BrandAdapterProtocol.

    Parameters
    ----------
    adapter : object
        Module or object to validate

    Returns
    -------
    bool
        True if adapter implements required interface
    """
    ...


def get_missing_members(adapter: object) -> list[str]:
    """
    Get list of missing required protocol members.

    Parameters
    ----------
    adapter : object
        Module or object to check

    Returns
    -------
    list[str]
        Names of missing required members
    """
    ...
