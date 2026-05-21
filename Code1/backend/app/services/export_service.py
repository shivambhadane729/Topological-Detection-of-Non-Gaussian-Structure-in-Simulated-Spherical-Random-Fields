"""
CosmoPH - Export Service
Generates export files: PNG plots, CSV data, JSON results, and ZIP bundles.
"""
import os, json, io, zipfile, csv
import numpy as np
from pathlib import Path
from app.config import get_settings

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MPL = True
except ImportError:
    MPL = False

def _dark_fig(w=8, h=8):
    fig, ax = plt.subplots(figsize=(w,h))
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_facecolor('#0a0a1a')
    return fig, ax

def _style_ax(ax, xlabel='', ylabel='', title=''):
    ax.set_xlabel(xlabel, color='white', fontsize=12)
    ax.set_ylabel(ylabel, color='white', fontsize=12)
    if title: ax.set_title(title, color='white', fontsize=14, fontweight='bold')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

def plot_persistence_diagram(pairs, path):
    if not MPL: return ""
    fig, ax = _dark_fig()
    colors = {0:'#00d4ff', 1:'#ff6b6b'}
    labels = {0:'H₀ (Components)', 1:'H₁ (Loops)'}
    for dim in [0,1]:
        dp = [p for p in pairs if p['dimension']==dim]
        if dp:
            ax.scatter([p['birth'] for p in dp],[p['death'] for p in dp],
                       c=colors[dim],label=labels[dim],alpha=0.7,s=30,edgecolors='white',linewidth=0.5)
    vals = [p['birth'] for p in pairs]+[p['death'] for p in pairs]
    if vals:
        mv = max(vals)*1.1
        ax.plot([0,mv],[0,mv],'w--',alpha=0.3)
    _style_ax(ax,'Birth','Death','Persistence Diagram')
    ax.legend(facecolor='#1a1a2e',edgecolor='#333',labelcolor='white')
    plt.tight_layout(); plt.savefig(path,dpi=150,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close()
    return path

def plot_betti_curves(betti, path):
    if not MPL: return ""
    fig, ax = _dark_fig(10,6)
    colors = {'H0':'#00d4ff','H1':'#ff6b6b'}
    for k,d in betti.items():
        c = colors.get(k,'#fff')
        ax.plot(d['thresholds'],d['counts'],color=c,label=f'β_{k[1:]}',linewidth=2)
        ax.fill_between(d['thresholds'],d['counts'],alpha=0.1,color=c)
    _style_ax(ax,'Threshold (ε)','Betti Number','Betti Curves')
    ax.legend(facecolor='#1a1a2e',edgecolor='#333',labelcolor='white')
    plt.tight_layout(); plt.savefig(path,dpi=150,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close()
    return path

def plot_heatmap(data_2d, path, title="CMB Patch"):
    if not MPL: return ""
    fig, ax = _dark_fig()
    im = ax.imshow(np.array(data_2d),cmap='RdBu_r',origin='lower',interpolation='bilinear')
    plt.colorbar(im,ax=ax)
    _style_ax(ax,title=title)
    plt.tight_layout(); plt.savefig(path,dpi=150,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close()
    return path

def plot_persistence_image(pi, path):
    if not MPL: return ""
    fig, ax = _dark_fig()
    im = ax.imshow(np.array(pi),cmap='magma',origin='lower',interpolation='bilinear')
    plt.colorbar(im,ax=ax)
    _style_ax(ax,'Birth','Persistence','Persistence Image')
    plt.tight_layout(); plt.savefig(path,dpi=150,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close()
    return path

def export_csv(data, path):
    with open(path,'w',newline='') as f:
        w = csv.writer(f)
        w.writerow(['dimension','birth','death','persistence'])
        for p in data.get('persistence_diagram',[]):
            w.writerow([p['dimension'],p['birth'],p['death'],p['death']-p['birth']])
        if 'betti_curves' in data:
            w.writerow([])
            for k,c in data['betti_curves'].items():
                w.writerow([f'# {k}'])
                w.writerow(['threshold','count'])
                for t,ct in zip(c['thresholds'],c['counts']): w.writerow([t,ct])
        if 'summary' in data:
            w.writerow([]); w.writerow(['# Summary'])
            for k,v in data['summary'].items(): w.writerow([k,v])
    return path

def export_json(data, path):
    def ser(o):
        if isinstance(o,np.ndarray): return o.tolist()
        if isinstance(o,(np.float32,np.float64)): return float(o)
        if isinstance(o,(np.int32,np.int64)): return int(o)
        if isinstance(o,dict): return {k:ser(v) for k,v in o.items()}
        if isinstance(o,list): return [ser(v) for v in o]
        return o
    with open(path,'w') as f: json.dump(ser(data),f,indent=2)
    return path

def create_zip_bundle(job_id, results):
    s = get_settings()
    d = s.OUTPUT_DIR / job_id
    d.mkdir(parents=True, exist_ok=True)
    files = []
    if MPL:
        if results.get('persistence_diagram'):
            files.append(plot_persistence_diagram(results['persistence_diagram'],str(d/'persistence_diagram.png')))
        if results.get('betti_curves'):
            files.append(plot_betti_curves(results['betti_curves'],str(d/'betti_curves.png')))
        if results.get('map_preview'):
            files.append(plot_heatmap(results['map_preview'],str(d/'cmb_heatmap.png')))
        if results.get('persistence_image'):
            files.append(plot_persistence_image(results['persistence_image'],str(d/'persistence_image.png')))
    files.append(export_csv(results,str(d/'results.csv')))
    files.append(export_json(results,str(d/'results.json')))
    zp = str(d/f'cosmoph_results_{job_id}.zip')
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as zf:
        for fp in files:
            if fp: zf.write(fp,os.path.basename(fp))
    return zp
