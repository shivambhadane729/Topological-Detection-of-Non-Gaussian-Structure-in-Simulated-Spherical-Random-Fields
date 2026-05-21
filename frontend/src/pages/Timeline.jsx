import React from 'react';
import { Link } from 'react-router-dom';
import { Atom, ArrowLeft, ArrowRight, Sparkles, Radar, Target, Eye, Network, ChevronRight, Zap } from 'lucide-react';

const scenes = [
  {
    number: '01',
    title: 'Birth of the Universe',
    caption: 'A cosmic shockwave ignites the first light.',
    kind: 'bang',
    overlay: 'Birth of the Universe',
    accent: 'from-white via-cyan-200 to-transparent',
  },
  {
    number: '02',
    title: 'Universe Expansion',
    caption: 'Matter, energy, and galaxies begin to unfold.',
    kind: 'expansion',
    overlay: 'The Universe Begins Expanding',
    accent: 'from-violet-300 via-fuchsia-200 to-transparent',
  },
  {
    number: '03',
    title: 'Ancient Cosmic Radiation',
    caption: 'Cooling plasma leaves behind a fading glow.',
    kind: 'radiation',
    overlay: 'Ancient Cosmic Radiation is Released',
    accent: 'from-amber-200 via-orange-200 to-transparent',
  },
  {
    number: '04',
    title: 'Cosmic Microwave Background',
    caption: 'A spherical map preserves the earliest imprint.',
    kind: 'cmb',
    overlay: 'Cosmic Microwave Background (CMB)',
    accent: 'from-sky-300 via-blue-200 to-transparent',
    subtitle: 'A snapshot of the early universe',
  },
  {
    number: '05',
    title: 'Hidden Patterns',
    caption: 'Subtle structures emerge inside temperature fluctuations.',
    kind: 'patterns',
    overlay: 'Tiny Hidden Patterns Exist in the Data',
    accent: 'from-emerald-300 via-teal-200 to-transparent',
  },
  {
    number: '06',
    title: 'Traditional Methods Fail',
    caption: 'Gaussian summaries blur away the complex shape.',
    kind: 'fail',
    overlay: 'Traditional Methods Miss Complex Structures',
    accent: 'from-stone-300 via-zinc-200 to-transparent',
  },
  {
    number: '07',
    title: 'Topology-Based Analysis',
    caption: 'Connected components and loops reveal data geometry.',
    kind: 'topology',
    overlay: 'Topology-Based Analysis',
    accent: 'from-cyan-300 via-indigo-200 to-transparent',
    subtitle: 'Analyzing the shape of data',
  },
  {
    number: '08',
    title: 'Hidden Structures Detected',
    caption: 'Anomalies light up as the topology becomes visible.',
    kind: 'detected',
    overlay: 'Hidden Structures are Detected',
    accent: 'from-rose-300 via-orange-200 to-transparent',
  },
  {
    number: '09',
    title: 'Final Understanding',
    caption: 'The universe resolves into a readable cosmic web.',
    kind: 'ending',
    overlay: 'Towards a Better Understanding of the Early Universe',
    accent: 'from-white via-violet-200 to-transparent',
    subtitle: 'Topology-Based Analysis of Cosmic Microwave Background Data',
    finalTitle: 'CosmoTDA',
  },
];

function scenePlaceholderSVG(title, index) {
  const colors = ["#0f172a","#001219","#1f2937","#071a52","#0f172a","#0b2545","#071a52","#001219","#0f172a"];
  const color = colors[index % colors.length];
  const svg = `
    <svg xmlns='http://www.w3.org/2000/svg' width='1200' height='800'>
      <defs>
        <linearGradient id='g' x1='0' x2='1'>
          <stop offset='0' stop-color='${color}' stop-opacity='1'/>
          <stop offset='1' stop-color='#000000' stop-opacity='0.2'/>
        </linearGradient>
      </defs>
      <rect width='100%' height='100%' fill='url(#g)' />
      <g fill='rgba(255,255,255,0.06)'>
        <circle cx='200' cy='120' r='180' />
        <circle cx='980' cy='640' r='260' />
      </g>
      <text x='60' y='720' font-family='Inter, Roboto, sans-serif' font-size='48' fill='rgba(255,255,255,0.9)'>${title}</text>
    </svg>
  `;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}
const SceneIcon = ({ kind }) => {
  switch (kind) {
    case 'bang':
      return <Sparkles size={18} />;
    case 'expansion':
      return <ArrowRight size={18} />;
    case 'radiation':
      return <Zap size={18} />;
    case 'cmb':
      return <Radar size={18} />;
    case 'patterns':
      return <Eye size={18} />;
    case 'fail':
      return <Target size={18} />;
    case 'topology':
      return <Network size={18} />;
    case 'detected':
      return <Sparkles size={18} />;
    case 'ending':
      return <Atom size={18} />;
    default:
      return <ChevronRight size={18} />;
  }
};

function SceneVisual({ kind }) {
  return (
    <div className={`timeline-visual timeline-visual--${kind}`}>
      <div className="timeline-stars" />
      {kind === 'bang' && (
        <>
          <div className="timeline-burst" />
          <div className="timeline-burst timeline-burst--soft" />
          <div className="timeline-particles">
            {Array.from({ length: 18 }).map((_, index) => (
              <span key={index} style={{ '--delay': `${index * 120}ms`, '--angle': `${index * 20}deg` }} />
            ))}
          </div>
        </>
      )}
      {kind === 'expansion' && (
        <>
          <div className="timeline-nebula timeline-nebula--left" />
          <div className="timeline-nebula timeline-nebula--right" />
          <div className="timeline-galaxy-grid" />
          {Array.from({ length: 6 }).map((_, index) => (
            <span key={index} className="timeline-galaxy" style={{ '--delay': `${index * 900}ms`, '--x': `${14 + index * 12}%`, '--y': `${18 + (index % 3) * 18}%` }} />
          ))}
        </>
      )}
      {kind === 'radiation' && (
        <>
          <div className="timeline-radiation-wave" />
          <div className="timeline-radiation-ring" />
          <div className="timeline-radiation-glow" />
        </>
      )}
      {kind === 'cmb' && (
        <>
          <div className="timeline-sphere">
            <div className="timeline-cmb-map" />
            <div className="timeline-sphere-glow" />
          </div>
          <div className="timeline-cmb-hud">
            <span>temperature fluctuations</span>
            <span>early universe snapshot</span>
          </div>
        </>
      )}
      {kind === 'patterns' && (
        <>
          <div className="timeline-lens" />
          <div className="timeline-pattern-grid" />
          <div className="timeline-pattern-signals">
            {Array.from({ length: 4 }).map((_, index) => (
              <span key={index} className="timeline-signal" style={{ '--delay': `${index * 700}ms`, '--x': `${20 + index * 14}%`, '--y': `${32 + (index % 2) * 18}%` }} />
            ))}
          </div>
        </>
      )}
      {kind === 'fail' && (
        <>
          <div className="timeline-chart-grid" />
          <div className="timeline-gaussian-curve" />
          <div className="timeline-fade-mask" />
        </>
      )}
      {kind === 'topology' && (
        <>
          <div className="timeline-network-grid" />
          <div className="timeline-node-cluster timeline-node-cluster--left" />
          <div className="timeline-node-cluster timeline-node-cluster--right" />
          <div className="timeline-loops" />
        </>
      )}
      {kind === 'detected' && (
        <>
          <div className="timeline-detection-rings" />
          <div className="timeline-detection-hud" />
          <div className="timeline-anomaly-pulse" />
        </>
      )}
      {kind === 'ending' && (
        <>
          <div className="timeline-cosmic-web" />
          <div className="timeline-cosmic-web timeline-cosmic-web--second" />
          <div className="timeline-final-glow" />
        </>
      )}
    </div>
  );
}

function TimelineCard({ scene }) {
  return (
    <article className="timeline-card snap-center">
      <div className="timeline-card-topbar">
        <span>{scene.number}</span>
        <span className="timeline-card-label"><SceneIcon kind={scene.kind} /> {scene.title}</span>
      </div>
      <div className="relative overflow-hidden rounded-[2rem] border border-outline bg-black shadow-[0_0_0_1px_rgba(255,255,255,0.02),0_30px_90px_rgba(0,0,0,0.6)]">
        <img src={scene.image || scenePlaceholderSVG(scene.title, Number(scene.number) - 1)} alt={scene.title} className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-black/30 backdrop-blur-[1px]" />
        <div className="absolute inset-x-0 bottom-0 p-6 md:p-8">
          <div className={`inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/40 px-3 py-1 text-[10px] uppercase tracking-[0.4em] text-on-surface-variant backdrop-blur-md`}>
            <span className="h-1.5 w-1.5 rounded-full bg-white animate-pulse" /> Scene {scene.number}
          </div>
          <h2 className="mt-4 max-w-3xl text-3xl font-semibold tracking-tight text-primary md:text-5xl">
            {scene.overlay}
          </h2>
          {scene.subtitle && (
            <p className="mt-3 max-w-xl text-sm text-on-surface-variant md:text-base">
              {scene.subtitle}
            </p>
          )}
        </div>
      </div>

      <div className="mt-4 flex items-start justify-between gap-4">
        <p className="max-w-xl text-sm leading-relaxed text-on-surface-variant md:text-base">
          {scene.caption}
        </p>
        <div className={`timeline-accent-bar bg-gradient-to-r ${scene.accent}`} />
      </div>

      {scene.finalTitle && (
        <div className="mt-8 rounded-3xl border border-white/10 bg-white/5 px-6 py-5 text-center backdrop-blur-md">
          <div className="text-4xl font-semibold tracking-[0.25em] text-primary md:text-5xl">
            {scene.finalTitle}
          </div>
        </div>
      )}
    </article>
  );
}

export default function Timeline() {
  return (
    <div className="min-h-screen bg-background text-on-surface font-sans selection:bg-accent/30 selection:text-white">
      <nav className="fixed top-0 z-50 w-full border-b border-white/10 bg-black/70 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2 text-lg font-bold tracking-tight text-primary transition-opacity hover:opacity-80">
            <Atom className="text-accent" size={22} />
            CosmoPH
          </Link>
          <div className="flex items-center gap-6 text-sm font-medium text-on-surface-variant">
            <Link to="/" className="hidden transition-colors hover:text-primary md:inline-flex items-center gap-2">
              <ArrowLeft size={15} /> Home
            </Link>
            <Link to="/timeline" className="text-primary inline-flex items-center gap-2">
              <Sparkles size={15} /> Timeline
            </Link>
            <Link to="/dashboard" className="rounded-full border border-white/15 bg-white px-5 py-2 font-semibold text-black shadow-[0_0_24px_rgba(255,255,255,0.22)] transition-transform hover:scale-[1.03]">
              Launch App
            </Link>
          </div>
        </div>
      </nav>

      <main className="timeline-page pt-24 md:pt-28">
        <section className="mx-auto max-w-7xl px-6 pb-10 pt-10 md:pb-14 md:pt-14">
          <div className="max-w-3xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-on-surface-variant backdrop-blur-md">
              <span className="h-2 w-2 rounded-full bg-white animate-pulse" /> Cinematic Scientific Story
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-primary md:text-6xl">
              A journey from the Big Bang to hidden structures in the CMB.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-on-surface-variant md:text-lg">
              A research-documentary style animation that follows cosmic evolution, the formation of the Cosmic Microwave Background, and the moment topology-based analysis reveals what standard statistics miss.
            </p>
          </div>
        </section>

        <section className="timeline-stage">
          <div className="timeline-rail" aria-label="Cosmic timeline story progression">
            {scenes.map((scene) => (
              <TimelineCard key={scene.number} scene={scene} />
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-6 py-12 md:py-16">
          <div className="grid gap-4 md:grid-cols-3">
            {[
              { title: 'Cinematic', desc: 'Dark cosmic visuals, glowing particles, and smooth motion.' },
              { title: 'Scientific', desc: 'A visual explanation of CMB maps and topology-based detection.' },
              { title: 'Minimal Text', desc: 'The story is driven by imagery, motion, and subtle UI overlays.' },
            ].map((item) => (
              <div key={item.title} className="rounded-3xl border border-outline bg-surface/50 p-6 backdrop-blur-md">
                <div className="text-sm font-bold uppercase tracking-[0.3em] text-primary">{item.title}</div>
                <p className="mt-3 text-sm leading-relaxed text-on-surface-variant">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
