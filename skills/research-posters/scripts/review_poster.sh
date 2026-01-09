#!/bin/bash

# Poster PDF Quality Check Script
# Usage: ./review_poster.sh poster.pdf

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if file argument provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No file specified${NC}"
    echo "Usage: $0 <poster.pdf>"
    exit 1
fi

POSTER_FILE="$1"

# Check if file exists
if [ ! -f "$POSTER_FILE" ]; then
    echo -e "${RED}Error: File '$POSTER_FILE' not found${NC}"
    exit 1
fi

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Poster PDF Quality Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}File:${NC} $POSTER_FILE"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Page Size Check
echo -e "${YELLOW}[1] Page Dimensions:${NC}"
if command_exists pdfinfo; then
    PAGE_SIZE=$(pdfinfo "$POSTER_FILE" 2>/dev/null | grep "Page size")
    if [ -n "$PAGE_SIZE" ]; then
        echo "    $PAGE_SIZE"
        
        # Extract dimensions and check common sizes
        WIDTH=$(echo "$PAGE_SIZE" | awk '{print $3}')
        HEIGHT=$(echo "$PAGE_SIZE" | awk '{print $5}')
        
        # Check against common poster sizes (approximate)
        if [ "$WIDTH" = "2384" ] && [ "$HEIGHT" = "3370" ]; then
            echo -e "    ${GREEN}✓ Detected: A0 Portrait${NC}"
        elif [ "$WIDTH" = "3370" ] && [ "$HEIGHT" = "2384" ]; then
            echo -e "    ${GREEN}✓ Detected: A0 Landscape${NC}"
        elif [ "$WIDTH" = "1684" ] && [ "$HEIGHT" = "2384" ]; then
            echo -e "    ${GREEN}✓ Detected: A1 Portrait${NC}"
        elif [ "$WIDTH" = "2592" ] && [ "$HEIGHT" = "3456" ]; then
            echo -e "    ${GREEN}✓ Detected: 36×48 inches Portrait${NC}"
        else
            echo -e "    ${YELLOW}⚠ Non-standard size detected${NC}"
        fi
    else
        echo -e "    ${RED}✗ Could not extract page size${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ pdfinfo not installed (install: brew install poppler or apt-get install poppler-utils)${NC}"
fi
echo ""

# 2. Page Count
echo -e "${YELLOW}[2] Page Count:${NC}"
if command_exists pdfinfo; then
    PAGE_COUNT=$(pdfinfo "$POSTER_FILE" 2>/dev/null | grep "Pages" | awk '{print $2}')
    if [ "$PAGE_COUNT" = "1" ]; then
        echo -e "    ${GREEN}✓ Single page (correct for poster)${NC}"
    else
        echo -e "    ${RED}✗ Multiple pages detected: $PAGE_COUNT${NC}"
        echo -e "    ${YELLOW}  Posters should be single page${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ pdfinfo not installed${NC}"
fi
echo ""

# 3. File Size
echo -e "${YELLOW}[3] File Size:${NC}"
if command_exists ls; then
    FILE_SIZE=$(ls -lh "$POSTER_FILE" | awk '{print $5}')
    FILE_SIZE_BYTES=$(ls -l "$POSTER_FILE" | awk '{print $5}')
    echo "    Size: $FILE_SIZE"
    
    # Check if file is too large for email
    if [ "$FILE_SIZE_BYTES" -gt 52428800 ]; then  # 50MB
        echo -e "    ${YELLOW}⚠ Large file (>50MB) - may need compression for email${NC}"
        echo -e "    ${BLUE}  Compress with: gs -sDEVICE=pdfwrite -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH -sOutputFile=compressed.pdf $POSTER_FILE${NC}"
    elif [ "$FILE_SIZE_BYTES" -lt 1048576 ]; then  # 1MB
        echo -e "    ${YELLOW}⚠ Small file - check image quality${NC}"
    else
        echo -e "    ${GREEN}✓ Reasonable file size${NC}"
    fi
fi
echo ""

# 4. Font Embedding Check
echo -e "${YELLOW}[4] Font Embedding:${NC}"
if command_exists pdffonts; then
    echo "    Checking first 20 fonts..."
    FONT_OUTPUT=$(pdffonts "$POSTER_FILE" 2>/dev/null | head -21)
    echo "$FONT_OUTPUT" | tail -20 | while IFS= read -r line; do
        echo "    $line"
    done
    
    # Check for non-embedded fonts
    NON_EMBEDDED=$(echo "$FONT_OUTPUT" | tail -n +3 | awk '{if ($4 == "no") print $0}')
    if [ -n "$NON_EMBEDDED" ]; then
        echo -e "    ${RED}✗ Some fonts are NOT embedded (printing may fail)${NC}"
        echo -e "    ${BLUE}  Fix: Recompile with 'pdflatex -dEmbedAllFonts=true poster.tex'${NC}"
    else
        echo -e "    ${GREEN}✓ All fonts appear to be embedded${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ pdffonts not installed (install: brew install poppler or apt-get install poppler-utils)${NC}"
fi
echo ""

# 5. Image Quality Check
echo -e "${YELLOW}[5] Image Quality:${NC}"
if command_exists pdfimages; then
    IMAGE_COUNT=$(pdfimages -list "$POSTER_FILE" 2>/dev/null | tail -n +3 | wc -l | tr -d ' ')
    if [ "$IMAGE_COUNT" -gt 0 ]; then
        echo "    Found $IMAGE_COUNT image(s)"
        echo "    Image details:"
        pdfimages -list "$POSTER_FILE" 2>/dev/null | head -20
        
        # Note: DPI calculation would require page size knowledge
        echo -e "    ${BLUE}  Verify images are at least 300 DPI for printing${NC}"
        echo -e "    ${BLUE}  Formula: DPI = pixels / (inches in poster)${NC}"
    else
        echo -e "    ${YELLOW}⚠ No images found${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ pdfimages not installed (install: brew install poppler or apt-get install poppler-utils)${NC}"
fi
echo ""

# 6. Word Count Check
echo -e "${YELLOW}[6] Word Count:${NC}"
TEX_FILE="${POSTER_FILE%.pdf}.tex"
if [ -f "$TEX_FILE" ]; then
    if command_exists texcount; then
        WORD_COUNT=$(texcount -inc -sum -brief "$TEX_FILE" 2>/dev/null | grep -oE '^[0-9]+' | head -1)
        if [ -n "$WORD_COUNT" ]; then
            echo "    Total words: $WORD_COUNT"
            if [ "$WORD_COUNT" -gt 800 ]; then
                echo -e "    ${RED}✗ Exceeds 800 word maximum (too verbose for poster)${NC}"
            elif [ "$WORD_COUNT" -lt 300 ]; then
                echo -e "    ${YELLOW}⚠ Below 300 word minimum (may lack detail)${NC}"
            elif [ "$WORD_COUNT" -ge 400 ] && [ "$WORD_COUNT" -le 600 ]; then
                echo -e "    ${GREEN}✓ Ideal range (400-600 words)${NC}"
            else
                echo -e "    ${GREEN}✓ Within acceptable range (300-800)${NC}"
            fi
        else
            echo -e "    ${YELLOW}⚠ Could not parse word count${NC}"
        fi
    else
        echo -e "    ${YELLOW}⚠ texcount not installed (install: brew install texcount or apt-get install texcount)${NC}"
        # Fallback: rough word count from tex file
        ROUGH_COUNT=$(grep -v '^%' "$TEX_FILE" | grep -v '\\' | wc -w | tr -d ' ')
        if [ "$ROUGH_COUNT" -gt 0 ]; then
            echo "    Rough estimate (from non-command text): ~$ROUGH_COUNT words"
        fi
    fi
else
    echo -e "    ${YELLOW}⚠ Source .tex file not found: $TEX_FILE${NC}"
fi
echo ""

# 7. LaTeX Compilation Warnings
echo -e "${YELLOW}[7] LaTeX Compilation Warnings:${NC}"
LOG_FILE="${POSTER_FILE%.pdf}.log"
if [ -f "$LOG_FILE" ]; then
    OVERFULL=$(grep -c "Overfull" "$LOG_FILE" 2>/dev/null || echo "0")
    UNDERFULL=$(grep -c "Underfull" "$LOG_FILE" 2>/dev/null || echo "0")
    WARNINGS=$(grep -c "Warning" "$LOG_FILE" 2>/dev/null || echo "0")
    ERRORS=$(grep -c "^!" "$LOG_FILE" 2>/dev/null || echo "0")

    echo "    Errors: $ERRORS"
    echo "    Overfull boxes: $OVERFULL"
    echo "    Underfull boxes: $UNDERFULL"
    echo "    Other warnings: $WARNINGS"

    if [ "$ERRORS" -gt 0 ]; then
        echo -e "    ${RED}✗ LaTeX errors found - review log file${NC}"
        echo "    First error:"
        grep -A 2 "^!" "$LOG_FILE" 2>/dev/null | head -3 | while IFS= read -r line; do
            echo "      $line"
        done
    elif [ "$OVERFULL" -gt 10 ] || [ "$UNDERFULL" -gt 10 ]; then
        echo -e "    ${YELLOW}⚠ Many box warnings - review spacing${NC}"
    else
        echo -e "    ${GREEN}✓ Acceptable warning count${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ Log file not found: $LOG_FILE${NC}"
fi
echo ""

# 8. QR Code Detection
echo -e "${YELLOW}[8] QR Code Presence:${NC}"
if command_exists zbarimg; then
    QR_CONTENT=$(zbarimg --quiet "$POSTER_FILE" 2>/dev/null)
    QR_COUNT=$(echo "$QR_CONTENT" | grep -c "QR-Code" || echo "0")
    if [ "$QR_COUNT" -gt 0 ]; then
        echo -e "    ${GREEN}✓ QR code(s) detected: $QR_COUNT found${NC}"
        echo "    QR code content:"
        echo "$QR_CONTENT" | head -5 | while IFS= read -r line; do
            echo "      $line"
        done
    else
        echo -e "    ${YELLOW}⚠ No QR code detected${NC}"
        echo -e "    ${BLUE}  Consider adding QR code linking to paper/data/contact${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ zbarimg not installed (install: brew install zbar or apt-get install zbar-tools)${NC}"
fi
echo ""

# 9. Python Validation (if available)
echo -e "${YELLOW}[9] Python Validation:${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE_SCRIPT="$SCRIPT_DIR/validate_poster.py"
if [ -f "$VALIDATE_SCRIPT" ]; then
    if command_exists python3; then
        if [ -f "$TEX_FILE" ]; then
            echo "    Running comprehensive validation..."
            VALIDATION_OUTPUT=$(python3 "$VALIDATE_SCRIPT" "$TEX_FILE" "$POSTER_FILE" --json 2>/dev/null)
            if [ $? -eq 0 ]; then
                OVERALL_PASS=$(echo "$VALIDATION_OUTPUT" | grep -o '"overall_pass": true' || echo "")
                if [ -n "$OVERALL_PASS" ]; then
                    echo -e "    ${GREEN}✓ All automated checks passed${NC}"
                else
                    echo -e "    ${RED}✗ Some automated checks failed${NC}"
                    echo -e "    ${BLUE}  Run: python3 $VALIDATE_SCRIPT $TEX_FILE $POSTER_FILE${NC}"
                fi
            else
                echo -e "    ${YELLOW}⚠ Validation script encountered an error${NC}"
            fi
        else
            echo -e "    ${YELLOW}⚠ Skipped - requires .tex source file${NC}"
        fi
    else
        echo -e "    ${YELLOW}⚠ python3 not available${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ validate_poster.py not found${NC}"
fi
echo ""

# 10. Manual Checks Required
echo -e "${YELLOW}[10] Manual Visual Inspection Required:${NC}"
echo ""
echo -e "${BLUE}Layout and Spacing:${NC}"
echo "    [ ] Content fills entire page (no large white margins)"
echo "    [ ] Consistent spacing between columns"
echo "    [ ] Consistent spacing between blocks/sections"
echo "    [ ] All elements aligned properly"
echo "    [ ] No overlapping text or figures"
echo ""

echo -e "${BLUE}Typography:${NC}"
echo "    [ ] Title visible and large (72pt+)"
echo "    [ ] Section headers readable (48-72pt)"
echo "    [ ] Body text readable (24-36pt minimum)"
echo "    [ ] No text cutoff or running off edges"
echo "    [ ] Consistent font usage"
echo ""

echo -e "${BLUE}Visual Elements:${NC}"
echo "    [ ] All figures display correctly"
echo "    [ ] No pixelated or blurry images"
echo "    [ ] Figure captions present and readable"
echo "    [ ] Colors render as expected"
echo "    [ ] Logos display clearly"
echo "    [ ] QR codes visible and scannable"
echo ""

echo -e "${BLUE}Content:${NC}"
echo "    [ ] All sections present (Intro, Methods, Results, Conclusions)"
echo "    [ ] References included"
echo "    [ ] Contact information visible"
echo "    [ ] No placeholder text (Lorem ipsum, TODO, etc.)"
echo ""

# 11. Recommended Tests
echo -e "${YELLOW}[11] Recommended Next Steps:${NC}"
echo ""
echo -e "${BLUE}Test Print:${NC}"
echo "    • Print at 25% scale (A0→A4, 36×48→Letter)"
echo "    • Check readability from 2-3 feet"
echo "    • Verify colors printed accurately"
echo ""

echo -e "${BLUE}Digital Checks:${NC}"
echo "    • View at 100% zoom in PDF viewer"
echo "    • Test on different screens/devices"
echo "    • Verify QR codes work with scanner app"
echo ""

echo -e "${BLUE}Proofreading:${NC}"
echo "    • Spell-check all text"
echo "    • Verify author names and affiliations"
echo "    • Confirm all statistics and numbers"
echo "    • Ask colleague to review"
echo ""

# 12. Summary
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Quality Check Complete${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "Review the checks above and complete manual verification."
echo -e "For full checklist, see: ${BLUE}assets/poster_quality_checklist.md${NC}"
echo ""

exit 0

