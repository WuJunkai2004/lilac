import sys

import uvicorn


def main():
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=18000,
        reload=("dev" in sys.argv or "debug" in sys.argv),
    )


if __name__ == "__main__":
    main()
