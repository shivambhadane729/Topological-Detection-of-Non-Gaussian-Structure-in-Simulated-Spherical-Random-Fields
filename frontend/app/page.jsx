'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Orbit, Radar, Sparkles, Atom } from 'lucide-react';

const stats = [
  { value: '09', label: 'Cinematic scenes' },
  { value: '3D', label: 'React Three Fiber' },
  { value: 'TDA', label: 'Topological analysis' },
];

const features = [
  'Dark cosmic visuals with glassmorphism overlays',
  'Scroll-triggered documentary-style progression',
  'Framer Motion + GSAP motion choreography',
];

export default function HomePage() {
  return (
    <div className="relative overflow-hidden">
      <section className="relative mx-auto flex min-h-[calc(100vh-5rem)] max-w-7xl flex-col justify-center px-5 py-20 md:px-8">
        <div className="absolute inset-0 -z-10 opacity-60">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(255,255,255,0.03),transparent_18%),radial-gradient(circle_at_20%_80%,rgba(255,255,255,0.02),transparent_24%),radial-gradient(circle_at_80%_70%,rgba(255,255,255,0.02),transparent_24%)]" />
          <div className="absolute inset-0 cosmic-grid opacity-25" />
        </div>

        <div className="grid items-center gap-12 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="max-w-3xl">
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-white/70 backdrop-blur-md"
            >
              <Sparkles size={14} />
              Cinematic Research Experience
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.9, delay: 0.05 }}
              className="max-w-4xl text-5xl font-semibold tracking-tight text-white md:text-7xl"
            >
              Mapping the hidden topology of the early universe.
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.15 }}
              className="mt-6 max-w-2xl text-lg leading-relaxed text-white/70"
            >
              CosmoPH turns Cosmic Microwave Background maps into a cinematic scientific story — from primordial expansion to topology-based detection of hidden structures.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="mt-10 flex flex-wrap gap-4"
            >
              <Link href="/dashboard" className="inline-flex items-center gap-2 rounded-full border border-white/14 bg-white/92 px-7 py-4 font-semibold text-black transition-transform hover:scale-[1.02]">
                Enter Workspace <ArrowRight size={18} />
              </Link>
              <Link href="/timeline" className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/60 px-7 py-4 font-semibold text-white/80 backdrop-blur-md transition-colors hover:bg-white/8">
                <Radar size={18} /> View Story
              </Link>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.15 }}
            className="glass-panel-strong story-shadow relative overflow-hidden rounded-[2rem] p-6 md:p-8"
          >
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_30%,rgba(255,255,255,0.05),transparent_26%),radial-gradient(circle_at_20%_80%,rgba(255,255,255,0.03),transparent_22%),radial-gradient(circle_at_80%_20%,rgba(255,255,255,0.03),transparent_20%)]" />
            <div className="relative">
              <div className="flex items-center justify-between text-sm text-white/60">
                <span className="inline-flex items-center gap-2"><Atom size={16} /> Live Research Mode</span>
                <span>Scroll-driven</span>
              </div>
              <div className="mt-8 grid gap-4">
                {stats.map((item) => (
                  <div key={item.label} className="rounded-2xl border border-white/10 bg-black/70 px-5 py-4 backdrop-blur-md">
                    <div className="text-3xl font-semibold text-white">{item.value}</div>
                    <div className="text-sm text-white/60">{item.label}</div>
                  </div>
                ))}
              </div>
              <div id="highlights" className="mt-6 rounded-2xl border border-white/10 bg-black/60 p-5 text-sm text-white/70 backdrop-blur-md">
                {features.map((feature) => (
                  <div key={feature} className="flex items-start gap-3 py-2">
                    <Orbit className="mt-0.5 shrink-0 text-white/80" size={16} />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
