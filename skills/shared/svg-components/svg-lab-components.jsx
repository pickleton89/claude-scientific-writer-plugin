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
// COMPONENT 1: DNA Helix
// ============================================
const DNAHelix = ({ 
  width = 40, 
  height = 100, 
  color1 = BRAND.blue, 
  color2 = BRAND.orange 
}) => {
  const segments = 5;
  const segmentHeight = height / segments;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {[...Array(segments)].map((_, i) => {
        const y = i * segmentHeight;
        const phase = i % 2 === 0;
        
        return (
          <g key={i}>
            {/* Backbone curves */}
            <path
              d={`M ${phase ? 5 : width-5} ${y} 
                  Q ${width/2} ${y + segmentHeight/2} 
                  ${phase ? width-5 : 5} ${y + segmentHeight}`}
              fill="none"
              stroke={color1}
              strokeWidth={2.5}
            />
            <path
              d={`M ${phase ? width-5 : 5} ${y} 
                  Q ${width/2} ${y + segmentHeight/2} 
                  ${phase ? 5 : width-5} ${y + segmentHeight}`}
              fill="none"
              stroke={color2}
              strokeWidth={2.5}
            />
            {/* Base pair rungs */}
            <line
              x1={10}
              y1={y + segmentHeight/2}
              x2={width - 10}
              y2={y + segmentHeight/2}
              stroke={BRAND.lightGray}
              strokeWidth={2}
            />
            {/* Nodes at crossings */}
            <circle cx={10} cy={y + segmentHeight/2} r={3} fill={color1} />
            <circle cx={width - 10} cy={y + segmentHeight/2} r={3} fill={color2} />
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 2: Atom Icon
// ============================================
const AtomIcon = ({ 
  size = 60, 
  color = BRAND.blue,
  nucleusColor = BRAND.orange
}) => {
  const center = size / 2;
  const orbitRadius = size * 0.35;
  
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* Orbital ellipses */}
      <ellipse
        cx={center}
        cy={center}
        rx={orbitRadius}
        ry={orbitRadius * 0.4}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        transform={`rotate(0 ${center} ${center})`}
      />
      <ellipse
        cx={center}
        cy={center}
        rx={orbitRadius}
        ry={orbitRadius * 0.4}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        transform={`rotate(60 ${center} ${center})`}
      />
      <ellipse
        cx={center}
        cy={center}
        rx={orbitRadius}
        ry={orbitRadius * 0.4}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        transform={`rotate(-60 ${center} ${center})`}
      />
      {/* Nucleus */}
      <circle cx={center} cy={center} r={size * 0.12} fill={nucleusColor} />
      {/* Electrons */}
      <circle cx={center + orbitRadius} cy={center} r={4} fill={color} />
      <circle cx={center - orbitRadius * 0.5} cy={center - orbitRadius * 0.35} r={4} fill={color} />
      <circle cx={center - orbitRadius * 0.5} cy={center + orbitRadius * 0.35} r={4} fill={color} />
    </svg>
  );
};

// ============================================
// COMPONENT 3: Lab Flask with Burner
// ============================================
const LabFlaskWithBurner = ({
  width = 120,
  height = 160,
  flaskColor = BRAND.blue,
  liquidColor = BRAND.orange
}) => (
  <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
    {/* Stand */}
    <rect x={15} y={140} width={90} height={8} rx={2} fill={BRAND.darkGray} />
    <rect x={55} y={100} width={10} height={40} fill={BRAND.darkGray} />
    
    {/* Burner base */}
    <ellipse cx={60} cy={135} rx={20} ry={6} fill={BRAND.mediumGray} />
    <rect x={45} y={120} width={30} height={15} fill={BRAND.mediumGray} />
    
    {/* Flame */}
    <ellipse cx={60} cy={110} rx={8} ry={12} fill={BRAND.orange} opacity={0.8} />
    <ellipse cx={60} cy={108} rx={4} ry={8} fill="#FFD700" />
    
    {/* Flask */}
    <path
      d={`M 45 30 L 45 60 L 25 100 Q 20 110 30 115 L 90 115 Q 100 110 95 100 L 75 60 L 75 30`}
      fill={flaskColor}
      opacity={0.2}
      stroke={flaskColor}
      strokeWidth={2}
    />
    
    {/* Liquid in flask */}
    <path
      d={`M 30 90 Q 25 100 35 105 L 85 105 Q 95 100 90 90 L 75 70 L 45 70 Z`}
      fill={liquidColor}
      opacity={0.5}
    />
    
    {/* Flask neck */}
    <rect x={45} y={15} width={30} height={15} fill={flaskColor} opacity={0.3} stroke={flaskColor} strokeWidth={2} />
    <ellipse cx={60} cy={15} rx={15} ry={4} fill={flaskColor} />
    
    {/* Bubbles */}
    <circle cx={50} cy={85} r={3} fill={BRAND.white} opacity={0.6} />
    <circle cx={65} cy={80} r={2} fill={BRAND.white} opacity={0.6} />
    <circle cx={55} cy={75} r={2.5} fill={BRAND.white} opacity={0.6} />
  </svg>
);

// ============================================
// COMPONENT 4: Beaker
// ============================================
const Beaker = ({
  size = 80,
  fillPercent = 60,
  liquidColor = BRAND.blue
}) => {
  const liquidHeight = (fillPercent / 100) * 50;
  
  return (
    <svg width={size} height={size} viewBox="0 0 80 80">
      {/* Beaker body */}
      <path
        d="M 15 15 L 15 65 Q 15 70 20 70 L 60 70 Q 65 70 65 65 L 65 15"
        fill={BRAND.white}
        stroke={BRAND.mediumGray}
        strokeWidth={2}
      />
      
      {/* Liquid */}
      <rect
        x={17}
        y={70 - liquidHeight}
        width={46}
        height={liquidHeight - 3}
        fill={liquidColor}
        opacity={0.4}
      />
      
      {/* Pour spout */}
      <path
        d="M 15 15 L 10 10 L 15 12"
        fill="none"
        stroke={BRAND.mediumGray}
        strokeWidth={2}
      />
      
      {/* Measurement lines */}
      {[25, 40, 55].map((y, i) => (
        <line key={i} x1={17} y1={y} x2={25} y2={y} stroke={BRAND.lightGray} strokeWidth={1} />
      ))}
    </svg>
  );
};

// ============================================
// COMPONENT 5: Test Tubes
// ============================================
const TestTubes = ({
  tubes = [
    { fillPercent: 80, color: BRAND.blue },
    { fillPercent: 60, color: BRAND.orange },
    { fillPercent: 40, color: BRAND.mediumBlue }
  ],
  width = 100,
  height = 100
}) => {
  const tubeWidth = 16;
  const tubeHeight = 70;
  const spacing = width / tubes.length;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {tubes.map((tube, i) => {
        const x = i * spacing + spacing/2 - tubeWidth/2;
        const liquidHeight = (tube.fillPercent / 100) * (tubeHeight - 15);
        
        return (
          <g key={i}>
            {/* Tube body */}
            <rect
              x={x}
              y={10}
              width={tubeWidth}
              height={tubeHeight - 10}
              rx={tubeWidth/2}
              fill={BRAND.white}
              stroke={BRAND.mediumGray}
              strokeWidth={1.5}
            />
            {/* Liquid */}
            <rect
              x={x + 2}
              y={10 + tubeHeight - 12 - liquidHeight}
              width={tubeWidth - 4}
              height={liquidHeight}
              rx={(tubeWidth - 4)/2}
              fill={tube.color}
              opacity={0.6}
            />
            {/* Cap */}
            <rect
              x={x - 2}
              y={5}
              width={tubeWidth + 4}
              height={8}
              rx={2}
              fill={tube.color}
            />
          </g>
        );
      })}
      
      {/* Rack */}
      <rect x={5} y={75} width={width - 10} height={6} rx={2} fill={BRAND.lightGray} />
    </svg>
  );
};

// ============================================
// COMPONENT 6: Droplet Breakdown
// ============================================
const DropletBreakdown = ({
  segments = [
    { percent: 65, color: BRAND.blue, label: 'Primary' },
    { percent: 35, color: BRAND.orange, label: 'Secondary' }
  ],
  width = 160,
  height = 200
}) => {
  const dropletHeight = 120;
  const dropletWidth = 80;
  
  // Calculate segment heights
  let currentY = 40;
  const segmentData = segments.map(seg => {
    const segHeight = (seg.percent / 100) * (dropletHeight - 30);
    const data = { ...seg, y: currentY, height: segHeight };
    currentY += segHeight;
    return data;
  });
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <defs>
        <clipPath id="droplet-clip">
          <path d={`M ${width/2} 10 
                    Q ${width/2 + 5} 30 ${width/2 + dropletWidth/2} 80
                    Q ${width/2 + dropletWidth/2 + 10} 120 ${width/2} 150
                    Q ${width/2 - dropletWidth/2 - 10} 120 ${width/2 - dropletWidth/2} 80
                    Q ${width/2 - 5} 30 ${width/2} 10`} />
        </clipPath>
      </defs>
      
      {/* Droplet outline */}
      <path
        d={`M ${width/2} 10 
            Q ${width/2 + 5} 30 ${width/2 + dropletWidth/2} 80
            Q ${width/2 + dropletWidth/2 + 10} 120 ${width/2} 150
            Q ${width/2 - dropletWidth/2 - 10} 120 ${width/2 - dropletWidth/2} 80
            Q ${width/2 - 5} 30 ${width/2} 10`}
        fill={BRAND.lightGray}
        opacity={0.3}
      />
      
      {/* Filled segments */}
      <g clipPath="url(#droplet-clip)">
        {segmentData.map((seg, i) => (
          <rect
            key={i}
            x={0}
            y={seg.y}
            width={width}
            height={seg.height + 5}
            fill={seg.color}
          />
        ))}
      </g>
      
      {/* Labels */}
      {segmentData.map((seg, i) => (
        <g key={i}>
          <text
            x={width/2 + 55}
            y={seg.y + seg.height/2}
            fill={seg.color}
            fontSize="18"
            fontWeight="bold"
            fontFamily="Arial"
          >
            {seg.percent}%
          </text>
          <text
            x={width/2 + 55}
            y={seg.y + seg.height/2 + 16}
            fill={BRAND.mediumGray}
            fontSize="10"
            fontFamily="Arial"
          >
            {seg.label}
          </text>
        </g>
      ))}
    </svg>
  );
};

// ============================================
// COMPONENT 7: Pie Chart Row
// ============================================
const PieChart = ({ percent = 75, color = BRAND.blue, size = 60, label = '' }) => {
  const radius = size / 2 - 4;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percent / 100) * circumference;
  
  return (
    <div style={{ textAlign: 'center' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background circle */}
        <circle
          cx={size/2}
          cy={size/2}
          r={radius}
          fill={BRAND.lightGray}
          opacity={0.3}
        />
        {/* Filled portion */}
        <circle
          cx={size/2}
          cy={size/2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={radius}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform={`rotate(-90 ${size/2} ${size/2})`}
        />
        {/* Cutout to make it look like pie */}
        <circle
          cx={size/2}
          cy={size/2}
          r={radius * 0.001}
          fill={BRAND.white}
        />
      </svg>
      <div style={{
        fontSize: 14,
        fontWeight: 'bold',
        color: color,
        fontFamily: 'Arial',
        marginTop: 4
      }}>
        {percent}%
      </div>
      {label && (
        <div style={{
          fontSize: 9,
          color: BRAND.mutedGray,
          fontFamily: 'Arial'
        }}>
          {label}
        </div>
      )}
    </div>
  );
};

const PieChartRow = ({
  items = [
    { percent: 80, color: BRAND.blue, label: 'Efficacy' },
    { percent: 60, color: BRAND.mediumBlue, label: 'Uptake' },
    { percent: 45, color: BRAND.orange, label: 'Selectivity' },
    { percent: 20, color: BRAND.mutedGray, label: 'Toxicity' }
  ]
}) => (
  <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
    {items.map((item, i) => (
      <PieChart key={i} {...item} />
    ))}
  </div>
);

// ============================================
// COMPONENT 8: Team/Milestone Timeline
// ============================================
const MilestoneTimeline = ({
  milestones = [
    { label: 'TEAM', sublabel: 'A', color: BRAND.darkTeal },
    { label: 'TEAM', sublabel: 'B', color: BRAND.mediumGray },
    { label: 'TEAM', sublabel: 'C', color: BRAND.orange },
    { label: 'TEAM', sublabel: 'D', color: BRAND.blue }
  ],
  width = 320
}) => {
  const nodeRadius = 28;
  const spacing = (width - nodeRadius * 2) / (milestones.length - 1);
  
  return (
    <svg width={width} height={90} viewBox={`0 0 ${width} 90`}>
      {/* Connecting line */}
      <line
        x1={nodeRadius}
        y1={45}
        x2={width - nodeRadius}
        y2={45}
        stroke={BRAND.darkGray}
        strokeWidth={3}
      />
      
      {/* Nodes */}
      {milestones.map((m, i) => {
        const x = nodeRadius + i * spacing;
        
        return (
          <g key={i}>
            {/* Outer ring */}
            <circle
              cx={x}
              cy={45}
              r={nodeRadius}
              fill={BRAND.white}
              stroke={m.color}
              strokeWidth={3}
            />
            {/* Inner circle */}
            <circle
              cx={x}
              cy={45}
              r={nodeRadius - 6}
              fill={m.color}
            />
            {/* Label */}
            <text
              x={x}
              y={40}
              textAnchor="middle"
              fill={BRAND.white}
              fontSize="8"
              fontFamily="Arial"
            >
              {m.label}
            </text>
            {/* Sublabel */}
            <text
              x={x}
              y={53}
              textAnchor="middle"
              fill={BRAND.white}
              fontSize="14"
              fontWeight="bold"
              fontFamily="Arial"
            >
              {m.sublabel}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 9: Population Grid
// ============================================
const PopulationGrid = ({
  rows = [
    { count: 10, color: BRAND.blue, filled: 8 },
    { count: 10, color: BRAND.orange, filled: 6 }
  ],
  personWidth = 16,
  personHeight = 28
}) => {
  const personPath = "M6 2a2 2 0 104 0 2 2 0 00-4 0zm2 3c-2 0-4 1.5-4 4v5h2v6h4v-6h2V9c0-2.5-2-4-4-4z";
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {rows.map((row, ri) => (
        <svg 
          key={ri} 
          width={row.count * personWidth} 
          height={personHeight} 
          viewBox={`0 0 ${row.count * 16} 20`}
        >
          {[...Array(row.count)].map((_, i) => (
            <g key={i} transform={`translate(${i * 16}, 0) scale(0.8)`}>
              <path
                d={personPath}
                fill={i < row.filled ? row.color : BRAND.lightGray}
              />
            </g>
          ))}
        </svg>
      ))}
    </div>
  );
};

// ============================================
// COMPONENT 10: Gender Comparison
// ============================================
const GenderComparison = ({
  malePercent = 25,
  femalePercent = 75,
  maleColor = BRAND.mediumBlue,
  femaleColor = BRAND.orange
}) => {
  const malePath = "M12 4a4 4 0 100 8 4 4 0 000-8zM6 20v-4c0-2.2 2.7-4 6-4s6 1.8 6 4v4H6z";
  const femalePath = "M12 4a4 4 0 100 8 4 4 0 000-8zM6 20v-4c0-2.2 2.7-4 6-4s6 1.8 6 4v4H6z";
  
  return (
    <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
      {/* Male */}
      <div style={{ textAlign: 'center' }}>
        <svg width={40} height={50} viewBox="0 0 24 24">
          <path d={malePath} fill={maleColor} />
        </svg>
        <div style={{
          fontSize: 16,
          fontWeight: 'bold',
          color: maleColor,
          fontFamily: 'Arial'
        }}>
          {malePercent}%
        </div>
      </div>
      
      {/* Female */}
      <div style={{ textAlign: 'center' }}>
        <svg width={40} height={50} viewBox="0 0 24 24">
          <path d={femalePath} fill={femaleColor} />
          {/* Dress indication */}
          <path d="M8 16l4 4 4-4" fill={femaleColor} />
        </svg>
        <div style={{
          fontSize: 16,
          fontWeight: 'bold',
          color: femaleColor,
          fontFamily: 'Arial'
        }}>
          {femalePercent}%
        </div>
      </div>
    </div>
  );
};

// ============================================
// COMPONENT 11: Molecule Icon
// ============================================
const MoleculeIcon = ({ size = 50, color = BRAND.blue }) => (
  <svg width={size} height={size} viewBox="0 0 50 50">
    {/* Bonds */}
    <line x1={25} y1={15} x2={12} y2={30} stroke={BRAND.mediumGray} strokeWidth={2} />
    <line x1={25} y1={15} x2={38} y2={30} stroke={BRAND.mediumGray} strokeWidth={2} />
    <line x1={12} y1={30} x2={25} y2={42} stroke={BRAND.mediumGray} strokeWidth={2} />
    <line x1={38} y1={30} x2={25} y2={42} stroke={BRAND.mediumGray} strokeWidth={2} />
    
    {/* Atoms */}
    <circle cx={25} cy={15} r={7} fill={color} />
    <circle cx={12} cy={30} r={5} fill={BRAND.orange} />
    <circle cx={38} cy={30} r={5} fill={BRAND.orange} />
    <circle cx={25} cy={42} r={6} fill={BRAND.mediumBlue} />
  </svg>
);

// ============================================
// MAIN DEMO COMPONENT
// ============================================
export default function SVGLabComponents() {
  return (
    <div style={{ 
      padding: 24, 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: BRAND.white,
      maxWidth: 900
    }}>
      <h2 style={{ color: BRAND.darkGray, borderBottom: `3px solid ${BRAND.blue}`, paddingBottom: 8 }}>
        Lab & Science Illustration Components
      </h2>
      <p style={{ color: BRAND.mediumGray, fontSize: 14, marginBottom: 32 }}>
        Equipment, molecules, and data visualization elements
      </p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40 }}>
        
        {/* Decorative Icons Row */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Decorative Science Icons</h3>
          <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
            <DNAHelix height={80} />
            <AtomIcon size={60} />
            <MoleculeIcon size={50} />
          </div>
        </section>
        
        {/* Lab Equipment */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Lab Equipment Set</h3>
          <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end' }}>
            <LabFlaskWithBurner width={100} height={140} />
            <Beaker size={70} fillPercent={65} liquidColor={BRAND.blue} />
            <TestTubes width={80} height={90} />
          </div>
        </section>
        
        {/* Droplet Breakdown */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Droplet Breakdown</h3>
          <DropletBreakdown 
            segments={[
              { percent: 70, color: BRAND.blue, label: 'On-target' },
              { percent: 30, color: BRAND.orange, label: 'Off-target' }
            ]}
          />
        </section>
        
        {/* Pie Chart Row */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Pie Chart Series</h3>
          <PieChartRow 
            items={[
              { percent: 85, color: BRAND.blue, label: 'Knockdown' },
              { percent: 62, color: BRAND.mediumBlue, label: 'Uptake' },
              { percent: 48, color: BRAND.orange, label: 'Specificity' },
              { percent: 15, color: BRAND.mutedGray, label: 'Toxicity' }
            ]}
          />
        </section>
        
        {/* Milestone Timeline */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Milestone Timeline</h3>
          <MilestoneTimeline 
            milestones={[
              { label: 'PHASE', sublabel: '1', color: BRAND.darkGray },
              { label: 'PHASE', sublabel: '2', color: BRAND.blue },
              { label: 'PHASE', sublabel: '3', color: BRAND.orange },
              { label: 'PHASE', sublabel: '4', color: BRAND.darkTeal }
            ]}
          />
        </section>
        
        {/* Gender Comparison */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Gender Comparison</h3>
          <GenderComparison 
            malePercent={42}
            femalePercent={58}
          />
        </section>
        
        {/* Population Grid */}
        <section style={{ gridColumn: 'span 2' }}>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Population Grid</h3>
          <PopulationGrid 
            rows={[
              { count: 15, color: BRAND.blue, filled: 12 },
              { count: 15, color: BRAND.orange, filled: 9 }
            ]}
          />
          <div style={{ fontSize: 10, color: BRAND.mutedGray, marginTop: 8 }}>
            Treatment responders (blue: 80%) vs. Control responders (orange: 60%)
          </div>
        </section>
        
      </div>
      
      {/* Summary */}
      <section style={{ 
        marginTop: 40, 
        padding: 20, 
        backgroundColor: '#f8f8f8', 
        borderRadius: 8,
        borderLeft: `4px solid ${BRAND.darkTeal}`
      }}>
        <h4 style={{ color: BRAND.darkGray, margin: '0 0 12px 0' }}>Components from Template 3</h4>
        <div style={{ fontSize: 12, color: BRAND.mediumGray, lineHeight: 1.8 }}>
          <strong>11 New Components:</strong> DNAHelix, AtomIcon, MoleculeIcon, LabFlaskWithBurner, 
          Beaker, TestTubes, DropletBreakdown, PieChart/Row, MilestoneTimeline, 
          PopulationGrid, GenderComparison
          <br/>
          <strong>Running Total:</strong> 34 parametric components across all artifacts
        </div>
      </section>
    </div>
  );
}
