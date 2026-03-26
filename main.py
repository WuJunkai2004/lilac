import uvicorn


def main():
    uvicorn.run("server.main:app", host="0.0.0.0", port=18000, reload=True)


if __name__ == "__main__":
    main()
