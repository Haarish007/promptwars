import React, { useState } from 'react';
import { AlertCircle, Phone, HeartHandshake, Wind, X } from 'lucide-react';
import { apiClient } from '../../lib/api-client';

interface OneTapAction {
  id: string;
  label: string;
  action_type: string;
  target: string;
}

interface SOSResponse {
  response_text: string;
  crisis_line: { name: string; phone: string; description: string };
  emergency_contacts: Array<{ name: string; relationship: string; phone: string; is_sponsor: boolean }>;
  one_tap_actions: OneTapAction[];
  timestamp: string;
}

export const SOSButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sosData, setSosData] = useState<SOSResponse | null>(null);
  const [urgeActive, setUrgeActive] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(240);
  const [cravingBefore, setCravingBefore] = useState(8);
  const [cravingAfter, setCravingAfter] = useState(3);
  const [urgeStep, setUrgeStep] = useState(1);
  const [interventionId, setInterventionId] = useState<string | null>(null);
  const [urgeDoneMessage, setUrgeDoneMessage] = useState<string | null>(null);

  const handleTriggerSOS = async () => {
    setIsOpen(true);
    setLoading(true);
    try {
      const res = await apiClient.request<SOSResponse>('/sos', {
        method: 'POST',
        body: JSON.stringify({ region: 'US', voice_triggered: false }),
      });
      setSosData(res);
    } catch {
      // Fallback default crisis response
      setSosData({
        response_text: "We are here with you right now. Your safety and well-being come first. Please connect with human support.",
        crisis_line: { name: "988 Lifeline", phone: "988", description: "Free, confidential 24/7 support" },
        emergency_contacts: [{ name: "David (Guardian)", relationship: "Guardian", phone: "+15550199", is_sponsor: false }],
        one_tap_actions: [
          { id: "call_988", label: "Call 988 Crisis Line", action_type: "call", target: "tel:988" },
          { id: "start_urge_surf", label: "Start 4-Minute Urge Surf", action_type: "urge_surf", target: "/interventions" }
        ],
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const startUrgeSurfSession = async () => {
    setUrgeActive(true);
    setUrgeDoneMessage(null);
    try {
      const res = await apiClient.request<any>('/interventions/urge-surf/start', {
        method: 'POST',
        body: JSON.stringify({ craving_before: cravingBefore })
      });
      setInterventionId(res.intervention_id);
    } catch {
      setInterventionId("demo-id");
    }
  };

  const completeUrgeSurfSession = async () => {
    try {
      const res = await apiClient.request<any>(`/interventions/urge-surf/${interventionId || 'demo'}/complete`, {
        method: 'POST',
        body: JSON.stringify({ craving_after: cravingAfter, outcome: "completed" })
      });
      setUrgeDoneMessage(res.message || "Urge surfing completed!");
    } catch {
      setUrgeDoneMessage(`Great work! Your craving dropped by ${Math.max(0, cravingBefore - cravingAfter)} points.`);
    }
  };

  return (
    <>
      <button
        type="button"
        aria-label="I'm Struggling — Launch immediate zero-typing crisis support"
        className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-lg py-4 px-6 rounded-2xl shadow-xl shadow-red-600/30 flex items-center justify-center gap-3 transition-all transform active:scale-95 border border-red-400/30 min-h-[56px]"
        onClick={handleTriggerSOS}
      >
        <AlertCircle className="w-6 h-6 animate-pulse" />
        <span>I'm Struggling</span>
      </button>

      {/* SOS Crisis Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-red-500/30 rounded-3xl p-6 w-full max-w-md space-y-5 text-white shadow-2xl relative">
            <button
              onClick={() => { setIsOpen(false); setUrgeActive(false); }}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-6 h-6" />
            </button>

            {!urgeActive ? (
              <>
                <div className="flex items-center gap-3 text-red-400">
                  <AlertCircle className="w-8 h-8 animate-pulse" />
                  <div>
                    <h2 className="text-xl font-extrabold tracking-tight text-white">Crisis Support Active</h2>
                    <p className="text-xs text-red-400 font-medium">Zero-typing emergency response</p>
                  </div>
                </div>

                <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 text-sm text-slate-200">
                  {loading ? (
                    <p className="animate-pulse">Resolving immediate support & emergency contacts...</p>
                  ) : (
                    <p>{sosData?.response_text}</p>
                  )}
                </div>

                {/* One-Tap Action Buttons */}
                <div className="space-y-3 pt-2">
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">One-Tap Immediate Actions</h3>

                  <a
                    href={`tel:${sosData?.crisis_line.phone || '988'}`}
                    className="w-full bg-red-600 hover:bg-red-500 text-white font-bold py-3.5 px-4 rounded-xl flex items-center justify-center gap-3 shadow-lg shadow-red-600/20"
                  >
                    <Phone className="w-5 h-5" />
                    <span>Call {sosData?.crisis_line.name || '988 Lifeline'} ({sosData?.crisis_line.phone || '988'})</span>
                  </a>

                  {sosData?.emergency_contacts.map((contact, idx) => (
                    <a
                      key={idx}
                      href={`tel:${contact.phone}`}
                      className="w-full bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold py-3.5 px-4 rounded-xl flex items-center justify-center gap-3 border border-slate-700"
                    >
                      <HeartHandshake className="w-5 h-5 text-sky-400" />
                      <span>Call {contact.name} ({contact.relationship})</span>
                    </a>
                  ))}

                  <button
                    onClick={startUrgeSurfSession}
                    className="w-full bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-bold py-3.5 px-4 rounded-xl flex items-center justify-center gap-3 shadow-lg shadow-sky-600/20"
                  >
                    <Wind className="w-5 h-5" />
                    <span>Start 4-Minute Guided Urge Surf</span>
                  </button>
                </div>
              </>
            ) : (
              /* Urge Surfing Wave Session */
              <div className="space-y-5 text-center">
                <div className="flex items-center justify-center gap-2 text-sky-400">
                  <Wind className="w-7 h-7 animate-spin" />
                  <h2 className="text-xl font-bold text-white">4-Minute Urge Surfing</h2>
                </div>

                {!urgeDoneMessage ? (
                  <>
                    <div className="p-6 bg-slate-800/80 rounded-2xl border border-sky-500/30 space-y-3">
                      <div className="text-3xl font-extrabold text-sky-400 font-mono">03:59</div>
                      <p className="text-sm font-medium text-slate-200">
                        {urgeStep === 1 && "Step 1: Notice where in your body you feel the craving."}
                        {urgeStep === 2 && "Step 2: Picture the craving as an ocean wave rising up."}
                        {urgeStep === 3 && "Step 3: Inhale for 4 seconds, exhale for 6 seconds."}
                        {urgeStep === 4 && "Step 4: Watch the wave reach its peak and naturally subside."}
                      </p>
                    </div>

                    <div className="flex justify-center gap-2">
                      {[1, 2, 3, 4].map(s => (
                        <button
                          key={s}
                          onClick={() => setUrgeStep(s)}
                          className={`w-8 h-8 rounded-full text-xs font-bold ${urgeStep === s ? 'bg-sky-500 text-slate-950' : 'bg-slate-800 text-slate-400'}`}
                        >
                          {s}
                        </button>
                      ))}
                    </div>

                    <div className="space-y-2 pt-2">
                      <label className="text-xs text-slate-400 block">Craving after session (0-10):</label>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        value={cravingAfter}
                        onChange={(e) => setCravingAfter(parseInt(e.target.value))}
                        className="w-full accent-sky-500"
                      />
                      <span className="text-sm font-bold text-sky-400">{cravingAfter} / 10</span>
                    </div>

                    <button
                      onClick={completeUrgeSurfSession}
                      className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl shadow-lg shadow-emerald-600/20"
                    >
                      Complete Session
                    </button>
                  </>
                ) : (
                  <div className="space-y-4 py-4">
                    <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-emerald-400 text-sm font-medium">
                      {urgeDoneMessage}
                    </div>
                    <button
                      onClick={() => setIsOpen(false)}
                      className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-xl"
                    >
                      Return to Dashboard
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
