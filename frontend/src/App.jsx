import { useState, useRef } from 'react';

const SAMPLE_SCRIPT = `INT. KITCHEN - NIGHT

A dark room. A candle burns on the table.

JOHN
Hello, MARY.

MARY
Hi, JOHN.

FADE OUT.`;

export default function App() {
  const [script, setScript] = useState(SAMPLE_SCRIPT);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [aiResult, setAiResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  
  const fileInputRef = useRef(null);

  const handleAnalyze = async () => {
    if (!script.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    setAiResult(null);

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to analyze');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setAiResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to upload file');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleAiAnalyze = async () => {
    setAiLoading(true);
    setAiResult(null);
    try {
      const response = await fetch('/ai-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script })
      });
      const text = await response.text();
      if (!text) throw new Error("Server returned an empty response.");
      const data = JSON.parse(text);
      if (!response.ok) throw new Error(data.detail || 'AI failed');
      setAiResult(data.ai_analysis);
    } catch (err) {
      setAiResult("Error: " + err.message);
    } finally {
      setAiLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    let text = `===============================================\n`;
    text += `               SCRIPTSCOPE REPORT               \n`;
    text += `===============================================\n\n`;
    text += `Score: ${result.score} / 100\n`;
    text += `Rating: ${result.tier}\n`;
    text += `Language: ${result.language}\n`;
    text += `Age Rating: ${result.content_rating}\n`;
    text += `Mood: ${result.emotion_balance.mood}\n\n`;
    text += `--- Genres ---\n`;
    Object.entries(result.genres).forEach(([genre, pct]) => {
      text += `${genre}: ${pct.toFixed(1)}%\n`;
    });
    text += `\n--- Errors (${result.errors.length}) ---\n`;
    result.errors.forEach(err => {
      const where = err.line === null ? "Script" : `Line ${err.line}`;
      text += `[${err.severity}] ${where}: ${err.message}\n  Fix: ${err.fix}\n\n`;
    });
    text += `--- In plain words ---\n`;
    result.explanation.forEach(s => { text += `- ${s}\n`; });
    text += `\n`;
    if (aiResult && !aiResult.startsWith("Error")) {
      text += `--- AI Analysis ---\n${aiResult}\n\n`;
    }
    text += `Interesting: ${result.comment}\n`;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ScriptScope_Report_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getTierColor = (tier) => {
    switch(tier) {
      case 'POOR': return 'text-red-600';
      case 'AVERAGE': return 'text-yellow-600';
      case 'GOOD': return 'text-cyan-600';
      case 'EXCELLENT': return 'text-green-600';
      case 'PERFECT': return 'text-emerald-700';
      default: return 'text-gray-800';
    }
  };

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'CRITICAL': return 'text-red-600 font-bold';
      case 'MODERATE': return 'text-yellow-600 font-bold';
      case 'MINOR': return 'text-cyan-600 font-bold';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 font-sans text-gray-900 bg-gray-50 min-h-screen">
      
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-1">ScriptScope</h1>
        <p className="text-gray-500">Paste a script and click Analyze. Rules-based analysis — no AI.</p>
      </header>

      <div className="mb-4">
        <textarea
          value={script}
          onChange={(e) => setScript(e.target.value)}
          className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
          placeholder="Paste your script here..."
        />
      </div>

      <div className="flex gap-4 mb-8">
        <button
          onClick={handleAnalyze}
          disabled={loading || !script.trim()}
          className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors"
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
        
        <input 
          type="file" 
          accept=".pdf,.docx,.txt" 
          ref={fileInputRef} 
          onChange={handleFileUpload} 
          className="hidden" 
        />
        <button
          onClick={() => fileInputRef.current.click()}
          disabled={loading}
          className="px-8 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors"
        >
          Upload File (PDF/Word/TXT)
        </button>
      </div>

      {error && (
        <div className="p-4 mb-6 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          
          <div className="bg-white p-6 rounded-lg shadow-sm border border-indigo-200 border-l-4 border-l-indigo-500 mb-8">
            <h2 className="text-xl font-bold mb-2 text-indigo-900">Want deeper feedback?</h2>
            <p className="text-gray-600 mb-4 text-sm">Let Gemini AI find plot holes, weak dialogue, and write a real summary.</p>
            <button
              onClick={handleAiAnalyze}
              disabled={aiLoading}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold rounded shadow transition-colors"
            >
              {aiLoading ? 'AI is reading... (wait 5s)' : 'Get AI Analysis'}
            </button>
            {aiResult && (
              <div className="mt-6 p-5 bg-indigo-50 border border-indigo-100 rounded text-gray-800 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                {aiResult}
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold mb-4">Score</h2>
            <p className={`text-4xl font-extrabold ${getTierColor(result.tier)} mb-2`}>{result.score} / 100</p>
            <p className="text-gray-700 mb-1"><strong>Rating:</strong> {result.tier}</p>
            <p className="text-gray-700 mb-4"><strong>Language:</strong> {result.language}</p>
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-900 text-white text-sm font-semibold rounded shadow transition-colors"
            >
              ⬇ Download Report (.txt)
            </button>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold mb-4">Content Rating & Mood</h2>
            <p className="text-gray-700 mb-2">
              <strong>Age Rating:</strong> {result.content_rating}
              {result.genres["Erotic"] > 0 && <span className="text-sm text-red-500 ml-2">(Contains adult themes)</span>}
            </p>
            <p className="text-gray-700">
              <strong>Mood:</strong> {result.emotion_balance.mood} 
              <span className="text-sm text-gray-500 ml-2">({result.emotion_balance.positive_words} positive, {result.emotion_balance.negative_words} negative words)</span>
            </p>
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
                <li key={genre} className="flex justify-between border-b border-gray-100 pb-1">
                  <span>{genre}</span>
                  <span className="font-mono">{pct.toFixed(1)}%</span>
                </li>
              ))}
            </ul>
          </div>

          {result.genre_by_section && result.genre_by_section.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Genre by Section (Mood Shift)</h2>
              <div className="flex gap-2 flex-wrap">
                {result.genre_by_section.map((sec, i) => (
                  <div key={i} className="bg-gray-100 p-2 rounded text-sm flex-1 text-center min-w-[100px]">
                    <div className="text-gray-500 mb-1">Part {sec.section}</div>
                    <div className="font-semibold text-blue-700">{sec.genre}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.scenes?.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Scenes ({result.scenes.length})</h2>
              <ul className="list-disc pl-5 space-y-1 text-gray-700">
                {result.scenes.map((sc, i) => (
                  <li key={i}>
                    <span className="font-mono text-sm bg-gray-100 px-1 py-0.5 rounded mr-2">{sc.interior}.</span>
                    {sc.location} - {sc.time}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.shoot_schedule && result.shoot_schedule.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Estimated 5-Day Shoot Schedule</h2>
              <p className="text-sm text-gray-500 mb-4">(A rough guide - assumes 5 days of shooting)</p>
              <div className="space-y-4">
                {result.shoot_schedule.map((day, i) => (
                  <div key={i} className="bg-gray-50 p-3 rounded border border-gray-100">
                    <h3 className="font-bold text-blue-800 mb-2">Day {day.day}</h3>
                    <ul className="list-disc pl-5 text-gray-700">
                      {day.scenes.map((sceneName, j) => (
                        <li key={j}>{sceneName}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {Object.keys(result.characters || {}).length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Characters ({Object.keys(result.characters).length})</h2>
              <ul className="space-y-1 text-gray-700">
                {Object.entries(result.characters).map(([name, info]) => (
                  <li key={name} className="flex justify-between border-b border-gray-100 pb-1">
                    <span className="font-semibold">{name}</span>
                    <span>{info.speeches} speeches, {info.words} words</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold mb-4">Errors ({result.errors.length})</h2>
            {result.errors.length === 0 ? (
              <p className="text-gray-500">No errors found.</p>
            ) : (
              <ul className="space-y-4">
                {result.errors.map((err, i) => {
                  const where = err.line === null ? "Script" : `Line ${err.line}`;
                  return (
                    <li key={i} className="bg-gray-50 p-3 rounded border border-gray-100">
                      <div className="mb-1">
                        <span className={`mr-2 ${getSeverityColor(err.severity)}`}>[{err.severity}]</span>
                        <span className="text-gray-800">{where}: {err.message}</span>
                      </div>
                      <div className="text-sm text-gray-500 pl-1"><strong>Fix:</strong> {err.fix}</div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {result.explanation?.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">In plain words</h2>
              <ul className="list-disc pl-5 space-y-1 text-gray-700">
                {result.explanation.map((sentence, i) => (
                  <li key={i}>{sentence}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 border-l-4 border-l-blue-500">
            <h2 className="text-xl font-bold mb-2">Interesting</h2>
            <p className="italic text-gray-600">{result.comment}</p>
          </div>

        </div>
      )}
    </div>
  );
}