'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  LayoutDashboard,
  MessageSquare,
  Search,
  FileText,
  BookOpen,
  Wrench,
  Settings,
  Send,
  Menu,
  ChevronLeft,
  ExternalLink,
  Clock,
  Sparkles,
  Zap,
  Database,
  Play,
  TrendingUp,
  Bot,
  FolderOpen,
  Layers,
  Tag,
  Users,
  Megaphone,
  Plug,
  Workflow,
  Bug,
  Shield,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from '@/components/ui/sheet';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { EliMarkdown } from '@/components/eli-markdown';

// ─── Types ───────────────────────────────────────────────────────
type ViewId =
  | 'dashboard'
  | 'chat'
  | 'knowledge'
  | 'seo-skills'
  | 'keywords'
  | 'intro'
  | 'leads'
  | 'audits'
  | 'campaigns'
  | 'content'
  | 'rank'
  | 'integrations'
  | 'workflows'
  | 'scrapers'
  | 'vault'
  | 'settings';

interface NavItem {
  id: ViewId;
  label: string;
  icon: React.ElementType;
  group: 'main' | 'systems' | 'beta';
}

interface ChatMessage {
  id: string;
  role: 'user' | 'eli';
  content: string;
  sources?: Array<{ title: string; source: string; category: string }>;
  timestamp: Date;
}

interface KnowledgeCategory {
  key: string;
  count: number;
}

interface KnowledgeStats {
  totalFiles: number;
  totalCategories: number;
  totalSizeMB: string;
  categories: KnowledgeCategory[];
}

// ─── Navigation ──────────────────────────────────────────────────
const NAV_ITEMS: NavItem[] = [
  // Active features
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, group: 'main' },
  { id: 'chat', label: 'Chat', icon: MessageSquare, group: 'main' },
  { id: 'intro', label: 'Introduction', icon: Play, group: 'main' },
  { id: 'seo-skills', label: 'SEO Skills', icon: Wrench, group: 'main' },
  { id: 'keywords', label: 'Keywords', icon: Tag, group: 'main' },
  { id: 'knowledge', label: 'Knowledge', icon: BookOpen, group: 'main' },
  // Beta (coming soon)
  { id: 'leads', label: 'Leads', icon: Users, group: 'beta' },
  { id: 'audits', label: 'Audits', icon: Search, group: 'beta' },
  { id: 'campaigns', label: 'Campaigns', icon: Megaphone, group: 'beta' },
  { id: 'content', label: 'Content', icon: FileText, group: 'beta' },
  { id: 'rank', label: 'Rank', icon: TrendingUp, group: 'beta' },
  { id: 'integrations', label: 'Integrations', icon: Plug, group: 'beta' },
  { id: 'workflows', label: 'Workflows', icon: Workflow, group: 'beta' },
  { id: 'scrapers', label: 'Scrapers', icon: Bug, group: 'beta' },
  { id: 'vault', label: 'Vault', icon: Shield, group: 'beta' },
  { id: 'settings', label: 'Settings', icon: Settings, group: 'beta' },
];

const CATEGORY_META: Record<string, { emoji: string; label: string; color: string }> = {
  'seo': { emoji: '\uD83D\uDD0D', label: 'SEO & Marketing', color: '#2563eb' },
  'codebase': { emoji: '\uD83D\uDCBB', label: 'Code & Scraping', color: '#7c3aed' },
  'web-design': { emoji: '\uD83C\uDFA8', label: 'Web Design & UI', color: '#dc2626' },
  'ai-agent': { emoji: '\uD83E\uDD16', label: 'AI Agents & Tools', color: '#059669' },
  'saas': { emoji: '\uD83D\uDCB0', label: 'SaaS & Business', color: '#d97706' },
  'productivity': { emoji: '\u26A1', label: 'Productivity & Automation', color: '#2563eb' },
  'reference': { emoji: '\uD83D\uDCDA', label: 'Reference & Research', color: '#7c3aed' },
  'brand': { emoji: '\uD83C\uDFF7\uFE0F', label: 'VirtuaLab Brand', color: '#dc2626' },
  'strategy': { emoji: '\uD83D\uDCCB', label: 'Strategy & Planning', color: '#059669' },
  'analysis': { emoji: '\uD83D\uDCCA', label: 'Design Analysis', color: '#d97706' },
  'screenshot': { emoji: '\uD83D\uDCF8', label: 'Screenshots', color: '#64748b' },
  'eli-core': { emoji: '\uD83E\uDDE0', label: 'Eli Core Identity', color: '#7c3aed' },
  'obsidian': { emoji: '\uD83D\uDCE6', label: 'Obsidian Vault', color: '#2563eb' },
  'agent-eli': { emoji: '\u2699\uFE0F', label: 'Agent Eli v1 Architecture', color: '#059669' },
  'google-api': { emoji: '\uD83D\uDD17', label: 'Google API Ecosystem', color: '#059669' },
  'crm-sales': { emoji: '\uD83D\uDCCA', label: 'CRM & Sales Tools', color: '#2563eb' },
  'project-mgmt': { emoji: '\uD83D\uDCCB', label: 'Project Management', color: '#7c3aed' },
  'copywriting-ai': { emoji: '\u270D\uFE0F', label: 'Copywriting & AI Content', color: '#dc2626' },
  'cloud-infra': { emoji: '\u2601\uFE0F', label: 'Cloud & Infrastructure', color: '#d97706' },
  'cybersecurity': { emoji: '\uD83D\uDD12', label: 'Cybersecurity', color: '#dc2626' },
  'design-uiux': { emoji: '\uD83C\uDFA8', label: 'Design & UI/UX Tools', color: '#2563eb' },
  'llm-ai': { emoji: '\uD83E\uDD16', label: 'LLM & AI Frameworks', color: '#059669' },
  'vps-hosting': { emoji: '\uD83D\uDDA5\uFE0F', label: 'VPS & Hosting', color: '#7c3aed' },
  'database': { emoji: '\uD83D\uDDC2\uFE0F', label: 'Database Tools', color: '#d97706' },
  'github-multi': { emoji: '\uD83D\uDCC2', label: 'GitHub Multi-Topic Directory', color: '#64748b' },
  'notion-tools': { emoji: '\uD83D\uDCD3', label: 'Notion & Knowledge Mgmt', color: '#2563eb' },
  'gohighlevel-agency': { emoji: '\uD83C\uDFE2', label: 'GoHighLevel & Agency', color: '#059669' },
  'automation-workflow': { emoji: '\u2699\uFE0F', label: 'Automation & Workflow', color: '#7c3aed' },
  'backlink-seo': { emoji: '\uD83D\uDD17', label: 'Backlink & SEO', color: '#dc2626' },
  'exec-assistant': { emoji: '\uD83E\uDDD5', label: 'Executive Assistant', color: '#2563eb' },
  'social-media': { emoji: '\uD83D\uDCF1', label: 'Social Media Mgmt', color: '#059669' },
  'shopify-ecommerce': { emoji: '\uD83D\uDED2', label: 'Shopify & E-Commerce', color: '#d97706' },
  'github-batch4': { emoji: '\uD83D\uDCC2', label: 'GitHub Batch 4 Directory', color: '#64748b' },
  'seo-tools': { emoji: '\uD83D\uDD27', label: 'SEO Tools & Keyword Research', color: '#059669' },
};

const ELI_WELCOME = `Hey! I'm **Eli** — VirtuaLab Digital's AI Growth Intelligence.

I have **170+ knowledge files** across **35+ categories** — SEO, AI agents, agency marketing methodology, paid media strategy, keyword research, automation, and more.

**What I can do:**
- Keyword research strategy and clustering
- SEO audits and technical analysis
- Content strategy and AEO/GEO optimization
- Competitive intelligence and backlink analysis
- Paid media strategy (PPC, programmatic, paid social)
- Automation workflow design (n8n, GHL, Baserow)
- Agency-grade 12-part marketing strategy

Ask me anything about growth.`;

// ─── Helper: Count-up animation hook ────────────────────────────
function useMetricCounts(targets: number[], duration = 800) {
  const [counts, setCounts] = useState(targets.map(() => 0));
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (!started) return;
    const startTime = performance.now();
    let rafId: number;
    const step = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCounts(targets.map((t) => Math.round(eased * t)));
      if (progress < 1) rafId = requestAnimationFrame(step);
    };
    rafId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(rafId);
  }, [started, duration, ...targets]);

  return { counts, start: () => setStarted(true) };
}

// ─── Helper: Live time ──────────────────────────────────────────
function useLiveTime() {
  const [time, setTime] = useState('');
  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        })
      );
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);
  return time;
}

// ─── Topbar ─────────────────────────────────────────────────────
function Topbar({ onMenuClick, provider }: { onMenuClick: () => void; provider: string }) {
  const time = useLiveTime();

  return (
    <header
      className="h-14 sticky top-0 z-50 flex items-center justify-between px-4 md:px-6"
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.85)',
        backdropFilter: 'blur(24px)',
        borderBottom: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}
    >
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden text-[#64748b] hover:text-[#1e293b] hover:bg-[#f1f5f9]"
          onClick={onMenuClick}
        >
          <Menu className="w-5 h-5" />
        </Button>
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm"
            style={{
              background: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
              boxShadow: '0 2px 8px rgba(124,58,237,0.25)',
            }}
          >
            E
          </div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-[#1e293b] text-sm">Eli OS</span>
            <span className="text-[#e2e8f0] hidden sm:inline">.</span>
            <span className="text-[#64748b] text-xs hidden sm:inline">Growth Command Center</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-[#64748b]">
          <div className="w-2 h-2 rounded-full bg-[#059669] animate-pulse" />
          <span className="hidden sm:inline">Online</span>
        </div>
        {provider && (
          <Badge
            variant="secondary"
            className="text-[9px] font-mono hidden sm:inline-flex"
            style={{ backgroundColor: '#f1f5f9', color: '#64748b', border: '1px solid #e2e8f0' }}
          >
            {provider}
          </Badge>
        )}
        <Separator orientation="vertical" className="h-4 bg-[#e2e8f0]" />
        <div className="flex items-center gap-1.5 text-xs text-[#64748b] font-mono">
          <Clock className="w-3.5 h-3.5" />
          {time}
        </div>
      </div>
    </header>
  );
}

// ─── Sidebar ────────────────────────────────────────────────────
function SidebarNav({
  activeView,
  onViewChange,
  collapsed,
  onToggle,
}: {
  activeView: ViewId;
  onViewChange: (v: ViewId) => void;
  collapsed: boolean;
  onToggle: () => void;
}) {
  const groups = [
    { key: 'main', label: 'ACTIVE' },
    { key: 'beta', label: 'BETA' },
  ];

  return (
    <aside
      className={`hidden md:flex flex-col h-full transition-all duration-300 ease-in-out ${
        collapsed ? 'w-16' : 'w-60'
      }`}
      style={{
        backgroundColor: '#1e1b4b',
        borderRight: '1px solid #312e81',
      }}
    >
      <div className="flex-1 overflow-y-auto py-4 px-2">
        {groups.map((group) => {
          const items = NAV_ITEMS.filter((n) => n.group === group.key);
          return (
            <div key={group.key} className="mb-4">
              {!collapsed && (
                <div className="px-3 mb-2 text-[10px] font-semibold tracking-[0.15em] text-[#c4b5fd]">
                  {group.label}
                </div>
              )}
              {collapsed && <div className="my-2" style={{ borderTop: '1px solid #312e81' }} />}
              {items.map((item) => {
                const isActive = activeView === item.id;
                const Icon = item.icon;
                const isBeta = group.key === 'beta';
                return (
                  <TooltipProvider key={item.id} delayDuration={0}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          onClick={() => onViewChange(item.id)}
                          className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 group relative ${
                            isActive
                              ? 'bg-[rgba(167,139,250,0.15)] text-[#a78bfa]'
                              : isBeta
                              ? 'text-[#6366f1] hover:bg-[rgba(49,46,129,0.3)] hover:text-[#818cf8]'
                              : 'text-[#c4b5fd] hover:bg-[rgba(49,46,129,0.5)] hover:text-[#e0e7ff]'
                          }`}
                          style={{
                            ...(isActive && !collapsed ? { borderLeft: '2px solid #a78bfa', marginLeft: '-2px' } : {}),
                            ...(isBeta && !collapsed ? { opacity: 0.6 } : {}),
                          }}
                        >
                          <Icon className={`w-4.5 h-4.5 flex-shrink-0 transition-colors ${
                            isActive ? 'text-[#a78bfa]' : isBeta ? 'text-[#6366f1]' : 'text-[#c4b5fd] group-hover:text-[#e0e7ff]'
                          }`} />
                          {!collapsed && <span>{item.label}</span>}
                          {isActive && (
                            <div className="absolute inset-0 rounded-lg pointer-events-none"
                              style={{ boxShadow: 'inset 0 0 12px rgba(167,139,250,0.08)' }} />
                          )}
                        </button>
                      </TooltipTrigger>
                      {collapsed && (
                        <TooltipContent side="right" className="text-xs">
                          {item.label} {isBeta ? '(beta)' : ''}
                        </TooltipContent>
                      )}
                    </Tooltip>
                  </TooltipProvider>
                );
              })}
            </div>
          );
        })}
      </div>

      <div className="p-2" style={{ borderTop: '1px solid #312e81' }}>
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={`w-full text-[#c4b5fd] hover:text-[#e0e7ff] hover:bg-[rgba(49,46,129,0.5)] ${
            collapsed ? 'rotate-180' : ''
          } transition-transform duration-300`}
        >
          <ChevronLeft className="w-4 h-4" />
        </Button>
      </div>
    </aside>
  );
}

// ─── Mobile Sidebar ─────────────────────────────────────────────
function MobileSidebar({
  activeView,
  onViewChange,
  open,
  onOpenChange,
}: {
  activeView: ViewId;
  onViewChange: (v: ViewId) => void;
  open: boolean;
  onOpenChange: (o: boolean) => void;
}) {
  const groups = [
    { key: 'main', label: 'ACTIVE' },
    { key: 'beta', label: 'BETA' },
  ];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="left"
        className="w-64 p-0"
        style={{ backgroundColor: '#1e1b4b', borderRight: '1px solid #312e81' }}
      >
        <SheetTitle className="sr-only">Navigation</SheetTitle>
        <div className="pt-6 px-3 pb-4">
          <div className="flex items-center gap-3 px-3 mb-6">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm"
              style={{ background: 'linear-gradient(135deg, #7c3aed, #6d28d9)' }}>E</div>
            <span className="font-semibold text-[#e0e7ff] text-sm">Eli OS</span>
          </div>
          {groups.map((group) => {
            const items = NAV_ITEMS.filter((n) => n.group === group.key);
            return (
              <div key={group.key} className="mb-4">
                <div className="px-3 mb-2 text-[10px] font-semibold tracking-[0.15em] text-[#c4b5fd]">
                  {group.label}
                </div>
                {items.map((item) => {
                  const isActive = activeView === item.id;
                  const Icon = item.icon;
                  const isBeta = group.key === 'beta';
                  return (
                    <button
                      key={item.id}
                      onClick={() => { onViewChange(item.id); onOpenChange(false); }}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                        isActive ? 'bg-[rgba(167,139,250,0.15)] text-[#a78bfa]' : ''
                      } ${isBeta ? 'opacity-50' : ''}`}
                      style={isActive ? { borderLeft: '2px solid #a78bfa', marginLeft: '-2px' } : {}}
                    >
                      <Icon className={`w-4.5 h-4.5 flex-shrink-0 ${isActive ? 'text-[#a78bfa]' : ''}`} />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      </SheetContent>
    </Sheet>
  );
}

// ─── Dashboard View (Real Metrics) ──────────────────────────────
function DashboardView() {
  const [stats, setStats] = useState<KnowledgeStats | null>(null);
  const [kwData, setKwData] = useState<{ totalDatasets: number; totalKeywords: number } | null>(null);
  const [skillsCount, setSkillsCount] = useState<number>(0);

  useEffect(() => {
    fetch('/api/knowledge-stats').then(r => r.json()).then(setStats).catch(() => {});
    fetch('/api/keywords').then(r => r.json()).then(d => setKwData({ totalDatasets: d.totalDatasets, totalKeywords: d.totalKeywords })).catch(() => {});
    fetch('/api/skills').then(r => r.json()).then(d => setSkillsCount(d.total || 0)).catch(() => {});
  }, []);

  const files = stats?.totalFiles || 0;
  const categories = stats?.totalCategories || 0;
  const keywords = kwData?.totalKeywords || 0;
  const skills = skillsCount;

  const METRICS = [
    { label: 'Knowledge Files', value: files, icon: Database, color: '#2563eb', glowClass: 'glow-cyan' },
    { label: 'Categories', value: categories, icon: FolderOpen, color: '#7c3aed', glowClass: 'glow-purple' },
    { label: 'Keywords', value: keywords, icon: Tag, color: '#059669', glowClass: 'glow-green' },
    { label: 'SEO Skills', value: skills, icon: Wrench, color: '#d97706', glowClass: 'glow-amber' },
  ];

  const { counts, start } = useMetricCounts(METRICS.map((m) => m.value));
  useEffect(() => { const t = setTimeout(start, 200); return () => clearTimeout(t); }, [start]);

  const topCategories = (stats?.categories || [])
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
    .map(c => ({ ...c, ...(CATEGORY_META[c.key] || { emoji: '\uD83D\uDCC4', label: c.key, color: '#64748b' }) }));

  return (
    <div className="animate-fadeIn space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#1e293b] mb-1">Eli's Dashboard</h1>
        <p className="text-sm text-[#64748b]">
          Eli's growth intelligence overview — {files} knowledge files, {keywords} keywords, {skills} skills loaded.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {METRICS.map((metric, i) => {
          const Icon = metric.icon;
          const count = counts[i];
          return (
            <div
              key={metric.label}
              className={`animate-slideUp rounded-xl p-5 transition-all duration-300 cursor-default group hover:-translate-y-0.5 ${metric.glowClass}`}
              style={{
                animationDelay: `${i * 100}ms`,
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
              }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = metric.color + '40'; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = '#e2e8f0'; }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: metric.color + '15' }}>
                  <Icon className="w-5 h-5" style={{ color: metric.color }} />
                </div>
                <Zap className="w-3.5 h-3.5 text-[#94a3b8] opacity-50 group-hover:opacity-80 transition-opacity" />
              </div>
              <div className="text-2xl font-bold text-[#1e293b]">{count}</div>
              <div className="text-xs text-[#64748b] mt-1">{metric.label}</div>
            </div>
          );
        })}
      </div>

      {/* Top Knowledge Categories */}
      {topCategories.length > 0 && (
        <div className="rounded-xl overflow-hidden" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
          <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: '1px solid #e2e8f0' }}>
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#7c3aed]" />
              <h2 className="text-sm font-semibold text-[#1e293b]">Top Knowledge Categories</h2>
            </div>
            <Badge variant="secondary" className="text-[10px] font-medium"
              style={{ backgroundColor: '#7c3aed10', color: '#7c3aed', border: '1px solid #7c3aed20' }}>
              {categories} total
            </Badge>
          </div>
          <div className="divide-y" style={{ borderColor: '#e2e8f0' }}>
            {topCategories.map((cat, i) => (
              <div key={cat.key} className="px-5 py-3 flex items-center gap-4 hover:bg-[#f8fafc] transition-colors animate-slideUp"
                style={{ animationDelay: `${i * 80 + 400}ms`, borderBottomColor: '#e2e8f0' }}>
                <span className="text-lg flex-shrink-0">{cat.emoji}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-[#1e293b] truncate">{cat.label}</div>
                </div>
                <div className="w-24 flex-shrink-0 hidden sm:block">
                  <div className="flex items-center justify-between text-[10px] text-[#64748b] mb-1">
                    <span>Files</span><span>{cat.count}</span>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: '#f1f5f9' }}>
                    <div className="h-full rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${Math.min((cat.count / (topCategories[0]?.count || 1)) * 100, 100)}%`, backgroundColor: cat.color, transitionDelay: `${i * 100 + 600}ms` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Introduction View ───────────────────────────────────────────
function IntroView() {
  const [intro, setIntro] = useState<{ title: string; subtitle: string; videoUrl: string; description: string } | null>(null);

  useEffect(() => {
    fetch('/api/eli-intro').then(r => r.json()).then(setIntro).catch(() => {});
  }, []);

  return (
    <div className="animate-fadeIn space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#1e293b] mb-1">{intro?.title || 'Meet Eli'}</h1>
        <p className="text-sm text-[#64748b]">{intro?.subtitle || 'VirtuaLab Digital\'s AI Growth Intelligence'}</p>
      </div>

      {/* Video Embed */}
      <div className="rounded-xl overflow-hidden" style={{ backgroundColor: '#000000', border: '1px solid #e2e8f0' }}>
        {intro?.videoUrl ? (
          <div className="aspect-video w-full">
            <iframe
              src={intro.videoUrl}
              title="Eli Introduction"
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        ) : (
          <div className="aspect-video w-full flex flex-col items-center justify-center text-center p-8">
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center mb-4"
              style={{ background: 'linear-gradient(135deg, #7c3aed, #6d28d9)', boxShadow: '0 8px 30px rgba(124,58,237,0.3)' }}>
              <Bot className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-white text-lg font-semibold mb-2">Eli Introduction Video</h3>
            <p className="text-[#94a3b8] text-sm max-w-md">
              Video coming soon. Set the ELI_INTRO_VIDEO_URL environment variable to display Eli's introduction video here.
            </p>
            <Badge variant="secondary" className="mt-4 text-[10px]"
              style={{ backgroundColor: 'rgba(124,58,237,0.2)', color: '#a78bfa', border: '1px solid rgba(124,58,237,0.3)' }}>
              <Play className="w-3 h-3 mr-1" /> Video Pending
            </Badge>
          </div>
        )}
      </div>

      {/* Description */}
      <div className="rounded-xl p-6" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-[#7c3aed]" />
          <h2 className="text-sm font-semibold text-[#1e293b]">About Eli</h2>
        </div>
        <div className="text-sm text-[#475569] leading-relaxed whitespace-pre-line">
          {intro?.description || 'Loading...'}
        </div>
      </div>
    </div>
  );
}

// ─── SEO Skills View ─────────────────────────────────────────────
function SeoSkillsView() {
  const [skills, setSkills] = useState<Array<{ filename: string; name: string; description: string; content: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/skills')
      .then(r => r.json())
      .then(d => { setSkills(d.skills || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const selected = skills.find(s => s.filename === selectedSkill);

  return (
    <div className="animate-fadeIn space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#1e293b] mb-1">SEO Skill Registry</h1>
        <p className="text-sm text-[#64748b]">
          {loading ? 'Loading skills...' : `${skills.length} specialized skills powering Eli's SEO intelligence.`}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Skills List */}
        <div className="lg:col-span-1 space-y-2">
          {loading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-lg p-4 animate-pulse" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
                <div className="h-4 w-24 bg-[#e2e8f0] rounded mb-2" />
                <div className="h-3 w-40 bg-[#e2e8f0] rounded" />
              </div>
            ))
          ) : (
            skills.map((skill, i) => (
              <button
                key={skill.filename}
                onClick={() => setSelectedSkill(selectedSkill === skill.filename ? null : skill.filename)}
                className={`w-full text-left rounded-lg p-4 transition-all duration-200 animate-slideUp ${
                  selectedSkill === skill.filename
                    ? 'ring-1 ring-[#7c3aed] bg-[#7c3aed08]'
                    : 'hover:bg-[#f8fafc]'
                }`}
                style={{
                  backgroundColor: selectedSkill === skill.filename ? '#7c3aed08' : '#ffffff',
                  border: '1px solid ' + (selectedSkill === skill.filename ? '#7c3aed30' : '#e2e8f0'),
                  animationDelay: `${i * 50}ms`,
                }}
              >
                <div className="text-sm font-medium text-[#1e293b]">{skill.name}</div>
                <div className="text-xs text-[#64748b] mt-1 line-clamp-2">{skill.description}</div>
              </button>
            ))
          )}
        </div>

        {/* Skill Detail */}
        <div className="lg:col-span-2">
          {selected ? (
            <div className="rounded-xl overflow-hidden" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
              <div className="px-5 py-4" style={{ borderBottom: '1px solid #e2e8f0' }}>
                <div className="flex items-center gap-2">
                  <Wrench className="w-4 h-4 text-[#7c3aed]" />
                  <h2 className="text-sm font-semibold text-[#1e293b]">{selected.name}</h2>
                </div>
              </div>
              <ScrollArea className="h-[500px]">
                <div className="p-5">
                  <EliMarkdown content={selected.content} />
                </div>
              </ScrollArea>
            </div>
          ) : (
            <div className="rounded-xl p-10 flex flex-col items-center justify-center text-center"
              style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
              <Wrench className="w-10 h-10 text-[#e2e8f0] mb-3" />
              <p className="text-sm text-[#64748b]">Select a skill to view its full definition and methodology.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Keywords View ───────────────────────────────────────────────
function KeywordsView() {
  const [data, setData] = useState<{ datasets: Array<{ filename: string; label: string; count: number; keywords: any[] }>; totalKeywords: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetch('/api/keywords')
      .then(r => r.json())
      .then(d => { setData(d); if (d.datasets?.[0]) setSelectedDataset(d.datasets[0].filename); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const selected = data?.datasets.find(d => d.filename === selectedDataset);
  const filteredKw = (selected?.keywords || []).filter((kw: any) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (kw.keyword || kw.query || kw.term || '').toLowerCase().includes(q) ||
      (kw.search_volume || kw.volume || '').toString().includes(q);
  });

  return (
    <div className="animate-fadeIn space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#1e293b] mb-1">Keyword Research Explorer</h1>
        <p className="text-sm text-[#64748b]">
          {loading ? 'Loading keyword data...' : `${data?.totalKeywords || 0} keywords across ${data?.datasets?.length || 0} datasets.`}
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="rounded-lg p-4 animate-pulse" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
              <div className="h-4 w-20 bg-[#e2e8f0] rounded mb-2" />
              <div className="h-3 w-12 bg-[#e2e8f0] rounded" />
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* Dataset pills */}
          <div className="flex flex-wrap gap-2">
            {data?.datasets.map((ds) => (
              <button
                key={ds.filename}
                onClick={() => setSelectedDataset(ds.filename)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedDataset === ds.filename
                    ? 'text-white'
                    : 'text-[#64748b] hover:text-[#1e293b]'
                }`}
                style={{
                  backgroundColor: selectedDataset === ds.filename ? '#7c3aed' : '#f1f5f9',
                  border: '1px solid ' + (selectedDataset === ds.filename ? '#7c3aed' : '#e2e8f0'),
                }}
              >
                {ds.label} ({ds.count})
              </button>
            ))}
          </div>

          {/* Search within keywords */}
          {selected && (
            <>
              <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94a3b8]" />
                <Input value={search} onChange={e => setSearch(e.target.value)} placeholder={`Search ${selected.label} keywords...`} className="pl-10"
                  style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', color: '#1e293b' }} />
              </div>

              <div className="rounded-xl overflow-hidden" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
                <div className="px-5 py-3 flex items-center justify-between" style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <span className="text-sm font-semibold text-[#1e293b]">{selected.label}</span>
                  <Badge variant="secondary" className="text-[10px]"
                    style={{ backgroundColor: '#f1f5f9', color: '#64748b' }}>
                    {filteredKw.length} keywords
                  </Badge>
                </div>
                <ScrollArea className="h-[400px]">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-[10px] font-semibold text-[#64748b] uppercase tracking-wider" style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <th className="px-5 py-2">Keyword</th>
                        <th className="px-3 py-2 hidden sm:table-cell">Volume</th>
                        <th className="px-3 py-2 hidden md:table-cell">CPC</th>
                        <th className="px-3 py-2 hidden lg:table-cell">Intent</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y" style={{ borderColor: '#f1f5f9' }}>
                      {filteredKw.slice(0, 100).map((kw: any, i: number) => (
                        <tr key={i} className="hover:bg-[#f8fafc] transition-colors">
                          <td className="px-5 py-2.5 text-[#1e293b] font-medium truncate max-w-[300px]">
                            {kw.keyword || kw.query || kw.term || '-'}
                          </td>
                          <td className="px-3 py-2.5 text-[#64748b] hidden sm:table-cell">
                            {(kw.search_volume || kw.volume || '-').toLocaleString()}
                          </td>
                          <td className="px-3 py-2.5 text-[#64748b] hidden md:table-cell">
                            {kw.cpc || kw.avg_cpc || '-'}
                          </td>
                          <td className="px-3 py-2.5 hidden lg:table-cell">
                            {kw.intent || kw.search_intent ? (
                              <Badge variant="secondary" className="text-[10px]"
                                style={{ backgroundColor: '#f1f5f9', color: '#64748b' }}>
                                {kw.intent || kw.search_intent}
                              </Badge>
                            ) : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {filteredKw.length === 0 && (
                    <div className="text-center py-8 text-sm text-[#64748b]">No keywords found matching &quot;{search}&quot;</div>
                  )}
                </ScrollArea>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

// ─── Chat View ──────────────────────────────────────────────────
const SUGGESTION_CHIPS = [
  "What's our SEO strategy for home services?",
  'Analyze keyword gaps in our niche',
  'What does the vault say about AEO?',
  'Build me a content calendar for next month',
];

function ChatView({ onProviderChange }: { onProviderChange: (p: string) => void }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, isLoading, scrollToBottom]);

  const handleSend = async (overrideMessage?: string) => {
    const trimmed = (overrideMessage || input).trim();
    if (!trimmed || isLoading) return;

    const userMsg: ChatMessage = { id: `user-${Date.now()}`, role: 'user', content: trimmed, timestamp: new Date() };
    if (!overrideMessage) setInput('');
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    try {
      const history = messages.filter((m) => m.id !== 'welcome').map((m) => ({ role: m.role, content: m.content }));
      const res = await fetch('/api/eli-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed, history }),
      });

      const data = await res.json();

      if (data.provider) onProviderChange(data.provider);

      const eliMsg: ChatMessage = {
        id: `eli-${Date.now()}`, role: 'eli',
        content: data.response || 'I encountered an issue processing your request.',
        sources: data.sources, timestamp: new Date(),
      };
      setMessages((prev) => [...prev, eliMsg]);
    } catch {
      setMessages((prev) => [...prev, {
        id: `error-${Date.now()}`, role: 'eli',
        content: 'Sorry, I encountered a connection error. Please try again.',
        timestamp: new Date(),
      }]);
    } finally { setIsLoading(false); }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleSuggestionClick = (text: string) => {
    handleSend(text);
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const ta = e.target;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  };

  const renderUserContent = (text: string) =>
    text.split('\n').map((line, i) => {
      if (line.startsWith('- ') || line.startsWith('. '))
        return <div key={i} className="flex gap-2 pl-1"><span className="mt-0.5">.</span><span>{line.replace(/^[.-]\s*/, '')}</span></div>;
      if (line.trim() === '') return <div key={i} className="h-2" />;
      return <p key={i} className="leading-relaxed">{line}</p>;
    });

  return (
    <div className="flex flex-col h-full animate-fadeIn">
      <div className="px-5 py-3 flex items-center gap-3 flex-shrink-0" style={{ borderBottom: '1px solid #e2e8f0' }}>
        <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
          style={{ background: 'linear-gradient(135deg, #7c3aed, #6d28d9)', boxShadow: '0 0 12px rgba(124,58,237,0.2)' }}>E</div>
        <div>
          <div className="text-sm font-semibold text-[#1e293b]">Eli</div>
          <div className="text-[10px] text-[#059669] flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-[#059669]" /> Growth Intelligence Online
          </div>
        </div>
      </div>

      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 animate-fadeIn">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold text-white mb-6 animate-pulse-glow"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #6d28d9)', boxShadow: '0 8px 32px rgba(124,58,237,0.25)' }}>
            E
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-[#1e293b] mb-3 text-center">
            Hey, I'm <span style={{ background: 'linear-gradient(135deg, #7c3aed, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Eli</span>.
          </h1>
          <p className="text-sm md:text-base text-[#64748b] text-center max-w-lg mb-10 leading-relaxed">
            Your AI growth intelligence at VirtuaLab Digital. I know SEO, content strategy,
            keyword research, and automation — and I actually have opinions about all of it.
          </p>
          <div className="flex flex-wrap justify-center gap-2.5 max-w-xl">
            {SUGGESTION_CHIPS.map((chip) => (
              <button
                key={chip}
                onClick={() => handleSuggestionClick(chip)}
                disabled={isLoading}
                className="group text-xs text-[#4c1d95] bg-[#f5f3ff] hover:bg-[#ede9fe] border border-[#e9d5ff] hover:border-[#c4b5fd] px-3.5 py-2.5 rounded-full transition-all duration-200 hover:shadow-md hover:shadow-purple-100 cursor-pointer text-left max-w-[300px] leading-relaxed"
              >
                <span className="opacity-60 group-hover:opacity-100 mr-1.5">→</span>
                {chip}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <ScrollArea className="flex-1 px-4 md:px-6 py-4">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg) => (
              <div key={msg.id} className={`animate-slideUp flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user' ? 'rounded-2xl rounded-tr-sm text-white' : 'rounded-2xl rounded-tl-sm text-[#1e293b]'
                }`}
                style={msg.role === 'user'
                  ? { background: 'linear-gradient(135deg, #7c3aed, #6d28d9)', boxShadow: '0 4px 15px rgba(124,58,237,0.15)' }
                  : { backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }
                }>
                  {msg.role === 'eli' && (
                    <div className="flex items-center gap-1.5 mb-2">
                      <span className="text-[10px] font-semibold text-[#7c3aed]">ELI</span>
                      <span className="text-[10px] text-[#64748b]">
                        {msg.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })}
                      </span>
                    </div>
                  )}
                  <div className="text-[#1e293b]/90">
                    {msg.role === 'eli' ? <EliMarkdown content={msg.content} /> : renderUserContent(msg.content)}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-2 flex flex-wrap gap-1.5" style={{ borderTop: '1px solid #e2e8f0' }}>
                      {msg.sources.map((src, idx) => (
                        <div key={idx} className="flex items-center gap-1 text-[10px] text-[#64748b] hover:text-[#2563eb] transition-colors cursor-default px-2 py-1 rounded-md"
                          style={{ backgroundColor: '#f1f5f9' }}>
                          <ExternalLink className="w-2.5 h-2.5" />
                          <span className="truncate max-w-[160px]">{src.title}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start animate-fadeIn">
                <div className="rounded-2xl rounded-tl-sm px-4 py-3" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] font-semibold text-[#7c3aed] mr-1">ELI</span>
                    <div className="w-1.5 h-1.5 rounded-full bg-[#7c3aed] animate-bounce-dot" style={{ animationDelay: '0ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-[#7c3aed] animate-bounce-dot" style={{ animationDelay: '150ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-[#7c3aed] animate-bounce-dot" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
      )}

      <div className="flex-shrink-0 p-4 md:px-6" style={{ borderTop: '1px solid #e2e8f0' }}>
        <div className="flex items-end gap-3 max-w-3xl mx-auto rounded-xl p-2 transition-all duration-300"
          style={{
            backgroundColor: '#ffffff',
            border: isFocused ? '1.5px solid #a78bfa' : '1px solid #e2e8f0',
            boxShadow: isFocused
              ? '0 0 0 3px rgba(124,58,237,0.08), 0 4px 16px rgba(124,58,237,0.1)'
              : '0 1px 3px rgba(0,0,0,0.06)',
          }}>
          <textarea ref={textareaRef} value={input} onChange={handleTextareaChange} onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)} onBlur={() => setIsFocused(false)}
            placeholder="Ask Eli anything..." rows={1}
            className="flex-1 bg-transparent border-none outline-none resize-none text-sm text-[#1e293b] placeholder:text-[#94a3b8] py-2 px-2 min-h-[36px] max-h-[160px]"
            style={{ scrollbarWidth: 'none' }} />
          <Button size="icon" disabled={!input.trim() || isLoading} onClick={() => handleSend()}
            className="flex-shrink-0 w-9 h-9 rounded-lg transition-all duration-300 hover:scale-105 active:scale-95"
            style={{
              background: input.trim() && !isLoading ? 'linear-gradient(135deg, #7c3aed, #6d28d9)' : '#e2e8f0',
              boxShadow: input.trim() && !isLoading ? '0 0 20px rgba(124,58,237,0.3)' : 'none',
              cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
            }}>
            <Send className="w-4 h-4 text-[#ffffff]" />
          </Button>
        </div>
        <div className="flex items-center justify-between mt-2 max-w-3xl mx-auto">
          <span className="text-[10px] text-[#94a3b8]/70">
            Press Enter to send, Shift+Enter for new line.
          </span>
        </div>
      </div>
    </div>
  );
}

// ─── Knowledge View ─────────────────────────────────────────────
function KnowledgeView() {
  const [search, setSearch] = useState('');
  const [stats, setStats] = useState<KnowledgeStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/knowledge-stats').then(r => r.json()).then(d => { setStats(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const categories = (stats?.categories || []).map((c) => ({ ...c, ...(CATEGORY_META[c.key] || { emoji: '\uD83D\uDCC4', label: c.key, color: '#64748b' }) }));
  const filtered = categories.filter(c => c.label.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="animate-fadeIn space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#1e293b] mb-1">Knowledge Base</h1>
        <p className="text-sm text-[#64748b]">
          {loading ? 'Scanning knowledge files...' : `${stats?.totalFiles || 0} files across ${stats?.totalCategories || 0} categories (${stats?.totalSizeMB || '0'} MB) powering Eli's intelligence.`}
        </p>
      </div>
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94a3b8]" />
        <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search categories..." className="pl-10"
          style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', color: '#1e293b' }} />
      </div>
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="rounded-xl p-4 animate-pulse" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
              <div className="h-5 w-8 bg-[#e2e8f0] rounded mb-3" /><div className="h-4 w-24 bg-[#e2e8f0] rounded" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {filtered.map((cat, i) => (
            <div key={cat.key} className="animate-slideUp rounded-xl p-4 transition-all duration-200 cursor-default hover:-translate-y-0.5 group"
              style={{ animationDelay: `${i * 50}ms`, backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = cat.color + '40'; (e.currentTarget as HTMLElement).style.boxShadow = `0 0 20px ${cat.color}10`; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = '#e2e8f0'; (e.currentTarget as HTMLElement).style.boxShadow = 'none'; }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-lg">{cat.emoji}</span>
                <Badge variant="secondary" className="text-[10px]"
                  style={{ backgroundColor: cat.color + '15', color: cat.color, border: `1px solid ${cat.color}30` }}>{cat.count}</Badge>
              </div>
              <div className="text-sm text-[#1e293b] group-hover:text-[#7c3aed] transition-colors">{cat.label}</div>
            </div>
          ))}
        </div>
      )}
      {!loading && filtered.length === 0 && (
        <div className="text-center py-12 text-sm text-[#64748b]">No categories found matching &quot;{search}&quot;</div>
      )}
    </div>
  );
}

// ─── Beta Placeholder View ───────────────────────────────────────
function BetaView({ title, description, icon: Icon }: { title: string; description: string; icon: React.ElementType }) {
  return (
    <div className="animate-fadeIn flex items-center justify-center h-full">
      <div className="text-center max-w-md rounded-2xl p-10" style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}>
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-5"
          style={{ background: 'linear-gradient(135deg, rgba(124,58,237,0.08), rgba(124,58,237,0.04))', border: '1px solid rgba(124,58,237,0.12)' }}>
          <Icon className="w-7 h-7 text-[#7c3aed]" />
        </div>
        <h2 className="text-lg font-semibold text-[#1e293b] mb-2">{title}</h2>
        <p className="text-sm text-[#64748b] mb-5 leading-relaxed">{description}</p>
        <Badge variant="secondary" className="text-[11px] font-medium"
          style={{ backgroundColor: 'rgba(124,58,237,0.08)', color: '#7c3aed', border: '1px solid rgba(124,58,237,0.15)' }}>
          <Sparkles className="w-3 h-3 mr-1" /> Beta — Coming Soon
        </Badge>
      </div>
    </div>
  );
}

// ─── Main Page ──────────────────────────────────────────────────
export default function Home() {
  const [activeView, setActiveView] = useState<ViewId>('chat');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [provider, setProvider] = useState('');

  const renderView = () => {
    switch (activeView) {
      case 'dashboard': return <DashboardView />;
      case 'chat': return <ChatView onProviderChange={setProvider} />;
      case 'intro': return <IntroView />;
      case 'seo-skills': return <SeoSkillsView />;
      case 'keywords': return <KeywordsView />;
      case 'knowledge': return <KnowledgeView />;
      case 'leads': return <BetaView icon={Users} title="Lead Management" description="Track, score, and nurture leads through your growth pipeline. AI-powered lead qualification and automated follow-ups." />;
      case 'audits': return <BetaView icon={Search} title="SEO Audits" description="Comprehensive site audits powered by Eli's knowledge. Technical SEO, content gaps, and competitive analysis." />;
      case 'campaigns': return <BetaView icon={Megaphone} title="Campaign Manager" description="Plan, execute, and track growth campaigns across channels." />;
      case 'content': return <BetaView icon={FileText} title="Content Engine" description="AI-powered content creation, scheduling, and optimization." />;
      case 'rank': return <BetaView icon={TrendingUp} title="Rank Tracker" description="Monitor keyword rankings and track SERP positions." />;
      case 'integrations': return <BetaView icon={Plug} title="Integrations Hub" description="Connect Eli OS to Google Analytics, Search Console, CMS, CRMs, and more." />;
      case 'workflows': return <BetaView icon={Workflow} title="Workflow Automation" description="Design and deploy automated growth workflows with n8n." />;
      case 'scrapers': return <BetaView icon={Bug} title="Web Scrapers" description="Deploy and manage web scraping tasks for growth intelligence." />;
      case 'vault': return <BetaView icon={Shield} title="Secure Vault" description="Encrypted storage for sensitive business data and credentials." />;
      case 'settings': return <BetaView icon={Settings} title="Settings" description="Configure Eli OS preferences, API connections, and system behavior." />;
      default: return <DashboardView />;
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden animate-fadeIn">
      <Topbar onMenuClick={() => setMobileMenuOpen(true)} provider={provider} />
      <div className="flex flex-1 overflow-hidden">
        <SidebarNav activeView={activeView} onViewChange={setActiveView} collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
        <MobileSidebar activeView={activeView} onViewChange={setActiveView} open={mobileMenuOpen} onOpenChange={setMobileMenuOpen} />
        <main className="flex-1 overflow-hidden">
          {activeView === 'chat' ? renderView() : (
            <ScrollArea className="h-full"><div className="p-4 md:p-6 lg:p-8 max-w-6xl mx-auto">{renderView()}</div></ScrollArea>
          )}
        </main>
      </div>
    </div>
  );
}
