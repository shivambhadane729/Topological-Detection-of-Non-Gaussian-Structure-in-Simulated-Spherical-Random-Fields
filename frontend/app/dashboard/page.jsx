'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false, loading: () => <div className="h-64" /> });
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
import { API_BASE_URL, api } from '../../src/services/api';

  const Card = ({ children, title, icon: Icon, className = '', footer }) => (
    <div className={`card ${className}`}> 
      {title && (
        <div className="px-4 py-3 bg-transparent flex items-center gap-3 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
          {Icon && (
            <div className="w-8 h-8 flex items-center justify-center rounded bg-white/4" style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))' }}>
              <Icon size={16} className="text-white/90" />
            </div>
          )}
          <h3 className="font-semibold text-white text-sm">{title}</h3>
        </div>
      )}
      <div className="p-4 flex-1">{children}</div>
      {footer && <div className="px-4 py-3 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>{footer}</div>}
    </div>
  );

export default function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [loadingDatasets, setLoadingDatasets] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState(null);
  // left controls permanently visible
  const [preprocessConfig, setPreprocessConfig] = useState({
    apply_mask: true,
    mask_type: 'galactic',
    patch_center_lon: 0,
    patch_center_lat: 90,
    patch_size: 64,
    normalize: true,
    apply_filter: false,
    filter_scale: 1,
    target_nside: 64,
  });
  const [tdaConfig, setTdaConfig] = useState({
    max_dimension: 1,
    max_edge_length: 2,
    max_points: 1000,
    compute_betti: true,
    compute_persistence_image: true,
    compare_gaussian: true,
    n_gaussian_samples: 5,
  });
  const [activeResultView, setActiveResultView] = useState('diagram');
  
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
      const preprocessResponse = await api.preprocess(selectedDataset.id, preprocessConfig);
      await pollJob(preprocessResponse.job_id, 'preprocessing');
      setJobProgress(50);
      
      setJobStatus('computing');
      setJobMessage('Extracting topological signatures...');
      const tdaResponse = await api.computeTDA(preprocessResponse.job_id, tdaConfig);
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
    const allPoints = [...h0, ...h1].flatMap((point) => [point.birth, point.death]).filter((value) => Number.isFinite(value));
    const minValue = allPoints.length > 0 ? Math.min(...allPoints) : 0;
    const maxValue = allPoints.length > 0 ? Math.max(...allPoints) : 1;
    const span = Math.max(maxValue - minValue, 1e-6);
    const padding = span * 0.1;
    const axisMin = Math.max(0, minValue - padding);
    const axisMax = maxValue + padding;

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
          xaxis: {
            title: 'Birth',
            color: '#94a3b8',
            gridcolor: '#27272a',
            zeroline: false,
            range: [axisMin, axisMax],
            fixedrange: false,
          },
          yaxis: {
            title: 'Death',
            color: '#94a3b8',
            gridcolor: '#27272a',
            zeroline: false,
            range: [axisMin, axisMax],
            scaleanchor: 'x',
            scaleratio: 1,
            fixedrange: false,
          },
          legend: { font: { color: '#94a3b8', size: 12 }, bgcolor: 'rgba(9,9,11,0.9)' },
          margin: { l: 60, r: 20, b: 60, t: 20 },
          autosize: true,
          hovermode: 'closest',
          font: { family: 'Inter, sans-serif' }
        }}
        useResizeHandler
        className="w-full h-[360px] md:h-[480px] lg:h-[560px]"
      />
    );
  };

  const renderBettiCurves = () => {
    if (!results?.betti_curves) return null;
    const series = Object.entries(results.betti_curves).map(([key, value], index) => ({
      x: value.thresholds || [],
      y: value.counts || [],
      mode: 'lines',
      name: key,
      line: { width: 2, color: index === 0 ? '#f5f5f5' : '#a3a3a3' },
    }));

    return (
      <Plot
        data={series}
        layout={{
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          xaxis: { title: 'Filtration', color: '#94a3b8', gridcolor: '#27272a', zeroline: false },
          yaxis: { title: 'Betti Count', color: '#94a3b8', gridcolor: '#27272a', zeroline: false },
          legend: { font: { color: '#94a3b8', size: 12 }, bgcolor: 'rgba(9,9,11,0.9)' },
          margin: { l: 60, r: 20, b: 60, t: 20 },
          autosize: true,
          hovermode: 'closest',
          font: { family: 'Inter, sans-serif' }
        }}
        useResizeHandler
        className="w-full h-[360px] md:h-[480px] lg:h-[560px]"
      />
    );
  };

  const renderPersistenceImage = () => {
    if (!results?.persistence_image) return null;
    return (
      <Plot
        data={[
          {
            z: results.persistence_image,
            type: 'heatmap',
            colorscale: 'Greys',
            showscale: true,
          },
        ]}
        layout={{
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          xaxis: { title: 'Birth', color: '#94a3b8', gridcolor: '#27272a', zeroline: false },
          yaxis: { title: 'Persistence', color: '#94a3b8', gridcolor: '#27272a', zeroline: false },
          margin: { l: 60, r: 20, b: 60, t: 20 },
          autosize: true,
          font: { family: 'Inter, sans-serif' }
        }}
        useResizeHandler
        className="w-full h-[360px] md:h-[480px] lg:h-[560px]"
      />
    );
  };

  const renderGaussianComparison = () => {
    if (!results?.gaussian_comparison) return null;

    const distances = results.gaussian_comparison.wasserstein_distances || {};
    const labels = Object.keys(distances);
    const means = labels.map((key) => distances[key]?.mean || 0);
    const statuses = results.gaussian_comparison.is_non_gaussian || {};

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-full">
        <Plot
          data={[
            {
              x: labels,
              y: means,
              type: 'bar',
              marker: { color: '#f5f5f5' },
            },
          ]}
          layout={{
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            xaxis: { title: 'Homology Dimension', color: '#94a3b8', gridcolor: '#27272a' },
            yaxis: { title: 'Mean Wasserstein Distance', color: '#94a3b8', gridcolor: '#27272a' },
            margin: { l: 60, r: 20, b: 60, t: 20 },
            autosize: true,
            font: { family: 'Inter, sans-serif' }
          }}
          useResizeHandler
          className="w-full h-[360px] md:h-[480px] lg:h-[560px]"
        />
        <div className="space-y-3 rounded-md border border-white/10 bg-black p-4">
          <h4 className="text-sm font-semibold text-white">Gaussian comparison</h4>
          {labels.map((label) => (
            <div key={label} className="flex items-center justify-between rounded-md border border-white/10 px-3 py-2">
              <span className="text-sm text-white/75">{label}</span>
              <span className={`text-xs font-medium ${statuses[label] ? 'text-white' : 'text-white/45'}`}>
                {statuses[label] ? 'Potentially non-Gaussian' : 'Consistent with Gaussian'}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const sampleDatasets = datasets.filter((dataset) => dataset.category === 'sample');
  const otherDatasets = datasets.filter((dataset) => dataset.category !== 'sample');
  // controls panel is always expanded
  const showControls = true;

  return (
    <div className="min-h-screen bg-black text-white flex flex-col font-sans selection:bg-white/20 selection:text-black overflow-x-hidden">

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 bg-black">
        {/* Dashboard Content */}
        <div className="p-4 md:p-6 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 flex flex-col gap-4">
          
          {/* Analysis View */}
          {['explore', 'compute', 'results'].includes(activeTab) && (
            <div className="grid grid-cols-1 xl:grid-cols-[320px_1fr] gap-6">
              
              {/* Controls Column */}
              <div className="xl:col-span-1 flex flex-col gap-4">
                <div className="w-full rounded-md text-left text-white btn-ghost flex items-center px-3 py-2">
                  <div className="flex items-center gap-2">
                    <Database size={15} className="text-white/70" />
                    <div>
                      <div className="text-sm font-semibold leading-tight">Data</div>
                      <div className="text-[11px] text-white/50 leading-tight">{selectedDataset?.name || 'No dataset selected'}</div>
                    </div>
                  </div>
                </div>

                    <Card title="Dataset" icon={Database} className="mb-4 overflow-hidden">
                      <div className="space-y-2">
                        <label className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-black/40 border border-white/6 border-dashed rounded-md text-sm font-medium text-white hover:bg-white/5 cursor-pointer transition-colors">
                          <Upload size={15} className="text-accent" />
                          Upload Map (FITS)
                          <input type="file" className="hidden" accept=".fits,.fit,.npy,.npz" onChange={handleFileUpload} />
                        </label>
                        <div className="text-[11px] text-white/45">Select a sample dataset below.</div>
                      </div>
                    </Card>

                    <Card title="Samples" icon={FileText} className="mb-4 overflow-hidden">
                      <div className="space-y-2 max-h-[260px] thin-scroll overflow-y-auto pr-1">
                        {loadingDatasets ? (
                          <div className="flex justify-center py-4"><Loader2 className="animate-spin text-accent" /></div>
                        ) : sampleDatasets.length > 0 ? (
                          sampleDatasets.map((ds) => (
                            <button
                              key={ds.id}
                              onClick={() => setSelectedDataset(ds)}
                              className={`w-full text-left p-3 rounded-md transition-colors flex flex-col gap-1 ${
                                selectedDataset?.id === ds.id
                                  ? 'bg-white/5 border border-white/20 text-white'
                                  : 'bg-black/40 border border-white/6 hover:border-white/20 text-white'
                              }`}
                            >
                              <div className="flex justify-between items-start gap-2 mb-1">
                                <div className="font-semibold text-sm truncate pr-2">{ds.name}</div>
                                <span className="text-[10px] bg-white/6 border border-white/8 text-white/90 px-2 py-0.5 rounded font-medium shrink-0">S</span>
                              </div>
                              <div className="text-[12px] text-white/65 line-clamp-2">{ds.description}</div>
                            </button>
                          ))
                        ) : (
                          <div className="text-[11px] text-white/60 py-2.5 px-3 rounded-md border border-white/10 bg-black">No sample datasets available.</div>
                        )}
                      </div>
                    </Card>

                    <Card title="Controls" icon={Cpu} className="border border-white/10 overflow-hidden">
                      <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-2 text-sm text-white/75">
                          <label className="space-y-1">
                            <span className="block text-[11px] text-white/50">Patch size</span>
                            <input className="w-full rounded-md border border-white/10 bg-black px-2.5 py-2 text-white" type="number" min="16" step="1" value={preprocessConfig.patch_size} onChange={(e) => setPreprocessConfig((current) => ({ ...current, patch_size: Number(e.target.value) }))} />
                          </label>
                          <label className="space-y-1">
                            <span className="block text-[11px] text-white/50">Mask type</span>
                            <select className="w-full rounded-md border border-white/10 bg-black px-2.5 py-2 text-white" value={preprocessConfig.mask_type} onChange={(e) => setPreprocessConfig((current) => ({ ...current, mask_type: e.target.value }))}>
                              <option value="galactic">Galactic</option>
                              <option value="point_source">Point Source</option>
                              <option value="custom">Custom</option>
                            </select>
                          </label>
                        </div>
                        <button
                          disabled={jobStatus === 'preprocessing' || jobStatus === 'computing' || !selectedDataset}
                          onClick={runAnalysis}
                          className={`w-full flex items-center justify-center gap-2 text-sm font-medium transition-colors ${
                            jobStatus === 'preprocessing' || jobStatus === 'computing' || !selectedDataset
                              ? 'btn-ghost cursor-not-allowed opacity-60'
                              : 'btn-primary'
                          } py-2`}
                        >
                          {jobStatus === 'idle' || jobStatus === 'completed' || jobStatus === 'error' ? (<><Play size={16} /> Run Analysis</>) : (<><Loader2 size={16} className="animate-spin" /> Processing...</>)}
                        </button>
                        <button
                          disabled={jobStatus === 'preprocessing' || jobStatus === 'computing'}
                          onClick={runDemo}
                          className={`w-full flex items-center justify-center gap-2 text-sm font-medium transition-colors ${
                            jobStatus === 'preprocessing' || jobStatus === 'computing'
                              ? 'btn-ghost cursor-not-allowed opacity-60'
                              : 'btn-ghost'
                          } py-2`}
                        >
                          Run Preconfigured Demo
                        </button>
                      </div>
                    </Card>
              </div>

              {/* Visualization Column */}
              <div className="xl:col-span-1 flex flex-col gap-4">
                <Card className="min-h-[520px] border border-white/10 overflow-hidden" title="Analysis Results" icon={BarChart3}>
                  {results ? (
                    <div className="h-full flex flex-col">
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                        <div className="flex flex-wrap gap-2">
                          {[
                            { key: 'diagram', label: 'Diagram' },
                            { key: 'betti', label: 'Betti Curves' },
                            { key: 'image', label: 'Persistence Image' },
                            { key: 'comparison', label: 'Gaussian Comparison' },
                            { key: 'summary', label: 'Summary' },
                          ].map((item) => (
                            <button
                              key={item.key}
                              onClick={() => setActiveResultView(item.key)}
                              className={`px-3 py-1.5 rounded-md text-sm border transition-colors ${
                                activeResultView === item.key
                                  ? 'bg-white text-black border-white'
                                  : 'bg-black text-white border-white/10 hover:border-white/20'
                              }`}
                            >
                              {item.label}
                            </button>
                          ))}
                        </div>
                        <button
                          onClick={handleExport}
                          className="flex items-center gap-2 px-3 py-1.5 btn-ghost"
                        >
                          <Download size={16} className="text-white/90" /> Export Data
                        </button>
                      </div>
                      <div className="flex-1 min-h-[560px] border border-white/10 rounded-md bg-black">
                        {activeResultView === 'diagram' && renderPersistenceDiagram()}
                        {activeResultView === 'betti' && renderBettiCurves()}
                        {activeResultView === 'image' && renderPersistenceImage()}
                        {activeResultView === 'comparison' && renderGaussianComparison()}
                        {activeResultView === 'summary' && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-3 h-full">
                            {[
                              { label: 'Total features', val: results.summary?.total_features || 0 },
                              { label: 'Max persistence', val: results.summary?.max_persistence?.toFixed?.(4) || results.summary?.max_persistence || 0 },
                              { label: 'Mean persistence', val: results.summary?.mean_persistence?.toFixed?.(4) || results.summary?.mean_persistence || 0 },
                              { label: 'Std persistence', val: results.summary?.std_persistence?.toFixed?.(4) || results.summary?.std_persistence || 0 },
                            ].map((stat) => (
                              <div key={stat.label} className="rounded-md border border-white/10 p-4 bg-black">
                                <div className="text-xs uppercase tracking-wider text-white/45">{stat.label}</div>
                                <div className="mt-2 text-xl font-semibold text-white">{stat.val}</div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 border-t border-white/10 pt-4">
                        {[
                          { label: 'Topological Features', val: results.persistence_diagram?.length || 0 },
                          { label: 'Classification', val: results.gaussian_comparison?.is_non_gaussian ? 'Non-Gaussian' : 'Gaussian' },
                          { label: 'Predicted Model', val: results.classification?.model_name?.split(' ')[0] || 'Standard' }
                        ].map((stat, i) => (
                          <div key={i} className="bg-black rounded-md p-3 border border-white/10">
                            <div className="text-xs text-white/60 mb-1">{stat.label}</div>
                            <div className="text-base font-semibold text-white">{stat.val}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-white/60 px-6 text-center">
                      <BarChart3 size={44} className="mb-4 text-white/30" />
                      <h3 className="font-semibold text-lg text-white">No Data to Display</h3>
                      <p className="text-sm mt-2 max-w-sm">Upload a dataset or select a sample map, then run an analysis or use the preconfigured demo to generate visualizations.</p>
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
