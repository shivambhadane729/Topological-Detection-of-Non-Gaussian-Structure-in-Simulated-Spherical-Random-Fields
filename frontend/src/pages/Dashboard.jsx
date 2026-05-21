import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import PlotlyPlot from 'react-plotly.js'; 
const Plot = typeof PlotlyPlot === 'object' && PlotlyPlot.default ? PlotlyPlot.default : PlotlyPlot;
import { 
  Database, 
  BarChart3, 
  Play, 
  Loader2,
  RefreshCw,
  Cpu,
  ArrowLeft,
  Upload,
  Book,
  Code,
  Download,
  FileText
} from 'lucide-react';
import { API_BASE_URL, api } from '../services/api';

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-md transition-colors text-sm font-medium ${
      active 
        ? 'bg-accent/10 text-accent' 
        : 'text-on-surface-variant hover:bg-surface hover:text-primary'
    }`}
  >
    <Icon size={18} />
    <span>{label}</span>
  </button>
);

const Card = ({ children, title, icon: Icon, className = '', footer }) => (
  <div className={`bg-background rounded-lg border border-outline flex flex-col shadow-sm ${className}`}>
    {title && (
      <div className="px-6 py-4 border-b border-outline bg-surface flex items-center gap-3">
        {Icon && <Icon size={18} className="text-on-surface-variant" />}
        <h3 className="font-semibold text-primary text-sm">{title}</h3>
      </div>
    )}
    <div className="p-6 flex-1">
      {children}
    </div>
    {footer && (
      <div className="px-6 py-4 border-t border-outline bg-surface">
        {footer}
      </div>
    )}
  </div>
);

export default function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [loadingDatasets, setLoadingDatasets] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState(null);
  
  const [activeTab, setActiveTab] = useState('explore'); 
  
  const [jobStatus, setJobStatus] = useState('idle'); 
  const [jobProgress, setJobProgress] = useState(0);
  const [jobMessage, setJobMessage] = useState('');
  const [currentJobId, setCurrentJobId] = useState(null);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  // Resources state
  const [resources, setResources] = useState([]);
  const [selectedResource, setSelectedResource] = useState(null);
  const [resourceContent, setResourceContent] = useState('');
  const [loadingResource, setLoadingResource] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, []);

  useEffect(() => {
    if (activeTab === 'scripts' || activeTab === 'notebooks') {
      fetchResources(activeTab);
    }
  }, [activeTab]);

  const fetchDatasets = async () => {
    try {
      setLoadingDatasets(true);
      const data = await api.getDatasets();
      setDatasets(data.datasets || []);
      if (data.datasets?.length > 0 && !selectedDataset) {
        setSelectedDataset(data.datasets[0]);
      }
    } catch (err) {
      console.error('Failed to fetch datasets:', err);
    } finally {
      setLoadingDatasets(false);
    }
  };

  const fetchResources = async (type) => {
    try {
      setLoadingResource(true);
      setResources([]);
      setSelectedResource(null);
      setResourceContent('');
      const data = await api.getResources(type);
      setResources(data.files || []);
    } catch (err) {
      console.error('Failed to fetch resources:', err);
    } finally {
      setLoadingResource(false);
    }
  };

  const loadResourceContent = async (type, path) => {
    try {
      setSelectedResource(path);
      setLoadingResource(true);
      const data = await api.getResourceContent(type, path);
      setResourceContent(data.content);
    } catch (err) {
      setResourceContent('Failed to load content.');
    } finally {
      setLoadingResource(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      setError(null);
      setJobStatus('uploading');
      setJobMessage('Uploading file...');
      await api.uploadDataset(file);
      setJobMessage('Upload complete.');
      setJobStatus('idle');
      fetchDatasets();
    } catch (err) {
      setError(err.message);
      setJobStatus('error');
    }
  };

  const runDemo = async () => {
    try {
      setError(null);
      setResults(null);
      setJobStatus('preprocessing');
      setJobMessage('Running Demo Pipeline...');
      setJobProgress(20);
      const res = await api.runDemo();
      await pollJob(res.job_id, 'demo');
    } catch (err) {
      setJobStatus('error');
      setError(err.message);
    }
  };

  const runAnalysis = async () => {
    if (!selectedDataset) return;
    try {
      setError(null);
      setResults(null);
      setJobStatus('preprocessing');
      setJobMessage('Aligning cosmic signals...');
      setJobProgress(10);
      const preprocessResponse = await api.preprocess(selectedDataset.id);
      await pollJob(preprocessResponse.job_id, 'preprocessing');
      setJobProgress(50);
      
      setJobStatus('computing');
      setJobMessage('Extracting topological signatures...');
      const tdaResponse = await api.computeTDA(preprocessResponse.job_id);
      await pollJob(tdaResponse.job_id, 'computing');
    } catch (err) {
      setJobStatus('error');
      setError(err.message);
    }
  };

  const pollJob = async (id, stage) => {
    setCurrentJobId(id);
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const job = await api.getResults(id);
          if (job.status === 'completed') {
            clearInterval(interval);
            setJobStatus('completed');
            setJobProgress(100);
            setResults(job.result);
            setActiveTab('results');
            resolve(job);
          } else if (job.status === 'failed') {
            clearInterval(interval);
            reject(new Error(job.message || 'Job failed'));
          } else {
            setJobMessage(job.message || `Processing ${stage}...`);
          }
        } catch (err) {
          clearInterval(interval);
          reject(err);
        }
      }, 1000);
    });
  };

  const handleExport = async () => {
    if (!currentJobId) return;
    try {
      const res = await api.exportResults(currentJobId);
      if (res.download_url) {
        window.open(`${API_BASE_URL}${res.download_url}`, '_blank');
      }
    } catch (err) {
      console.error("Export failed", err);
      alert("Failed to export results.");
    }
  };

  const renderPersistenceDiagram = () => {
    if (!results?.persistence_diagram) return null;

    const h0 = results.persistence_diagram.filter(p => p.dimension === 0);
    const h1 = results.persistence_diagram.filter(p => p.dimension === 1);

    return (
      <Plot
        data={[
          {
            x: h0.map(p => p.birth),
            y: h0.map(p => p.death),
            mode: 'markers',
            name: 'H₀',
            marker: { color: '#a3a3a3', size: 8, opacity: 0.7 },
          },
          {
            x: h1.map(p => p.birth),
            y: h1.map(p => p.death),
            mode: 'markers',
            name: 'H₁',
            marker: { color: '#f8fafc', size: 8, symbol: 'diamond' },
          },
          {
            x: [0, 2],
            y: [0, 2],
            mode: 'lines',
            showlegend: false,
            line: { color: '#27272a', dash: 'dash' },
          }
        ]}
        layout={{
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          xaxis: { title: 'Birth', color: '#94a3b8', gridcolor: '#27272a', zeroline: false },
          yaxis: { title: 'Death', color: '#94a3b8', gridcolor: '#27272a', zeroline: false },
          legend: { font: { color: '#94a3b8', size: 12 }, bgcolor: 'rgba(9,9,11,0.9)' },
          margin: { l: 60, r: 20, b: 60, t: 20 },
          autosize: true,
          hovermode: 'closest',
          font: { family: 'Inter, sans-serif' }
        }}
        useResizeHandler
        className="w-full h-full"
      />
    );
  };

  return (
    <div className="min-h-screen bg-surface text-on-surface flex font-sans selection:bg-accent/30">
      
      {/* Sidebar */}
      <aside className="w-64 border-r border-outline bg-background flex flex-col h-screen sticky top-0 shrink-0">
        <div className="p-6 border-b border-outline">
          <Link to="/" className="flex items-center gap-2 text-primary hover:text-accent transition-colors font-bold text-lg">
            <ArrowLeft size={18} className="text-on-surface-variant" />
            CosmoPH
          </Link>
        </div>
        
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <div className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-3 px-4 mt-2">Analysis</div>
          <SidebarItem icon={Database} label="Data Selection" active={activeTab === 'explore'} onClick={() => setActiveTab('explore')} />
          <SidebarItem icon={Cpu} label="Computation" active={activeTab === 'compute'} onClick={() => setActiveTab('compute')} />
          <SidebarItem icon={BarChart3} label="Results Viewer" active={activeTab === 'results'} onClick={() => setActiveTab('results')} />
          
          <div className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-3 px-4 mt-8">Resources</div>
          <SidebarItem icon={Book} label="Notebooks" active={activeTab === 'notebooks'} onClick={() => setActiveTab('notebooks')} />
          <SidebarItem icon={Code} label="Scripts" active={activeTab === 'scripts'} onClick={() => setActiveTab('scripts')} />
        </nav>

        <div className="p-4 border-t border-outline bg-surface">
          <div className="flex items-center gap-2 text-sm text-on-surface-variant">
            <div className={`w-2 h-2 rounded-full ${jobStatus === 'idle' ? 'bg-secondary' : 'bg-primary animate-pulse'}`} />
            {jobStatus === 'idle' ? 'System Idle' : 'Job Running'}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto bg-surface">
        {/* Header */}
        <header className="px-8 py-6 border-b border-outline bg-background flex justify-between items-center shrink-0">
          <div>
            <h1 className="text-2xl font-bold text-primary capitalize">{activeTab} Environment</h1>
            <p className="text-sm text-on-surface-variant mt-1">
              {activeTab === 'notebooks' || activeTab === 'scripts' 
                ? 'View project resources, datasets documentation, and Jupyter notebooks.'
                : 'Configure parameters and analyze cosmic microwave background topological structures.'}
            </p>
          </div>
          {['explore', 'compute', 'results'].includes(activeTab) && (
            <button 
              onClick={fetchDatasets}
              className="p-2 rounded-md border border-outline hover:bg-surface transition-colors text-on-surface-variant"
              title="Refresh Datasets"
            >
              <RefreshCw size={18} className={loadingDatasets ? 'animate-spin' : ''} />
            </button>
          )}
        </header>

        {/* Dashboard Content */}
        <div className="p-8 max-w-7xl mx-auto w-full h-full flex flex-col">
          
          {/* Analysis View */}
          {['explore', 'compute', 'results'].includes(activeTab) && (
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              
              {/* Controls Column */}
              <div className="xl:col-span-1 flex flex-col gap-6">
                <Card title="Data Source" icon={Database}>
                  <div className="mb-4 pb-4 border-b border-outline">
                    <label className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-background border border-outline border-dashed rounded-md text-sm font-medium text-primary hover:bg-surface cursor-pointer transition-colors">
                      <Upload size={16} className="text-accent" />
                      Upload Map (FITS)
                      <input type="file" className="hidden" accept=".fits,.fit,.npy,.npz" onChange={handleFileUpload} />
                    </label>
                  </div>
                  
                  <div className="space-y-3">
                    {loadingDatasets ? (
                      <div className="flex justify-center py-8"><Loader2 className="animate-spin text-accent" /></div>
                    ) : (
                      datasets.map((ds) => (
                        <button
                          key={ds.id}
                          onClick={() => setSelectedDataset(ds)}
                          className={`w-full text-left p-4 rounded-md border transition-colors ${
                            selectedDataset?.id === ds.id
                              ? 'bg-accent/10 border-accent text-primary'
                              : 'bg-background border-outline hover:border-outline-variant text-on-surface'
                          }`}
                        >
                          <div className="flex justify-between items-start mb-1">
                            <div className="font-semibold text-sm truncate pr-2">{ds.name}</div>
                            {ds.category === 'sample' && <span className="text-[10px] bg-surface border border-outline text-on-surface-variant px-2 py-0.5 rounded font-medium shrink-0">Sample</span>}
                          </div>
                          <div className="text-xs text-on-surface-variant">
                            NSIDE {ds.nside || '1024'}
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                </Card>

                <Card title="Execution Engine" icon={Cpu}>
                  <div className="space-y-4">
                    <div className="text-sm text-on-surface-variant">
                      Selected: <span className="font-semibold text-primary truncate block mt-1">{selectedDataset?.name || 'None'}</span>
                    </div>
                    
                    {error && (
                      <div className="p-3 bg-red-950 border border-red-900 text-red-200 text-xs rounded-md break-words">
                        {error}
                      </div>
                    )}
                    
                    <button 
                      disabled={jobStatus === 'preprocessing' || jobStatus === 'computing' || !selectedDataset}
                      onClick={runAnalysis}
                      className={`w-full py-2.5 rounded-md flex items-center justify-center gap-2 text-sm font-medium transition-colors ${
                        jobStatus === 'preprocessing' || jobStatus === 'computing' || !selectedDataset
                          ? 'bg-surface text-on-surface-variant cursor-not-allowed border border-outline'
                          : 'bg-primary text-on-primary hover:bg-secondary'
                      }`}
                    >
                      {jobStatus === 'idle' || jobStatus === 'completed' || jobStatus === 'error' ? (
                        <>
                          <Play size={16} /> Run Analysis
                        </>
                      ) : (
                        <>
                          <Loader2 size={16} className="animate-spin" /> Processing...
                        </>
                      )}
                    </button>

                    <button 
                      disabled={jobStatus === 'preprocessing' || jobStatus === 'computing'}
                      onClick={runDemo}
                      className={`w-full py-2.5 rounded-md border border-outline flex items-center justify-center gap-2 text-sm font-medium transition-colors ${
                        jobStatus === 'preprocessing' || jobStatus === 'computing'
                          ? 'bg-surface text-on-surface-variant cursor-not-allowed'
                          : 'bg-background text-primary hover:bg-surface'
                      }`}
                    >
                      Run Preconfigured Demo
                    </button>

                    {jobStatus !== 'idle' && jobStatus !== 'completed' && jobStatus !== 'error' && (
                      <div className="mt-4">
                        <div className="flex justify-between text-xs text-on-surface-variant mb-1">
                          <span>{jobMessage}</span>
                          <span>{jobProgress}%</span>
                        </div>
                        <div className="h-1.5 w-full bg-surface rounded-full overflow-hidden border border-outline">
                          <div className="h-full bg-accent transition-all duration-300" style={{ width: `${jobProgress}%` }} />
                        </div>
                      </div>
                    )}
                  </div>
                </Card>
              </div>

              {/* Visualization Column */}
              <div className="xl:col-span-2 flex flex-col gap-6">
                <Card className="flex-1 min-h-[500px]" title="Analysis Results" icon={BarChart3}>
                  {results ? (
                    <div className="h-full flex flex-col">
                      <div className="flex justify-end mb-4">
                        <button 
                          onClick={handleExport}
                          className="flex items-center gap-2 px-4 py-2 bg-surface border border-outline rounded-md text-sm font-medium hover:bg-outline-variant transition-colors"
                        >
                          <Download size={16} /> Export Data
                        </button>
                      </div>
                      <div className="flex-1 min-h-[400px] border border-outline rounded-md bg-background">
                        {renderPersistenceDiagram()}
                      </div>
                      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 border-t border-outline pt-6">
                        {[
                          { label: 'Topological Features', val: results.persistence_diagram?.length || 0 },
                          { label: 'Classification', val: results.gaussian_comparison?.is_non_gaussian ? 'Non-Gaussian' : 'Gaussian' },
                          { label: 'Predicted Model', val: results.classification?.model_name?.split(' ')[0] || 'Standard' }
                        ].map((stat, i) => (
                          <div key={i} className="bg-surface rounded-md p-4 border border-outline">
                            <div className="text-xs text-on-surface-variant mb-1">{stat.label}</div>
                            <div className="text-lg font-semibold text-primary">{stat.val}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-on-surface-variant">
                      <BarChart3 size={48} className="mb-4 text-outline-variant" />
                      <h3 className="font-semibold text-lg text-primary">No Data to Display</h3>
                      <p className="text-sm mt-2 max-w-sm text-center">Upload a dataset or select a sample map, then run an analysis or use the preconfigured demo to generate visualizations.</p>
                    </div>
                  )}
                </Card>
              </div>

            </div>
          )}

          {/* Resources View (Scripts & Notebooks) */}
          {(activeTab === 'scripts' || activeTab === 'notebooks') && (
            <div className="flex-1 flex border border-outline rounded-lg bg-background overflow-hidden shadow-sm min-h-[500px]">
              <div className="w-64 border-r border-outline flex flex-col bg-surface">
                <div className="p-4 border-b border-outline font-semibold text-sm text-primary flex items-center gap-2">
                  <FileText size={16} className="text-on-surface-variant" />
                  Files
                </div>
                <div className="flex-1 overflow-y-auto p-2">
                  {resources.length === 0 ? (
                    <div className="text-sm text-on-surface-variant p-4 text-center">No files found.</div>
                  ) : (
                    resources.map(file => (
                      <button
                        key={file}
                        onClick={() => loadResourceContent(activeTab, file)}
                        className={`w-full text-left px-3 py-2 text-sm rounded-md truncate transition-colors ${
                          selectedResource === file ? 'bg-accent/10 text-accent font-medium' : 'text-on-surface-variant hover:bg-outline-variant'
                        }`}
                      >
                        {file}
                      </button>
                    ))
                  )}
                </div>
              </div>
              <div className="flex-1 bg-background relative">
                {loadingResource ? (
                  <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-10 backdrop-blur-sm">
                    <Loader2 className="animate-spin text-accent" />
                  </div>
                ) : null}
                {selectedResource ? (
                  <div className="h-full flex flex-col">
                    <div className="px-4 py-2 border-b border-outline bg-surface text-xs font-mono text-on-surface-variant shrink-0">
                      {selectedResource}
                    </div>
                    <div className="flex-1 overflow-auto p-4 bg-background">
                      <pre className="text-sm font-mono text-primary whitespace-pre-wrap break-words">
                        {resourceContent}
                      </pre>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-sm text-on-surface-variant">
                    Select a file from the sidebar to view its content.
                  </div>
                )}
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
