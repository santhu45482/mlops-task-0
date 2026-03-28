import argparse
import yaml
import pandas as pd
import numpy as np
import logging
import json
import time
import sys
import os

def setup_logging(log_file):
    """Configures logging to write to a file and output to the console."""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def write_metrics(output_file, data):
    """Writes the JSON metrics to a file and prints to stdout."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print("\n--- Final Metrics ---")
    print(json.dumps(data, indent=4))

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="MLOps Batch Job: Rolling Mean Signal")
    parser.add_argument('--input', required=True, help="Path to input CSV")
    parser.add_argument('--config', required=True, help="Path to config YAML")
    parser.add_argument('--output', required=True, help="Path to output metrics JSON")
    parser.add_argument('--log-file', required=True, help="Path to log file")
    
    args = parser.parse_args()
    
    setup_logging(args.log_file)
    logging.info("Job started")
    
    version = "unknown" 
    
    try:
        # 1. Load + validate config
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Config file not found: {args.config}")
            
        with open(args.config, 'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML structure in config: {e}")
                
        if not isinstance(config, dict):
            raise ValueError("Invalid config structure: expected a dictionary")

        required_keys = ['seed', 'window', 'version']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Config missing required key: '{key}'")
                
        version = config['version']
        seed = config['seed']
        window = config['window']
        
        np.random.seed(seed)
        logging.info(f"Config loaded and validated. Seed: {seed}, Window: {window}, Version: {version}")
        
        # 2. Load + validate dataset
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found: {args.input}")
            
        if os.path.getsize(args.input) == 0:
            raise ValueError("Input file is empty")
            
        try:
            df = pd.read_csv(args.input)
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {e}")
            
        # --- THE FIX: Sanitize column names (lowercase and strip spaces) ---
        df.columns = df.columns.str.strip().str.lower()
            
        # Now validate that 'close' exists [cite: 27]
        if 'close' not in df.columns:
            raise ValueError("Missing required column: 'close'")
            
        rows_processed = len(df)
        if rows_processed == 0:
            raise ValueError("Input file contains no data rows")
            
        logging.info(f"Dataset loaded successfully. Rows: {rows_processed}")
        
        # 3. Rolling mean computation
        logging.info(f"Computing rolling mean (window={window})...")
        df['rolling_mean'] = df['close'].rolling(window=window).mean()
        
        # 4. Signal generation
        logging.info("Generating signals...")
        df['signal'] = (df['close'] > df['rolling_mean']).astype(int)
        
        # 5. Metrics + timing
        signal_rate = float(df['signal'].mean())
        latency_ms = int((time.time() - start_time) * 1000)
        
        metrics_success = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }
        
        write_metrics(args.output, metrics_success)
        logging.info(f"Metrics summary - Rows: {rows_processed}, Signal Rate: {round(signal_rate, 4)}, Latency: {latency_ms}ms")
        logging.info("Job completed with status: success")
        sys.exit(0)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        logging.error(f"Job failed: {error_msg}", exc_info=True)
        
        metrics_error = {
            "version": version,
            "status": "error",
            "error_message": error_msg
        }
        write_metrics(args.output, metrics_error)
        logging.info(f"Job exited with error. Latency: {latency_ms}ms")
        sys.exit(1)

if __name__ == "__main__":
    main()
