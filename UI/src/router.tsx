import React, { useState, useEffect, useRef } from 'react';
import { apiClient } from './lib/api-client';
import { SOSButton } from './components/ui/SOSButton';
import {
  MessageSquare, Heart, Shield, Award, Send, CheckCircle2, Lock,
  UserCheck, Sparkles, ArrowRight, Activity, TrendingUp, Smile,
  Moon, Flame, ExternalLink, LogOut, Compass, BookOpen, Phone, Wind
} from 'lucide-react';

// ── Types ───────────────────────────────────────────────────────────
interface Resource {
  title: string;
  url: string;
  description: string;
}

interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
  citations?: string[];
  resources?: Resource[];
  timestamp: string;
  followUps?: string[];
}

// ── Login View ──────────────────────────────────────────────────────
const LoginView: React.FC<{ onLogin: (token: string, refresh: string, user: any) => void }> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'member' | 'guardian'>('member');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const demoUsers = {
    member: { email: 'maya@example.com', password: 'Password123!', label: 'Maya', desc: 'Member — Recovery Journey' },
    guardian: { email: 'david@example.com', password: 'Password123!', label: 'David', desc: 'Guardian — Caregiver Copilot' },
  };

  const selectDemo = (r: 'member' | 'guardian') => {
    setRole(r);
    setEmail(demoUsers[r].email);
    setPassword(demoUsers[r].password);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) { setError('Please enter email and password.'); return; }
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.request<any>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      onLogin(res.access_token, res.refresh_token, res.user || { email, role });
    } catch (err: any) {
      setError(err?.message || `Login failed. Verify credentials and that the backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080c14] flex items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6">
        {/* Brand */}
        <div className="text-center space-y-3">
          <div className="w-16 h-16 mx-auto rounded-3xl bg-gradient-to-br from-sky-500 to-indigo-600 p-[2px] shadow-2xl shadow-sky-500/20">
            <div className="w-full h-full bg-[#080c14] rounded-[22px] flex items-center justify-center">
              <Compass className="w-7 h-7 text-sky-400" />
            </div>
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Anchor</h1>
          <p className="text-sm text-slate-400 leading-relaxed max-w-xs mx-auto">
            AI-powered recovery & prevention platform for substance use disorders
          </p>
        </div>

        {/* Demo Persona Cards */}
        <div className="space-y-2">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Test Credentials</span>
          <div className="grid grid-cols-2 gap-3">
            {(['member', 'guardian'] as const).map(r => (
              <button
                key={r}
                type="button"
                onClick={() => selectDemo(r)}
                className={`p-4 rounded-2xl border text-center transition-all duration-200 ${
                  role === r
                    ? r === 'member'
                      ? 'bg-sky-500/15 border-sky-500/60 shadow-lg shadow-sky-500/10'
                      : 'bg-indigo-500/15 border-indigo-500/60 shadow-lg shadow-indigo-500/10'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                {r === 'member'
                  ? <UserCheck className={`w-5 h-5 mx-auto mb-1.5 ${role === r ? 'text-sky-400' : 'text-slate-500'}`} />
                  : <Shield className={`w-5 h-5 mx-auto mb-1.5 ${role === r ? 'text-indigo-400' : 'text-slate-500'}`} />
                }
                <div className={`text-xs font-bold ${role === r ? 'text-white' : 'text-slate-400'}`}>{demoUsers[r].label}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">{demoUsers[r].desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="bg-slate-900/70 border border-slate-800/80 rounded-3xl p-6 space-y-4 backdrop-blur-sm">
          <div className="space-y-1.5">
            <label className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
              className="w-full bg-slate-950/80 border border-slate-800 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-sky-500 transition" />
          </div>
          <div className="space-y-1.5">
            <label className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
              className="w-full bg-slate-950/80 border border-slate-800 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-sky-500 transition" />
          </div>
          {error && (
            <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 p-3 rounded-xl">{error}</div>
          )}
          <button type="submit" disabled={loading}
            className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-extrabold text-sm py-3.5 rounded-2xl shadow-xl shadow-sky-500/15 transition transform active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-2">
            <Lock className="w-4 h-4" />
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

// ── Onboarding Assessment ───────────────────────────────────────────
const OnboardingView: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const questions = [
    { q: "What is your primary goal in recovery right now?", opts: ["Overcoming Alcohol & Cravings", "Managing Stress & Emotional Triggers", "Building Long-Term Relapse Resilience", "Strengthening Family & Caregiver Support"] },
    { q: "When do high-risk moments or triggers happen most?", opts: ["Evening Solitude (6pm–9pm)", "Emotional Stress or Work Conflicts", "Social Gatherings & Peer Pressure", "Physical Fatigue or Lack of Sleep"] },
    { q: "Which coping technique resonates with you?", opts: ["4-Minute Urge Surfing", "5-4-3-2-1 Sensory Grounding", "Talking to AI Recovery Coach", "Contacting My Caregiver Circle"] },
    { q: "How should we schedule daily check-in nudges?", opts: ["Morning Only", "Morning & Evening", "Quiet Hours (No 10pm–7am Nudges)"] },
  ];

  const select = (opt: string) => {
    if (step < questions.length - 1) setStep(s => s + 1);
    else onComplete();
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sky-400">
          <Sparkles className="w-5 h-5" />
          <h2 className="text-lg font-black text-white">Recovery Onboarding</h2>
        </div>
        <span className="text-xs text-slate-400 font-mono font-bold">{step + 1} / {questions.length}</span>
      </div>
      <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
        <div className="bg-gradient-to-r from-sky-400 to-indigo-500 h-full transition-all duration-300 rounded-full"
          style={{ width: `${((step + 1) / questions.length) * 100}%` }} />
      </div>
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 space-y-4">
        <h3 className="text-base font-bold text-white leading-snug">{questions[step].q}</h3>
        <div className="space-y-2.5">
          {questions[step].opts.map((opt, i) => (
            <button key={i} onClick={() => select(opt)}
              className="w-full text-left bg-slate-950/70 hover:bg-slate-800 border border-slate-800 hover:border-sky-500/50 p-4 rounded-2xl text-sm text-slate-200 transition flex items-center justify-between group">
              <span>{opt}</span>
              <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-sky-400 transition transform group-hover:translate-x-1" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// ── Dashboard ───────────────────────────────────────────────────────
const DashboardView: React.FC = () => {
  const [risk, setRisk] = useState<any>(null);
  const [milestone, setMilestone] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [checkinOpen, setCheckinOpen] = useState(false);
  const [mood, setMood] = useState(3); const [sleep, setSleep] = useState(3); const [craving, setCraving] = useState(3);
  const [checkinResult, setCheckinResult] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try { const r = await apiClient.request<any>('/risk/current'); setRisk(r); } catch {}
      try { const m = await apiClient.request<any>('/tracking/milestones'); setMilestone(m); } catch {}
      setLoading(false);
    })();
  }, []);

  const submitCheckin = async () => {
    setCheckinResult(null);
    try {
      const res = await apiClient.request<any>('/checkins', {
        method: 'POST',
        body: JSON.stringify({ mood, sleep_quality: sleep, craving, halt: { hungry: false, angry: false, lonely: false, tired: false }, source: 'tap' }),
      });
      setCheckinResult(res.suggested_action?.label || 'Check-in submitted and processed.');
      if (res.risk) setRisk(res.risk);
    } catch (err: any) {
      setCheckinResult(`Error: ${err?.message || 'Failed to submit check-in. Is the backend running?'}`);
    }
  };

  if (loading) return <div className="text-slate-400 text-sm text-center py-12 animate-pulse">Loading live data from backend...</div>;

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-black text-white tracking-tight">Recovery Dashboard</h1>

      {/* Steady Score */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-sky-400" /> Steady Score
          </span>
          {risk && (
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold uppercase ${
              risk.band === 'high' ? 'bg-red-500/15 text-red-400 border border-red-500/30' :
              risk.band === 'elevated' ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30' :
              'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
            }`}>{risk.band} risk</span>
          )}
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-5xl font-black text-white">{risk?.score ?? '—'}</span>
          <span className="text-lg text-slate-600">/ 100</span>
        </div>
        {risk?.factors?.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
            <span className="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Contributing Factors</span>
            {risk.factors.slice(0, 3).map((f: any, i: number) => (
              <div key={i} className="text-xs flex justify-between bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/60">
                <span className="text-slate-300">{f.detail || f.factor}</span>
                <span className="text-sky-400 font-bold font-mono">{f.impact}</span>
              </div>
            ))}
          </div>
        )}
        {!risk && <p className="text-xs text-slate-500">Unable to load risk data from backend.</p>}
      </div>

      {/* Milestone */}
      {milestone && (
        <div className="bg-gradient-to-r from-indigo-950/70 to-slate-900/70 border border-indigo-500/20 rounded-3xl p-4 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-white">{milestone.days_count} Days</div>
            <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">Sobriety Streak</div>
          </div>
        </div>
      )}

      {/* Check-in */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-bold text-white flex items-center gap-1.5"><TrendingUp className="w-4 h-4 text-sky-400" /> Daily Check-in</span>
          <button onClick={() => setCheckinOpen(!checkinOpen)}
            className="text-[11px] font-bold text-sky-400 bg-sky-500/10 hover:bg-sky-500/20 px-3 py-1.5 rounded-lg transition">
            {checkinOpen ? 'Close' : 'Log Signals'}
          </button>
        </div>
        {checkinOpen && (
          <div className="space-y-3 pt-3 border-t border-slate-800/80">
            {[
              { label: 'Mood', icon: <Smile className="w-3.5 h-3.5 text-amber-400" />, val: mood, set: setMood, max: 5 },
              { label: 'Sleep', icon: <Moon className="w-3.5 h-3.5 text-indigo-400" />, val: sleep, set: setSleep, max: 5 },
              { label: 'Craving', icon: <Flame className="w-3.5 h-3.5 text-red-400" />, val: craving, set: setCraving, max: 10 },
            ].map(s => (
              <div key={s.label} className="space-y-1">
                <div className="flex justify-between text-xs text-slate-300">
                  <span className="flex items-center gap-1 font-medium">{s.icon} {s.label}</span>
                  <span className="font-bold text-sky-400">{s.val}/{s.max}</span>
                </div>
                <input type="range" min={s.label === 'Craving' ? 0 : 1} max={s.max} value={s.val}
                  onChange={e => s.set(parseInt(e.target.value))} className="w-full accent-sky-500" />
              </div>
            ))}
            <button onClick={submitCheckin}
              className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 text-white font-bold py-3 rounded-2xl shadow-lg shadow-sky-500/15 transition transform active:scale-[0.98]">
              Submit Check-in
            </button>
          </div>
        )}
        {checkinResult && (
          <div className={`text-xs p-3 rounded-xl flex items-center gap-2 ${
            checkinResult.startsWith('Error') ? 'bg-red-500/10 border border-red-500/20 text-red-400' : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
          }`}>
            <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> {checkinResult}
          </div>
        )}
      </div>

      {/* Educational Resources */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-5 space-y-3">
        <span className="text-sm font-bold text-white flex items-center gap-1.5"><BookOpen className="w-4 h-4 text-sky-400" /> Recovery Resources</span>
        {[
          { title: 'SAMHSA National Helpline', url: 'https://www.samhsa.gov/find-help/national-helpline', desc: 'Free 24/7 referral service' },
          { title: 'NIAAA Rethinking Drinking', url: 'https://www.rethinkingdrinking.niaaa.nih.gov/', desc: 'NIH alcohol self-assessment' },
          { title: 'SMART Recovery', url: 'https://www.smartrecovery.org/', desc: 'Science-based mutual support' },
          { title: '988 Crisis Lifeline', url: 'https://988lifeline.org/', desc: '24/7 suicide & crisis support' },
        ].map((r, i) => (
          <a key={i} href={r.url} target="_blank" rel="noopener noreferrer"
            className="flex items-center justify-between bg-slate-950/60 border border-slate-800/60 p-3 rounded-xl text-xs hover:border-sky-500/40 transition group">
            <div>
              <div className="text-slate-200 font-semibold group-hover:text-sky-400 transition">{r.title}</div>
              <div className="text-slate-500">{r.desc}</div>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-600 group-hover:text-sky-400 shrink-0" />
          </a>
        ))}
      </div>
    </div>
  );
};

// ── AI Companion Chat ───────────────────────────────────────────────
const ChatView: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => { scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' }); }, [messages]);

  const sendMessage = async (text: string) => {
    const msg = text.trim();
    if (!msg || loading) return;
    setInput('');
    const userMsg: ChatMessage = { sender: 'user', text: msg, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await apiClient.request<any>('/companion/chat', {
        method: 'POST',
        body: JSON.stringify({ message: msg }),
      });

      // Parse follow-up questions from response text
      const parts = res.reply.split(/(?:Follow-up|Follow-ups|Questions):/i);
      const mainText = parts[0].trim();
      const followUpText = parts[1] || '';
      const followUps: string[] = [];
      if (followUpText) {
        const matches = followUpText.match(/(?:\d+\.\s*|[•\-*]\s*)(.+)/g);
        if (matches) {
          matches.forEach((m: string) => {
            followUps.push(m.replace(/^(?:\d+\.\s*|[•\-*]\s*)/, '').trim());
          });
        }
      }

      const botMsg: ChatMessage = {
        sender: 'bot',
        text: mainText,
        citations: res.citations || [],
        resources: res.resources || [],
        timestamp: new Date().toISOString(),
        followUps: followUps.length > 0 ? followUps : undefined,
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err: any) {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: `⚠️ ${err?.message || 'Could not reach the AI companion. Please verify the backend is running and your Gemini API key is configured.'}`,
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-180px)]">
      <div className="flex items-center gap-2 pb-3 border-b border-slate-800/80">
        <MessageSquare className="w-5 h-5 text-sky-400" />
        <h2 className="text-lg font-black text-white">AI Recovery Companion</h2>
        <span className="text-[10px] text-slate-500 ml-auto">Powered by Gemini</span>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12 space-y-4">
            <Compass className="w-10 h-10 text-sky-500/30 mx-auto" />
            <p className="text-slate-500 text-sm">Start a conversation with your AI recovery companion.</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {[
                "I'm struggling with alcohol cravings, how can I overcome them?",
                "What is urge surfing and how does it work?",
                "How can my caregiver support me without being judgmental?",
                "I'm feeling stressed after work, what should I do?",
              ].map((q, i) => (
                <button key={i} onClick={() => sendMessage(q)}
                  className="bg-slate-900/80 border border-slate-800 hover:border-sky-500/40 text-slate-300 hover:text-white text-xs py-2 px-3 rounded-xl transition text-left">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[90%] rounded-3xl p-4 text-sm leading-relaxed ${
              m.sender === 'user'
                ? 'bg-gradient-to-r from-sky-600 to-indigo-600 text-white rounded-br-sm'
                : 'bg-slate-900/90 border border-slate-800/80 text-slate-100 rounded-bl-sm'
            }`}>
              <p className="whitespace-pre-line">{m.text}</p>

              {/* Citations */}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-800/60 text-[11px] text-sky-400/80 font-mono flex items-center gap-1">
                  <Shield className="w-3 h-3" /> Citation: {m.citations.join(', ')}
                </div>
              )}

              {/* Resource Links */}
              {m.resources && m.resources.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-800/60 space-y-1.5">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Helpful Resources:</span>
                  {m.resources.map((r, ri) => (
                    <a key={ri} href={r.url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-2 text-xs text-sky-400 hover:text-sky-300 transition group">
                      <ExternalLink className="w-3 h-3 shrink-0" />
                      <span className="underline underline-offset-2">{r.title}</span>
                      <span className="text-slate-600 no-underline">— {r.description}</span>
                    </a>
                  ))}
                </div>
              )}
            </div>

            {/* Follow-up Question Chips */}
            {m.sender === 'bot' && m.followUps && m.followUps.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2 max-w-[90%] justify-start">
                {m.followUps.map((q, qi) => (
                  <button key={qi} onClick={() => sendMessage(q)}
                    className="bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-sky-500/50 text-sky-400 hover:text-sky-300 text-xs py-1.5 px-3 rounded-full transition text-left font-medium">
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-900/80 border border-slate-800/80 text-slate-400 text-xs rounded-2xl py-3 px-4 animate-pulse">
              Generating response via Gemini...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="pt-3 border-t border-slate-800/80 flex gap-2">
        <input type="text" value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage(input)}
          placeholder="Type how you feel or ask a question..."
          className="flex-1 bg-slate-900/80 border border-slate-800 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-sky-500 transition" />
        <button onClick={() => sendMessage(input)} disabled={loading}
          className="bg-gradient-to-r from-sky-500 to-indigo-600 text-white p-3 rounded-2xl shadow-lg shadow-sky-500/15 transition transform active:scale-95 disabled:opacity-50">
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

// ── Caregiver Copilot ───────────────────────────────────────────────
const CaregiverView: React.FC = () => {
  const [feed, setFeed] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiClient.request<any>('/caregiver/feed');
        setFeed(res);
      } catch {}
      setLoading(false);
    })();
  }, []);

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2">
        <Shield className="w-5 h-5 text-indigo-400" />
        <h2 className="text-lg font-black text-white">Caregiver Copilot</h2>
      </div>

      {loading ? (
        <div className="text-slate-400 text-sm text-center py-12 animate-pulse">Loading caregiver feed from backend...</div>
      ) : !feed ? (
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-5 space-y-3">
          <p className="text-xs text-slate-400">Could not load caregiver feed. Verify you are logged in as a Guardian and the backend is running.</p>
        </div>
      ) : (
        <>
          <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Member Status</span>
              {feed.member_status && (
                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase ${
                  feed.member_status.band === 'low' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-amber-500/15 text-amber-400'
                }`}>{feed.member_status.band} ({feed.member_status.score}/100)</span>
              )}
            </div>
            {feed.member_name && <p className="text-xs text-slate-300">Linked member: {feed.member_name}</p>}
          </div>

          {feed.copilot_guidance && (
            <div className="bg-indigo-950/40 border border-indigo-500/30 rounded-3xl p-5 space-y-3">
              <div className="flex items-center gap-2 text-indigo-400">
                <Heart className="w-4 h-4" />
                <h3 className="font-bold text-white text-sm">CRAFT Support Guidance</h3>
              </div>
              {feed.copilot_guidance.message_to_send && (
                <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block mb-1">Suggested Message:</span>
                  <p className="text-sm text-indigo-200">{feed.copilot_guidance.message_to_send}</p>
                </div>
              )}
              {feed.copilot_guidance.avoid_list && (
                <div>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block mb-1">Avoid:</span>
                  <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                    {feed.copilot_guidance.avoid_list.map((a: string, i: number) => <li key={i}>{a}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Static resources for caregiver education */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-5 space-y-2">
        <span className="text-sm font-bold text-white flex items-center gap-1.5"><BookOpen className="w-4 h-4 text-indigo-400" /> Caregiver Resources</span>
        {[
          { title: 'CRAFT Method for Families', url: 'https://www.motivationandchange.com/craft', desc: 'Evidence-based family support' },
          { title: 'Al-Anon Family Groups', url: 'https://al-anon.org/', desc: 'Support for families of alcoholics' },
          { title: 'SAMHSA Family Toolkit', url: 'https://www.samhsa.gov/families', desc: 'Family recovery resources' },
        ].map((r, i) => (
          <a key={i} href={r.url} target="_blank" rel="noopener noreferrer"
            className="flex items-center justify-between bg-slate-950/60 border border-slate-800/60 p-3 rounded-xl text-xs hover:border-indigo-500/40 transition group">
            <div>
              <div className="text-slate-200 font-semibold group-hover:text-indigo-400 transition">{r.title}</div>
              <div className="text-slate-500">{r.desc}</div>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 shrink-0" />
          </a>
        ))}
      </div>
    </div>
  );
};

// ── Root App Router ─────────────────────────────────────────────────
export const AppRouter: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [page, setPage] = useState<'onboarding' | 'dashboard' | 'chat' | 'caregiver'>('onboarding');

  const handleLogin = (access: string, refresh: string, u: any) => {
    apiClient.setTokens(access, refresh);
    setUser(u);
    setPage('onboarding');
  };

  const handleLogout = () => {
    apiClient.clearTokens();
    setUser(null);
    setPage('onboarding');
  };

  if (!user) return <LoginView onLogin={handleLogin} />;

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col max-w-md mx-auto border-x border-slate-900/50">
      {/* Header */}
      <header className="p-3 border-b border-slate-900/60 flex items-center justify-between bg-[#080c14]/95 backdrop-blur-lg sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center">
            <Compass className="w-4 h-4 text-white" />
          </div>
          <span className="font-black text-base text-white">Anchor</span>
        </div>
        <nav className="flex items-center gap-0.5 bg-slate-900/80 p-0.5 rounded-xl border border-slate-800/60 text-[11px] font-bold">
          {[
            { key: 'dashboard', label: 'Home' },
            { key: 'chat', label: 'AI Chat' },
            { key: 'caregiver', label: 'Copilot' },
          ].map(t => (
            <button key={t.key} onClick={() => setPage(t.key as any)}
              className={`px-2.5 py-1.5 rounded-lg transition ${
                page === t.key
                  ? t.key === 'caregiver' ? 'bg-indigo-600 text-white' : 'bg-sky-500 text-slate-950'
                  : 'text-slate-500 hover:text-white'
              }`}>{t.label}</button>
          ))}
        </nav>
      </header>

      {/* Content */}
      <main className="flex-1 p-4 pb-24">
        {page === 'onboarding' && <OnboardingView onComplete={() => setPage('dashboard')} />}
        {page === 'dashboard' && <DashboardView />}
        {page === 'chat' && <ChatView />}
        {page === 'caregiver' && <CaregiverView />}
      </main>

      {/* Bottom Bar */}
      <div className="fixed bottom-0 left-0 right-0 p-3 bg-[#080c14]/95 backdrop-blur-lg border-t border-slate-900/60 z-50 max-w-md mx-auto flex items-center gap-2">
        <button onClick={handleLogout}
          className="bg-slate-900/80 hover:bg-slate-800 text-slate-500 hover:text-white text-[11px] font-bold py-3 px-3 rounded-xl border border-slate-800/60 flex items-center gap-1.5 transition">
          <LogOut className="w-3.5 h-3.5" /> Sign Out
        </button>
        <div className="flex-1"><SOSButton /></div>
      </div>
    </div>
  );
};
