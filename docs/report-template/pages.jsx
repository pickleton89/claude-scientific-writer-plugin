// pages.jsx — Report page mocks for the Oligon report template.
// Each page is fixed at US Letter (816 × 1056 px). Variants ('editorial' /
// 'banded' / 'data') swap a class on the .page root; CSS overlays handle
// the styling deltas. Cover is variant-specific because the layouts differ
// substantially.

const REPORT = {
  programCode: 'SeekR-AT-08',
  reportNum:   'OL-RR-2026-014',
  date:        'May 2026',
  classification: 'Internal · Pre-clinical',
  title: <>Choosing the door:<br/> <em>extracellular targets for aptamer–siRNA internalization</em></>,
  titlePlain: 'Choosing the door — extracellular targets for aptamer–siRNA internalization',
  deck: 'A target-by-target evaluation of receptor candidates for the SeekR aptamer–siRNA delivery platform, comparing CCR6 and CTLA-4 against the platform\'s endosomal-trafficking and selectivity requirements.',
  authors: [
    { name: 'J. Chambers, PhD',  role: 'Lead, Discovery Biology' },
    { name: 'Research Pod 03',   role: 'SeekR platform' },
    { name: 'Document control', role: 'Strategy & Knowledge' },
  ],
};

// ───────────────────────────────────────────────────────────────────────────
// Shared chrome
// ───────────────────────────────────────────────────────────────────────────
function PageChrome({ pageLabel, pageNo, total, children, variant }) {
  return (
    <>
      <div className="page-header">
        <img className="icon" src="assets/Oligon_Icon_BrandBlue.svg" alt="" />
        <span className="meta">Oligon · {pageLabel}</span>
        <span className="rule" />
        <span>{REPORT.programCode}</span>
      </div>
      <div className="page-body">{children}</div>
      <div className="page-footer">
        <span>{REPORT.reportNum}</span>
        <span className="rule" />
        <span className="conf">{REPORT.classification}</span>
        <span className="pg">{String(pageNo).padStart(2, '0')} / {String(total).padStart(2, '0')}</span>
      </div>
    </>
  );
}

function Page({ variant = 'editorial', children, className = '', cover = false }) {
  const cls = ['page', `v-${variant}`, className, cover ? 'cover' : ''].filter(Boolean).join(' ');
  return <div className={cls}>{children}</div>;
}

// ═══════════════════════════════════════════════════════════════════════════
// COVERS
// ═══════════════════════════════════════════════════════════════════════════

// V1 — Editorial: minimal, orbital-dot motif, restraint
function CoverEditorial() {
  return (
    <Page variant="editorial" cover>
      <OrbitalArt />
      <div className="top">
        <img src="assets/Oligon_Logo_BrandBlue.svg" alt="Oligon" />
        <div className="meta-block">
          <strong>{REPORT.programCode}</strong>
          Research Report &nbsp;·&nbsp; {REPORT.date}
        </div>
      </div>
      <div className="cover-body">
        <div className="eyebrow">Research Report &nbsp;·&nbsp; SeekR Platform</div>
        <h1>{REPORT.title}</h1>
        <p className="deck">{REPORT.deck}</p>
        <div className="auth-grid">
          {REPORT.authors.map(a => (
            <div key={a.name}><strong>{a.name}</strong>{a.role}</div>
          ))}
        </div>
      </div>
    </Page>
  );
}

// V2 — Banded: Brand Blue band w/ white wordmark, lower section deck
function CoverBanded() {
  return (
    <Page variant="banded" cover>
      <div className="band">
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <img src="assets/Oligon_Logo_White.svg" alt="Oligon" />
          <div className="meta-block" style={{color:'rgba(255,255,255,0.85)'}}>
            <strong style={{color:'#fff'}}>{REPORT.programCode}</strong>
            Research Report &nbsp;·&nbsp; {REPORT.date}
          </div>
        </div>
        <div>
          <div className="eyebrow">Target Assessment · Internal</div>
          <h1>{REPORT.title}</h1>
        </div>
      </div>
      <div className="lower">
        <p className="deck">{REPORT.deck}</p>
        <div className="auth-grid">
          {REPORT.authors.map(a => (
            <div key={a.name}><strong>{a.name}</strong>{a.role}</div>
          ))}
        </div>
      </div>
    </Page>
  );
}

// V3 — Data-led: hero figure, title compressed below
function CoverData() {
  return (
    <Page variant="data" cover>
      <div className="top">
        <img src="assets/Oligon_Logo_BrandBlue.svg" alt="Oligon" />
        <div className="meta-block">
          <strong>{REPORT.programCode}</strong>
          Research Report &nbsp;·&nbsp; {REPORT.date}
        </div>
      </div>
      <div className="hero-fig">
        <FigHeroTarget />
      </div>
      <div className="cover-body">
        <div className="eyebrow">Research Report &nbsp;·&nbsp; SeekR Platform</div>
        <h1>{REPORT.title}</h1>
        <div className="auth-grid">
          {REPORT.authors.map(a => (
            <div key={a.name}><strong>{a.name}</strong>{a.role}</div>
          ))}
        </div>
      </div>
    </Page>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// INNER PAGES — same content across variants; styling deltas via CSS class
// ═══════════════════════════════════════════════════════════════════════════

function ExecSummary({ variant }) {
  return (
    <Page variant={variant}>
      <PageChrome pageLabel="Executive Summary" pageNo={2} total={28} variant={variant}>
        <div className="sec-marker">
          <span className="num">01</span>
          <span className="label">Executive Summary</span>
        </div>
        <h1 className="display">A modular delivery platform <em>only works if its door does</em>.</h1>
        <p className="lede">
          Picking the right surface protein for aptamer targeting is really
          asking which door into the cell gets the cargo to the right room,
          fast enough, without getting shredded. This report assesses two
          candidate doors against the SeekR platform's three non-negotiable
          criteria and recommends the next-step shortlist.
        </p>

        <div className="summary-grid">
          <div className="stat"><div className="num">12</div><div className="lab">Candidate receptors screened</div></div>
          <div className="stat"><div className="num">4 / 10</div><div className="lab">CCR6 overall suitability</div></div>
          <div className="stat"><div className="num">5 / 10</div><div className="lab">CTLA-4 overall suitability</div></div>
        </div>

        <h2>What we found</h2>
        <p>
          <strong>CCR6</strong> has the best Th17 selectivity of any candidate
          (signature marker on Th17, partial overlap with Tregs, B cells, ILC3).
          But the trafficking is wrong: CCR6 is a Class A GPCR. β-arrestin 2
          recruitment peaks at ~5 minutes and decays by 20 minutes, predicting
          rapid recycling and a short endosomal dwell time. No published
          aptamer exists. <span className="pill warn">High biology, low delivery</span>
        </p>
        <p>
          <strong>CTLA-4</strong> has outstanding delivery mechanics —
          constitutive clathrin-mediated endocytosis, dual recycling/degradation
          paths with a Rab11-dominant route, ~2 h surface half-life, and a
          published 11.84 nM DNA aptamer. But it is expressed on virtually all
          activated T cells and Tregs, and ectodomain binding risks accidental
          checkpoint blockade. <span className="pill">Strong delivery, weak selectivity</span>
        </p>

        <div className="callout">
          <div className="label">Key recommendation · 01</div>
          <p>Neither candidate is sufficient as a single target. Advance both
          in parallel as platform-modularity exemplars, but elevate IL-23R and
          CD161 (KLRB1) into the next-round screen — both are Th17-enriched
          and have published trafficking precedent.</p>
        </div>
        <div className="callout warn">
          <div className="label">Risk flag · 01</div>
          <p>For CTLA-4, any aptamer binding the IgV ECD risks competing with
          CD80 / CD86 — i.e. acting as ipilimumab. Engineer a non-competing
          epitope or a pH-dependent release linker before therapeutic claims.</p>
        </div>
      </PageChrome>
    </Page>
  );
}

function TocPage({ variant }) {
  const sections = [
    ['01', 'Executive summary',  'Headline findings, recommendation, risk flags',  '02'],
    ['02', 'Methodology',        'Search strategy, scoring matrix, evidence codes', '04'],
    ['03', 'Decision framework', 'Seven criteria, ranked by clinical impact',       '06'],
    ['04', 'CCR6 dossier',       'Th17 selectivity vs. Class A GPCR trafficking',   '09'],
    ['05', 'CTLA-4 dossier',     'Constitutive endocytosis, Rab11 recycling',       '13'],
    ['06', 'Head-to-head',       'Six-criterion scoring matrix; figure suite',      '17'],
    ['07', 'Recommendation',     'Shortlist, next-round candidates, decision gates','22'],
    ['08', 'Appendix · References', 'Source papers, GO terms, database queries',    '25'],
  ];
  return (
    <Page variant={variant}>
      <PageChrome pageLabel="Contents" pageNo={3} total={28} variant={variant}>
        <div className="eyebrow">Contents</div>
        <h1 className="display">Eight sections, in order.</h1>
        <p className="lede">
          Eight sections. Read the executive summary if you have five minutes;
          jump to §6 for the head-to-head if you have fifteen.
        </p>
        <div className="divider" />
        <div>
          {sections.map(([n, title, sub, pg]) => (
            <div className="toc-row" key={n}>
              <div className="toc-num">{n}</div>
              <div>
                <div className="toc-title">{title}</div>
                <div className="toc-sub">{sub}</div>
              </div>
              <div className="toc-pg">p.&nbsp;{pg}</div>
            </div>
          ))}
        </div>
      </PageChrome>
    </Page>
  );
}

function MethodPage({ variant }) {
  return (
    <Page variant={variant}>
      <PageChrome pageLabel="Methodology" pageNo={4} total={28} variant={variant}>
        <div className="sec-marker">
          <span className="num">02</span>
          <span className="label">Methodology &amp; Sources</span>
        </div>
        <h1 className="display">How we mined trafficking data <em>without a wet lab</em>.</h1>
        <p className="lede">
          Endosomal trafficking data is fragmented across thousands of
          papers and rarely compiled into clean databases. Our approach uses
          five layered sources, each with explicit evidence codes.
        </p>

        <h2><span className="num">2.1</span>Rab GTPase decoder</h2>
        <p>
          Rab markers are the zip codes of the endosomal system. Receptor
          colocalization with Rab5 (early endosome) → Rab11 (slow recycling)
          predicts a long dwell time and is the win condition. Rab7 / LAMP1
          colocalization predicts lysosomal degradation.
        </p>

        <h2><span className="num">2.2</span>Search strategy</h2>
        <div className="kv">
          <dt>Database layer</dt><dd>UniProt · Human Protein Atlas · Reactome · KEGG · Gene Ontology · COMPARTMENTS · BioGRID · STRING</dd>
          <dt>Aptamer corpus</dt><dd>Aptamer Base · APTANI · PubMed `[receptor] AND aptamer AND (SELEX OR selection)`</dd>
          <dt>Evidence threshold</dt><dd>IDA / IMP preferred; IEA reported with caveat flag</dd>
          <dt>Inclusion window</dt><dd>2005 – present, supplemented with seminal pre-2005 papers</dd>
        </div>

        <h2><span className="num">2.3</span>Scoring matrix</h2>
        <p>
          Each candidate scored against twelve criteria; four are
          gating (internalization confirmed, ECD accessible, no shedding sink,
          tumor/normal differential ≥ 10×). "Unknown" is treated as a risk
          flag, not a neutral.
        </p>
        <div className="callout neutral">
          <div className="label">Honest gap</div>
          <p>The literature gives a receptor's <i>native</i> trafficking
          behavior. The aptamer chimera may change that. This is a genuine
          unknown that ultimately requires experimental validation; our scoring
          identifies candidates worth running, not candidates that will work.</p>
        </div>
      </PageChrome>
    </Page>
  );
}

function FindingsPage({ variant }) {
  return (
    <Page variant={variant}>
      <PageChrome pageLabel="Key Findings" pageNo={5} total={28} variant={variant}>
        <div className="sec-marker">
          <span className="num">03</span>
          <span className="label">Key Findings</span>
        </div>
        <h1 className="display">Three findings <em>that should change the program plan</em>.</h1>

        <h2><span className="num">3.1</span>CCR6 trafficking is the wrong shape</h2>
        <p>
          Lu et al. (2018, <i>Front. Immunol.</i>) characterised CCR6 / β-arrestin 2
          binding kinetics directly: complex formation peaks at ~5 minutes
          and decays by 20 minutes. This is the canonical Class A GPCR
          pattern — fast in, fast out. The endosomal dwell time available for
          siRNA escape is short, and no published Rab colocalization
          time-course exists for CCR6 specifically.
        </p>
        <div className="callout">
          <div className="label">Key finding · 01</div>
          <p>CCR6's biology is excellent (<strong>9/10</strong> on disease relevance),
          but its post-internalization trafficking scores <strong>3/10</strong>.
          A modular platform built on CCR6 inherits this ceiling.</p>
        </div>

        <h2><span className="num">3.2</span>CTLA-4 has the trafficking, not the selectivity</h2>
        <p>
          Janman et al. (2021) provides the Rab time-course CCR6 lacks:
          CTLA-4 internalises constitutively, dwells in Rab5⁺ early endosomes,
          and routes preferentially through Rab11⁺ slow recycling endosomes
          with a ~2 h surface half-life. LRBA deficiency redirects CTLA-4 to
          lysosomal degradation, providing a clean genetic lever.
        </p>
        <div className="callout warn">
          <div className="label">Key finding · 02 · Risk</div>
          <p>~90% of CTLA-4 is intracellular at steady state. Surface density
          is the rate-limiter, not internalisation. A multivalent aptamer or
          higher-affinity binder is required to compete with native CD80/86
          engagement.</p>
        </div>

        <h2><span className="num">3.3</span>Modularity is the platform story, not the target</h2>
        <p>
          Both candidates fail the single-target test. The strategic answer
          is to lean into the SeekR platform's modularity: ship a panel of
          aptamer modules against 3–4 internalising targets and let
          target-swap velocity be the differentiator vs. ADC competition.
          For ARENA, that <i>is</i> the deck.
        </p>
      </PageChrome>
    </Page>
  );
}

function FigurePage({ variant }) {
  return (
    <Page variant={variant}>
      <PageChrome pageLabel="Figures · Trafficking" pageNo={17} total={28} variant={variant}>
        <div className="sec-marker">
          <span className="num">06</span>
          <span className="label">Figure suite · 6.1</span>
        </div>
        <h1 className="display">Where the cargo ends up <em>determines whether the cargo works</em>.</h1>

        <div className="fig-wrap">
          <div className="fig"><FigTrafficking /></div>
          <div className="caption-side">
            <span className="fnum">Figure 6.1</span>
            <span className="ftitle">Endosomal fates of an internalised aptamer–siRNA chimera.</span>
            Three branch points decide whether the siRNA reaches the cytoplasm:
            (i) fast Rab4 recycling returns intact cargo to the surface before
            escape;
            (ii) Rab11 slow recycling provides a long dwell window — the
            preferred fate;
            (iii) Rab7 → LAMP1 routes to lysosomal degradation.
            <br/><br/>
            <strong style={{color:'#222'}}>Reading the graphic.</strong> Rab marker
            colours follow the report's convention — Brand Blue for the
            preferred recycling pathway, Contrast Orange for the rapid
            recycling that defeats delivery, neutrals for compartments that
            destroy payload.
          </div>
        </div>

        <div className="fig-bleed">
          <div className="fig" style={{padding:'18px 24px'}}>
            <FigScoring />
          </div>
          <div className="fig-cap">
            <div>
              <span className="fnum">Figure 6.2</span>
              Six-criterion scoring matrix for CCR6 and CTLA-4. Bars show
              scaled scores 0 – 10; CCR6 outperforms on Th17 selectivity and
              off-target safety, CTLA-4 dominates on internalisation mechanics,
              endosomal trafficking, and aptamer feasibility (an existing
              11.84 nM DNA aptamer is published).
            </div>
            <div style={{borderLeft:'1px solid #E5E5E5', paddingLeft:'14px', fontSize:'8.5pt'}}>
              <strong style={{color:'#222',display:'block',marginBottom:'4px'}}>n / Source</strong>
              n = 6 criteria, weighted equally. Sources: Lu 2018; Janman 2021;
              Qureshi 2012; Huang 2017; Krummey 2014.
            </div>
          </div>
        </div>
      </PageChrome>
    </Page>
  );
}

function TablePage({ variant }) {
  return (
    <Page variant={variant}>
      <PageChrome pageLabel="Head-to-Head" pageNo={20} total={28} variant={variant}>
        <div className="sec-marker">
          <span className="num">06</span>
          <span className="label">Comparison · 6.4</span>
        </div>
        <h1 className="display">Head-to-head: <em>CCR6 vs. CTLA-4</em></h1>
        <p className="lede">
          Same eleven criteria, scored against the same evidence threshold. A
          single &quot;winner&quot; column is intentionally provocative — neither
          target wins the platform; both should advance into the next gating
          experiment.
        </p>
        <table className="tbl">
          <thead>
            <tr>
              <th style={{width:'30%'}}>Criterion</th>
              <th>CCR6</th>
              <th>CTLA-4</th>
              <th style={{width:'14%'}}>Winner</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Th17 selectivity</td><td>Moderate — also on Tregs, B cells, DCs</td><td>Poor — all activated T cells + Tregs</td><td className="score-good">CCR6</td></tr>
            <tr><td>Internalisation trigger</td><td>Ligand-induced (CCL20)</td><td>Constitutive (always cycling)</td><td className="score-good">CTLA-4</td></tr>
            <tr><td>Trafficking for escape</td><td>Class A GPCR · ~5 min β-arr peak</td><td>Rab11 slow recycling · ~2 h t½</td><td className="score-good">CTLA-4</td></tr>
            <tr><td>Rab colocalisation data</td><td>None published</td><td>Complete (Rab5 / 7 / 9 / 11)</td><td className="score-good">CTLA-4</td></tr>
            <tr><td>ECD accessibility</td><td>Small GPCR loops · ~46 aa N-term</td><td>Large IgV domain · ~120 aa</td><td className="score-good">CTLA-4</td></tr>
            <tr><td>Aptamer precedent</td><td>None</td><td>Published · K<sub>d</sub> 11.84 nM</td><td className="score-good">CTLA-4</td></tr>
            <tr><td>Surface copy number</td><td>Moderate (~1 – 10K)</td><td>Very low (~10% surface)</td><td className="score-good">CCR6</td></tr>
            <tr><td>Serum sink risk</td><td>None (no shedding)</td><td>sCTLA-4 splice variant</td><td className="score-good">CCR6</td></tr>
            <tr><td>Off-target pharmacology</td><td>Minimal</td><td>Checkpoint-blockade risk</td><td className="score-good">CCR6</td></tr>
            <tr><td>Disease relevance (Th17)</td><td>Outstanding · GWAS-linked</td><td>Outstanding · CHAI; AID</td><td className="score-mid">Tie</td></tr>
            <tr><td><strong>Overall</strong></td><td><strong>4 / 10</strong></td><td><strong>5 / 10</strong></td><td className="score-good">CTLA-4</td></tr>
          </tbody>
        </table>
        <div className="callout neutral" style={{marginTop:'14px'}}>
          <div className="label">Reading the table</div>
          <p>"Winner" is a directional cue, not a rank. CTLA-4 takes 6 of 11
          criteria but loses safety and selectivity decisively. The
          recommended path forward (§07) is platform-level, not target-level.</p>
        </div>
      </PageChrome>
    </Page>
  );
}

function ReferencesPage({ variant }) {
  const refs = [
    ['Qureshi, O. S., et al. (2012). Constitutive clathrin-mediated endocytosis of CTLA-4 persists during T cell activation. ', <i key="i1">J. Biol. Chem.</i>, ' 287(12), 9429–9440. ', <span key="d1" className="doi">10.1074/jbc.m111.304329</span>],
    ['Janman, D., et al. (2021). Regulation of CTLA-4 recycling by LRBA and Rab11. ', <i key="i2">Immunology</i>, ' 164(1), 106–119. ', <span key="d2" className="doi">10.1111/imm.13343</span>],
    ['Lu, M.-Y., et al. (2018). Phosphorylation of CCR6 on distinct Ser/Thr residues differentially regulates biological function. ', <i key="i3">Front. Immunol.</i>, ' 9, 415. ', <span key="d3" className="doi">10.3389/fimmu.2018.00415</span>],
    ['Huang, Z., et al. (2017). A DNA aptamer recognising CTLA-4 with K\u2090 = 11.84 nM. ', <i key="i4">Mol. Ther. Nucleic Acids</i>, ' 8, 520–528. ', <span key="d4" className="doi">10.1016/j.omtn.2017.08.006</span>],
    ['Valk, E., Rudd, C. E., & Schneider, H. (2008). CTLA-4 trafficking and surface expression. ', <i key="i5">Trends Immunol.</i>, ' 29(6), 272–279. ', <span key="d5" className="doi">10.1016/j.it.2008.02.011</span>],
    ['Krummey, S. M., et al. (2014). High CTLA-4 expression on Th17 memory cells confers coinhibitory sensitivity. ', <i key="i6">Am. J. Transplant.</i>, ' 14(3), 607–614. ', <span key="d6" className="doi">10.1111/ajt.12600</span>],
    ['Lo, B., et al. (2015). Patients with LRBA deficiency show CTLA4 loss and immune dysregulation. ', <i key="i7">Science</i>, ' 349(6246), 436–440. ', <span key="d7" className="doi">10.1126/science.aaa1663</span>],
    ['Zhang, Y., et al. (2025). pH-dependent dissociation of anti-CTLA-4 antibodies improves intratumoral specificity. ', <i key="i8">PNAS</i>, ' 122(8). ', <span key="d8" className="doi">10.1073/pnas.2422731122</span>],
    ['Gilboa, E., et al. (2013). Aptamer-targeted immunotherapy. ', <i key="i9">Clin. Cancer Res.</i>, ' 19(5), 1054–1062. ', <span key="d9" className="doi">10.1158/1078-0432.ccr-12-2067</span>],
    ['Liao, F., et al. (1999). CC-chemokine receptor 6 is expressed on diverse memory subsets of T cells. ', <i key="ia">J. Immunol.</i>, ' 162(1), 186–194.'],
    ['Ying, H., et al. (2010). CTLA-4–B7 interactions specifically suppress Th17 differentiation. ', <i key="ib">J. Immunol.</i>, ' 185(3), 1375–1382. ', <span key="db" className="doi">10.4049/jimmunol.0903369</span>],
  ];
  return (
    <Page variant={variant}>
      <PageChrome pageLabel="References" pageNo={26} total={28} variant={variant}>
        <div className="sec-marker">
          <span className="num">08</span>
          <span className="label">Appendix · References</span>
        </div>
        <h1 className="display">Sources cited.</h1>
        <p className="lede">
          Eleven primary sources, weighted toward direct trafficking
          measurements (Rab colocalisation, half-life, internalisation
          kinetics) and published aptamer characterisations.
        </p>
        <div className="refs">
          <ol>
            {refs.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ol>
        </div>

        <h2 style={{marginTop:'24px'}}><span className="num">A.1</span>Search queries used</h2>
        <div className="kv">
          <dt>PubMed q1</dt><dd><code>"[receptor]" AND (endocytosis OR internalization OR trafficking) AND (Rab5 OR Rab7 OR Rab11 OR endosome OR lysosome)</code></dd>
          <dt>PubMed q2</dt><dd><code>"[receptor]" AND (internalization rate OR half-life OR recycling)</code></dd>
          <dt>Aptamer q</dt><dd><code>"[receptor]" AND aptamer AND (SELEX OR selection)</code></dd>
        </div>
      </PageChrome>
    </Page>
  );
}

Object.assign(window, {
  REPORT, Page, PageChrome,
  CoverEditorial, CoverBanded, CoverData,
  ExecSummary, TocPage, MethodPage, FindingsPage,
  FigurePage, TablePage, ReferencesPage,
});
