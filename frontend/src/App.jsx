import { useState } from 'react';

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

  const handleAnalyze = async () => {
    if (!script.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script })
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to analyze');
      }
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper for tier colors
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

  // Helper for severity colors
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
      
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-1">ScriptScope</h1>
        <p className="text-gray-500">Paste a script and click Analyze. Rules-based analysis — no AI.</p>
      </header>

      {/* Input Area */}
      <div className="mb-4">
        <textarea
          value={script}
          onChange={(e) => setScript(e.target.value)}
          className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
          placeholder="Paste your script here..."
        />
      </div>

      {/* Action Button */}
      <button
        onClick={handleAnalyze}
        disabled={loading || !script.trim()}
        className="w-full sm:w-auto px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg shadow transition-colors mb-8"
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>

      {/* Error Message */}
      {error && (
        <div className="p-4 mb-6 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          
          {/* Score Card */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold mb-4">Score</h2>
            <p className={`text-4xl font-extrabold ${getTierColor(result.tier)} mb-2`}>
              {result.score} / 100
            </p>
            <p className="text-gray-700"><strong>Rating:</strong> {result.tier}</p>
            <p className="text-gray-700"><strong>Language:</strong> {result.language}</p>
          </div>

          {/* Genres Card */}
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

          {/* Scenes Card */}
          {result.scenes?.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Scenes ({result.scenes.length})</h2>
              <ul className="list-disc pl-5 space-y-1 text-gray-700">
                {result.scenes.map((sc, i) => (
                  <li key={i}>
                    <span className="font-mono text-sm bg-gray-100 px-1 py-0.5 rounded mr-2">{sc.interior}</span>
                    {sc.location} - {sc.time}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Characters Card */}
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

          {/* Errors Card */}
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
                        <span className={`mr-2 ${getSeverityColor(err.severity)}`}>
                          [{err.severity}]
                        </span>
                        <span className="text-gray-800">{where}: {err.message}</span>
                      </div>
                      <div className="text-sm text-gray-500 pl-1">
                        <strong>Fix:</strong> {err.fix}
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* Plain Words Card */}
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

          {/* Comment Card */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 border-l-4 border-l-blue-500">
            <h2 className="text-xl font-bold mb-2">Interesting</h2>
            <p className="italic text-gray-600">{result.comment}</p>
          </div>

        </div>
      )}
    </div>
  );
}  
