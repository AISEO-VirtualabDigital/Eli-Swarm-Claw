'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  LayoutDashboard,
  MessageSquare,
  Users,
  Search,
  Megaphone,
  FileText,
  TrendingUp,
  CheckSquare,
  Plug,
  Workflow,
  Bug,
  Wrench,
  BookOpen,
  Settings,
  Send,
  Menu,
  ChevronLeft,
  ExternalLink,
  Clock,
  Sparkles,
  Zap,
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
  | 'leads'
  | 'audits'
  | 'campaigns'
  | 'content'
  | 'rank'
  | 'integrations'
  | 'workflows'
  | 'scrapers'
  | 'seo-skills'
  | 'knowledge'
  | 'vault'
  | 'settings';

interface NavItem {
  id: ViewId;
  label: string;
  icon: React.ElementType;
  group: 'main' | 'systems' | 'knowledge';
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

// ─── Data ────────────────────────────────────────────────────────
const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, group: 'main' },
  { id: 'chat', label: 'Chat', icon: MessageSquare, group: 'main' },
  { id: 'leads', label: 'Leads', icon: Users, group: 'main' },
  { id: 'audits', label: 'Audits', icon: Search, group: 'main' },
  { id: 'campaigns', label: 'Campaigns', icon: Megaphone, group: 'main' },
  { id: 'content', label: 'Content', icon: FileText, group: 'main' },
  { id: 'rank', label: 'Rank', icon: TrendingUp, group: 'main' },
  { id: 'integrations', label: 'Integrations', icon: Plug, group: 'systems' },
  { id: 'workflows', label: 'Workflows', icon: Workflow, group: 'systems' },
  { id: 'scrapers', label: 'Scrapers', icon: Bug, group: 'systems' },
  { id: 'seo-skills', label: 'SEO Skills', icon: Wrench, group: 'systems' },
  { id: 'knowledge', label: 'Knowledge', icon: BookOpen, group: 'knowledge' },
  { id: 'vault', label: 'Vault', icon: Shield, group: 'knowledge' },
  { id: 'settings', label: 'Settings', icon: Settings, group: 'knowledge' },
];

const METRICS = [
  { label: 'Active Leads', value: 12, icon: Users, color: '#2563eb', glowClass: 'glow-cyan' },
  { label: 'Audits Pending', value: 5, icon: Search, color: '#7c3aed', glowClass: 'glow-purple' },
  { label: 'Campaigns Running', value: 8, icon: Megaphone, color: '#059669', glowClass: 'glow-green' },
  { label: 'Waiting Approval', value: 4, icon: CheckSquare, color: '#d97706', glowClass: 'glow-amber' },
];

const MISSIONS = [
  { name: 'SEO Audit — VirtuaLab.com', status: 'In Progress', statusColor: '#2563eb', priority: 'High', progress: 72 },
  { name: 'Content Calendar — Q4 Strategy', status: 'Pending Review', statusColor: '#d97706', priority: 'Medium', progress: 45 },
  { name: 'Backlink Outreach — Tier 1 Sites', status: 'Active', statusColor: '#059669', priority: 'High', progress: 88 },
  { name: 'Google Business Profile Optimization', status: 'Queued', statusColor: '#64748b', priority: 'Low', progress: 12 },
];

const CATEGORY_META: Record<string, { emoji: string; label: string; color: string }> = {
  'seo': { emoji: '🔍', label: 'SEO & Marketing', color: '#2563eb' },
  'codebase': { emoji: '💻', label: 'Code & Scraping', color: '#7c3aed' },
  'web-design': { emoji: '🎨', label: 'Web Design & UI', color: '#dc2626' },
  'ai-agent': { emoji: '🤖', label: 'AI Agents & Tools', color: '#059669' },
  'saas': { emoji: '💰', label: 'SaaS & Business', color: '#d97706' },
  'productivity': { emoji: '⚡', label: 'Productivity & Automation', color: '#2563eb' },
  'reference': { emoji: '📚', label: 'Reference & Research', color: '#7c3aed' },
  'brand': { emoji: '🏷️', label: 'VirtuaLab Brand', color: '#dc2626' },
  'strategy': { emoji: '📋', label: 'Strategy & Planning', color: '#059669' },
  'analysis': { emoji: '📊', label: 'Design Analysis', color: '#d97706' },
  'screenshot': { emoji: '📸', label: 'Screenshots', color: '#64748b' },
  'eli-core': { emoji: '🧠', label: 'Eli Core Identity', color: '#7c3aed' },
  'obsidian': { emoji: '📦', label: 'Obsidian Vault', color: '#2563eb' },
  'agent-eli': { emoji: '⚙️', label: 'Agent Eli v1 Architecture', color: '#059669' },
  'google-api': { emoji: '🔗', label: 'Google API Ecosystem', color: '#059669' },
  'crm-sales': { emoji: '📊', label: 'CRM & Sales Tools', color: '#2563eb' },
  'project-mgmt': { emoji: '📋', label: 'Project Management', color: '#7c3aed' },
  'copywriting-ai': { emoji: '✍️', label: 'Copywriting & AI Content', color: '#dc2626' },
  'cloud-infra': { emoji: '☁️', label: 'Cloud & Infrastructure', color: '#d97706' },
  'cybersecurity': { emoji: '🔒', label: 'Cybersecurity', color: '#dc2626' },
  'design-uiux': { emoji: '🎨', label: 'Design & UI/UX Tools', color: '#2563eb' },
  'llm-ai': { emoji: '🤖', label: 'LLM & AI Frameworks', color: '#059669' },
  'vps-hosting': { emoji: '🖥️', label: 'VPS & Hosting', color: '#7c3aed' },
  'database': { emoji: '🗄️', label: 'Database Tools', color: '#d97706' },
  'github-multi': { emoji: '📂', label: 'GitHub Multi-Topic Directory', color: '#64748b' },
  'notion-tools': { emoji: '📓', label: 'Notion & Knowledge Mgmt', color: '#2563eb' },
  'gohighlevel-agency': { emoji: '🏢', label: 'GoHighLevel & Agency', color: '#059669' },
  'automation-workflow': { emoji: '⚙️', label: 'Automation & Workflow', color: '#7c3aed' },
  'backlink-seo': { emoji: '🔗', label: 'Backlink & SEO', color: '#dc2626' },
  'exec-assistant': { emoji: '🤵', label: 'Executive Assistant', color: '#2563eb' },
  'social-media': { emoji: '📱', label: 'Social Media Mgmt', color: '#059669' },
  'shopify-ecommerce': { emoji: '🛒', label: 'Shopify & E-Commerce', color: '#d97706' },
  'github-batch4': { emoji: '📂', label: 'GitHub Batch 4 Directory', color: '#64748b' },
  'seo-tools': { emoji: '🔧', label: 'SEO Tools & Keyword Research', color: '#059669' },
};

const ELI_WELCOME = `Hey! I'm **Eli** — VirtuaLab Digital's AI Growth Intelligence.

I have **160+ knowledge files** across **33 categories** — SEO tools, keyword research workflows, AI agents, automation, competitor analysis, and more.

**What I can do:**
• Keyword research strategy (Keywords Everywhere + Gemini + Claude + Perplexity)
• SEO audits and technical analysis
• Content strategy and optimization
• Competitive intelligence and backlink analysis
• Automation workflow design (n8n, GHL, Baserow)
• Tool recommendations and stack guidance

Ask me anything about growth.`;

// ─── Helper: Count-up animation hook (fixed count) ───────────
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
function Topbar({ onMenuClick }: { onMenuClick: () => void }) {
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
            <span className="text-[#e2e8f0] hidden sm:inline">·</span>
            <span className="text-[#64748b] text-xs hidden sm:inline">Growth Command Center</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-[#64748b]">
          <div className="w-2 h-2 rounded-full bg-[#059669] animate-pulse" />
          <span className="hidden sm:inline">Online</span>
        </div>
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
    { key: 'main', label: 'MAIN' },
    { key: 'systems', label: 'SYSTEMS' },
    { key: 'knowledge', label: 'KNOWLEDGE' },
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
                return (
                  <TooltipProvider key={item.id} delayDuration={0}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          onClick={() => onViewChange(item.id)}
                          className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 group relative ${
                            isActive
                              ? 'bg-[rgba(167,139,250,0.15)] text-[#a78bfa]'
                              : 'text-[#c4b5fd] hover:bg-[rgba(49,46,129,0.5)] hover:text-[#e0e7ff]'
                          }`}
                          style={{
                            ...(isActive && !collapsed
                              ? { borderLeft: '2px solid #a78bfa', marginLeft: '-2px' }
                              : {}),
                          }}
                        >
                          <Icon
                            className={`w-4.5 h-4.5 flex-shrink-0 transition-colors ${
                              isActive ? 'text-[#a78bfa]' : 'text-[#c4b5fd] group-hover:text-[#e0e7ff]'
                            }`}
                          />
                          {!collapsed && <span>{item.label}</span>}
                          {isActive && (
                            <div
                              className="absolute inset-0 rounded-lg pointer-events-none"
                              style={{
                                boxShadow: 'inset 0 0 12px rgba(167,139,250,0.08)',
                              }}
                            />
                          )}
                        </button>
                      </TooltipTrigger>
                      {collapsed && (
                        <TooltipContent side="right" className="text-xs">
                          {item.label}
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

// ─── Mobile Sidebar (Sheet) ─────────────────────────────────────
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
    { key: 'main', label: 'MAIN' },
    { key: 'systems', label: 'SYSTEMS' },
    { key: 'knowledge', label: 'KNOWLEDGE' },
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
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm"
              style={{ background: 'linear-gradient(135deg, #7c3aed, #6d28d9)' }}
            >
              E
            </div>
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
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        onViewChange(item.id);
                        onOpenChange(false);
                      }}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                        isActive
                          ? 'bg-[rgba(167,139,250,0.15)] text-[#a78bfa]'
                          : 'text-[#c4b5fd] hover:bg-[rgba(49,46,129,0.5)] hover:text-[#e0e7ff]'
                      }`}
                      style={{
                        ...(isActive
                          ? { borderLeft: '2px solid #a78bfa', marginLeft: '-2px' }
                          : {}),
                      }}
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

// ─── Dashboard View ─────────────────────────────────────────────
function DashboardView() {
  const { counts, start } = useMetricCounts(METRICS.map((m) => m.value));

  useEffect(() => {
    const t = setTimeout(start, 200);
    return () => clearTimeout(t);
  }, [start]);

  return (
    <div className="animate-fadeIn space-y-6">
      {/* Greeting */}
      <div>
        <h1 className="text-xl font-bold text-[#1e293b] mb-1">
          Welcome back, Operator
        </h1>
        <p className="text-sm text-[#64748b]">
          Here's your growth intelligence overview for today.
        </p>
      </div>

      {/* Metric Cards */}
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
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = metric.color + '40';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = '#e2e8f0';
              }}
            >
              <div className="flex items-start justify-between mb-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: metric.color + '15' }}
                >
                  <Icon className="w-5 h-5" style={{ color: metric.color }} />
                </div>
                <Zap className="w-3.5 h-3.5 text-[#94a3b8] opacity-50 group-hover:opacity-80 transition-opacity" />
              </div>
              <div className="text-2xl font-bold text-[#1e293b] animate-count-up" style={{ animationDelay: `${i * 100 + 200}ms` }}>
                {count}
              </div>
              <div className="text-xs text-[#64748b] mt-1">{metric.label}</div>
            </div>
          );
        })}
      </div>

      {/* Mission List */}
      <div
        className="rounded-xl overflow-hidden"
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
        }}
      >
        <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: '1px solid #e2e8f0' }}>
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#7c3aed]" />
            <h2 className="text-sm font-semibold text-[#1e293b]">Active Missions</h2>
          </div>
          <Badge
            variant="secondary"
            className="text-[10px] font-medium"
            style={{ backgroundColor: '#7c3aed10', color: '#7c3aed', border: '1px solid #7c3aed20' }}
          >
            {MISSIONS.length} active
          </Badge>
        </div>
        <div className="divide-y" style={{ borderColor: '#e2e8f0' }}>
          {MISSIONS.map((mission, i) => (
            <div
              key={mission.name}
              className="px-5 py-3.5 flex items-center gap-4 hover:bg-[#f8fafc] transition-colors animate-slideUp"
              style={{
                animationDelay: `${i * 80 + 400}ms`,
                borderBottomColor: '#e2e8f0',
              }}
            >
              <div className="flex-1 min-w-0">
                <div className="text-sm text-[#1e293b] truncate">{mission.name}</div>
              </div>
              <Badge
                variant="secondary"
                className="text-[10px] flex-shrink-0 hidden sm:inline-flex"
                style={{
                  backgroundColor: mission.statusColor + '15',
                  color: mission.statusColor,
                  border: `1px solid ${mission.statusColor}30`,
                }}
              >
                {mission.status}
              </Badge>
              <Badge
                variant="outline"
                className="text-[10px] flex-shrink-0 hidden md:inline-flex"
                style={{
                  borderColor: '#e2e8f0',
                  color: mission.priority === 'High' ? '#dc2626' : mission.priority === 'Medium' ? '#d97706' : '#64748b',
                }}
              >
                {mission.priority}
              </Badge>
              <div className="w-24 flex-shrink-0 hidden sm:block">
                <div className="flex items-center justify-between text-[10px] text-[#64748b] mb-1">
                  <span>Progress</span>
                  <span>{mission.progress}%</span>
                </div>
                <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: '#f1f5f9' }}>
                  <div
                    className="h-full rounded-full transition-all duration-1000 ease-out"
                    style={{
                      width: `${mission.progress}%`,
                      backgroundColor: mission.statusColor,
                      boxShadow: `0 0 8px ${mission.statusColor}40`,
                      transitionDelay: `${i * 100 + 600}ms`,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Chat View ──────────────────────────────────────────────────
function ChatView() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  // Welcome message on mount
  useEffect(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'eli',
        content: ELI_WELCOME,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      const history = messages
        .filter((m) => m.id !== 'welcome')
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch('/api/eli-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed, history }),
      });

      const data = await res.json();

      const eliMsg: ChatMessage = {
        id: `eli-${Date.now()}`,
        role: 'eli',
        content: data.response || 'I encountered an issue processing your request. Please try again.',
        sources: data.sources,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, eliMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'eli',
        content: 'Sorry, I encountered a connection error. Please check that the server is running and try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-resize
    const ta = e.target;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  };

  // Simple markdown-like rendering for user messages only (no code blocks needed)
  const renderUserContent = (text: string) => {
    return text.split('\n').map((line, i) => {
      if (line.startsWith('- ') || line.startsWith('• ')) {
        return (
          <div key={i} className="flex gap-2 pl-1">
            <span className="mt-0.5">•</span>
            <span>{line.replace(/^[•-]\s*/, '')}</span>
          </div>
        );
      }
      if (line.trim() === '') return <div key={i} className="h-2" />;
      return <p key={i} className="leading-relaxed">{line}</p>;
    });
  };

  return (
    <div className="flex flex-col h-full animate-fadeIn">
      {/* Chat Header */}
      <div
        className="px-5 py-3 flex items-center gap-3 flex-shrink-0"
        style={{ borderBottom: '1px solid #e2e8f0' }}
      >
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
          style={{
            background: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
            boxShadow: '0 0 12px rgba(124,58,237,0.2)',
          }}
        >
          E
        </div>
        <div>
          <div className="text-sm font-semibold text-[#1e293b]">Eli</div>
          <div className="text-[10px] text-[#059669] flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
            Growth Intelligence Online
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 px-4 md:px-6 py-4">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`animate-slideUp flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'rounded-2xl rounded-tr-sm text-white'
                    : 'rounded-2xl rounded-tl-sm text-[#1e293b]'
                }`}
                style={
                  msg.role === 'user'
                    ? {
                        background: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
                        boxShadow: '0 4px 15px rgba(124,58,237,0.15)',
                      }
                    : {
                        backgroundColor: '#ffffff',
                        border: '1px solid #e2e8f0',
                      }
                }
              >
                {msg.role === 'eli' && (
                  <div className="flex items-center gap-1.5 mb-2">
                    <span className="text-[10px] font-semibold text-[#7c3aed]">ELI</span>
                    <span className="text-[10px] text-[#64748b]">
                      {msg.timestamp.toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true,
                      })}
                    </span>
                  </div>
                )}
                <div className="text-[#1e293b]/90">
                  {msg.role === 'eli' ? <EliMarkdown content={msg.content} /> : renderUserContent(msg.content)}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div
                    className="mt-3 pt-2 flex flex-wrap gap-1.5"
                    style={{ borderTop: '1px solid #e2e8f0' }}
                  >
                    {msg.sources.map((src, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-1 text-[10px] text-[#64748b] hover:text-[#2563eb] transition-colors cursor-default px-2 py-1 rounded-md"
                        style={{ backgroundColor: '#f1f5f9' }}
                      >
                        <ExternalLink className="w-2.5 h-2.5" />
                        <span className="truncate max-w-[160px]">{src.title}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isLoading && (
            <div className="flex justify-start animate-fadeIn">
              <div
                className="rounded-2xl rounded-tl-sm px-4 py-3"
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                }}
              >
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-semibold text-[#7c3aed] mr-1">ELI</span>
                  <div
                    className="w-1.5 h-1.5 rounded-full bg-[#7c3aed] animate-bounce-dot"
                    style={{ animationDelay: '0ms' }}
                  />
                  <div
                    className="w-1.5 h-1.5 rounded-full bg-[#7c3aed] animate-bounce-dot"
                    style={{ animationDelay: '150ms' }}
                  />
                  <div
                    className="w-1.5 h-1.5 rounded-full bg-[#7c3aed] animate-bounce-dot"
                    style={{ animationDelay: '300ms' }}
                  />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div
        className="flex-shrink-0 p-4 md:px-6"
        style={{ borderTop: '1px solid #e2e8f0' }}
      >
        <div
          className="flex items-end gap-3 max-w-3xl mx-auto rounded-xl p-2 transition-all duration-200"
          style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
          }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask Eli anything about growth..."
            rows={1}
            className="flex-1 bg-transparent border-none outline-none resize-none text-sm text-[#1e293b] placeholder:text-[#94a3b8] py-2 px-2 min-h-[36px] max-h-[160px]"
            style={{ scrollbarWidth: 'none' }}
          />
          <Button
            size="icon"
            disabled={!input.trim() || isLoading}
            onClick={handleSend}
            className="flex-shrink-0 w-9 h-9 rounded-lg transition-all duration-200"
            style={{
              background: input.trim() && !isLoading
                ? 'linear-gradient(135deg, #7c3aed, #6d28d9)'
                : '#e2e8f0',
              boxShadow: input.trim() && !isLoading
                ? '0 0 15px rgba(124,58,237,0.2)'
                : 'none',
              cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
            }}
          >
            <Send className="w-4 h-4 text-[#ffffff]" />
          </Button>
        </div>
        <div className="flex items-center justify-between mt-2 max-w-3xl mx-auto">
          <span className="text-[10px] text-[#94a3b8]/70">
            Eli runs on Llama. Press Enter to send, Shift+Enter for new line.
          </span>
          <span className="text-[10px] text-[#059669]/80 flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
            Llama Core Active
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
    fetch('/api/knowledge-stats')
      .then((res) => res.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const categories = (stats?.categories || []).map((c) => ({
    ...c,
    ...(CATEGORY_META[c.key] || { emoji: '📄', label: c.key, color: '#64748b' }),
  }));

  const filtered = categories.filter((c) =>
    c.label.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-fadeIn space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#1e293b] mb-1">Knowledge Base</h1>
        <p className="text-sm text-[#64748b]">
          {loading
            ? 'Scanning knowledge files...'
            : `${stats?.totalFiles || 0} files across ${stats?.totalCategories || 0} categories (${stats?.totalSizeMB || '0'} MB) powering Eli's intelligence.`
          }
        </p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94a3b8]" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search categories..."
          className="pl-10"
          style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            color: '#1e293b',
          }}
        />
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="rounded-xl p-4 animate-pulse"
              style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0' }}
            >
              <div className="h-5 w-8 bg-[#e2e8f0] rounded mb-3" />
              <div className="h-4 w-24 bg-[#e2e8f0] rounded" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {filtered.map((cat, i) => (
            <div
              key={cat.key}
              className="animate-slideUp rounded-xl p-4 transition-all duration-200 cursor-default hover:-translate-y-0.5 group"
              style={{
                animationDelay: `${i * 50}ms`,
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = cat.color + '40';
                (e.currentTarget as HTMLElement).style.boxShadow = `0 0 20px ${cat.color}10`;
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = '#e2e8f0';
                (e.currentTarget as HTMLElement).style.boxShadow = 'none';
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-lg">{cat.emoji}</span>
                <Badge
                  variant="secondary"
                  className="text-[10px]"
                  style={{
                    backgroundColor: cat.color + '15',
                    color: cat.color,
                    border: `1px solid ${cat.color}30`,
                  }}
                >
                  {cat.count}
                </Badge>
              </div>
              <div className="text-sm text-[#1e293b] group-hover:text-[#7c3aed] transition-colors">
                {cat.label}
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="text-center py-12 text-sm text-[#64748b]">
          No categories found matching &quot;{search}&quot;
        </div>
      )}
    </div>
  );
}

// ─── Placeholder View ───────────────────────────────────────────
function PlaceholderView({
  title,
  description,
  icon: Icon,
}: {
  title: string;
  description: string;
  icon: React.ElementType;
}) {
  return (
    <div className="animate-fadeIn flex items-center justify-center h-full">
      <div
        className="text-center max-w-md rounded-2xl p-10"
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
        }}
      >
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-5"
          style={{
            background: 'linear-gradient(135deg, rgba(124,58,237,0.08), rgba(124,58,237,0.04))',
            border: '1px solid rgba(124,58,237,0.12)',
          }}
        >
          <Icon className="w-7 h-7 text-[#7c3aed]" />
        </div>
        <h2 className="text-lg font-semibold text-[#1e293b] mb-2">{title}</h2>
        <p className="text-sm text-[#64748b] mb-5 leading-relaxed">{description}</p>
        <Badge
          variant="secondary"
          className="text-[11px] font-medium"
          style={{
            backgroundColor: 'rgba(124,58,237,0.08)',
            color: '#7c3aed',
            border: '1px solid rgba(124,58,237,0.15)',
          }}
        >
          <Sparkles className="w-3 h-3 mr-1" />
          Coming Soon
        </Badge>
      </div>
    </div>
  );
}

// ─── Main Page ──────────────────────────────────────────────────
export default function Home() {
  const [activeView, setActiveView] = useState<ViewId>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return <DashboardView />;
      case 'chat':
        return <ChatView />;
      case 'knowledge':
        return <KnowledgeView />;
      case 'leads':
        return (
          <PlaceholderView
            icon={Users}
            title="Lead Management"
            description="Track, score, and nurture leads through your growth pipeline. AI-powered lead qualification and automated follow-ups coming soon."
          />
        );
      case 'audits':
        return (
          <PlaceholderView
            icon={Search}
            title="SEO Audits"
            description="Comprehensive site audits powered by Eli's knowledge of 157+ SEO resources. Technical SEO, content gaps, and competitive analysis."
          />
        );
      case 'campaigns':
        return (
          <PlaceholderView
            icon={Megaphone}
            title="Campaign Manager"
            description="Plan, execute, and track growth campaigns across channels. Content campaigns, email sequences, and social media automation."
          />
        );
      case 'content':
        return (
          <PlaceholderView
            icon={FileText}
            title="Content Engine"
            description="AI-powered content creation, scheduling, and optimization. Blog posts, landing pages, social content, and more."
          />
        );
      case 'rank':
        return (
          <PlaceholderView
            icon={TrendingUp}
            title="Rank Tracker"
            description="Monitor keyword rankings, track SERP positions, and get alerts on ranking changes. Integrated with Eli's SEO intelligence."
          />
        );
      case 'integrations':
        return (
          <PlaceholderView
            icon={Plug}
            title="Integrations Hub"
            description="Connect Eli OS to your existing tools. Google Analytics, Search Console, CMS platforms, CRMs, and automation services."
          />
        );
      case 'workflows':
        return (
          <PlaceholderView
            icon={Workflow}
            title="Workflow Automation"
            description="Design and deploy automated growth workflows. Trigger-based actions, multi-step sequences, and conditional logic."
          />
        );
      case 'scrapers':
        return (
          <PlaceholderView
            icon={Bug}
            title="Web Scrapers"
            description="Deploy and manage web scraping tasks. Extract data from competitors, directories, and public sources for growth intelligence."
          />
        );
      case 'seo-skills':
        return (
          <PlaceholderView
            icon={Wrench}
            title="SEO Skill Registry"
            description="Eli's specialized SEO skills and capabilities. Technical SEO, link building, content optimization, and local search expertise."
          />
        );
      case 'vault':
        return (
          <PlaceholderView
            icon={Shield}
            title="Secure Vault"
            description="Encrypted storage for sensitive business data, API keys, credentials, and confidential strategy documents."
          />
        );
      case 'settings':
        return (
          <PlaceholderView
            icon={Settings}
            title="Settings"
            description="Configure Eli OS preferences, notification settings, API connections, and system behavior."
          />
        );
      default:
        return <DashboardView />;
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden animate-fadeIn">
      <Topbar onMenuClick={() => setMobileMenuOpen(true)} />

      <div className="flex flex-1 overflow-hidden">
        {/* Desktop Sidebar */}
        <SidebarNav
          activeView={activeView}
          onViewChange={setActiveView}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Mobile Sidebar */}
        <MobileSidebar
          activeView={activeView}
          onViewChange={setActiveView}
          open={mobileMenuOpen}
          onOpenChange={setMobileMenuOpen}
        />

        {/* Main Workspace */}
        <main className="flex-1 overflow-hidden">
          {activeView === 'chat' ? (
            renderView()
          ) : (
            <ScrollArea className="h-full">
              <div className="p-4 md:p-6 lg:p-8 max-w-6xl mx-auto">
                {renderView()}
              </div>
            </ScrollArea>
          )}
        </main>
      </div>
    </div>
  );
}
