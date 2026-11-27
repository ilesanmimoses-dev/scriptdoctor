import { useState, useRef, useEffect } from 'react';

const SAMPLE_SCRIPT = `INT. KITCHEN - NIGHT\n\nA dark room. A candle burns on the table.\n\nJOHN\nHello, MARY.\n\nMARY\nHi, JOHN.\n\nFADE OUT.`;

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [authError, setAuthError] = useState(null);
  
  const [history, setHistory] = useState([]);
  const [adminStats, setAdminStats] = useState(null);
  const [adminReports, setAdminReports] = useState(null);

  const [script, setScript] = useState(SAMPLE_SCRIPT);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiResult, setAiResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const fileInputRef = useRef(null);

  const [activeTab, setActiveTab] = useState(null); 
  const [scheduleDays, setScheduleDays] = useState(5);
  const [generatedSchedule, setGeneratedSchedule] = useState(null);
  
  const [explanationScenes, setExplanationScenes] = useState(null);
  const [currentSceneIndex, setCurrentSceneIndex] = useState(0);

  const [coverageResult, setCoverageResult] = useState(null);
  const [coverageLoading, setCoverageLoading] = useState(false);

  const [showReportModal, setShowReportModal] = useState(false);
  const [reportMessage, setReportMessage] = useState("");
  const [reportStatus, setReportStatus] = useState(null);

  const [draftA, setDraftA] = useState("");
  const [draftB, setDraftB] = useState("");
  const [compareResult, setCompareResult] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    fetch('/history', { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(data => { if (Array.isArray(data)) setHistory(data); })
      .catch(err => console.log("Could not load history"));
  }, [token, result]);

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthError(null);
    const endpoint = isSignup ? '/signup' : '/login';
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Authentication failed');
      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleLogout = () => {
    setToken(null); localStorage.removeItem('token'); setResult(null); setAiResult(null); setHistory([]); setAdminStats(null); setActiveTab(null); setAdminReports(null);
  };

  const handleAnalyze = async () => {
    if (!script.trim()) return;
    setLoading(true); setError(null); setResult(null); setAiResult(null); setActiveTab('analyze');
    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ script })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed');
      setResult(data);
      fetch('/history', { headers: { 'Authorization': `Bearer ${token}` } }).then(res => res.json()).then(data => setHistory(data));
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  };

  const handleGenerateSchedule = async () => {
    if (!script.trim()) return;
    setLoading(true); setError(null); setGeneratedSchedule(null); setActiveTab('schedule');
    try {
      const response = await fetch(`/schedule?days=${scheduleDays}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ script })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed');
      setGeneratedSchedule(data.schedule);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  };

  const handleExplainScript = async () => {
    if (!script.trim()) return;
    setLoading(true); setError(null); setExplanationScenes(null); setCurrentSceneIndex(0); setActiveTab('explain');
    try {
      const response = await fetch('/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ script })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed');
      setExplanationScenes(data.scenes);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  };

  const handleCoverageReport = async () => {
    if (!script.trim()) return;
    setCoverageLoading(true); setCoverageResult(null); setActiveTab('coverage');
    try {
      const response = await fetch('/coverage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ script })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed');
      setCoverageResult(data.coverage);
    } catch (err) { setError(err.message); } finally { setCoverageLoading(false); }
  };

  const handleCompareDrafts = async () => {
    if (!draftA.trim() || !draftB.trim()) {
      setError("Please paste a script in both Draft A and Draft B.");
      return;
    }
    setCompareLoading(true); setError(null); setCompareResult(null); setActiveTab('compare');
    try {
      const response = await fetch('/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ draft_a: draftA, draft_b: draftB })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to compare');
      setCompareResult(data);
    } catch (err) { setError(err.message); } finally { setCompareLoading(false); }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setLoading(true); setError(null); setResult(null); setActiveTab('analyze');
    const formData = new FormData(); formData.append("file", file);
    try {
      const response = await fetch('/upload', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` }, body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed');
      setResult(data);
    } catch (err) { setError(err.message); } finally { setLoading(false); if (fileInputRef.current) fileInputRef.current.value = ""; }
  };

  const handleAiAnalyze = async () => {
    setAiLoading(true); setAiResult(null);
    try {
      const response = await fetch('/ai-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ script })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'AI failed');
      setAiResult(data.ai_analysis);
    } catch (err) { setAiResult("Error: " + err.message); } finally { setAiLoading(false); }
  };

  const handleAdminFetch = async () => {
    try {
      const res = await fetch('/admin-stats', { headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setAdminStats(data);
      setAdminReports(null);
    } catch (err) { alert(err.message); }
  };

  const handleAdminReports = async () => {
    try {
      const res = await fetch('/admin-reports', { headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setAdminReports(data);
    } catch (err) { alert(err.message); }
  };

  const handleSubmitReport = async (e) => {
    e.preventDefault();
    setReportStatus("Sending...");
    try {
      const response = await fetch('/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ message: reportMessage })
      });
      if (!response.ok) throw new Error("Failed to send");
      setReportStatus("Sent successfully! Thank you.");
      setReportMessage("");
      setTimeout(() => { setShowReportModal(false); setReportStatus(null); }, 2000);
    } catch (err) {
      setReportStatus("Error: " + err.message);
    }
  };

  const getTierColor = (tier) => {
    switch(tier) { case 'POOR': return 'text-red-600'; case 'AVERAGE': return 'text-yellow-600'; case 'GOOD': return 'text-cyan-600'; case 'EXCELLENT': return 'text-green-600'; case 'PERFECT': return 'text-emerald-700'; default: return 'text-gray-800'; }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white font-sans">
        <div className="bg-gray-800 p-8 rounded-lg shadow-2xl w-full max-w-md border border-gray-700">
          <h1 className="text-3xl font-bold text-center mb-2 text-yellow-500">ScriptScope</h1>
          <p className="text-center text-gray-400 mb-6">Your script, read like a pro.</p>
          {authError && <div className="bg-red-500/20 text-red-300 p-3 rounded mb-4 text-sm">{authError}</div>}
          <form onSubmit={handleAuth} className="space-y-4">
            <div><label className="block text-sm font-semibold mb-1">Email</label><input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full p-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-yellow-500 text-white" /></div>
            <div><label className="block text-sm font-semibold mb-1">Password</label><input type="password" value={password} onChange={e => setPassword(e.target.value)} required className="w-full p-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-yellow-500 text-white" /></div>
            <button type="submit" className="w-full bg-yellow-600 hover:bg-yellow-500 text-black font-bold py-3 rounded transition-colors mt-2">{isSignup ? 'Create Account' : 'Log In'}</button>
          </form>
          <div className="text-center mt-6 text-sm text-gray-400">{isSignup ? "Already have an account?" : "Don't have an account?"}<button onClick={() => { setIsSignup(!isSignup); setAuthError(null); }} className="ml-2 text-yellow-500 hover:underline font-semibold">{isSignup ? 'Log In' : 'Sign Up'}</button></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 font-sans text-gray-900 bg-gray-50 min-h-screen flex gap-8 relative">
      
      {showReportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Send a Report</h2>
            <p className="text-gray-600 mb-4 text-sm">Found a bug? Have a suggestion? Let us know!</p>
            <form onSubmit={handleSubmitReport}>
              <textarea value={reportMessage} onChange={(e) => setReportMessage(e.target.value)} required className="w-full h-32 p-3 border rounded-lg mb-4" placeholder="Describe your issue or suggestion here..." />
              {reportStatus && <p className="text-sm text-blue-600 mb-2">{reportStatus}</p>}
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setShowReportModal(false)} className="px-4 py-2 bg-gray-200 rounded">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Send Report</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="w-64 flex-shrink-0 bg-white p-4 rounded-lg shadow-sm border border-gray-200 h-fit flex flex-col gap-4">
        <div>
          <h2 className="text-lg font-bold mb-4 text-gray-800">Your History</h2>
          {history.length === 0 ? <p className="text-sm text-gray-500">No scripts analyzed yet.</p> : (
            <ul className="space-y-2 max-h-64 overflow-y-auto">
              {history.map((item) => (
                <li key={item.id} className="p-2 bg-gray-50 rounded border border-gray-100 text-sm hover:bg-gray-100 cursor-pointer">
                  <div className="font-semibold text-gray-800">Script #{item.id}</div>
                  <div className="flex justify-between text-gray-500 mt-1"><span>Score: {item.score}</span><span className={`font-bold ${getTierColor(item.tier)}`}>{item.tier}</span></div>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <button onClick={() => setShowReportModal(true)} className="mt-4 w-full py-2 bg-gray-100 hover:bg-gray-200 border border-gray-300 text-gray-700 font-semibold rounded text-sm transition-colors">
          ⚠️ Report a Problem
        </button>
      </div>

      <div className="flex-1">
        <header className="mb-8 flex justify-between items-center">
          <div><h1 className="text-3xl font-bold mb-1">ScriptScope</h1><p className="text-gray-500">Welcome back! Paste a script to begin.</p></div>
          <div className="flex gap-3">
            <button onClick={handleAdminFetch} className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded transition-colors text-sm">Admin Panel</button>
            <button onClick={handleLogout} className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded transition-colors text-sm">Log Out</button>
          </div>
        </header>

        {adminStats && (
          <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg mb-8 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-yellow-800">Admin Dashboard</h2>
              <button onClick={() => { setAdminStats(null); setAdminReports(null); }} className="text-gray-500 hover:text-black font-bold">✕</button>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-white p-4 rounded shadow border border-gray-100"><p className="text-gray-500 text-sm">Total Users</p><p className="text-2xl font-bold text-gray-800">{adminStats.total_users}</p></div>
              <div className="bg-white p-4 rounded shadow border border-gray-100"><p className="text-gray-500 text-sm">Scripts Analyzed</p><p className="text-2xl font-bold text-gray-800">{adminStats.total_scripts}</p></div>
            </div>

            <button onClick={handleAdminReports} className="px-4 py-2 bg-yellow-600 text-white rounded text-sm font-semibold mb-4">View User Reports</button>

            {adminReports && (
              <div className="bg-white rounded border border-yellow-100 p-4 max-h-64 overflow-y-auto">
                <h3 className="font-bold text-gray-800 mb-2">User Reports Inbox</h3>
                {adminReports.length === 0 ? <p className="text-sm text-gray-500">No reports yet.</p> : (
                  <ul className="space-y-2">
                    {adminReports.map((r) => (
                      <li key={r.id} className="bg-gray-50 p-3 rounded border border-gray-200 text-sm">
                        <div className="flex justify-between font-semibold text-gray-700 mb-1">
                          <span>{r.email}</span>
                          <span className="text-xs bg-gray-200 px-2 py-1 rounded">{r.status}</span>
                        </div>
                        <p className="text-gray-600">{r.message}</p>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}

        <div className="mb-4">
          <textarea value={script} onChange={(e) => setScript(e.target.value)} className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y" />
        </div>

        <div className="flex flex-wrap gap-4 mb-8">
          <button onClick={handleAnalyze} disabled={loading || coverageLoading} className="px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors flex-1 min-w-[150px]">Analyze Script</button>
          <button onClick={handleGenerateSchedule} disabled={loading || coverageLoading} className="px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors flex-1 min-w-[150px]">Prepare Schedule</button>
          <button onClick={handleExplainScript} disabled={loading || coverageLoading} className="px-4 py-3 bg-teal-600 hover:bg-teal-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors flex-1 min-w-[150px]">Explain Script</button>
          <button onClick={handleCoverageReport} disabled={loading || coverageLoading} className="px-4 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors flex-1 min-w-[150px]">Coverage Report</button>
          <button onClick={() => { setActiveTab('compare'); setCompareResult(null); }} className="px-4 py-3 bg-pink-600 hover:bg-pink-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors flex-1 min-w-[150px]">Compare Drafts</button>
        </div>

        <div className="flex gap-4 mb-8">
          <input type="file" accept=".pdf,.docx,.txt" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />
          <button onClick={() => fileInputRef.current.click()} disabled={loading} className="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg shadow transition-colors text-sm">Or Upload File (PDF/Word/TXT)</button>
        </div>

        {error && <div className="p-4 mb-6 bg-red-50 border border-red-200 text-red-700 rounded-lg"><strong>Error:</strong> {error}</div>}

        {activeTab === 'analyze' && result && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-indigo-200 border-l-4 border-l-indigo-500 mb-8">
              <h2 className="text-xl font-bold mb-2 text-indigo-900">Want deeper feedback?</h2>
              <button onClick={handleAiAnalyze} disabled={aiLoading} className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold rounded shadow transition-colors">{aiLoading ? 'AI is reading...' : 'Get AI Analysis'}</button>
              {aiResult && <div className="mt-6 p-5 bg-indigo-50 border border-indigo-100 rounded text-gray-800 text-sm whitespace-pre-wrap font-sans">{aiResult}</div>}
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Score</h2>
              <p className={`text-4xl font-extrabold ${getTierColor(result.tier)} mb-2`}>{result.score} / 100</p>
              <p className="text-gray-700 mb-1"><strong>Rating:</strong> {result.tier}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Content Rating & Mood</h2>
              <p className="text-gray-700 mb-2"><strong>Age Rating:</strong> {result.content_rating}</p>
              <p className="text-gray-700"><strong>Mood:</strong> {result.emotion_balance.mood}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Errors ({result.errors.length})</h2>
              <ul className="space-y-4">
                {result.errors.map((err, i) => (<li key={i} className="bg-gray-50 p-3 rounded border border-gray-100"><div className="mb-1"><span className="mr-2 font-bold text-red-600">[{err.severity}]</span><span>{err.message}</span></div><div className="text-sm text-gray-500"><strong>Fix:</strong> {err.fix}</div></li>))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'schedule' && (
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold mb-4">Prepare Schedule</h2>
            <div className="flex justify-center items-center gap-4 mb-8">
              <input type="number" value={scheduleDays} onChange={(e) => setScheduleDays(Number(e.target.value))} className="w-24 p-3 border rounded text-center text-xl font-bold" min="1" />
              <span className="text-lg text-gray-700">Days</span>
            </div>
            <button onClick={handleGenerateSchedule} className="w-full px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg shadow-md transition-colors">Generate {scheduleDays}-Day Schedule</button>
            {generatedSchedule && (
              <div className="mt-8 border-t pt-6">
                <div className="space-y-4">
                  {generatedSchedule.map((day, i) => (
                    <div key={i} className="bg-purple-50 p-4 rounded border border-purple-100">
                      <h4 className="font-bold text-purple-900 mb-2">Day {day.day}</h4>
                      <ul className="list-disc pl-5 text-gray-700">{day.scenes.map((s, j) => <li key={j}>{s}</li>)}</ul>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'explain' && explanationScenes && explanationScenes.length > 0 && (
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold mb-4 text-teal-800">Scene-by-Scene Explanation</h2>
            <div className="bg-teal-50 border border-teal-100 p-6 rounded-lg mb-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-xl text-teal-900">Scene {explanationScenes[currentSceneIndex].scene_number}</h3>
                <span className="text-sm font-semibold text-teal-600 bg-teal-100 px-3 py-1 rounded-full">{currentSceneIndex + 1} of {explanationScenes.length}</span>
              </div>
              <p className="text-sm text-teal-700 mb-4">{explanationScenes[currentSceneIndex].location}</p>
              <div className="bg-white p-4 rounded mb-4 shadow-sm">
                <p className="text-gray-800 mb-2"><strong>Who is in it:</strong> {explanationScenes[currentSceneIndex].who_is_in_it}</p>
                <p className="text-gray-800"><strong>What happens:</strong> {explanationScenes[currentSceneIndex].what_happens}</p>
              </div>
              <div className="flex justify-between mt-6">
                <button onClick={() => setCurrentSceneIndex(currentSceneIndex - 1)} disabled={currentSceneIndex === 0} className="px-6 py-2 bg-teal-700 hover:bg-teal-800 text-white font-semibold rounded shadow disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors">← Previous Scene</button>
                <button onClick={() => setCurrentSceneIndex(currentSceneIndex + 1)} disabled={currentSceneIndex === explanationScenes.length - 1} className="px-6 py-2 bg-teal-700 hover:bg-teal-800 text-white font-semibold rounded shadow disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors">Next Scene →</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'coverage' && (
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold mb-4 text-yellow-800">Professional Coverage Report</h2>
            {coverageLoading ? (
              <p className="text-gray-500 italic">The AI studio reader is analyzing your script...</p>
            ) : coverageResult ? (
              <div className="bg-yellow-50 border border-yellow-100 p-6 rounded-lg whitespace-pre-wrap font-sans text-gray-800">
                {coverageResult}
              </div>
            ) : (
              <p className="text-gray-500">Click the button to generate your report.</p>
            )}
          </div>
        )}

        {activeTab === 'compare' && (
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold mb-4 text-pink-800">Compare Drafts</h2>
            <p className="text-gray-600 mb-6">Paste two versions of your script to see which one scores higher.</p>
            
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block font-bold mb-2">Draft A (Old)</label>
                <textarea 
                  value={draftA} 
                  onChange={(e) => setDraftA(e.target.value)}
                  className="w-full h-48 p-3 border border-gray-300 rounded-lg font-mono text-sm"
                  placeholder="Paste older version here..."
                />
              </div>
              <div>
                <label className="block font-bold mb-2">Draft B (New)</label>
                <textarea 
                  value={draftB} 
                  onChange={(e) => setDraftB(e.target.value)}
                  className="w-full h-48 p-3 border border-gray-300 rounded-lg font-mono text-sm"
                  placeholder="Paste newer version here..."
                />
              </div>
            </div>

            <button 
              onClick={handleCompareDrafts} 
              disabled={compareLoading}
              className="w-full px-8 py-3 bg-pink-600 hover:bg-pink-700 text-white font-bold rounded-lg shadow-md transition-colors mb-6"
            >
              {compareLoading ? 'Comparing...' : 'Compare Drafts'}
            </button>

            {compareResult && (
              <div className="bg-pink-50 border border-pink-200 p-6 rounded-lg text-center">
                <h3 className="text-2xl font-bold text-pink-900 mb-2">Winner: {compareResult.winner}</h3>
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="bg-white p-4 rounded shadow border border-gray-100">
                    <p className="text-gray-500">Draft A</p>
                    <p className="text-3xl font-bold">{compareResult.draft_a.score} / 100</p>
                    <p className="text-gray-700 font-semibold">{compareResult.draft_a.tier}</p>
                  </div>
                  <div className="bg-white p-4 rounded shadow border border-gray-100">
                    <p className="text-gray-500">Draft B</p>
                    <p className="text-3xl font-bold">{compareResult.draft_b.score} / 100</p>
                    <p className="text-gray-700 font-semibold">{compareResult.draft_b.tier}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
