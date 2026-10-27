import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Industrial current-condition monitor")
    sub = parser.add_subparsers(dest="command", required=True)
    train_cmd = sub.add_parser("train")
    train_cmd.add_argument("--data", default="data/raw/ai4i2020.csv")
    train_cmd.add_argument("--output", default="var/model")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    sub.add_parser("dashboard")
    simulation = sub.add_parser("simulate")
    simulation.add_argument("--api", default="http://127.0.0.1:8000")
    simulation.add_argument("--asset", default="DEMO-01")
    simulation.add_argument("--steps", type=int, default=80)
    simulation.add_argument("--interval", type=float, default=1.0)
    simulation.add_argument("--scenario", choices=["normal", "alarm", "cycle"], default="cycle")
    args = parser.parse_args()
    if args.command == "train":
        from .training import train

        report = train(args.data, args.output)
        print(
            json.dumps(
                {"model_id": report["model_id"], "test": report["evaluation"]["test"]}, indent=2
            )
        )
    elif args.command == "serve":
        import uvicorn

        uvicorn.run(
            "predictive_monitor.api:create_app", factory=True, host=args.host, port=args.port
        )
    elif args.command == "dashboard":
        import subprocess
        import sys
        from pathlib import Path

        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(Path(__file__).with_name("dashboard.py")),
                "--server.address=127.0.0.1",
                "--browser.gatherUsageStats=false",
            ],
            check=True,
        )
    elif args.command == "simulate":
        from .simulation import simulate

        simulate(args.api, args.asset, args.steps, args.interval, args.scenario)


if __name__ == "__main__":
    main()
