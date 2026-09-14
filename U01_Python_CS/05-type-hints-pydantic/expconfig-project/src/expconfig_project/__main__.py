"""Integration demo: AppSettings + schemas working together end-to-end."""
from __future__ import annotations
from .config import AppSettings
from .schemas import EvalResult, TrainConfig, TrainResponse, parse_train_request


def main() -> None:
    settings = AppSettings()  # type: ignore[call-arg]
    print(f"[{settings.app_name}] max_epochs allowed by server: {settings.max_epochs}")

    raw_request = '{"dataset_path": "sales.csv", "model_type": "linear", "epochs": 30}'
    request = parse_train_request(raw_request)
    if request is None:
        return

    if request.epochs > settings.max_epochs:
        print(f"Rejected: epochs={request.epochs} exceeds server limit "
              f"{settings.max_epochs}")
        return

    config = TrainConfig(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    response = TrainResponse(run_id="run-001", status="queued")
    print(f"Accepted request: {request}")
    print(f"Using split config: {config}")
    print(f"Response: {response}")

    result = EvalResult(accuracy=0.91, f1_score=0.88)
    print(f"Final evaluation: {result}")


if __name__ == "__main__":
    main()
