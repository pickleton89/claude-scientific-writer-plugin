import React from 'react';

// Brand Colors from BRAND_COLORS_v4.md
const BRAND = {
  blue: '#2DB2E8',
  darkGray: '#222222',
  mediumGray: '#666666',
  mutedGray: '#999999',
  lightGray: '#BDBDBD',
  orange: '#E8622D',
  mediumBlue: '#158BBB',
  darkTeal: '#0F5D7D',
  white: '#FFFFFF',
  black: '#000000'
};

// ============================================
// COMPONENT 1: 3D Cylinder Chart
// ============================================
const CylinderChart = ({
  data = [
    { label: 'Q1', value: 80, color: BRAND.orange },
    { label: 'Q2', value: 60, color: BRAND.blue },
    { label: 'Q3', value: 90, color: BRAND.mediumBlue },
    { label: 'Q4', value: 70, color: BRAND.darkTeal }
  ],
  width = 200,
  height = 180,
  maxHeight = 120
}) => {
  const cylWidth = 32;
  const spacing = width / data.length;
  const ellipseRy = 8;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {data.map((item, i) => {
        const x = i * spacing + spacing/2;
        const cylHeight = (item.value / 100) * maxHeight;
        const baseY = height - 30;
        const topY = baseY - cylHeight;
        
        // Darker shade for cylinder body
        const darkerColor = item.color + 'CC';
        
        return (
          <g key={i}>
            {/* Cylinder body */}
            <rect
              x={x - cylWidth/2}
              y={topY}
              width={cylWidth}
              height={cylHeight}
              fill={item.color}
            />
            {/* Bottom ellipse (base) */}
            <ellipse
              cx={x}
              cy={baseY}
              rx={cylWidth/2}
              ry={ellipseRy}
              fill={item.color}
              opacity={0.7}
            />
            {/* Top ellipse (cap) */}
            <ellipse
              cx={x}
              cy={topY}
              rx={cylWidth/2}
              ry={ellipseRy}
              fill={item.color}
            />
            {/* Highlight on top */}
            <ellipse
              cx={x}
              cy={topY}
              rx={cylWidth/2 - 4}
              ry={ellipseRy - 2}
              fill={BRAND.white}
              opacity={0.3}
            />
            {/* Label */}
            <text
              x={x}
              y={height - 8}
              textAnchor="middle"
              fill={BRAND.mediumGray}
              fontSize="11"
              fontFamily="Arial"
            >
              {item.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 2: Scientific Method Timeline
// ============================================
const ScientificMethodTimeline = ({
  steps = [
    { icon: '👁️', title: 'Observation', desc: 'Initial data collection' },
    { icon: '❓', title: 'Question', desc: 'Define the problem' },
    { icon: '💡', title: 'Hypothesis', desc: 'Proposed explanation' },
    { icon: '🧪', title: 'Experiment', desc: 'Test the hypothesis' },
    { icon: '📊', title: 'Analysis', desc: 'Interpret results' },
    { icon: '✓', title: 'Conclusion', desc: 'Draw conclusions' }
  ],
  width = 220,
  color = BRAND.blue
}) => {
  const stepHeight = 70;
  const height = steps.length * stepHeight + 40;
  const nodeRadius = 24;
  const lineX = 40;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {/* Curved connecting line */}
      <path
        d={`M ${lineX} 30 
            ${steps.map((_, i) => {
              const y = i * stepHeight + 50;
              const nextY = (i + 1) * stepHeight + 50;
              if (i < steps.length - 1) {
                return `Q ${lineX + 15} ${y + stepHeight/2} ${lineX} ${nextY}`;
              }
              return '';
            }).join(' ')}`}
        fill="none"
        stroke={BRAND.lightGray}
        strokeWidth={3}
        strokeDasharray="8,4"
      />
      
      {/* Straight fallback line */}
      <line
        x1={lineX}
        y1={30}
        x2={lineX}
        y2={height - 40}
        stroke={BRAND.lightGray}
        strokeWidth={3}
      />
      
      {steps.map((step, i) => {
        const y = i * stepHeight + 50;
        
        return (
          <g key={i}>
            {/* Node circle */}
            <circle
              cx={lineX}
              cy={y}
              r={nodeRadius}
              fill={color}
            />
            {/* Icon */}
            <text
              x={lineX}
              y={y + 6}
              textAnchor="middle"
              fontSize="18"
            >
              {step.icon}
            </text>
            {/* Title */}
            <text
              x={lineX + nodeRadius + 15}
              y={y - 5}
              fill={BRAND.darkGray}
              fontSize="12"
              fontWeight="bold"
              fontFamily="Arial"
            >
              {step.title}
            </text>
            {/* Description */}
            <text
              x={lineX + nodeRadius + 15}
              y={y + 12}
              fill={BRAND.mutedGray}
              fontSize="10"
              fontFamily="Arial"
            >
              {step.desc}
            </text>
          </g>
        );
      })}
      
      {/* Start label */}
      <text
        x={lineX}
        y={15}
        textAnchor="middle"
        fill={BRAND.mediumGray}
        fontSize="10"
        fontWeight="bold"
        fontFamily="Arial"
      >
        START
      </text>
    </svg>
  );
};

// ============================================
// COMPONENT 3: Isometric Block Stack
// ============================================
const IsometricBlocks = ({
  items = [
    { number: '01', label: 'ONE', desc: 'First phase', color: BRAND.orange },
    { number: '02', label: 'TWO', desc: 'Second phase', color: BRAND.blue },
    { number: '03', label: 'THREE', desc: 'Third phase', color: BRAND.mediumBlue },
    { number: '04', label: 'FOUR', desc: 'Fourth phase', color: BRAND.darkTeal }
  ],
  width = 280
}) => {
  const blockWidth = 50;
  const blockHeight = 35;
  const blockDepth = 20;
  const spacing = 70;
  
  return (
    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
      {items.map((item, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, width: 120 }}>
          {/* Isometric cube SVG */}
          <svg width={60} height={60} viewBox="0 0 60 60">
            {/* Top face */}
            <polygon
              points={`30,5 55,18 30,31 5,18`}
              fill={item.color}
            />
            {/* Left face */}
            <polygon
              points={`5,18 30,31 30,55 5,42`}
              fill={item.color}
              opacity={0.7}
            />
            {/* Right face */}
            <polygon
              points={`30,31 55,18 55,42 30,55`}
              fill={item.color}
              opacity={0.5}
            />
            {/* Number on top */}
            <text
              x={30}
              y={22}
              textAnchor="middle"
              fill={BRAND.white}
              fontSize="12"
              fontWeight="bold"
              fontFamily="Arial"
            >
              {item.number}
            </text>
          </svg>
          {/* Text */}
          <div>
            <div style={{ 
              fontSize: 11, 
              fontWeight: 'bold', 
              color: item.color,
              fontFamily: 'Arial'
            }}>
              {item.label}
            </div>
            <div style={{ 
              fontSize: 9, 
              color: BRAND.mutedGray,
              fontFamily: 'Arial',
              lineHeight: 1.3
            }}>
              {item.desc}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// ============================================
// COMPONENT 4: Ranked Bar List
// ============================================
const RankedBarList = ({
  items = [
    { rank: '01', label: 'First Item', value: 95, color: BRAND.blue },
    { rank: '02', label: 'Second', value: 78, color: BRAND.mediumBlue },
    { rank: '03', label: 'Third', value: 62, color: BRAND.orange },
    { rank: '04', label: 'Fourth', value: 45, color: BRAND.darkTeal }
  ],
  width = 260
}) => {
  const barMaxWidth = width - 80;
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {items.map((item, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* Rank circle */}
          <svg width={36} height={36} viewBox="0 0 36 36">
            <circle cx={18} cy={18} r={16} fill={item.color} />
            <text
              x={18}
              y={23}
              textAnchor="middle"
              fill={BRAND.white}
              fontSize="12"
              fontWeight="bold"
              fontFamily="Arial"
            >
              {item.rank}
            </text>
          </svg>
          {/* Bar and label */}
          <div style={{ flex: 1 }}>
            <div style={{ 
              fontSize: 11, 
              fontWeight: 'bold', 
              color: BRAND.darkGray,
              fontFamily: 'Arial',
              marginBottom: 4
            }}>
              {item.label}
            </div>
            <div style={{ 
              height: 8, 
              backgroundColor: BRAND.lightGray,
              borderRadius: 4,
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${item.value}%`,
                height: '100%',
                backgroundColor: item.color,
                borderRadius: 4
              }} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// ============================================
// COMPONENT 5: Hierarchical Tree
// ============================================
const HierarchicalTree = ({
  root = { label: 'Root Node' },
  children = [
    { label: 'Branch A', children: [{ label: 'Leaf 1' }, { label: 'Leaf 2' }] },
    { label: 'Branch B', children: [{ label: 'Leaf 3' }, { label: 'Leaf 4' }] }
  ],
  width = 300,
  color = BRAND.blue
}) => {
  const nodeWidth = 80;
  const nodeHeight = 30;
  const levelHeight = 70;
  
  return (
    <svg width={width} height={220} viewBox={`0 0 ${width} 220`}>
      {/* Root node */}
      <g transform={`translate(${width/2 - nodeWidth/2}, 10)`}>
        <rect width={nodeWidth} height={nodeHeight} rx={4} fill={color} />
        <text x={nodeWidth/2} y={20} textAnchor="middle" fill={BRAND.white}
          fontSize="10" fontWeight="bold" fontFamily="Arial">
          {root.label}
        </text>
      </g>
      
      {/* First level branches */}
      {children.map((branch, bi) => {
        const branchX = bi === 0 ? width/4 : (3 * width/4);
        const rootCenterX = width/2;
        
        return (
          <g key={bi}>
            {/* Connector line from root to branch */}
            <path
              d={`M ${rootCenterX} ${10 + nodeHeight} 
                  L ${rootCenterX} ${10 + nodeHeight + 15}
                  L ${branchX} ${10 + nodeHeight + 15}
                  L ${branchX} ${levelHeight}`}
              fill="none"
              stroke={BRAND.lightGray}
              strokeWidth={2}
            />
            
            {/* Branch node */}
            <g transform={`translate(${branchX - nodeWidth/2}, ${levelHeight})`}>
              <rect width={nodeWidth} height={nodeHeight} rx={4} fill={color} opacity={0.8} />
              <text x={nodeWidth/2} y={20} textAnchor="middle" fill={BRAND.white}
                fontSize="10" fontFamily="Arial">
                {branch.label}
              </text>
            </g>
            
            {/* Leaf nodes */}
            {branch.children && branch.children.map((leaf, li) => {
              const leafOffset = li === 0 ? -35 : 35;
              const leafX = branchX + leafOffset;
              
              return (
                <g key={li}>
                  {/* Connector to leaf */}
                  <path
                    d={`M ${branchX} ${levelHeight + nodeHeight}
                        L ${branchX} ${levelHeight + nodeHeight + 15}
                        L ${leafX} ${levelHeight + nodeHeight + 15}
                        L ${leafX} ${levelHeight * 2}`}
                    fill="none"
                    stroke={BRAND.lightGray}
                    strokeWidth={2}
                  />
                  
                  {/* Leaf node */}
                  <g transform={`translate(${leafX - nodeWidth/2 + 5}, ${levelHeight * 2})`}>
                    <rect width={nodeWidth - 10} height={nodeHeight - 4} rx={4} 
                      fill={BRAND.white} stroke={color} strokeWidth={2} />
                    <text x={(nodeWidth-10)/2} y={18} textAnchor="middle" fill={BRAND.darkGray}
                      fontSize="9" fontFamily="Arial">
                      {leaf.label}
                    </text>
                  </g>
                </g>
              );
            })}
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 6: S-Curve Process Flow
// ============================================
const SCurveProcess = ({
  steps = [
    { label: 'Start', color: BRAND.darkGray },
    { label: 'Step 1', color: BRAND.blue },
    { label: 'Step 2', color: BRAND.blue },
    { label: 'Step 3', color: BRAND.mediumBlue },
    { label: 'Step 4', color: BRAND.mediumBlue },
    { label: 'Step 5', color: BRAND.orange },
    { label: 'Step 6', color: BRAND.orange },
    { label: 'Finish', color: BRAND.darkTeal }
  ],
  width = 340,
  rowHeight = 60,
  itemsPerRow = 4
}) => {
  const rows = Math.ceil(steps.length / itemsPerRow);
  const height = rows * rowHeight + 40;
  const nodeRadius = 20;
  
  // Calculate positions with snake pattern
  const getPosition = (index) => {
    const row = Math.floor(index / itemsPerRow);
    const col = index % itemsPerRow;
    const isReversed = row % 2 === 1;
    const actualCol = isReversed ? (itemsPerRow - 1 - col) : col;
    
    const x = 40 + actualCol * ((width - 80) / (itemsPerRow - 1));
    const y = 30 + row * rowHeight;
    
    return { x, y, row };
  };
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {/* Draw connecting path */}
      {steps.map((step, i) => {
        if (i === steps.length - 1) return null;
        
        const pos = getPosition(i);
        const nextPos = getPosition(i + 1);
        
        // If same row, draw horizontal line
        if (pos.row === nextPos.row) {
          return (
            <line key={`line-${i}`}
              x1={pos.x + (nextPos.x > pos.x ? nodeRadius : -nodeRadius)}
              y1={pos.y}
              x2={nextPos.x + (nextPos.x > pos.x ? -nodeRadius : nodeRadius)}
              y2={nextPos.y}
              stroke={BRAND.lightGray}
              strokeWidth={3}
            />
          );
        } else {
          // Draw curve to next row
          return (
            <path key={`line-${i}`}
              d={`M ${pos.x} ${pos.y + nodeRadius}
                  Q ${pos.x} ${pos.y + rowHeight/2} ${nextPos.x} ${nextPos.y - nodeRadius}`}
              fill="none"
              stroke={BRAND.lightGray}
              strokeWidth={3}
            />
          );
        }
      })}
      
      {/* Draw nodes */}
      {steps.map((step, i) => {
        const pos = getPosition(i);
        
        return (
          <g key={i}>
            <circle
              cx={pos.x}
              cy={pos.y}
              r={nodeRadius}
              fill={step.color}
            />
            <text
              x={pos.x}
              y={pos.y + 4}
              textAnchor="middle"
              fill={BRAND.white}
              fontSize="9"
              fontWeight="bold"
              fontFamily="Arial"
            >
              {step.label.length > 6 ? step.label.slice(0, 6) : step.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 7: Science Icon Badge Grid
// ============================================
const ScienceIconBadge = ({ label, color = BRAND.blue, size = 44 }) => {
  // Simple geometric icons for different sciences
  const getIconPath = (label) => {
    const icons = {
      'Physics': <circle cx="12" cy="12" r="4" fill="none" stroke={BRAND.white} strokeWidth="1.5"/>,
      'Chemistry': <path d="M8 3v7l-3 6h14l-3-6V3M9 3h6" fill="none" stroke={BRAND.white} strokeWidth="1.5"/>,
      'Biology': <path d="M12 2c-4 4-4 8 0 12 4-4 4-8 0-12M12 2v20" fill="none" stroke={BRAND.white} strokeWidth="1.5"/>,
      'Genetics': <path d="M6 3c0 6 12 6 12 12M18 3c0 6-12 6-12 12" fill="none" stroke={BRAND.white} strokeWidth="1.5"/>,
      'Bioinfo': <path d="M4 6h16M4 12h16M4 18h16M8 4v16M16 4v16" fill="none" stroke={BRAND.white} strokeWidth="1"/>,
      'Medicine': <path d="M12 4v16M4 12h16" stroke={BRAND.white} strokeWidth="2.5"/>,
      'Ecology': <circle cx="12" cy="12" r="8" fill="none" stroke={BRAND.white} strokeWidth="1.5"/>,
      'Statistics': <path d="M4 18l4-6 4 4 4-8 4 6" fill="none" stroke={BRAND.white} strokeWidth="1.5"/>,
      'default': <circle cx="12" cy="12" r="6" fill="none" stroke={BRAND.white} strokeWidth="1.5"/>
    };
    return icons[label] || icons['default'];
  };
  
  return (
    <div style={{ textAlign: 'center', width: size + 10 }}>
      <svg width={size} height={size} viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="11" fill={color} />
        {getIconPath(label)}
      </svg>
      <div style={{
        fontSize: 8,
        color: BRAND.mediumGray,
        fontFamily: 'Arial',
        marginTop: 3,
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        {label}
      </div>
    </div>
  );
};

const ScienceIconGrid = ({
  items = [
    { label: 'Physics', color: BRAND.blue },
    { label: 'Chemistry', color: BRAND.orange },
    { label: 'Biology', color: BRAND.mediumBlue },
    { label: 'Genetics', color: BRAND.darkTeal },
    { label: 'Bioinfo', color: BRAND.blue },
    { label: 'Medicine', color: BRAND.orange },
    { label: 'Ecology', color: BRAND.mediumBlue },
    { label: 'Statistics', color: BRAND.darkGray }
  ],
  columns = 4
}) => (
  <div style={{
    display: 'grid',
    gridTemplateColumns: `repeat(${columns}, 1fr)`,
    gap: 12
  }}>
    {items.map((item, i) => (
      <ScienceIconBadge key={i} {...item} />
    ))}
  </div>
);

// ============================================
// COMPONENT 8: Lab Equipment Schematic
// ============================================
const LabSchematic = ({
  width = 280,
  height = 180,
  color = BRAND.blue
}) => (
  <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
    {/* Flask */}
    <path
      d={`M 60 30 L 60 70 L 30 130 L 90 130 L 60 70 L 60 30`}
      fill={color}
      opacity={0.2}
      stroke={color}
      strokeWidth={2}
    />
    <ellipse cx={60} cy={30} rx={15} ry={5} fill={color} />
    
    {/* Tube connecting */}
    <path
      d="M 90 80 Q 120 80 140 60"
      fill="none"
      stroke={BRAND.mediumGray}
      strokeWidth={3}
    />
    
    {/* Second vessel */}
    <rect x={140} y={40} width={50} height={80} rx={4}
      fill={BRAND.orange} opacity={0.2} stroke={BRAND.orange} strokeWidth={2} />
    
    {/* Arrow */}
    <path
      d="M 200 80 L 240 80 M 235 75 L 245 80 L 235 85"
      fill="none"
      stroke={BRAND.darkGray}
      strokeWidth={2}
    />
    
    {/* Output indicator */}
    <circle cx={260} cy={80} r={15} fill={BRAND.darkTeal} />
    <text x={260} y={84} textAnchor="middle" fill={BRAND.white}
      fontSize="10" fontWeight="bold" fontFamily="Arial">
      ✓
    </text>
    
    {/* Callout labels */}
    <g>
      <line x1={60} y1={145} x2={60} y2={160} stroke={BRAND.lightGray} strokeWidth={1} />
      <text x={60} y={172} textAnchor="middle" fill={BRAND.mediumGray}
        fontSize="9" fontFamily="Arial">
        Input
      </text>
    </g>
    <g>
      <line x1={165} y1={125} x2={165} y2={145} stroke={BRAND.lightGray} strokeWidth={1} />
      <text x={165} y={157} textAnchor="middle" fill={BRAND.mediumGray}
        fontSize="9" fontFamily="Arial">
        Process
      </text>
    </g>
    <g>
      <line x1={260} y1={100} x2={260} y2={115} stroke={BRAND.lightGray} strokeWidth={1} />
      <text x={260} y={127} textAnchor="middle" fill={BRAND.mediumGray}
        fontSize="9" fontFamily="Arial">
        Output
      </text>
    </g>
  </svg>
);

// ============================================
// MAIN DEMO COMPONENT
// ============================================
export default function SVGScienceComponents() {
  return (
    <div style={{ 
      padding: 24, 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: BRAND.white,
      maxWidth: 900
    }}>
      <h2 style={{ color: BRAND.darkGray, borderBottom: `3px solid ${BRAND.blue}`, paddingBottom: 8 }}>
        Science-Focused SVG Components
      </h2>
      <p style={{ color: BRAND.mediumGray, fontSize: 14, marginBottom: 32 }}>
        Additional components from science infographic template
      </p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40 }}>
        
        {/* 3D Cylinders */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>3D Cylinder Chart</h3>
          <CylinderChart 
            data={[
              { label: 'Ctrl', value: 45, color: BRAND.darkGray },
              { label: '10nM', value: 62, color: BRAND.blue },
              { label: '50nM', value: 78, color: BRAND.mediumBlue },
              { label: '100nM', value: 91, color: BRAND.orange }
            ]}
          />
        </section>
        
        {/* Scientific Method */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Scientific Method Timeline</h3>
          <ScientificMethodTimeline 
            steps={[
              { icon: '🔬', title: 'Observation', desc: 'Tumor growth patterns' },
              { icon: '❓', title: 'Question', desc: 'Can siRNA reduce growth?' },
              { icon: '💡', title: 'Hypothesis', desc: 'NR4A1 knockdown works' },
              { icon: '🧪', title: 'Experiment', desc: 'Treat cell lines' },
              { icon: '📊', title: 'Analysis', desc: 'Measure viability' }
            ]}
          />
        </section>
        
        {/* Isometric Blocks */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Isometric Block Stack</h3>
          <IsometricBlocks 
            items={[
              { number: '01', label: 'DESIGN', desc: 'siRNA selection', color: BRAND.blue },
              { number: '02', label: 'LINK', desc: 'Aptamer coupling', color: BRAND.orange },
              { number: '03', label: 'TEST', desc: 'In vitro assays', color: BRAND.mediumBlue },
              { number: '04', label: 'VALIDATE', desc: 'In vivo models', color: BRAND.darkTeal }
            ]}
          />
        </section>
        
        {/* Ranked Bars */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Ranked Bar List</h3>
          <RankedBarList 
            items={[
              { rank: '01', label: 'Lead Candidate A', value: 92, color: BRAND.blue },
              { rank: '02', label: 'Candidate B', value: 78, color: BRAND.mediumBlue },
              { rank: '03', label: 'Candidate C', value: 65, color: BRAND.orange },
              { rank: '04', label: 'Candidate D', value: 43, color: BRAND.mutedGray }
            ]}
          />
        </section>
        
        {/* Hierarchical Tree */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Hierarchical Tree</h3>
          <HierarchicalTree 
            root={{ label: 'SeekR Platform' }}
            children={[
              { label: 'Aptamers', children: [{ label: 'Cell-SELEX' }, { label: 'Optimized' }] },
              { label: 'siRNA', children: [{ label: 'Design' }, { label: 'Validated' }] }
            ]}
          />
        </section>
        
        {/* S-Curve Process */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>S-Curve Process Flow</h3>
          <SCurveProcess 
            steps={[
              { label: 'Target', color: BRAND.darkGray },
              { label: 'Design', color: BRAND.blue },
              { label: 'Screen', color: BRAND.blue },
              { label: 'Select', color: BRAND.mediumBlue },
              { label: 'Link', color: BRAND.orange },
              { label: 'Test', color: BRAND.orange },
              { label: 'Validate', color: BRAND.darkTeal },
              { label: 'Lead', color: BRAND.darkTeal }
            ]}
          />
        </section>
        
        {/* Science Icons */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Science Icon Grid</h3>
          <ScienceIconGrid 
            items={[
              { label: 'Genetics', color: BRAND.blue },
              { label: 'Bioinfo', color: BRAND.orange },
              { label: 'Chemistry', color: BRAND.mediumBlue },
              { label: 'Medicine', color: BRAND.darkTeal },
              { label: 'Biology', color: BRAND.blue },
              { label: 'Statistics', color: BRAND.darkGray },
              { label: 'Physics', color: BRAND.orange },
              { label: 'Ecology', color: BRAND.mediumBlue }
            ]}
          />
        </section>
        
        {/* Lab Schematic */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Lab Schematic</h3>
          <LabSchematic />
        </section>
        
      </div>
      
      {/* Summary */}
      <section style={{ 
        marginTop: 40, 
        padding: 20, 
        backgroundColor: '#f8f8f8', 
        borderRadius: 8,
        borderLeft: `4px solid ${BRAND.orange}`
      }}>
        <h4 style={{ color: BRAND.darkGray, margin: '0 0 12px 0' }}>New Components Added</h4>
        <div style={{ fontSize: 12, color: BRAND.mediumGray, lineHeight: 1.8 }}>
          <strong>8 Additional Components:</strong> CylinderChart, ScientificMethodTimeline, 
          IsometricBlocks, RankedBarList, HierarchicalTree, SCurveProcess, 
          ScienceIconGrid, LabSchematic
          <br/>
          <strong>Total Library:</strong> 23 parametric components across 3 artifacts
          <br/>
          <strong>Use cases:</strong> Pipeline diagrams, methods figures, grant graphics
        </div>
      </section>
    </div>
  );
}
