'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CircleDot, Compass, Gauge, Sparkles } from 'lucide-react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import CosmicCanvas from './CosmicCanvas';

gsap.registerPlugin(ScrollTrigger);

const scenes = [
  {
    kind: 'bang',
    label: 'Birth of the Universe',
    title: 'Birth of the Universe',
    subtitle: 'The universe begins expanding.',
    copy: 'Dark space ignites in a glowing shockwave, setting the scale for everything that follows.',
    detail: 'A cinematic Big Bang opens the story with expanding particles and cosmic waves.',
    accent: 'from-white via-zinc-300 to-zinc-500',
  },
  {
    kind: 'expansion',
    label: 'Early Universe Expansion',
    title: 'Universe Expansion',
    subtitle: 'Tiny fluctuations emerge in the early universe.',
    copy: 'Matter and radiation begin to spread, galaxies slowly condense, and the cosmic stage expands.',
    detail: 'This phase shows the universe stretching into a structure-rich landscape.',
    accent: 'from-zinc-300 via-zinc-400 to-zinc-600',
  },
  {
    kind: 'cmb',
    label: 'Cosmic Microwave Background',
    title: 'Cosmic Microwave Background (CMB)',
    subtitle: 'A snapshot of the early universe.',
    copy: 'The universe cools and releases relic radiation that becomes the CMB — a map of primordial conditions.',
    detail: 'A realistic glowing sphere reveals red and blue temperature fluctuations inspired by Planck data.',
    accent: 'from-zinc-200 via-zinc-400 to-zinc-600',
  },
  {
    kind: 'patterns',
    label: 'Hidden Patterns',
    title: 'Hidden Patterns Exist',
    subtitle: 'Tiny structures may contain clues about the early universe.',
    copy: 'Zoom into fluctuation regions and subtle structures begin to emerge from the heatmap.',
    detail: 'The scene highlights where topology can uncover what the eye cannot easily see.',
    accent: 'from-zinc-300 via-zinc-400 to-zinc-500',
  },
  {
    kind: 'stats',
    label: 'Traditional Methods Fail',
    title: 'Traditional Methods Miss Complex Structures',
    subtitle: 'Global statistics cannot detect all hidden patterns.',
    copy: 'Gaussian curves and standard graphs smooth away local complexity, hiding what matters most.',
    detail: 'This scene explains why conventional summaries are not enough for the morphology of CMB maps.',
    accent: 'from-zinc-300 via-zinc-400 to-zinc-500',
  },
  {
    kind: 'topology',
    label: 'Topology-Based Analysis',
    title: 'Topological Data Analysis',
    subtitle: 'Analyzing the shape of the data.',
    copy: 'Connected nodes, loops, and persistence-like geometry reveal how structures birth and die across scales.',
    detail: 'Topology converts a noisy map into interpretable shape signatures.',
    accent: 'from-zinc-200 via-zinc-400 to-zinc-600',
  },
  {
    kind: 'engine',
    label: 'Persistent Homology Engine',
    title: 'Persistent Homology Engine',
    subtitle: 'Detecting hidden structures in cosmological data.',
    copy: 'Data streams into a luminous engine core where the topology computation unfolds.',
    detail: 'This is the computational heart of the pipeline — the point where the story becomes analysis.',
    accent: 'from-zinc-300 via-zinc-500 to-zinc-700',
  },
  {
    kind: 'detected',
    label: 'Hidden Structures Detected',
    title: 'Hidden Structures Detected',
    subtitle: 'Topology reveals structures missed by traditional methods.',
    copy: 'Detected regions pulse on the map and a scientific UI confirms that patterns have been found.',
    detail: 'The map now shows where topology reveals anomalies hidden in the cosmic background.',
    accent: 'from-zinc-200 via-zinc-400 to-zinc-600',
  },
  {
    kind: 'ending',
    label: 'Final Cosmic Understanding',
    title: 'Understanding the Early Universe',
    subtitle: 'Topology-Based Analysis of Cosmic Microwave Background Data',
    copy: 'Zoom out into the cosmic web and the universe resolves into a connected, readable structure.',
    detail: 'The story ends with the project identity: TopoSphere.',
    accent: 'from-white via-zinc-200 to-zinc-400',
    finalTitle: 'TopoSphere',
  },
];

function scenePlaceholderSVG(title, index) {
  const colors = ["#071224","#0b1930","#12202b","#071a52","#08131f","#092038","#071a52","#0b1930","#071224"];
  const color = colors[index % colors.length];
  const svg = `
    <svg xmlns='http://www.w3.org/2000/svg' width='1200' height='800'>
      <defs>
        <linearGradient id='g' x1='0' x2='1'>
          <stop offset='0' stop-color='${color}' stop-opacity='1'/>
          <stop offset='1' stop-color='#000000' stop-opacity='0.25'/>
        </linearGradient>
      </defs>
      <rect width='100%' height='100%' fill='url(#g)' />
      <g fill='rgba(255,255,255,0.06)'>
        <rect x='80' y='60' width='420' height='280' rx='28' />
        <circle cx='980' cy='640' r='220' />
      </g>
      <text x='60' y='720' font-family='Inter, Roboto, sans-serif' font-size='48' fill='rgba(255,255,255,0.9)'>${title}</text>
    </svg>
  `;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

function SceneBadge({ active, index }) {
  return (
    <div className={`flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.35em] ${active ? 'text-white' : 'text-white/40'}`}>
      <CircleDot size={12} className={active ? 'text-white' : 'text-white/30'} />
      Scene {String(index + 1).padStart(2, '0')}
    </div>
  );
}

function ScenePanel({ scene, active }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -24 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className="glass-panel-strong story-shadow relative overflow-hidden rounded-[2rem] p-6 md:p-8"
    >
      <div className={`absolute inset-0 bg-[radial-gradient(circle_at_50%_15%,rgba(255,255,255,0.08),transparent_28%),linear-gradient(135deg,rgba(255,255,255,0.02),transparent_32%)]`} />
        <div className="relative">
          <SceneBadge active={active} index={scene.index} />
          <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/70 px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.35em] text-white/60 backdrop-blur-md">
            <Sparkles size={12} /> {scene.label}
          </div>
          <h2 className="mt-5 max-w-3xl text-3xl font-semibold tracking-tight text-white md:text-5xl">
            {scene.title}
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-white/72 md:text-lg">
            {scene.subtitle}
          </p>
        </div>
    </motion.div>
  );
}

export default function TimelineExperience() {
  const containerRef = useRef(null);
  const progressRef = useRef(null);
  const [activeIndex, setActiveIndex] = useState(0);

  const sceneData = useMemo(
    () => scenes.map((scene, index) => ({ ...scene, index })),
    []
  );

  useEffect(() => {
    const ctx = gsap.context(() => {
      const sections = gsap.utils.toArray('[data-scene]');

      sections.forEach((section, index) => {
        ScrollTrigger.create({
          trigger: section,
          start: 'top center',
          end: 'bottom center',
          onEnter: () => setActiveIndex(index),
          onEnterBack: () => setActiveIndex(index),
        });
      });

      gsap.to(progressRef.current, {
        scaleX: 1,
        ease: 'none',
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top top',
          end: 'bottom bottom',
          scrub: 1,
        },
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  const activeScene = sceneData[activeIndex];

  return (
    <div ref={containerRef} className="relative overflow-hidden">
      <div className="fixed inset-0 -z-10">
        <CosmicCanvas scene={activeScene} />
      </div>

      <div className="fixed inset-x-0 top-20 z-30 px-5 md:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="glass-panel-strong story-shadow flex items-center justify-between gap-4 rounded-full px-4 py-3 text-xs uppercase tracking-[0.35em] text-white/55 md:px-6">
            <span className="inline-flex items-center gap-2 text-white/80">
              <Compass size={14} /> Scroll the story
            </span>
            <div className="flex-1 px-4">
              <div className="h-1 overflow-hidden rounded-full bg-white/10">
                <div ref={progressRef} className="h-full w-full origin-left rounded-full bg-white/80" style={{ transform: 'scaleX(0)' }} />
              </div>
            </div>
            <span className="hidden items-center gap-2 text-white/50 md:inline-flex">
              <Gauge size={14} /> Cinematic timeline
            </span>
          </div>
        </div>
      </div>

      <section className="mx-auto flex min-h-[88vh] max-w-7xl items-end px-5 pb-16 pt-20 md:px-8 md:pb-20">
        <div className="max-w-4xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-white/65 backdrop-blur-md">
            <Sparkles size={14} /> Research Documentary Experience
          </div>
          <h1 className="max-w-5xl text-4xl font-semibold tracking-tight text-white md:text-7xl">
            A cinematic journey from the Big Bang to hidden structures in the CMB.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-relaxed text-white/70 md:text-lg">
            Scroll through the story of the early universe, the Cosmic Microwave Background, and the moment topology reveals what standard statistics miss.
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-5 pb-24 md:px-8">
        <div className="space-y-20 md:space-y-28">
          {sceneData.map((scene, index) => (
            <section key={scene.title} data-scene className="min-h-screen py-6 md:py-10">
              <div className="grid items-center gap-8 lg:grid-cols-[1.25fr_0.75fr]">

                    <ScenePanel key={scene.title} scene={scene} active={index === activeIndex} />

                    <div className="hidden min-h-[34rem] rounded-[2rem] border border-dashed border-white/8 bg-black/35 lg:block overflow-hidden" aria-hidden="true">
                      <img src={scene.image || scenePlaceholderSVG(scene.title, index)} alt={scene.title} className="h-full w-full object-cover" />
                    </div>

                <AnimatePresence mode="wait">
                  <div />
                </AnimatePresence>
              </div>
            </section>
          ))}
        </div>
      </div>

      <section className="mx-auto max-w-7xl px-5 pb-24 md:px-8">
        <div className="glass-panel-strong story-shadow rounded-[2rem] p-8 text-center md:p-12">
          <div className="text-xs font-semibold uppercase tracking-[0.4em] text-white/50">Final Reveal</div>
          <h2 className="mt-4 text-4xl font-semibold tracking-tight text-white md:text-6xl">TopoSphere</h2>
          <p className="mx-auto mt-5 max-w-3xl text-base leading-relaxed text-white/68 md:text-lg">
            Topology-Based Analysis of Cosmic Microwave Background Data.
          </p>
        </div>
      </section>
    </div>
  );
}
