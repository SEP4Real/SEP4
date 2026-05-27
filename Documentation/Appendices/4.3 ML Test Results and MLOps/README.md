# 5.3 ML Test Results and MLOps

MAL service test coverage report and MLOps pipeline documentation.

**Expected files:**
- `MAL_Coverage_Report/` — HTML coverage report (download as artifact from GitHub Actions `mlops` job → `mal-coverage-report`)
- `MAL_Coverage_Summary.txt` — plain-text summary of pytest-cov output
- `MAL_Test_Output.txt` — full pytest console output showing all passing tests

**Tested components:**
- `MAL/tests/test_build_unified_environment_dataset.py` — data merging, MICE imputation, schema validation
- `MAL/tests/test_prediction_api.py` — FastAPI endpoint availability, model loading, input validation, inference correctness

**MLOps pipeline (`mlops.yaml`):**
1. Python 3.10 environment + PostgreSQL sidecar setup
2. Full pytest suite run with coverage on `ml_pipeline/` and `backend/`
3. Model artifact integrity check (`rf_model.pkl` / `nn_model.pkl` present and loadable)
4. On merge to `main`: Docker image build and push to GHCR (`mal-api`)
5. Coolify webhook triggers redeployment of the `mal-api` container

**Source:** `.github/workflows/mlops.yaml`, `MAL/tests/`
