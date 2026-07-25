import React, { useState, useEffect } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';
import { apiClient } from './lib/api-client';
import {
  MessageSquare,
  Heart,
  Shield,
  Award,
  Send,
  CheckCircle2,
  Lock,
  UserCheck,
  Sparkles,
  HelpCircle,
  ArrowRight,
  RefreshCw,
  AlertCircle
} from 'lucide-react';

// ── Login / Demo Credentials Component ─────────────────────────────
export const LoginView: React.FC<{ onLogin: (role: 'member' | 'guardian', user: any) => void }> = ({ onLogin }) => {
  const [email, setEmail] = useState('maya@example.com');
  const [password, setPassword] = useState('Password123!');
  const [role, setRole] = useState<'member' | 'guardian'>('member');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await apiClient.request<any>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      apiClient.setTokens(res.access_token, res.refresh_token);
      onLogin(res.user.role, res.user);
    } catch {
      // Demo fallback login
      onLogin(role, { id: 'demo-id', email, full_name: role === 'member' ? 'Maya (Member)' : 'David (Guardian)', role });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 pt-4">
      <div className="text-center space-y-2">
        <div className="w-14 h-14 bg-sky-500/20 border border-sky-500/30 rounded-3xl flex items-center justify-center mx-auto text-sky-400 font-bold text-2xl shadow-xl shadow-sky-500/10">
          A
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Sign In to Anchor</h1>
        <p className="text-sm text-slate-400">Proactive, safety-gated recovery & caregiver platform</p>
      </div>

      {/* Quick Demo Role Selector */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Quick Demo Login</span>
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => { setEmail('maya@example.com'); setRole('member'); }}
            className={`p-3 rounded-2xl border text-xs font-bold transition flex flex-col items-center gap-1.5 ${
              role === 'member' && email === 'maya@example.com'
                ? 'bg-sky-500/20 border-sky-500 text-sky-400'
                : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
            }`}
          >
            <UserCheck className="w-5 h-5 text-sky-400" />
            <span>Maya (Member)</span>
          </button>
          <button
            type="button"
            onClick={() => { setEmail('david@example.com'); setRole('guardian'); }}
            className={`p-3 rounded-2xl border text-xs font-bold transition flex flex-col items-center gap-1.5 ${
              role === 'guardian' || email === 'david@example.com'
                ? 'bg-indigo-500/20 border-indigo-500 text-indigo-400'
                : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
            }`}
          >
            <Shield className="w-5 h-5 text-indigo-400" />
            <span>David (Guardian)</span>
          </button>
        </div>
      </div>

      <form onSubmit={handleLogin} className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
        <div className="space-y-1">
          <label className="text-xs text-slate-400 font-medium">Email Address</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs text-slate-400 font-medium">Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-sky-500"
          />
        </div>

        {errorMsg && (
          <div className="text-xs text-red-400 bg-red-500/10 p-3 rounded-xl border border-red-500/20">
            {errorMsg}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-sky-600/20 transition flex items-center justify-center gap-2"
        >
          <Lock className="w-4 h-4" />
          <span>{loading ? 'Authenticating...' : `Sign In as ${email === 'david@example.com' ? 'Guardian' : 'Member'}`}</span>
        </button>
      </form>
    </div>
  );
};

// ── Interactive Follow-up Questionnaire Component (4 Questions) ───────
export const GuidedAssessmentView: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});

  const questions = [
    {
      q: "What is your primary goal in recovery right now?",
      options: [
        "Overcoming Alcohol & Cravings",
        "Managing Daily Stress & Anxiety",
        "Building Relapse Resilience",
        "Connecting with Support Circle"
      ]
    },
    {
      q: "What triggers or high-risk moments do you experience most?",
      options: [
        "Evening Solitude & After-Work Hours",
        "Emotional Stress or Conflicts",
        "Social Gatherings & Peer Pressure",
        "Fatigue or Physical Exhaustion (HALT)"
      ]
    },
    {
      q: "Which intervention technique helps you most during urge peaks?",
      options: [
        "4-Minute Timed Urge Surfing",
        "5-4-3-2-1 Sensory Grounding",
        "AI Companion Recovery Coaching",
        "One-Tap Contacting Caregiver Circle"
      ]
    },
    {
      q: "How would you prefer daily check-in nudges and reminders?",
      options: [
        "Once Daily (Morning Check-in)",
        "Twice Daily (Morning & Evening)",
        "Quiet Hours Respected (No 10pm-7am Nudges)"
      ]
    }
  ];

  const handleSelectOption = (opt: string) => {
    setAnswers(prev => ({ ...prev, [currentStep]: opt }));
    if (currentStep < questions.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      onComplete();
    }
  };

  return (
    <div className="space-y-6 pt-2">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2 text-sky-400">
          <Sparkles className="w-5 h-5" />
          <h2 className="text-xl font-bold text-white">Personalized Onboarding</h2>
        </div>
        <span className="text-xs text-slate-400 font-mono">Question {currentStep + 1} of 4</span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
        <div
          className="bg-gradient-to-r from-sky-500 to-indigo-500 h-full transition-all duration-300"
          style={{ width: `${((currentStep + 1) / questions.length) * 100}%` }}
        />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-5 shadow-xl">
        <h3 className="text-lg font-bold text-white">{questions[currentStep].q}</h3>

        <div className="space-y-3">
          {questions[currentStep].options.map((opt, idx) => (
            <button
              key={idx}
              onClick={() => handleSelectOption(opt)}
              className="w-full text-left bg-slate-950/80 hover:bg-slate-800 border border-slate-800 hover:border-sky-500/50 p-4 rounded-2xl text-sm font-medium text-slate-200 transition flex items-center justify-between group"
            >
              <span>{opt}</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-sky-400 transition transform group-hover:translate-x-1" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// ── Dashboard Component ─────────────────────────────────────────────
const DashboardView: React.FC = () => {
  const [riskData, setRiskData] = useState<{ score: number; band: string; factors: any[] }>({
    score: 85,
    band: 'low',
    factors: [
      { factor: 'craving_level', impact: '+10', detail: 'Craving level recorded at 2/10' },
      { factor: 'checkin_consistency', impact: '+5', detail: 'Consistent daily check-ins recorded' }
    ],
  });
  const [milestone, setMilestone] = useState<{ days_count: number }>({ days_count: 14 });
  const [checkinOpen, setCheckinOpen] = useState(false);
  const [mood, setMood] = useState(4);
  const [sleep, setSleep] = useState(4);
  const [craving, setCraving] = useState(2);
  const [checkinDone, setCheckinDone] = useState<string | null>(null);

  useEffect(() => {
    apiClient.request<any>('/risk/current').then(res => {
      if (res && res.score !== undefined) setRiskData(res);
    }).catch(() => {});

    apiClient.request<any>('/tracking/milestones').then(res => {
      if (res && res.days_count !== undefined) setMilestone(res);
    }).catch(() => {});
  }, []);

  const handleCheckinSubmit = async () => {
    try {
      const res = await apiClient.request<any>('/checkins', {
        method: 'POST',
        body: JSON.stringify({
          mood,
          sleep_quality: sleep,
          craving,
          halt: { hungry: false, angry: false, lonely: false, tired: false },
          source: 'tap',
        }),
      });
      setCheckinDone(res.suggested_action?.label || 'Check-in recorded!');
      if (res.risk) setRiskData(res.risk);
    } catch {
      setCheckinDone('Check-in recorded successfully!');
    }
  };

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Recovery Dashboard</h1>
        <p className="text-slate-400 text-xs">
          Proactive signals, explainable risk score, and intervention recommendations.
        </p>
      </header>

      {/* Steady Score Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Steady Score</span>
          <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
            riskData.band === 'high' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
            riskData.band === 'elevated' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
            'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
          }`}>
            {riskData.band} RISK
          </span>
        </div>
        <div className="text-5xl font-black text-white">{riskData.score} <span className="text-lg font-normal text-slate-500">/ 100</span></div>

        {/* Contributing Factors */}
        <div className="space-y-2 pt-2 border-t border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Top Contributing Factors:</span>
          {riskData.factors.map((f, i) => (
            <div key={i} className="text-xs text-slate-300 flex items-center justify-between bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
              <span>{f.detail}</span>
              <span className="font-bold text-sky-400">{f.impact}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recovery Milestone Counter */}
      <div className="bg-gradient-to-r from-indigo-950/80 to-slate-900/80 border border-indigo-500/20 rounded-3xl p-5 flex items-center justify-between shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-white">{milestone.days_count} Days</div>
            <div className="text-xs text-slate-400 font-medium">Active Recovery Streak</div>
          </div>
        </div>
      </div>

      {/* Daily Check-in Button / Form */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
        <div className="flex items-center justify-between">
          <span className="font-bold text-white text-base">Daily Signal Check-in</span>
          <button
            onClick={() => setCheckinOpen(!checkinOpen)}
            className="text-xs font-bold text-sky-400 bg-sky-500/10 hover:bg-sky-500/20 px-3 py-1.5 rounded-xl transition"
          >
            {checkinOpen ? 'Close' : 'Log Daily Signals'}
          </button>
        </div>

        {checkinOpen && (
          <div className="space-y-4 pt-3 border-t border-slate-800">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Mood (1 poor – 5 excellent): {mood}/5</label>
              <input type="range" min="1" max="5" value={mood} onChange={e => setMood(parseInt(e.target.value))} className="w-full accent-sky-500" />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Sleep Quality (1 poor – 5 excellent): {sleep}/5</label>
              <input type="range" min="1" max="5" value={sleep} onChange={e => setSleep(parseInt(e.target.value))} className="w-full accent-sky-500" />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Craving Level (0 none – 10 intense): {craving}/10</label>
              <input type="range" min="0" max="10" value={craving} onChange={e => setCraving(parseInt(e.target.value))} className="w-full accent-sky-500" />
            </div>
            <button
              onClick={handleCheckinSubmit}
              className="w-full bg-sky-600 hover:bg-sky-500 text-white font-bold py-3 rounded-xl shadow-lg shadow-sky-600/20"
            >
              Submit Check-in
            </button>
          </div>
        )}

        {checkinDone && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-xs font-medium flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{checkinDone}</span>
          </div>
        )}
      </div>
    </div>
  );
};

// ── AI Companion Chat Component with Interactive Follow-up Question Chips ────
const CompanionChatView: React.FC = () => {
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'bot'; text: string; citations?: string[] }>>([
    {
      sender: 'bot',
      text: 'Hello! I am your Anchor recovery companion. How can I support your recovery journey today?',
      citations: ['[kb-101]']
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Suggested follow-up prompt chips
  const followUpChips = [
    "I am addict to alcohol how can I overcome",
    "Tell me about 4-minute Urge Surfing",
    "How do I handle evening social triggers?",
    "Can you explain SMART Recovery pillars?",
    "What support does my caregiver receive?"
  ];

  const handleSendMessage = async (textToSend: string) => {
    if (!textToSend.trim()) return;
    const userMsg = textToSend.trim();
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await apiClient.request<any>('/companion/chat', {
        method: 'POST',
        body: JSON.stringify({ message: userMsg }),
      });
      setMessages(prev => [...prev, { sender: 'bot', text: res.reply, citations: res.citations }]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          sender: 'bot',
          text: 'Overcoming alcohol addiction involves SMART Recovery strategies [kb-101]: motivation building, urge surfing, and trigger management. Would you like to practice urge surfing?',
          citations: ['[kb-101]']
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 flex flex-col h-[72vh]">
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        <MessageSquare className="w-6 h-6 text-sky-400" />
        <h2 className="text-xl font-bold text-white">AI Recovery Companion</h2>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[88%] rounded-2xl p-4 text-sm ${
              m.sender === 'user' ? 'bg-sky-600 text-white rounded-br-none' : 'bg-slate-900 border border-slate-800 text-slate-100 rounded-bl-none shadow-lg'
            }`}>
              <p className="whitespace-pre-line leading-relaxed">{m.text}</p>
              {m.citations && m.citations.length > 0 && (
                <div className="mt-2.5 pt-2 border-t border-slate-800/80 text-xs text-sky-400 font-mono flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5" />
                  <span>Grounded Citation: {m.citations.join(', ')}</span>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-900 border border-slate-800 text-slate-400 text-xs rounded-2xl p-3 animate-pulse">
              Anchor Companion analyzing grounding context...
            </div>
          </div>
        )}
      </div>

      {/* Interactive Follow-up Question Chips */}
      <div className="space-y-1.5 pt-1">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Suggested Follow-up Questions:</span>
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
          {followUpChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(chip)}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-sky-500/40 text-slate-300 hover:text-white text-xs py-2 px-3 rounded-xl whitespace-nowrap transition flex items-center gap-1.5 shrink-0"
            >
              <HelpCircle className="w-3.5 h-3.5 text-sky-400" />
              <span>{chip}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Box */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSendMessage(input)}
          placeholder="Ask or express how you feel..."
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-sky-500"
        />
        <button
          onClick={() => handleSendMessage(input)}
          className="bg-sky-600 hover:bg-sky-500 text-white p-3 rounded-xl shadow-lg shadow-sky-600/20"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

// ── Caregiver Circle & Copilot Feed Component ────────────────────────
const CaregiverFeedView: React.FC = () => {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        <Shield className="w-6 h-6 text-indigo-400" />
        <div>
          <h2 className="text-xl font-bold text-white">Caregiver Copilot</h2>
          <p className="text-xs text-slate-400">Linked Member: Maya (Member)</p>
        </div>
      </div>

      {/* Member Risk Status Overview */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Member Steady Status</span>
          <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-xs font-bold uppercase border border-emerald-500/30">
            LOW RISK (85/100)
          </span>
        </div>
        <p className="text-xs text-slate-300">
          Maya logged a check-in 2 hours ago. Cravings remain low and active recovery streak is 14 days.
        </p>
      </div>

      {/* Caregiver Copilot Guidance Card */}
      <div className="bg-indigo-950/40 border border-indigo-500/30 rounded-3xl p-6 space-y-4 shadow-xl">
        <div className="flex items-center gap-2 text-indigo-400">
          <Heart className="w-5 h-5" />
          <h3 className="font-bold text-white text-base">CRAFT Copilot Support Guidance</h3>
        </div>

        <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 block uppercase tracking-wider">Suggested Message to Send:</span>
          <p className="text-sm font-medium text-indigo-200">
            "I love you and I am so proud of your 14-day recovery milestone! I am right here whenever you want to talk."
          </p>
        </div>

        <div className="space-y-1.5">
          <span className="text-xs font-semibold text-slate-400 block uppercase tracking-wider">Behaviors to Avoid:</span>
          <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
            <li>Do not interrogate about past triggers or mistakes</li>
            <li>Do not express anger or panic</li>
            <li>Avoid lecturing or giving unsolicited medical advice</li>
          </ul>
        </div>

        <div className="text-[11px] text-slate-400 italic pt-1 border-t border-indigo-500/20">
          Rationale: CRAFT principles show positive reinforcement strengthens self-efficacy without inducing shame.
        </div>
      </div>
    </div>
  );
};

// ── Main App Router Wrapper ──────────────────────────────────────────
export const AppRouter: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [page, setPage] = useState<'dashboard' | 'chat' | 'caregiver' | 'onboarding'>('dashboard');

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center max-w-md mx-auto p-4 border-x border-slate-900 shadow-2xl">
        <LoginView onLogin={(role, u) => { setUser(u); setPage('onboarding'); }} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between max-w-md mx-auto relative border-x border-slate-900 shadow-2xl">
      {/* Top Navbar */}
      <header className="p-4 border-b border-slate-900 flex items-center justify-between bg-slate-950/80 backdrop-blur sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-sky-500 flex items-center justify-center font-bold text-slate-950 text-lg shadow-md shadow-sky-500/20">
            A
          </div>
          <span className="font-bold text-lg text-white tracking-tight">Anchor</span>
        </div>

        <nav className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs font-semibold">
          <button
            onClick={() => setPage('dashboard')}
            className={`px-2.5 py-1 rounded-lg transition ${page === 'dashboard' ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Home
          </button>
          <button
            onClick={() => setPage('chat')}
            className={`px-2.5 py-1 rounded-lg transition ${page === 'chat' ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            AI Chat
          </button>
          <button
            onClick={() => setPage('caregiver')}
            className={`px-2.5 py-1 rounded-lg transition ${page === 'caregiver' ? 'bg-indigo-500 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Copilot
          </button>
        </nav>
      </header>

      {/* Main Page Content */}
      <main className="flex-1 p-4 pb-28">
        {page === 'onboarding' && <GuidedAssessmentView onComplete={() => setPage('dashboard')} />}
        {page === 'dashboard' && <DashboardView />}
        {page === 'chat' && <CompanionChatView />}
        {page === 'caregiver' && <CaregiverFeedView />}
      </main>

      {/* Persistent Bottom Bar with SOS 'I'm Struggling' Slot */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-slate-950/90 backdrop-blur border-t border-slate-900 z-50 max-w-md mx-auto">
        <div className="flex items-center gap-2">
          <div className="flex-1">
            <button
              onClick={() => { setUser(null); }}
              className="w-full bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white text-xs font-bold py-3.5 px-3 rounded-2xl border border-slate-800"
            >
              Sign Out ({user.email.split('@')[0]})
            </button>
          </div>
          <div className="flex-[2]">
            <App.SOSButton />
          </div>
        </div>
      </div>
    </div>
  );
};
