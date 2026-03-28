# ML/MLOps Engineering Internship - Task 0

This is a minimal MLOps-style batch job that computes a rolling mean and generates a binary trading signal. It emphasizes reproducibility, observability, and containerized deployment.

## Files Included
- `run.py`: Core batch job script.
- `config.yaml`: Configuration (seed, window size, version).
- `data.csv`: Cleaned OHLCV dataset.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Container definition for isolated execution.
- `metrics.json`: Sample output metrics.
- `run.log`: Sample execution log.

## Local Execution Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the pipeline:
   ```bash
   python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
   ```

## Docker Execution Instructions
Build the Docker image:
```bash
docker build -t mlops-task .
```
Run the container:
```bash
docker run --rm mlops-task
```

### Example metrics.json
```json
{
    "version": "v1",
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.5005,
    "latency_ms": 150,
    "seed": 42,
    "status": "success"
}
```
