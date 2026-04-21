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
// COMPONENT 1: Line/Area Chart (Time Series)
// ============================================
const LineAreaChart = ({
  data = [
    { year: '2018', value: 51 },
    { year: '2019', value: 39 },
    { year: '2020', value: 19 },
    { year: '2021', value: 51 },
    { year: '2022', value: 99 },
    { year: '2023', value: 78 },
    { year: '2024', value: 72 }
  ],
  width = 300,
  height = 180,
  color = BRAND.blue,
  showArea = true,
  showDots = true,
  title = ''
}) => {
  const padding = { top: 30, right: 20, bottom: 40, left: 40 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  
  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = 0;
  
  const xScale = (i) => padding.left + (i / (data.length - 1)) * chartWidth;
  const yScale = (v) => padding.top + chartHeight - ((v - minValue) / (maxValue - minValue)) * chartHeight;
  
  // Build path
  const linePath = data.map((d, i) => 
    `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(d.value)}`
  ).join(' ');
  
  const areaPath = linePath + 
    ` L ${xScale(data.length - 1)} ${padding.top + chartHeight}` +
    ` L ${padding.left} ${padding.top + chartHeight} Z`;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {/* Title */}
      {title && (
        <text x={width/2} y={16} textAnchor="middle" 
          fill={BRAND.darkGray} fontSize="12" fontWeight="bold" fontFamily="Arial">
          {title}
        </text>
      )}
      
      {/* Area fill */}
      {showArea && (
        <path d={areaPath} fill={color} opacity={0.15} />
      )}
      
      {/* Line */}
      <path d={linePath} fill="none" stroke={color} strokeWidth={2.5} strokeLinejoin="round" />
      
      {/* Data points */}
      {showDots && data.map((d, i) => (
        <g key={i}>
          <circle cx={xScale(i)} cy={yScale(d.value)} r={5} fill={BRAND.white} stroke={color} strokeWidth={2} />
          <text x={xScale(i)} y={yScale(d.value) - 10} textAnchor="middle"
            fill={BRAND.darkGray} fontSize="10" fontWeight="bold" fontFamily="Arial">
            {d.value}
          </text>
        </g>
      ))}
      
      {/* X-axis labels */}
      {data.map((d, i) => (
        <text key={i} x={xScale(i)} y={height - 10} textAnchor="middle"
          fill={BRAND.mediumGray} fontSize="10" fontFamily="Arial">
          {d.year}
        </text>
      ))}
      
      {/* Y-axis line */}
      <line x1={padding.left} y1={padding.top} x2={padding.left} y2={padding.top + chartHeight}
        stroke={BRAND.lightGray} strokeWidth={1} />
    </svg>
  );
};

// ============================================
// COMPONENT 2: Vertical Progress Bars
// ============================================
const VerticalProgressBars = ({
  data = [
    { label: 'Consect', value: 81, color: BRAND.blue },
    { label: 'Aliquam', value: 55, color: BRAND.orange },
    { label: 'Vivamus', value: 87, color: BRAND.mediumBlue },
    { label: 'Tincidun', value: 99, color: BRAND.darkTeal }
  ],
  width = 280,
  height = 200,
  barWidth = 45
}) => {
  const spacing = width / data.length;
  const maxBarHeight = height - 60;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {data.map((item, i) => {
        const x = i * spacing + spacing/2 - barWidth/2;
        const barHeight = (item.value / 100) * maxBarHeight;
        const y = height - 30 - barHeight;
        
        return (
          <g key={i}>
            {/* Track */}
            <rect x={x} y={height - 30 - maxBarHeight} width={barWidth} height={maxBarHeight}
              fill={BRAND.lightGray} opacity={0.3} rx={4} />
            {/* Bar */}
            <rect x={x} y={y} width={barWidth} height={barHeight}
              fill={item.color} rx={4} />
            {/* Percentage */}
            <text x={x + barWidth/2} y={y - 8} textAnchor="middle"
              fill={BRAND.darkGray} fontSize="14" fontWeight="bold" fontFamily="Arial">
              {item.value}%
            </text>
            {/* Label */}
            <text x={x + barWidth/2} y={height - 10} textAnchor="middle"
              fill={BRAND.mediumGray} fontSize="10" fontFamily="Arial">
              {item.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 3: Funnel / Arrow Stack
// ============================================
const ArrowStack = ({
  items = [
    { label: 'Screening', value: '1,247', color: BRAND.blue },
    { label: 'Validated', value: '423', color: BRAND.mediumBlue },
    { label: 'Lead Opts', value: '89', color: BRAND.orange },
    { label: 'Candidates', value: '12', color: BRAND.darkTeal }
  ],
  width = 180,
  arrowHeight = 50
}) => {
  const height = items.length * arrowHeight + 20;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {items.map((item, i) => {
        const y = i * arrowHeight + 10;
        const arrowWidth = width - 20;
        const tipWidth = 15;
        
        // Arrow polygon points
        const points = `
          10,${y}
          ${10 + arrowWidth - tipWidth},${y}
          ${10 + arrowWidth},${y + arrowHeight/2}
          ${10 + arrowWidth - tipWidth},${y + arrowHeight}
          10,${y + arrowHeight}
        `;
        
        return (
          <g key={i}>
            <polygon points={points} fill={item.color} />
            <text x={25} y={y + arrowHeight/2 + 4} 
              fill={BRAND.white} fontSize="11" fontWeight="bold" fontFamily="Arial">
              {item.label}
            </text>
            <text x={width - 35} y={y + arrowHeight/2 + 4} textAnchor="end"
              fill={BRAND.white} fontSize="12" fontWeight="bold" fontFamily="Arial">
              {item.value}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 4: Icon Badge Grid
// ============================================
const IconBadge = ({ icon, color = BRAND.blue, size = 48, label = '' }) => {
  const icons = {
    beaker: <path d="M6 3v6l-2 4v2h12v-2l-2-4V3H6zm2 0h4v5h-4V3zm-1 7h6l1.5 3H5.5L7 10z" fill={BRAND.white}/>,
    dna: <path d="M4 2h2v2c0 1.1.45 2.1 1.17 2.83L9 8.66V10H7v2h2v1.34l-1.83 1.83C6.45 15.9 6 16.9 6 18v2H4v-2c0-1.66.68-3.16 1.76-4.24L7.5 12l-1.74-1.76C4.68 9.16 4 7.66 4 6V2zm12 0v4c0 1.66-.68 3.16-1.76 4.24L12.5 12l1.74 1.76c1.08 1.08 1.76 2.58 1.76 4.24v2h-2v-2c0-1.1-.45-2.1-1.17-2.83L11 13.34V12h2v-2h-2V8.66l1.83-1.83C13.55 6.1 14 5.1 14 4V2h2z" fill={BRAND.white}/>,
    chart: <path d="M3 3v18h18V3H3zm16 16H5V5h14v14zM7 12h2v5H7v-5zm4-3h2v8h-2V9zm4-2h2v10h-2V7z" fill={BRAND.white}/>,
    target: <path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 18a8 8 0 110-16 8 8 0 010 16zm0-14a6 6 0 100 12 6 6 0 000-12zm0 10a4 4 0 110-8 4 4 0 010 8zm0-6a2 2 0 100 4 2 2 0 000-4z" fill={BRAND.white}/>,
    cells: <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill={BRAND.white}/>,
    molecule: <path d="M12 7a2 2 0 100-4 2 2 0 000 4zm0 14a2 2 0 100-4 2 2 0 000 4zM5.5 14.5a2 2 0 100-4 2 2 0 000 4zm13 0a2 2 0 100-4 2 2 0 000 4zM12 7v4m0 2v4M7 12h3m4 0h3" stroke={BRAND.white} strokeWidth="1.5" fill="none"/>
  };
  
  return (
    <div style={{ textAlign: 'center' }}>
      <svg width={size} height={size} viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="12" fill={color} />
        <g transform="scale(0.7) translate(5, 5)">
          {icons[icon] || icons.chart}
        </g>
      </svg>
      {label && (
        <div style={{ fontSize: 10, color: BRAND.mediumGray, marginTop: 4, fontFamily: 'Arial' }}>
          {label}
        </div>
      )}
    </div>
  );
};

const IconBadgeGrid = ({ items, columns = 3 }) => (
  <div style={{ 
    display: 'grid', 
    gridTemplateColumns: `repeat(${columns}, 1fr)`,
    gap: 16,
    padding: 8
  }}>
    {items.map((item, i) => (
      <IconBadge key={i} {...item} />
    ))}
  </div>
);

// ============================================
// COMPONENT 5: Comparison Cards (2x2 Grid)
// ============================================
const ComparisonGrid = ({
  items = [
    { number: '01', title: 'CONSE', subtitle: 'Primary endpoint', color: BRAND.blue },
    { number: '02', title: 'ETIAM', subtitle: 'Secondary endpoint', color: BRAND.orange },
    { number: '04', title: 'GRAVID', subtitle: 'Safety profile', color: BRAND.mediumBlue },
    { number: '03', title: 'BLAND', subtitle: 'Tolerability', color: BRAND.darkTeal }
  ],
  width = 280
}) => {
  const cardSize = (width - 16) / 2;
  
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 16,
      width: width
    }}>
      {items.map((item, i) => (
        <div key={i} style={{
          border: `2px solid ${item.color}`,
          borderRadius: 8,
          padding: 12,
          textAlign: 'center',
          backgroundColor: BRAND.white
        }}>
          <div style={{ 
            fontSize: 28, 
            fontWeight: 'bold', 
            color: item.color,
            fontFamily: 'Arial'
          }}>
            {item.number}
          </div>
          <div style={{ 
            fontSize: 12, 
            fontWeight: 'bold',
            color: BRAND.darkGray,
            fontFamily: 'Arial',
            marginTop: 4
          }}>
            {item.title}
          </div>
          <div style={{ 
            fontSize: 10, 
            color: BRAND.mutedGray,
            fontFamily: 'Arial'
          }}>
            {item.subtitle}
          </div>
        </div>
      ))}
    </div>
  );
};

// ============================================
// COMPONENT 6: Multi-Series Line Chart
// ============================================
const MultiLineChart = ({
  series = [
    { name: 'Treatment', color: BRAND.blue, data: [10, 25, 35, 32, 38, 40, 42, 45] },
    { name: 'Control', color: BRAND.darkGray, data: [8, 12, 15, 18, 20, 22, 24, 25] },
    { name: 'Placebo', color: BRAND.orange, data: [5, 8, 10, 12, 11, 13, 14, 15] }
  ],
  width = 320,
  height = 200,
  xLabels = ['01', '02', '03', '04', '05', '06', '07', '08']
}) => {
  const padding = { top: 20, right: 20, bottom: 40, left: 40 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  
  const allValues = series.flatMap(s => s.data);
  const maxValue = Math.max(...allValues);
  const minValue = 0;
  
  const xScale = (i, len) => padding.left + (i / (len - 1)) * chartWidth;
  const yScale = (v) => padding.top + chartHeight - ((v - minValue) / (maxValue - minValue)) * chartHeight;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {/* Grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
        <line key={i}
          x1={padding.left} y1={padding.top + chartHeight * (1 - pct)}
          x2={width - padding.right} y2={padding.top + chartHeight * (1 - pct)}
          stroke={BRAND.lightGray} strokeWidth={1} opacity={0.5}
        />
      ))}
      
      {/* Lines */}
      {series.map((s, si) => {
        const path = s.data.map((v, i) => 
          `${i === 0 ? 'M' : 'L'} ${xScale(i, s.data.length)} ${yScale(v)}`
        ).join(' ');
        
        return (
          <g key={si}>
            <path d={path} fill="none" stroke={s.color} strokeWidth={2.5} 
              strokeDasharray={si === 1 ? '8,4' : si === 2 ? '2,2' : 'none'} />
            {s.data.map((v, i) => (
              <circle key={i} cx={xScale(i, s.data.length)} cy={yScale(v)} 
                r={4} fill={s.color} />
            ))}
          </g>
        );
      })}
      
      {/* X labels */}
      {xLabels.map((label, i) => (
        <text key={i} x={xScale(i, xLabels.length)} y={height - 10} textAnchor="middle"
          fill={BRAND.mediumGray} fontSize="10" fontFamily="Arial">
          {label}
        </text>
      ))}
      
      {/* Legend */}
      {series.map((s, i) => (
        <g key={i} transform={`translate(${padding.left + i * 90}, ${height - 25})`}>
          <line x1={0} y1={0} x2={20} y2={0} stroke={s.color} strokeWidth={2}
            strokeDasharray={i === 1 ? '8,4' : i === 2 ? '2,2' : 'none'} />
          <text x={25} y={4} fill={BRAND.mediumGray} fontSize="9" fontFamily="Arial">
            {s.name}
          </text>
        </g>
      ))}
    </svg>
  );
};

// ============================================
// COMPONENT 7: Grouped Bar Chart (Vertical)
// ============================================
const GroupedBarChart = ({
  categories = ['Tris', 'Que', 'Non', 'Lac', 'Sin', 'Ame'],
  series = [
    { name: 'Group A', color: BRAND.blue, data: [35, 28, 22, 30, 25, 18] },
    { name: 'Group B', color: BRAND.orange, data: [25, 32, 18, 28, 20, 15] }
  ],
  width = 320,
  height = 200
}) => {
  const padding = { top: 20, right: 20, bottom: 50, left: 40 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  
  const allValues = series.flatMap(s => s.data);
  const maxValue = Math.max(...allValues);
  
  const groupWidth = chartWidth / categories.length;
  const barWidth = (groupWidth - 10) / series.length;
  
  const yScale = (v) => (v / maxValue) * chartHeight;
  
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {/* Y-axis line */}
      <line x1={padding.left} y1={padding.top} x2={padding.left} y2={padding.top + chartHeight}
        stroke={BRAND.lightGray} strokeWidth={1} />
      
      {/* X-axis line */}
      <line x1={padding.left} y1={padding.top + chartHeight} 
        x2={width - padding.right} y2={padding.top + chartHeight}
        stroke={BRAND.lightGray} strokeWidth={1} />
      
      {/* Bars */}
      {categories.map((cat, ci) => (
        <g key={ci}>
          {series.map((s, si) => {
            const x = padding.left + ci * groupWidth + si * barWidth + 5;
            const barHeight = yScale(s.data[ci]);
            const y = padding.top + chartHeight - barHeight;
            
            return (
              <rect key={si} x={x} y={y} width={barWidth - 2} height={barHeight}
                fill={s.color} rx={2} />
            );
          })}
          <text x={padding.left + ci * groupWidth + groupWidth/2} y={height - 30}
            textAnchor="middle" fill={BRAND.mediumGray} fontSize="10" fontFamily="Arial">
            {cat}
          </text>
        </g>
      ))}
      
      {/* Legend */}
      {series.map((s, i) => (
        <g key={i} transform={`translate(${padding.left + i * 80}, ${height - 12})`}>
          <rect x={0} y={-8} width={12} height={12} fill={s.color} rx={2} />
          <text x={16} y={2} fill={BRAND.mediumGray} fontSize="9" fontFamily="Arial">
            {s.name}
          </text>
        </g>
      ))}
    </svg>
  );
};

// ============================================
// COMPONENT 8: Circular Process / Hub
// ============================================
const CircularHub = ({
  centerLabel = 'Core',
  centerValue = '999',
  nodes = [
    { label: 'Step A', icon: '📊' },
    { label: 'Step B', icon: '🧬' },
    { label: 'Step C', icon: '💊' },
    { label: 'Step D', icon: '📈' }
  ],
  color = BRAND.blue,
  size = 220
}) => {
  const centerRadius = 45;
  const nodeRadius = 28;
  const orbitRadius = size/2 - nodeRadius - 10;
  
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* Orbit circle */}
      <circle cx={size/2} cy={size/2} r={orbitRadius} 
        fill="none" stroke={BRAND.lightGray} strokeWidth={2} strokeDasharray="8,4" />
      
      {/* Center hub */}
      <circle cx={size/2} cy={size/2} r={centerRadius} fill={color} />
      <text x={size/2} y={size/2 - 5} textAnchor="middle" 
        fill={BRAND.white} fontSize="20" fontWeight="bold" fontFamily="Arial">
        {centerValue}
      </text>
      <text x={size/2} y={size/2 + 14} textAnchor="middle" 
        fill={BRAND.white} fontSize="10" fontFamily="Arial">
        {centerLabel}
      </text>
      
      {/* Orbital nodes */}
      {nodes.map((node, i) => {
        const angle = (i / nodes.length) * 2 * Math.PI - Math.PI/2;
        const x = size/2 + Math.cos(angle) * orbitRadius;
        const y = size/2 + Math.sin(angle) * orbitRadius;
        
        return (
          <g key={i}>
            {/* Connector line */}
            <line x1={size/2} y1={size/2} x2={x} y2={y}
              stroke={BRAND.lightGray} strokeWidth={1} />
            {/* Node circle */}
            <circle cx={x} cy={y} r={nodeRadius} fill={BRAND.white} 
              stroke={color} strokeWidth={2} />
            <text x={x} y={y - 3} textAnchor="middle" fontSize="16">
              {node.icon}
            </text>
            <text x={x} y={y + 14} textAnchor="middle" 
              fill={BRAND.mediumGray} fontSize="8" fontFamily="Arial">
              {node.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================
// COMPONENT 9: Feature Box Grid
// ============================================
const FeatureBoxGrid = ({
  items = [
    { title: 'IACULS', desc: 'In vitro screening', color: BRAND.blue },
    { title: 'FUSCE', desc: 'Target validation', color: BRAND.orange },
    { title: 'EFFICIT', desc: 'Lead optimization', color: BRAND.mediumBlue },
    { title: 'SODAL', desc: 'ADMET profiling', color: BRAND.darkTeal },
    { title: 'FEUGIA', desc: 'Formulation dev', color: BRAND.darkGray },
    { title: 'AUCTO', desc: 'Scale-up synthesis', color: BRAND.mutedGray }
  ],
  columns = 2
}) => (
  <div style={{
    display: 'grid',
    gridTemplateColumns: `repeat(${columns}, 1fr)`,
    gap: 8
  }}>
    {items.map((item, i) => (
      <div key={i} style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '10px 12px',
        borderLeft: `4px solid ${item.color}`,
        backgroundColor: '#f9f9f9'
      }}>
        <div>
          <div style={{ 
            fontSize: 12, 
            fontWeight: 'bold', 
            color: item.color,
            fontFamily: 'Arial'
          }}>
            {item.title}
          </div>
          <div style={{ 
            fontSize: 10, 
            color: BRAND.mutedGray,
            fontFamily: 'Arial'
          }}>
            {item.desc}
          </div>
        </div>
      </div>
    ))}
  </div>
);

// ============================================
// COMPONENT 10: Big Stat with Mini Chart
// ============================================
const StatWithMiniChart = ({
  value = '725',
  label = 'Total Subjects',
  miniData = [3, 5, 4, 7, 6, 8, 7],
  color = BRAND.blue
}) => {
  const chartWidth = 60;
  const chartHeight = 30;
  const maxVal = Math.max(...miniData);
  
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12 }}>
      {/* Mini bar chart */}
      <svg width={chartWidth} height={chartHeight} viewBox={`0 0 ${chartWidth} ${chartHeight}`}>
        {miniData.map((v, i) => {
          const barWidth = chartWidth / miniData.length - 2;
          const barHeight = (v / maxVal) * chartHeight;
          return (
            <rect key={i}
              x={i * (barWidth + 2)}
              y={chartHeight - barHeight}
              width={barWidth}
              height={barHeight}
              fill={color}
              opacity={0.6 + (i / miniData.length) * 0.4}
            />
          );
        })}
      </svg>
      {/* Big number */}
      <div>
        <div style={{ 
          fontSize: 42, 
          fontWeight: 'bold', 
          color: color,
          fontFamily: 'Arial',
          lineHeight: 1
        }}>
          {value}
        </div>
        <div style={{ 
          fontSize: 11, 
          color: BRAND.mediumGray,
          fontFamily: 'Arial'
        }}>
          {label}
        </div>
      </div>
    </div>
  );
};

// ============================================
// MAIN DEMO COMPONENT
// ============================================
export default function SVGComponentLibraryExpanded() {
  return (
    <div style={{ 
      padding: 24, 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: BRAND.white,
      maxWidth: 900
    }}>
      <h2 style={{ color: BRAND.darkGray, borderBottom: `3px solid ${BRAND.blue}`, paddingBottom: 8 }}>
        Extended SVG Component Library
      </h2>
      <p style={{ color: BRAND.mediumGray, fontSize: 14, marginBottom: 32 }}>
        Additional infographic building blocks • All brand-compliant
      </p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40 }}>
        
        {/* Line/Area Chart */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Line/Area Chart</h3>
          <LineAreaChart 
            title="Annual Enrollment"
            data={[
              { year: '2019', value: 45 },
              { year: '2020', value: 32 },
              { year: '2021', value: 58 },
              { year: '2022', value: 89 },
              { year: '2023', value: 76 },
              { year: '2024', value: 94 }
            ]}
            color={BRAND.blue}
          />
        </section>
        
        {/* Vertical Progress Bars */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Vertical Progress Bars</h3>
          <VerticalProgressBars />
        </section>
        
        {/* Arrow/Funnel Stack */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Arrow Funnel Stack</h3>
          <ArrowStack 
            items={[
              { label: 'Screened', value: '2,847', color: BRAND.blue },
              { label: 'Validated', value: '892', color: BRAND.mediumBlue },
              { label: 'Optimized', value: '156', color: BRAND.orange },
              { label: 'Selected', value: '24', color: BRAND.darkTeal }
            ]}
          />
        </section>
        
        {/* Icon Badge Grid */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Icon Badges</h3>
          <IconBadgeGrid 
            columns={3}
            items={[
              { icon: 'beaker', color: BRAND.blue, label: 'Assays' },
              { icon: 'dna', color: BRAND.orange, label: 'Genomics' },
              { icon: 'target', color: BRAND.mediumBlue, label: 'Targets' },
              { icon: 'cells', color: BRAND.darkTeal, label: 'Cell Lines' },
              { icon: 'molecule', color: BRAND.darkGray, label: 'Compounds' },
              { icon: 'chart', color: BRAND.mutedGray, label: 'Analysis' }
            ]}
          />
        </section>
        
        {/* Multi-Line Chart */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Multi-Series Line Chart</h3>
          <MultiLineChart />
        </section>
        
        {/* Grouped Bar Chart */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Grouped Bar Chart</h3>
          <GroupedBarChart />
        </section>
        
        {/* Comparison Grid */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Comparison Grid (2×2)</h3>
          <ComparisonGrid 
            items={[
              { number: '01', title: 'Efficacy', subtitle: 'Primary endpoint', color: BRAND.blue },
              { number: '02', title: 'Safety', subtitle: 'AE profile', color: BRAND.orange },
              { number: '03', title: 'PK/PD', subtitle: 'Exposure metrics', color: BRAND.darkTeal },
              { number: '04', title: 'Biomarkers', subtitle: 'Target engagement', color: BRAND.mediumBlue }
            ]}
          />
        </section>
        
        {/* Circular Hub */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Circular Hub</h3>
          <CircularHub 
            centerLabel="Pipeline"
            centerValue="48"
            nodes={[
              { label: 'Discovery', icon: '🔬' },
              { label: 'Preclinical', icon: '🐁' },
              { label: 'Phase I', icon: '💉' },
              { label: 'Phase II', icon: '📋' }
            ]}
          />
        </section>
        
        {/* Feature Box Grid */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Feature Box Grid</h3>
          <FeatureBoxGrid />
        </section>
        
        {/* Stat with Mini Chart */}
        <section>
          <h3 style={{ color: BRAND.darkGray, fontSize: 14 }}>Stat with Mini Chart</h3>
          <StatWithMiniChart 
            value="1,247"
            label="siRNA Candidates Screened"
            miniData={[2, 4, 3, 6, 5, 8, 9]}
            color={BRAND.blue}
          />
        </section>
        
      </div>
      
      {/* Component Summary */}
      <section style={{ 
        marginTop: 40, 
        padding: 20, 
        backgroundColor: '#f8f8f8', 
        borderRadius: 8,
        borderLeft: `4px solid ${BRAND.blue}`
      }}>
        <h4 style={{ color: BRAND.darkGray, margin: '0 0 12px 0' }}>Component Summary</h4>
        <div style={{ fontSize: 12, color: BRAND.mediumGray, lineHeight: 1.8 }}>
          <strong>10 Components Total:</strong> LineAreaChart, VerticalProgressBars, ArrowStack, 
          IconBadge/Grid, ComparisonGrid, MultiLineChart, GroupedBarChart, CircularHub, 
          FeatureBoxGrid, StatWithMiniChart
          <br/>
          <strong>All parametric</strong> — pass data arrays, colors, labels as props
          <br/>
          <strong>Brand-locked</strong> — uses BRAND object from your v4 spec
        </div>
      </section>
    </div>
  );
}
