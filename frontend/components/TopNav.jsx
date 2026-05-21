"use client";

import Link from 'next/link';
import { Atom, Sparkles } from 'lucide-react';

const links = [
  { href: '/', label: 'Home' },
  { href: '/timeline', label: 'Timeline' },
];

export default function TopNav() {
  return (
    <header className="fixed inset-x-0 top-0 z-[60] border-b border-white/10 bg-black/95 backdrop-blur-2xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3 md:px-8">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold tracking-tight text-white transition-opacity hover:opacity-80">
          <Atom className="text-white" size={22} />
          CosmoPH
        </Link>

        <nav className="flex items-center gap-2 md:gap-6 text-sm text-white/70">
          <div className="hidden items-center gap-6 md:flex">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="transition-colors hover:text-white">
                {link.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/timeline"
              className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/70 px-4 py-2 text-sm font-semibold text-white/90 backdrop-blur-md transition-colors hover:bg-white/8"
            >
              <Sparkles size={16} />
              Story
            </Link>
            
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-full border border-white/14 bg-white/92 px-4 py-2.5 text-sm font-semibold text-black shadow-[0_0_24px_rgba(255,255,255,0.08)] transition-transform hover:scale-[1.02] relative z-50"
            >
              Launch App
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}
