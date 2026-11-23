import { useState, useRef, useEffect } from 'react';

const SAMPLE_SCRIPT = `INT. KITCHEN - NIGHT\n\nA dark room. A candle burns on the table.\n\nJOHN\nHello, MARY.\n\nMARY\nHi, JOHN.\n\nFADE OUT.`;

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [authError, setAuthError] = useState(null);
  
  const [history, setHistory] = useState([]);

  const [script, setScript] = useState(SAMPLE_SCRIPT);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiResult, setAiResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const fileInputRef = useRef(null);

  // Fetch history when logged in
  useEffect(() => {
    if (!token) return;
    fetch('/history', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setHistory(data);
      })
      .catch(err => console.log("Could not load history"));
  }, [token, result]); // Reload when token changes or a new result is added

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
    setToken(null);
    localStorage.removeItem('token');
    setResult(null);
    setAiResult(null);
    setHistory([]);
  };

   const handleAnalyze = async () => {
    if (!script.trim()) return;
    setLoading(true); setError(null); setResult(null); setAiResult(null);
    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ script })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to analyze');
      setResult(data);
      
      // THIS IS THE NEW PART: Reload the history from the database
      const histRes = await fetch('/history', { headers: { 'Authorization': `Bearer ${token}` } });
      const histData = await histRes.json();
      if (Array.isArray(histData)) setHistory(histData);

    } catch (err) { 
      setError(err.message); 
    } finally { 
      setLoading(false); 
    }
  };
  

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setLoading(true); setError(null); setResult(null); setAiResult(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await fetch('/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to upload');
      setResult(data);
    } catch (err) { setError(err.message); } 
    finally { setLoading(false); if (fileInputRef.current) fileInputRef.current.value = ""; }
  };

  const handleAiAnalyze = async () => {
    setAiLoading(true); setAiResult(null);
    try {
      const response = await fetch('/ai-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ script })
      });
      const text = await response.text();
      const data = JSON.parse(text);
      if (!response.ok) throw new Error(data.detail || 'AI failed');
      setAiResult(data.ai_analysis);
    } catch (err) { setAiResult("Error: " + err.message); } 
    finally { setAiLoading(false); }
  };

  const handleDownload = () => {
    if (!result) return;
    let text = `===============================================\n`;
    text += `               SCRIPTSCOPE REPORT               \n`;
    text += `===============================================\n\n`;
    text += `Score: ${result.score} / 100\nRating: ${result.tier}\nLanguage: ${result.language}\n`;
    text += `Age Rating: ${result.content_rating}\nMood: ${result.emotion_balance.mood}\n\n`;
    text += `--- Genres ---\n`;
    Object.entries(result.genres).forEach(([genre, pct]) => { text += `${genre}: ${pct.toFixed(1)}%\n`; });
    text += `\n--- Errors (${result.errors.length}) ---\n`;
    result.errors.forEach(err => { text += `[${err.severity}] ${err.message}\n  Fix: ${err.fix}\n\n`; });
    text += `--- In plain words ---\n`;
    result.explanation.forEach(s => { text += `- ${s}\n`; });
    if (aiResult && !aiResult.startsWith("Error")) { text += `\n--- AI Analysis ---\n${aiResult}\n`; }
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `ScriptScope_Report_${new Date().getTime()}.txt`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
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
            <div>
              <label className="block text-sm font-semibold mb-1">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full p-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-yellow-500 text-white" placeholder="writer@example.com" />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required className="w-full p-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-yellow-500 text-white" placeholder="••••••••" />
            </div>
            <button type="submit" className="w-full bg-yellow-600 hover:bg-yellow-500 text-black font-bold py-3 rounded transition-colors mt-2">
              {isSignup ? 'Create Account' : 'Log In'}
            </button>
          </form>
          
          <div className="text-center mt-6 text-sm text-gray-400">
            {isSignup ? "Already have an account?" : "Don't have an account?"}
            <button onClick={() => { setIsSignup(!isSignup); setAuthError(null); }} className="ml-2 text-yellow-500 hover:underline font-semibold">
              {isSignup ? 'Log In' : 'Sign Up'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 font-sans text-gray-900 bg-gray-50 min-h-screen flex gap-8">
      
      {/* SIDEBAR (History) */}
      <div className="w-64 flex-shrink-0 bg-white p-4 rounded-lg shadow-sm border border-gray-200 h-fit">
        <h2 className="text-lg font-bold mb-4 text-gray-800">Your History</h2>
        {history.length === 0 ? (
          <p className="text-sm text-gray-500">No scripts analyzed yet.</p>
        ) : (
          <ul className="space-y-2 max-h-96 overflow-y-auto">
            {history.map((item) => (
              <li key={item.id} className="p-2 bg-gray-50 rounded border border-gray-100 text-sm hover:bg-gray-100 cursor-pointer">
                <div className="font-semibold text-gray-800">Script #{item.id}</div>
                <div className="flex justify-between text-gray-500 mt-1">
                  <span>Score: {item.score}</span>
                  <span className={`font-bold ${getTierColor(item.tier)}`}>{item.tier}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-1">ScriptScope</h1>
            <p className="text-gray-500">Welcome back! Paste a script to begin.</p>
          </div>
          <button onClick={handleLogout} className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded transition-colors text-sm">Log Out</button>
        </header>

        <div className="mb-4">
          <textarea value={script} onChange={(e) => setScript(e.target.value)} className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y" placeholder="Paste your script here..." />
        </div>

        <div className="flex gap-4 mb-8">
          <button onClick={handleAnalyze} disabled={loading || !script.trim()} className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors">
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
          <input type="file" accept=".pdf,.docx,.txt" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />
          <button onClick={() => fileInputRef.current.click()} disabled={loading} className="px-8 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors">
            Upload File (PDF/Word/TXT)
          </button>
        </div>

        {error && <div className="p-4 mb-6 bg-red-50 border border-red-200 text-red-700 rounded-lg"><strong>Error:</strong> {error}</div>}

        {result && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-indigo-200 border-l-4 border-l-indigo-500 mb-8">
              <h2 className="text-xl font-bold mb-2 text-indigo-900">Want deeper feedback?</h2>
              <button onClick={handleAiAnalyze} disabled={aiLoading} className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold rounded shadow transition-colors">
                {aiLoading ? 'AI is reading...' : 'Get AI Analysis'}
              </button>
              {aiResult && <div className="mt-6 p-5 bg-indigo-50 border border-indigo-100 rounded text-gray-800 text-sm whitespace-pre-wrap font-sans">{aiResult}</div>}
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Score</h2>
              <p className={`text-4xl font-extrabold ${getTierColor(result.tier)} mb-2`}>{result.score} / 100</p>
              <p className="text-gray-700 mb-1"><strong>Rating:</strong> {result.tier}</p>
              <p className="text-gray-700 mb-4"><strong>Language:</strong> {result.language}</p>
              <button onClick={handleDownload} className="px-4 py-2 bg-gray-800 hover:bg-gray-900 text-white text-sm font-semibold rounded shadow">⬇ Download Report (.txt)</button>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Content Rating & Mood</h2>
              <p className="text-gray-700 mb-2"><strong>Age Rating:</strong> {result.content_rating}</p>
              <p className="text-gray-700"><strong>Mood:</strong> {result.emotion_balance.mood}</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Budget & Audience</h2>
              <p className="text-gray-700 mb-2"><strong>Estimated Budget:</strong> {result.budget_and_audience.budget}</p>
              <p className="text-gray-700"><strong>Target Audience:</strong> {result.budget_and_audience.audience}</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Genres</h2>
              <ul className="space-y-1 text-gray-700">
                {Object.entries(result.genres).map(([genre, pct]) => (
                  <li key={genre} className="flex justify-between border-b border-gray-100 pb-1"><span>{genre}</span><span className="font-mono">{pct.toFixed(1)}%</span></li>
                ))}
              </ul>
            </div>

            {result.genre_by_section && (
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h2 className="text-xl font-bold mb-4">Genre by Section</h2>
                <div className="flex gap-2 flex-wrap">
                  {result.genre_by_section.map((sec, i) => (
                    <div key={i} className="bg-gray-100 p-2 rounded text-sm flex-1 text-center min-w-[100px]">
                      <div className="text-gray-500 mb-1">Part {sec.section}</div><div className="font-semibold text-blue-700">{sec.genre}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.shoot_schedule && (
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h2 className="text-xl font-bold mb-4">Estimated 5-Day Shoot Schedule</h2>
                <div className="space-y-4">
                  {result.shoot_schedule.map((day, i) => (
                    <div key={i} className="bg-gray-50 p-3 rounded border border-gray-100">
                      <h3 className="font-bold text-blue-800 mb-2">Day {day.day}</h3>
                      <ul className="list-disc pl-5 text-gray-700">{day.scenes.map((sceneName, j) => <li key={j}>{sceneName}</li>)}</ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Errors ({result.errors.length})</h2>
              <ul className="space-y-4">
                {result.errors.map((err, i) => (
                  <li key={i} className="bg-gray-50 p-3 rounded border border-gray-100">
                    <div className="mb-1"><span className="mr-2 font-bold text-red-600">[{err.severity}]</span><span>{err.message}</span></div>
                    <div className="text-sm text-gray-500"><strong>Fix:</strong> {err.fix}</div>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 border-l-4 border-l-blue-500">
              <h2 className="text-xl font-bold mb-2">Interesting</h2><p className="italic text-gray-600">{result.comment}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
