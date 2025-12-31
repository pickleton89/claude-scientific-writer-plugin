# Troubleshooting Guide

> Error handling and recovery procedures for the research-paper-summarizer skill

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Summary incomplete | Subagent failed mid-process | Retry the skill; check for PENDING markers in summary file |
| Context exceeded | Paper too long for chunked mode | Reduce page ranges; contact support for very long papers |
| Section detection failed | Non-standard paper format | Uses page-ratio fallback automatically |
| Missing statistics | Data in figures, not text | Check figure captions; may require manual extraction |
| Wrong article type | Misclassified paper | Re-run with correct article type selection |

## Processing Mode Issues

### Chunked mode not triggering for long papers
- Verify PDF is readable (not image-only scan)
- Check page count detection worked correctly
- Force chunked mode by confirming paper >12 pages

### Standard mode producing truncated output
- Paper may be near the 12-page threshold
- Dense text/tables increase token count
- Consider requesting chunked mode explicitly

## Subagent Pipeline Recovery

### If a subagent fails

1. Check the summary file for `<!-- SECTION: xxx PENDING -->` markers
2. Identify which section(s) failed
3. Claude will automatically:
   - Retry the failed agent once
   - Fall back to Standard Mode if retry fails
   - Report which sections couldn't be completed

### Partial completion recovery

```
# To resume from partial completion:
User: Continue summarizing this paper - some sections are still PENDING

Claude: [Reads existing summary file]
        Found 3 sections marked PENDING. Resuming from critique agent...
```

### Subagent Error Handling

| Scenario | Recovery |
|----------|----------|
| Subagent fails to write section | Retry once, then fall back to Standard Mode |
| Section detection fails | Use page-ratio fallback estimates |
| Context exceeded in subagent | Reduce page range, retry |

## PDF Reading Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Empty content extracted | Image-only PDF (scanned) | Use OCR tool first, then provide text |
| Garbled text | PDF encoding issues | Re-export from source or use different PDF |
| Missing sections | Multi-column layout confusion | Provide page hints for key sections |
| Figures not described | Text extraction excludes images | Refer to figure captions in PDF |

## Visual Output Issues

### HTML report not styling correctly
- Check browser console for errors
- Verify brand colors applied from Oligon brand (see `oligon-brand` skill)
- Single-file HTML should work offline

### PDF generation fails
- Ensure dependencies are installed: `pip install weasyprint pyyaml`
- Check YAML syntax in intermediate file
- Run: `python {baseDir}/scripts/generate_summary_pdf.py input.yaml`

### SVG infographic rendering issues
- Verify viewBox dimensions match content
- Check for unsupported CSS properties
- Test in multiple browsers

## When to Fall Back to Standard Mode

Standard mode (full-document) may work better when:
- Paper is well-structured with clear sections
- Paper is 10-15 pages (borderline length)
- You need faster processing (single pass)
- Chunked mode repeatedly fails

```
User: Use standard mode for this paper instead

Claude: Switching to Standard Mode (full-document analysis)...
```

## Getting Help

If issues persist:
1. Check that all required files exist (see Supporting Files in SKILL.md)
2. Verify the PDF is not corrupted
3. Try with a different paper to isolate the issue
4. Report issues at https://github.com/anthropics/claude-code/issues
