// figures.jsx — Inline SVG figures used in the report mock.
// Drawn with Oligon brand tokens: precise, white background, no shadows,
// brand-blue for the highlight series, contrast-orange for opposition,
// neutrals for ink.

const FIG_BLUE   = '#2DB2E8';
const FIG_ORANGE = '#E8622D';
const FIG_DARK   = '#222222';
const FIG_MID    = '#666666';
const FIG_MUTE   = '#999999';
const FIG_LINE   = '#BDBDBD';
const FIG_GRID   = '#E5E5E5';

// ───────────────────────────────────────────────────────────────────────────
// Figure 1 — Endosomal trafficking schematic
// Shows three fates of an internalized aptamer–siRNA chimera.
// ───────────────────────────────────────────────────────────────────────────
function FigTrafficking() {
  return (
    <svg viewBox="0 0 720 360" xmlns="http://www.w3.org/2000/svg">
      {/* Cell membrane */}
      <line x1="40" y1="80" x2="680" y2="80" stroke={FIG_DARK} strokeWidth="1.2" />
      <text x="40" y="68" fill={FIG_MID} fontSize="9" fontFamily="Arial">Plasma membrane</text>

      {/* Receptor + cargo */}
      <circle cx="120" cy="80" r="6" fill={FIG_BLUE} />
      <line x1="120" y1="80" x2="120" y2="105" stroke={FIG_BLUE} strokeWidth="1.2" />
      <circle cx="120" cy="115" r="5" fill="none" stroke={FIG_DARK} strokeWidth="1" />
      <text x="135" y="120" fill={FIG_MID} fontSize="9" fontFamily="Arial">Aptamer–siRNA</text>

      {/* Internalization arrow */}
      <path d="M120 130 L 120 165" stroke={FIG_DARK} strokeWidth="1" markerEnd="url(#arrow)" />

      {/* Early endosome */}
      <circle cx="120" cy="200" r="34" fill="none" stroke={FIG_DARK} strokeWidth="1.2" />
      <text x="120" y="204" fill={FIG_DARK} fontSize="9" fontFamily="Arial" textAnchor="middle" fontWeight="700">Rab5</text>
      <text x="120" y="216" fill={FIG_MID} fontSize="8" fontFamily="Arial" textAnchor="middle">pH ~6.2</text>
      <text x="120" y="252" fill={FIG_MID} fontSize="8.5" fontFamily="Arial" textAnchor="middle">Early endosome</text>

      {/* Three branch arrows */}
      <path d="M154 200 L 240 140" stroke={FIG_DARK} strokeWidth="1" markerEnd="url(#arrow)" />
      <path d="M154 210 L 240 240" stroke={FIG_DARK} strokeWidth="1" markerEnd="url(#arrow)" />
      <path d="M154 200 L 240 200" stroke={FIG_DARK} strokeWidth="1" markerEnd="url(#arrow)" />

      {/* Recycling — fast (Rab4) */}
      <circle cx="290" cy="130" r="26" fill="none" stroke={FIG_ORANGE} strokeWidth="1.5" strokeDasharray="3 2" />
      <text x="290" y="134" fill={FIG_ORANGE} fontSize="9" fontFamily="Arial" textAnchor="middle" fontWeight="700">Rab4</text>
      <text x="290" y="170" fill={FIG_MID} fontSize="8" fontFamily="Arial" textAnchor="middle">Fast recycle</text>
      <path d="M316 125 L 380 90 L 380 80" stroke={FIG_ORANGE} strokeWidth="1" strokeDasharray="3 2" markerEnd="url(#arrow-orange)" />

      {/* Slow recycling — Rab11 */}
      <circle cx="290" cy="200" r="28" fill={FIG_BLUE} fillOpacity="0.10" stroke={FIG_BLUE} strokeWidth="1.5" />
      <text x="290" y="204" fill={FIG_BLUE} fontSize="9" fontFamily="Arial" textAnchor="middle" fontWeight="700">Rab11</text>
      <text x="290" y="240" fill={FIG_MID} fontSize="8" fontFamily="Arial" textAnchor="middle">Slow recycle</text>

      {/* Late endosome → Rab7 */}
      <circle cx="290" cy="270" r="22" fill="none" stroke={FIG_DARK} strokeWidth="1.2" />
      <text x="290" y="274" fill={FIG_DARK} fontSize="9" fontFamily="Arial" textAnchor="middle" fontWeight="700">Rab7</text>
      <text x="290" y="306" fill={FIG_MID} fontSize="8" fontFamily="Arial" textAnchor="middle">Late endosome</text>

      {/* Lysosome */}
      <path d="M312 270 L 380 270" stroke={FIG_DARK} strokeWidth="1" markerEnd="url(#arrow)" />
      <g>
        <circle cx="420" cy="270" r="22" fill={FIG_LINE} fillOpacity="0.6" stroke={FIG_DARK} strokeWidth="1" />
        <text x="420" y="274" fill={FIG_DARK} fontSize="8.5" fontFamily="Arial" textAnchor="middle" fontWeight="700">LAMP1</text>
        <text x="420" y="306" fill={FIG_MID} fontSize="8" fontFamily="Arial" textAnchor="middle">Lysosome</text>
      </g>

      {/* Endosomal escape — the win */}
      <g>
        <rect x="500" y="180" width="170" height="56" fill={FIG_BLUE} fillOpacity="0.08" stroke={FIG_BLUE} strokeWidth="1" />
        <text x="585" y="200" fill={FIG_BLUE} fontSize="9.5" fontFamily="Arial" textAnchor="middle" fontWeight="700">ENDOSOMAL ESCAPE</text>
        <text x="585" y="216" fill={FIG_DARK} fontSize="8.5" fontFamily="Arial" textAnchor="middle">siRNA → cytoplasm</text>
        <text x="585" y="228" fill={FIG_MID} fontSize="8" fontFamily="Arial" textAnchor="middle">RISC loading</text>
      </g>
      <path d="M318 200 L 500 200" stroke={FIG_BLUE} strokeWidth="1.2" markerEnd="url(#arrow-blue)" />

      {/* Outcomes ribbon */}
      <line x1="40" y1="338" x2="680" y2="338" stroke={FIG_GRID} strokeWidth="1" />
      <text x="40" y="354" fill={FIG_ORANGE} fontSize="8" fontFamily="Arial" fontWeight="700">CCR6 — Class A GPCR pattern; rapid recycle, &lt;5 min dwell</text>
      <text x="380" y="354" fill={FIG_BLUE} fontSize="8" fontFamily="Arial" fontWeight="700">CTLA-4 — slow recycle via Rab11; ~2 h half-life</text>

      {/* Markers */}
      <defs>
        <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill={FIG_DARK} />
        </marker>
        <marker id="arrow-orange" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill={FIG_ORANGE} />
        </marker>
        <marker id="arrow-blue" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill={FIG_BLUE} />
        </marker>
      </defs>
    </svg>
  );
}

// ───────────────────────────────────────────────────────────────────────────
// Figure 2 — Head-to-head scoring (CCR6 vs CTLA-4) across six criteria.
// Grouped horizontal bar chart.
// ───────────────────────────────────────────────────────────────────────────
function FigScoring() {
  const data = [
    ['Disease relevance',          9, 9],
    ['Th17 selectivity',           6, 3],
    ['Internalization mechanics',  7, 9],
    ['Endosomal trafficking',      3, 7],
    ['Aptamer feasibility',        2, 9],
    ['Safety / off-target risk',   8, 2],
  ];
  const W = 720, H = 360;
  const padL = 160, padR = 40, padT = 28, padB = 36;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;
  const rowH = innerH / data.length;
  const x = v => padL + (v / 10) * innerW;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} xmlns="http://www.w3.org/2000/svg">
      {/* Gridlines at 2/4/6/8/10 */}
      {[0, 2, 4, 6, 8, 10].map(g => (
        <g key={g}>
          <line x1={x(g)} y1={padT} x2={x(g)} y2={H - padB} stroke={FIG_GRID} strokeWidth="0.6" />
          <text x={x(g)} y={H - padB + 14} fill={FIG_MID} fontSize="8" fontFamily="Arial" textAnchor="middle">{g}</text>
        </g>
      ))}
      {/* Axis labels */}
      <text x={padL + innerW / 2} y={H - 4} fill={FIG_MID} fontSize="8.5" fontFamily="Arial" textAnchor="middle">Score (0 – 10)</text>

      {data.map(([label, ccr6, ctla4], i) => {
        const yTop = padT + i * rowH;
        const barH = (rowH - 14) / 2;
        return (
          <g key={label}>
            <text x={padL - 10} y={yTop + rowH / 2 + 3} fill={FIG_DARK} fontSize="9" fontFamily="Arial" textAnchor="end">{label}</text>
            {/* CCR6 — orange */}
            <rect x={padL} y={yTop + 4} width={(ccr6 / 10) * innerW} height={barH} fill={FIG_ORANGE} />
            <text x={padL + (ccr6 / 10) * innerW + 6} y={yTop + 4 + barH - 2} fill={FIG_ORANGE} fontSize="8.5" fontFamily="Arial" fontWeight="700">{ccr6}</text>
            {/* CTLA-4 — blue */}
            <rect x={padL} y={yTop + 4 + barH + 2} width={(ctla4 / 10) * innerW} height={barH} fill={FIG_BLUE} />
            <text x={padL + (ctla4 / 10) * innerW + 6} y={yTop + 4 + barH + 2 + barH - 2} fill={FIG_BLUE} fontSize="8.5" fontFamily="Arial" fontWeight="700">{ctla4}</text>
          </g>
        );
      })}

      {/* Legend */}
      <g transform={`translate(${padL}, ${padT - 14})`}>
        <rect x="0" y="-8" width="10" height="8" fill={FIG_ORANGE} />
        <text x="14" y="-1" fill={FIG_DARK} fontSize="8.5" fontFamily="Arial">CCR6</text>
        <rect x="60" y="-8" width="10" height="8" fill={FIG_BLUE} />
        <text x="74" y="-1" fill={FIG_DARK} fontSize="8.5" fontFamily="Arial">CTLA-4</text>
      </g>
    </svg>
  );
}

// ───────────────────────────────────────────────────────────────────────────
// Cover hero figure for V3 (data-led cover): a stylized bullseye showing
// the orbital-dot motif as a target with concentric criteria.
// ───────────────────────────────────────────────────────────────────────────
function FigHeroTarget() {
  return (
    <svg viewBox="0 0 640 480" xmlns="http://www.w3.org/2000/svg">
      <text x="32" y="36" fill={FIG_DARK} fontSize="11" fontFamily="Arial" fontWeight="700">Figure 1 — Target assessment matrix, all candidates</text>
      <text x="32" y="50" fill={FIG_MID} fontSize="9" fontFamily="Arial">Internalization rate × endosomal dwell time, n = 12 candidate receptors. Brand Blue annotates targets with published trafficking data.</text>

      {/* Plot area */}
      <g transform="translate(60, 70)">
        {/* Axes */}
        <line x1="0" y1="360" x2="540" y2="360" stroke={FIG_DARK} strokeWidth="1" />
        <line x1="0" y1="0" x2="0" y2="360" stroke={FIG_DARK} strokeWidth="1" />
        <text x="270" y="392" fill={FIG_MID} fontSize="9" fontFamily="Arial" textAnchor="middle">Internalization t½ (min, log scale)</text>
        <text x="-44" y="180" fill={FIG_MID} fontSize="9" fontFamily="Arial" transform="rotate(-90, -44, 180)" textAnchor="middle">Endosomal dwell time (min)</text>

        {/* Gridlines */}
        {[0.25, 0.5, 0.75].map(f => (
          <line key={f} x1="0" y1={360 - f * 360} x2="540" y2={360 - f * 360} stroke={FIG_GRID} strokeWidth="0.6" />
        ))}

        {/* Quadrant fill — preferred zone (slow internalization × long dwell) */}
        <rect x="270" y="0" width="270" height="180" fill={FIG_BLUE} fillOpacity="0.06" />
        <text x="535" y="14" fill={FIG_BLUE} fontSize="8" fontFamily="Arial" textAnchor="end" fontWeight="700">PREFERRED ZONE</text>

        {/* Data points */}
        {[
          { x: 60,  y: 320, lab: 'TfR',     mute: true  },
          { x: 90,  y: 285, lab: 'EGFR',    mute: true  },
          { x: 80,  y: 200, lab: 'EpCAM',   mute: true  },
          { x: 50,  y: 340, lab: 'CCR6',    mute: false, color: FIG_ORANGE },
          { x: 360, y: 80,  lab: 'CTLA-4',  mute: false, color: FIG_BLUE   },
          { x: 410, y: 60,  lab: 'PSMA',    mute: false, color: FIG_BLUE   },
          { x: 250, y: 150, lab: 'PTK7',    mute: true  },
          { x: 180, y: 220, lab: 'HER2',    mute: true  },
          { x: 320, y: 140, lab: 'c-Met',   mute: true  },
          { x: 220, y: 260, lab: 'CD44',    mute: true  },
          { x: 310, y: 250, lab: 'Axl',     mute: true  },
          { x: 140, y: 270, lab: 'MUC1',    mute: true  },
        ].map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r={p.mute ? 4 : 6}
                    fill={p.color || FIG_MUTE}
                    fillOpacity={p.mute ? 0.55 : 1}
                    stroke={p.mute ? 'none' : FIG_DARK}
                    strokeWidth={p.mute ? 0 : 0.5} />
            <text x={p.x + 9} y={p.y + 3}
                  fill={p.mute ? FIG_MID : FIG_DARK}
                  fontSize={p.mute ? 8 : 9}
                  fontFamily="Arial"
                  fontWeight={p.mute ? 400 : 700}>{p.lab}</text>
          </g>
        ))}

        {/* Annotation */}
        <line x1="430" y1="60" x2="470" y2="40" stroke={FIG_BLUE} strokeWidth="0.8" />
        <text x="475" y="38" fill={FIG_BLUE} fontSize="8.5" fontFamily="Arial" fontWeight="700">Slow recycling, long dwell —</text>
        <text x="475" y="50" fill={FIG_BLUE} fontSize="8.5" fontFamily="Arial">ideal for endosomal escape.</text>
      </g>
    </svg>
  );
}

// Inner orbital-dot SVG used as a corner decoration on Editorial cover.
function OrbitalArt() {
  return (
    <svg viewBox="0 0 540 540" xmlns="http://www.w3.org/2000/svg" className="orbital-art">
      <circle cx="270" cy="270" r="240" fill="none" stroke={FIG_BLUE} strokeWidth="0.6" strokeOpacity="0.35" />
      <circle cx="270" cy="270" r="180" fill="none" stroke={FIG_BLUE} strokeWidth="0.6" strokeOpacity="0.35" />
      <circle cx="270" cy="270" r="120" fill="none" stroke={FIG_BLUE} strokeWidth="0.6" strokeOpacity="0.35" />
      <circle cx="270" cy="270" r="60" fill="none" stroke={FIG_BLUE} strokeWidth="0.8" strokeOpacity="0.55" />
      <circle cx="270" cy="270" r="2.5" fill={FIG_BLUE} />
      <circle cx="450" cy="270" r="6" fill={FIG_BLUE} />
    </svg>
  );
}

Object.assign(window, { FigTrafficking, FigScoring, FigHeroTarget, OrbitalArt });
