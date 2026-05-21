# CosmoPH

**Topological Data Analysis for Cosmic Microwave Background Maps**

CosmoPH is an interactive, web-based platform that brings cutting-edge Topological Data Analysis (TDA) to cosmology research. Upload, process, and visualize CMB maps to detect primordial non-Gaussianities using persistent homology.

---

## Features

- **Upload/Select Datasets** — Drag-drop FITS uploads or select pre-loaded Planck samples
- **Interactive Preprocessing** — Masking, patch extraction, normalization, wavelet filtering
- **Persistence Diagrams** — H0 (components) and H1 (loops) topological features
- **Betti Curves** — Track feature counts across filtration scales
- **Persistence Images** — Vectorized topological summaries
- **Gaussian Comparison** — Wasserstein distance against null hypothesis
- **ML Classification** — Inflation model classification (scaffold for production)
- **Export** — ZIP bundles with PNG plots, CSV data, JSON results
- **One-Click Demo** — Full pipeline with synthetic data, no upload needed

---

## Architecture

```text
Frontend (Vite + React + Tailwind CSS + Plotly)
    | REST API
Backend (FastAPI + Python)
    | Processing
Services (healpy + ripser + persim + scikit-learn)
    | Storage
Dataset Directory + Output Files
```

---

## Project Structure

```text
CosmoPH/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py       # FastAPI app entry point
│   │   ├── config.py     # Settings / env management
│   │   ├── routes/       # API endpoints (including resources for notebooks/scripts)
│   │   ├── services/     # Business logic (TDA, preprocessing, export)
│   │   ├── schemas/      # Pydantic models
│   │   └── utils/        # Validators, helpers
│   ├── tests/            # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # Vite + React frontend
│   ├── src/
│   │   ├── pages/        # React route pages (Home, Dashboard, Timeline)
│   │   ├── components/   # React components
│   │   ├── services/     # API client (api.js)
│   │   └── index.css     # Tailwind styling and minimal dark theme
│   ├── vite.config.js    # Vite configuration
│   └── package.json
├── dataset/              # Data directory
│   ├── raw/              # Original Planck FITS maps
│   ├── sample/           # Generated demo data
│   ├── processed/        # Preprocessed patches
│   ├── external/         # Third-party data
│   ├── metadata/         # Dataset metadata/configs
│   └── outputs/          # Analysis results & exports
├── scripts/              # Utility scripts
├── notebooks/            # Jupyter tutorials
├── docker-compose.yml
└── README.md
```

---

## Detailed Run Instructions (Local Development)

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### 1. Clone the Repository

```bash
git clone https://github.com/shivambhadane729/CosmoPH.git
cd CosmoPH
```

### 2. Setup & Start the Backend

The backend is a FastAPI server that handles heavy computation, TDA processing, and file management.

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Note: on Windows, `healpy` is skipped automatically because the backend
# services include fallbacks for demo/sample workflows. For full HEALPix
# support, install on Linux or use a conda-based environment.

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at: http://localhost:8000
Interactive API documentation (Swagger UI) is available at: http://localhost:8000/docs

### 3. Setup & Start the Frontend

The frontend is a Vite + React application providing a high-performance, minimal monochrome dashboard for running the analysis.

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend will be available at: http://localhost:3000
_(Note: The Vite configuration is explicitly set to port 3000. Do not use the default 5173)._

### 4. Generate Sample Datasets (Optional but Recommended)

To run the platform without uploading your own FITS files, you can generate synthetic Planck-like sample datasets.

```bash
# From the project root directory, run the download/generation script
python scripts/download_datasets.py
```

---

## End-to-End Workflow

1. **Select/Upload** — Navigate to http://localhost:3000/dashboard. Choose a sample dataset or upload a FITS file.
2. **Configure** — Set mask type, patch size, scale, normalization.
3. **Preprocess** — Click "Run Analysis". The backend extracts and cleans a 2D CMB patch.
4. **TDA Compute** — The system runs persistent homology (Ripser) automatically.
5. **Visualize** — View the interactive persistence diagram, Betti curves, and persistence images on the Results tab.
6. **Compare** — Evaluate the Wasserstein distance against the Gaussian null hypothesis.
7. **Export** — Download a ZIP bundle containing PNG plots, CSV data, and JSON results directly from the dashboard.

---

## Docker Setup

To run the entire stack using Docker Compose:

```bash
docker-compose up --build
```

This starts:

- **Backend** at http://localhost:8000
- **Frontend** at http://localhost:3000
- **Redis** at localhost:6379

---

## Deployment

### Frontend on Vercel

Deploy the `frontend/` directory as a Vercel project.

Set this environment variable in Vercel:

```text
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com
```

### Backend on Render

Deploy the backend with the root directory set to `backend/`, or use the included `render.yaml` blueprint.

Render will run:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The backend allows localhost and Vercel preview/production domains through CORS.

### Recommended flow

1. Deploy the backend on Render first.
2. Copy the Render service URL.
3. Add that URL as `NEXT_PUBLIC_API_URL` in Vercel.
4. Deploy the frontend on Vercel.

---

## API Endpoints

| Method | Endpoint                | Description             |
| ------ | ----------------------- | ----------------------- |
| GET    | `/health`               | Server health check     |
| GET    | `/api/datasets`         | List available datasets |
| POST   | `/api/upload`           | Upload a FITS file      |
| POST   | `/api/preprocess`       | Start preprocessing     |
| POST   | `/api/compute-tda`      | Run TDA computation     |
| GET    | `/api/results/{job_id}` | Get analysis results    |
| GET    | `/api/export/{job_id}`  | Download results ZIP    |
| POST   | `/api/demo`             | Run one-click demo      |

Full OpenAPI docs are dynamically generated at: http://localhost:8000/docs

---

## Testing

To run the backend test suite, use Pytest:

```bash
# Navigate to backend
cd backend

# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_health.py -v
pytest tests/test_tda.py -v
pytest tests/test_preprocess.py -v
```

---

## Tech Stack

| Layer      | Technology                                         |
| ---------- | -------------------------------------------------- |
| Frontend   | Vite, React, Tailwind CSS, React Router, Plotly.js |
| Backend    | FastAPI, Pydantic, Uvicorn                         |
| TDA        | Ripser, Persim, scikit-tda                         |
| Astronomy  | Healpy, Astropy                                    |
| ML         | scikit-learn (scaffold)                            |
| Queue      | In-memory (MVP) -> Celery + Redis (production)     |
| Testing    | Pytest, Jest                                       |
| Deployment | Docker, Docker Compose                             |

---

## License

MIT License — feel free to use, modify, and distribute.

---

Built for cosmology research.
