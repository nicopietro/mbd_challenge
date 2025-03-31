from argparse import ArgumentParser

import uvicorn

parser = ArgumentParser(
    "py_challenge data service",
    description="A REST API application to obtain the data required to complete the py_challenge proposed at https://github.com/jfaldanam/py_challenge",
)
subparsers = parser.add_subparsers(dest="command")

run_parser = subparsers.add_parser("run", help="Run the application")
run_parser.add_argument(
    "--host",
    type=str,
    default="0.0.0.0",
    help="The network address to listen to. Default is: '0.0.0.0'",
)
run_parser.add_argument(
    "--port",
    type=int,
    default=8777,
    help="The network port to listen to. Default is: 8777",
)

run_parser.add_argument(
    "--reload",
    action="store_true",
    help="Enable auto-reload of the server when the code changes",
)

args = parser.parse_args()

match args.command:
    case "run":
        uvicorn.run(
            "py_challenge_data_service.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
    case _:
        parser.print_help()
        exit(1)
