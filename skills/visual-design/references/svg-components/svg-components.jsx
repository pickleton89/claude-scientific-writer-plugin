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
// COMPONENT 1: Donut Chart
// ============================================
const DonutChart = ({ 
  percentage = 75, 
  size = 120, 
  strokeWidth = 12,
  color = BRAND.blue,
  trackColor = BRAND.lightGray,
  label = '',
  sublabel = ''
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* Track */}
      <circle
        cx={size/2}
        cy={size/2}
        r={radius}
        fill="none"
        stroke={trackColor}
        strokeWidth={strokeWidth}
      />
      {/* Progress */}
      <circle
        cx={size/2}
        cy={size/2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        transform={`rotate(-90 ${size/2} ${size/2})`}
      />
      {/* Center text */}
      <text
        x={size/2}
        y={size/2 - 5}
        textAnchor="middle"
        dominantBaseline="middle"
        fill={BRAND.darkGray}
        fontSize="24"
        fontWeight="bold"
        fontFamily="Arial, sans-serif"
      >
        {percentage}%
      </text>
      {label && (
        <text
          x={size/2}
          y={size/2 + 18}
          textAnchor="middle"
          fill={BRAND.mediumGray}
          fontSize="11"
          fontFamily="Arial, sans-serif"
        >
          {label}
        </text>
      )}
    </svg>
  );
};

// ============================================
// COMPONENT 2: Stat Callout
// ============================================
const StatCallout = ({
  value = '999',
  label = 'Total Count',
  icon = 'chart',
  color = BRAND.blue,
  size = 'medium'
}) => {
  const iconSize = size === 'large' ? 48 : 36;
  const valueSize = size === 'large' ? 42 : 32;
  
  const icons = {
    chart: (
      <path d="M4 20h4v-8H4v8zm6 0h4V4h-4v16zm6 0h4v-12h-4v12z" fill={BRAND.white}/>
    ),
    users: (
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill={BRAND.white}/>
    ),
    target: (
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" fill={BRAND.white}/>
    ),
    flask: (
      <path d="M7 2v2h1v6.17L3.41 14.76C2.78 15.39 2.78 16.39 3.41 17.02L6.59 20.2c.63.63 1.63.63 2.26 0L12 17.05l3.15 3.15c.63.63 1.63.63 2.26 0l3.18-3.18c.63-.63.63-1.63 0-2.26L16 10.17V4h1V2H7zm7 8.83l4.59 4.59-3.18 3.18L12 15.17l-3.41 3.43-3.18-3.18L10 10.83V4h4v6.83z" fill={BRAND.white}/>
    )
  };
  
  return (
    <div style={{ textAlign: 'center', padding: '16px' }}>
      {/* Icon circle */}
      <svg width={iconSize} height={iconSize} viewBox="0 0 24 24" style={{ marginBottom: 8 }}>
        <circle cx="12" cy="12" r="12" fill={color}/>
        <g transform="scale(0.6) translate(8, 8)">
          {icons[icon] || icons.chart}
        </g>
      </svg>
      {/* Value */}
      <div style={{
        fontSize: valueSize,
        fontWeight: 'bold',
        color: color,
        fontFamily: 'Arial, sans-serif',
        lineHeight: 1.1
      }}>
        {value}
      </div>
      {/* Label */}
      <div style={{
        fontSize: 12,
        color: BRAND.mediumGray,
        fontFamily: 'Arial, sans-serif',
        marginTop: 4
      }}>
        {label}
      </div>
    </div>
  );
};

// ============================================
// COMPONENT 3: Horizontal Bar Chart
// ============================================
const HorizontalBarChart = ({
  data = [
    { label: 'Treatment A', value: 85 },
    { label: 'Treatment B', value: 62 },
    { label: 'Control', value: 45 }
  ],
  colors = [BRAND.blue, BRAND.mediumBlue, BRAND.darkGray],
  width = 280,
  barHeight = 28,
  showValues = true
}) => {
  const maxValue = Math.max(...data.map(d => d.value));
  const barWidth = width - 100; // Leave space for labels
  const height = data.length * (barHeight + 12) + 20;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {data.map((item, i) => {
        const y = i * (barHeight + 12) + 10;
        const fillWidth = (item.value / maxValue) * barWidth;
        const color = colors[i % colors.length];
        
        return (
          <g key={i}>
            {/* Label */}
            <text
              x={0}
              y={y + barHeight/2 + 4}
              fill={BRAND.darkGray}
              fontSize="11"
              fontFamily="Arial, sans-serif"
            >
              {item.label}
            </text>
            {/* Track */}
            <rect
              x={90}
              y={y}
              width={barWidth}
              height={barHeight}
              fill={BRAND.lightGray}
              opacity={0.3}
              rx={4}
            />
            {/* Bar */}
            <rect
              x={90}
              y={y}
              width={fillWidth}
              height={barHeight}
              fill={color}
              rx={4}
            />
            {/* Value */}
            {showValues && (
              <text
                x={90 + fillWidth + 8}
                y={y + barHeight/2 + 4}
                fill={BRAND.darkGray}
                fontSize="12"
                fontWeight="bold"
                fontFamily="Arial, sans-serif"
              >
                {item.value}%
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 4: Timeline / Process Flow
// ============================================
const TimelineNode = ({
  steps = [
    { number: '01', label: 'Discovery', color: BRAND.blue },
    { number: '02', label: 'Validation', color: BRAND.orange },
    { number: '03', label: 'Preclinical', color: BRAND.mediumBlue },
    { number: '04', label: 'Clinical', color: BRAND.darkTeal }
  ],
  orientation = 'horizontal'
}) => {
  const nodeSize = 50;
  const spacing = 100;
  
  if (orientation === 'horizontal') {
    const width = steps.length * spacing + 40;
    return (
      <svg width={width} height={100} viewBox={`0 0 ${width} 100`}>
        {/* Connector line */}
        <line
          x1={nodeSize/2 + 20}
          y1={35}
          x2={width - nodeSize/2 - 20}
          y2={35}
          stroke={BRAND.lightGray}
          strokeWidth={3}
        />
        {/* Nodes */}
        {steps.map((step, i) => {
          const x = i * spacing + nodeSize/2 + 20;
          return (
            <g key={i}>
              <circle
                cx={x}
                cy={35}
                r={nodeSize/2}
                fill={step.color}
              />
              <text
                x={x}
                y={40}
                textAnchor="middle"
                fill={BRAND.white}
                fontSize="14"
                fontWeight="bold"
                fontFamily="Arial, sans-serif"
              >
                {step.number}
              </text>
              <text
                x={x}
                y={80}
                textAnchor="middle"
                fill={BRAND.darkGray}
                fontSize="11"
                fontFamily="Arial, sans-serif"
              >
                {step.label}
              </text>
            </g>
          );
        })}
      </svg>
    );
  }
  
  // Vertical orientation
  const height = steps.length * 80 + 20;
  return (
    <svg width={160} height={height} viewBox={`0 0 160 ${height}`}>
      {/* Connector line */}
      <line
        x1={30}
        y1={30}
        x2={30}
        y2={height - 30}
        stroke={BRAND.lightGray}
        strokeWidth={3}
      />
      {steps.map((step, i) => {
        const y = i * 80 + 30;
        return (
          <g key={i}>
            <circle cx={30} cy={y} r={20} fill={step.color}/>
            <text
              x={30}
              y={y + 5}
              textAnchor="middle"
              fill={BRAND.white}
              fontSize="12"
              fontWeight="bold"
              fontFamily="Arial, sans-serif"
            >
              {step.number}
            </text>
            <text
              x={60}
              y={y + 5}
              fill={BRAND.darkGray}
              fontSize="12"
              fontFamily="Arial, sans-serif"
            >
              {step.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 5: Pictograph (Human figures)
// ============================================
const Pictograph = ({
  filled = 7,
  total = 10,
  color = BRAND.blue,
  label = '70% Response Rate'
}) => {
  const personPath = "M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM12 7C14.2 7 16 8.8 16 11V17H14V22H10V17H8V11C8 8.8 9.8 7 12 7Z";
  
  return (
    <div style={{ textAlign: 'center' }}>
      <svg width={200} height={50} viewBox="0 0 200 50">
        {[...Array(total)].map((_, i) => (
          <g key={i} transform={`translate(${i * 20}, 0) scale(0.8)`}>
            <path
              d={personPath}
              fill={i < filled ? color : BRAND.lightGray}
            />
          </g>
        ))}
      </svg>
      <div style={{
        fontSize: 12,
        color: BRAND.mediumGray,
        fontFamily: 'Arial, sans-serif',
        marginTop: 8
      }}>
        {label}
      </div>
    </div>
  );
};

// ============================================
// MAIN DEMO COMPONENT
// ============================================
export default function SVGComponentLibrary() {
  return (
    <div style={{ 
      padding: 24, 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: BRAND.white,
      maxWidth: 800
    }}>
      <h2 style={{ color: BRAND.darkGray, borderBottom: `3px solid ${BRAND.blue}`, paddingBottom: 8 }}>
        SVG Infographic Components
      </h2>
      <p style={{ color: BRAND.mediumGray, fontSize: 14 }}>
        Brand-compliant building blocks for scientific infographics
      </p>
      
      {/* Donut Charts */}
      <section style={{ marginTop: 32 }}>
        <h3 style={{ color: BRAND.darkGray }}>Donut Charts</h3>
        <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
          <DonutChart percentage={81} color={BRAND.blue} label="Efficacy" />
          <DonutChart percentage={55} color={BRAND.orange} label="Toxicity" />
          <DonutChart percentage={99} color={BRAND.darkTeal} label="Purity" />
        </div>
      </section>
      
      {/* Stat Callouts */}
      <section style={{ marginTop: 32 }}>
        <h3 style={{ color: BRAND.darkGray }}>Stat Callouts</h3>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <StatCallout value="725" label="Patients Enrolled" icon="users" color={BRAND.blue} />
          <StatCallout value="48" label="Target Genes" icon="target" color={BRAND.orange} />
          <StatCallout value="12" label="Lead Compounds" icon="flask" color={BRAND.mediumBlue} />
        </div>
      </section>
      
      {/* Bar Chart */}
      <section style={{ marginTop: 32 }}>
        <h3 style={{ color: BRAND.darkGray }}>Horizontal Bar Chart</h3>
        <HorizontalBarChart 
          data={[
            { label: 'siRNA-Apt', value: 87 },
            { label: 'siRNA only', value: 54 },
            { label: 'Vehicle', value: 12 }
          ]}
          colors={[BRAND.blue, BRAND.mediumGray, BRAND.lightGray]}
        />
      </section>
      
      {/* Timeline */}
      <section style={{ marginTop: 32 }}>
        <h3 style={{ color: BRAND.darkGray }}>Process Timeline</h3>
        <TimelineNode 
          steps={[
            { number: '01', label: 'Target ID', color: BRAND.darkGray },
            { number: '02', label: 'siRNA Design', color: BRAND.blue },
            { number: '03', label: 'Aptamer Link', color: BRAND.orange },
            { number: '04', label: 'In Vivo', color: BRAND.darkTeal }
          ]}
        />
      </section>
      
      {/* Pictograph */}
      <section style={{ marginTop: 32 }}>
        <h3 style={{ color: BRAND.darkGray }}>Pictograph</h3>
        <Pictograph filled={7} total={10} color={BRAND.blue} label="70% Tumor Regression" />
      </section>
      
      {/* Color Reference */}
      <section style={{ marginTop: 40, padding: 16, backgroundColor: '#f8f8f8', borderRadius: 8 }}>
        <h4 style={{ color: BRAND.darkGray, margin: '0 0 12px 0' }}>Brand Palette Reference</h4>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {Object.entries(BRAND).map(([name, hex]) => (
            <div key={name} style={{ textAlign: 'center', fontSize: 10 }}>
              <div style={{ 
                width: 40, 
                height: 40, 
                backgroundColor: hex, 
                borderRadius: 4,
                border: hex === '#FFFFFF' ? '1px solid #ccc' : 'none'
              }}/>
              <div style={{ color: BRAND.mediumGray, marginTop: 4 }}>{hex}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
