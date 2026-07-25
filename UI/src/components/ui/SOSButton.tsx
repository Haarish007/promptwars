import React, { useState, useEffect, useRef } from 'react';
import { AlertCircle, Phone, HeartHandshake, Wind, X, ExternalLink } from 'lucide-react';
import { apiClient } from '../../lib/api-client';

export const SOSButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sosData, setSosData] = useState<any>(null);
  const [error, setError] = useState('');
  const [urgeActive, setUrgeActive] = useState(false);
  const [urgeStep, setUrgeStep] = useState(0);
  const [seconds, setSeconds] = useState(240);
  const [cravingAfter, setCravingAfter] = useState(3);
  const [completed, setCompleted] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Timer logic
  useEffect(() => {
    if (urgeActive && seconds > 0 && !completed) {
      timerRef.current = setInterval(() => {
        setSeconds(s => {
          if (s <= 1) { clearInterval(timerRef.current!); return 0; }
          return s - 1;
        });
        // Advance step every 60s
        setUrgeStep(s => Math.min(3, Math.floor((240 - seconds + 1) / 60)));
      }, 1000);
      return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }
  }, [urgeActive, completed]);

  const triggerSOS = async () => {
    setIsOpen(true);
    setLoading(true);
    setError('');
    setSosData(null);
    try {
      const res = await apiClient.request<any>('/sos', {
        method: 'POST',
        body: JSON.stringify({ region: 'US', voice_triggered: false }),
      });
      setSosData(res);
    } catch (err: any) {
      setError(err?.message || 'Could not reach the SOS endpoint. Please call 988 directly for immediate help.');
    } finally {
      setLoading(false);
    }
  };

  const close = () => {
    setIsOpen(false);
    setUrgeActive(false);
    setCompleted(false);
    setSeconds(240);
    setUrgeStep(0);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const startUrge = () => {
    setUrgeActive(true);
    setCompleted(false);
    setSeconds(240);
    setUrgeStep(0);
  };

  const completeUrge = async () => {
    setCompleted(true);
    if (timerRef.current) clearInterval(timerRef.current);
    try {
      await apiClient.request<any>('/interventions/urge-surf/start', {
        method: 'POST',
        body: JSON.stringify({ craving_before: 8 }),
      });
    } catch {}
  };

  const urgeSteps = [
    "Notice where in your body you feel the craving. Place your attention there gently.",
    "Picture the craving as an ocean wave. Watch it rising — it will peak soon.",
    "Breathe slowly: inhale for 4 seconds, exhale for 6 seconds. Ride the wave.",
    "The wave is subsiding. You rode through it. The craving is passing.",
  ];

  const fmtTime = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  return (
    <>
      <button type="button" onClick={triggerSOS}
        aria-label="I'm Struggling — Launch immediate zero-typing crisis support"
        className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-sm py-3.5 px-4 rounded-2xl shadow-xl shadow-red-600/20 flex items-center justify-center gap-2 transition transform active:scale-95 border border-red-400/20 min-h-[48px]">
        <AlertCircle className="w-5 h-5 animate-pulse" />
        I'm Struggling
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-[60] bg-slate-950/95 backdrop-blur-xl flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-red-500/30 rounded-3xl p-5 w-full max-w-sm space-y-4 text-white shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button onClick={close} className="absolute top-3 right-3 text-slate-500 hover:text-white p-1">
              <X className="w-5 h-5" />
            </button>

            {!urgeActive ? (
              <>
                <div className="flex items-center gap-2 text-red-400">
                  <AlertCircle className="w-6 h-6 animate-pulse" />
                  <div>
                    <h2 className="text-lg font-black text-white">Crisis Support</h2>
                    <p className="text-[11px] text-red-400 font-bold">Zero-typing emergency response</p>
                  </div>
                </div>

                {loading && <div className="text-xs text-slate-400 animate-pulse py-4 text-center">Connecting to crisis support...</div>}

                {error && (
                  <div className="space-y-3">
                    <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-3 text-xs text-red-400">{error}</div>
                    <a href="tel:988" className="w-full bg-red-600 text-white font-bold py-3.5 px-4 rounded-xl flex items-center justify-center gap-2 shadow-lg">
                      <Phone className="w-5 h-5" /> Call 988 Crisis Lifeline Now
                    </a>
                    <a href="https://988lifeline.org/" target="_blank" rel="noopener noreferrer"
                      className="w-full bg-slate-800 text-sky-400 font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 text-xs">
                      <ExternalLink className="w-4 h-4" /> Visit 988lifeline.org
                    </a>
                  </div>
                )}

                {sosData && (
                  <div className="space-y-3">
                    <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-3 text-sm text-slate-200">
                      {sosData.response_text}
                    </div>

                    {sosData.crisis_line && (
                      <a href={`tel:${sosData.crisis_line.phone}`}
                        className="w-full bg-red-600 hover:bg-red-500 text-white font-bold py-3.5 px-4 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-red-600/20">
                        <Phone className="w-5 h-5" />
                        Call {sosData.crisis_line.name} ({sosData.crisis_line.phone})
                      </a>
                    )}

                    {sosData.emergency_contacts?.map((c: any, i: number) => (
                      <a key={i} href={`tel:${c.phone}`}
                        className="w-full bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 border border-slate-700">
                        <HeartHandshake className="w-5 h-5 text-sky-400" />
                        Call {c.name} ({c.relationship})
                      </a>
                    ))}

                    <button onClick={startUrge}
                      className="w-full bg-gradient-to-r from-sky-600 to-indigo-600 text-white font-bold py-3.5 px-4 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-sky-600/20">
                      <Wind className="w-5 h-5" /> Start 4-Minute Urge Surf
                    </button>

                    <a href="https://988lifeline.org/" target="_blank" rel="noopener noreferrer"
                      className="block text-center text-xs text-sky-400 hover:text-sky-300 underline underline-offset-2">
                      Visit 988lifeline.org for more resources ↗
                    </a>
                  </div>
                )}
              </>
            ) : (
              <div className="space-y-4 text-center">
                <div className="flex items-center justify-center gap-2 text-sky-400">
                  <Wind className="w-6 h-6" />
                  <h2 className="text-lg font-black text-white">Urge Surfing</h2>
                </div>

                {!completed ? (
                  <>
                    <div className="bg-slate-800/80 rounded-2xl p-5 border border-sky-500/20 space-y-3">
                      <div className="text-3xl font-black text-sky-400 font-mono">{fmtTime(seconds)}</div>
                      <div className="flex gap-1 justify-center">
                        {[0,1,2,3].map(s => (
                          <div key={s} className={`w-2 h-2 rounded-full ${s <= urgeStep ? 'bg-sky-400' : 'bg-slate-700'}`} />
                        ))}
                      </div>
                      <p className="text-sm text-slate-200">{urgeSteps[urgeStep]}</p>
                    </div>

                    <div className="space-y-1">
                      <label className="text-[11px] text-slate-400">Craving level now: {cravingAfter}/10</label>
                      <input type="range" min="0" max="10" value={cravingAfter}
                        onChange={e => setCravingAfter(parseInt(e.target.value))} className="w-full accent-sky-500" />
                    </div>

                    <button onClick={completeUrge}
                      className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl shadow-lg">
                      Complete Session
                    </button>
                  </>
                ) : (
                  <div className="space-y-3 py-2">
                    <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 text-emerald-400 text-sm">
                      You completed the urge surfing session. Your craving is now at {cravingAfter}/10.
                    </div>
                    <button onClick={close}
                      className="w-full bg-slate-800 text-white font-bold py-3 rounded-xl">
                      Return to App
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};
