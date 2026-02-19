from __future__ import annotations

import os
from typing import Any, Dict, Optional

def log_mlflow(metrics: Dict[str, float], params: Optional[Dict[str, Any]] = None) -> None:
    """
    Minimal MLflow logger (optional).
    Set MLFLOW_TRACKING_URI (and optionally MLFLOW_EXPERIMENT_NAME) to enable.
    """
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        return

    import mlflow
    mlflow.set_tracking_uri(tracking_uri)
    exp_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "retail-rag-sim")
    mlflow.set_experiment(exp_name)

    with mlflow.start_run(run_name=os.getenv("MLFLOW_RUN_NAME", "offline-eval")):
        if params:
            mlflow.log_params({k: str(v) for k, v in params.items()})
        for k, v in metrics.items():
            mlflow.log_metric(k, float(v))


def log_wandb(metrics: Dict[str, float], config: Optional[Dict[str, Any]] = None) -> None:
    """
    Minimal W&B logger (optional).
    Set WANDB_API_KEY and WANDB_PROJECT to enable.
    """
    if not os.getenv("WANDB_API_KEY") or not os.getenv("WANDB_PROJECT"):
        return

    import wandb
    run = wandb.init(project=os.getenv("WANDB_PROJECT"), config=config or {}, reinit=True)
    wandb.log(metrics)
    run.finish()
