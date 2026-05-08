// app.jsx — wires the report pages into a DesignCanvas, organised so each
// section row shows the same page across the three template variations.

const { useEffect } = React;

const VARIANTS = [
  { id: 'editorial', label: 'V1 · Editorial',  cover: CoverEditorial },
  { id: 'banded',    label: 'V2 · Banded',     cover: CoverBanded },
];

const PAGE_W = 816;
const PAGE_H = 1056;

// Each section row: one page type, three variant artboards.
function VariantRow({ id, title, subtitle, render }) {
  return (
    <DCSection id={id} title={title} subtitle={subtitle}>
      {VARIANTS.map(v => (
        <DCArtboard
          key={v.id}
          id={`${id}-${v.id}`}
          label={v.label}
          width={PAGE_W}
          height={PAGE_H}
        >
          {render(v.id, v.cover)}
        </DCArtboard>
      ))}
    </DCSection>
  );
}

function App() {
  return (
    <DesignCanvas>
      <VariantRow
        id="cover"
        title="01 · Cover"
        subtitle="Three cover treatments — minimal, banded, data-led"
        render={(_, Cover) => <Cover />}
      />
      <VariantRow
        id="exec"
        title="02 · Executive Summary"
        subtitle="Numbered section markers · eyebrow · tinted callouts · stat strip"
        render={v => <ExecSummary variant={v} />}
      />
      <VariantRow
        id="toc"
        title="03 · Table of Contents"
        subtitle="Numbered, section-keyed; same scaffold across variants"
        render={v => <TocPage variant={v} />}
      />
      <VariantRow
        id="method"
        title="04 · Methodology"
        subtitle="Definition list, sub-numbered headings, neutral callout for honest gaps"
        render={v => <MethodPage variant={v} />}
      />
      <VariantRow
        id="findings"
        title="05 · Key Findings"
        subtitle="Tinted callouts (info / warn) carry the headline conclusions"
        render={v => <FindingsPage variant={v} />}
      />
      <VariantRow
        id="figures"
        title="06 · Figures & Data"
        subtitle="Caption sidebar (Fig 6.1) · full-bleed with data-source aside (Fig 6.2)"
        render={v => <FigurePage variant={v} />}
      />
      <VariantRow
        id="tables"
        title="07 · Comparison Table"
        subtitle="Standard scientific table; striped rows; brand-blue/orange score chips"
        render={v => <TablePage variant={v} />}
      />
      <VariantRow
        id="refs"
        title="08 · References & Appendix"
        subtitle="Numbered list with brand-blue markers; mono DOI; embedded query block"
        render={v => <ReferencesPage variant={v} />}
      />
    </DesignCanvas>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
