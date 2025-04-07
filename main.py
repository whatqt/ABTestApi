if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.asgi:main_app", log_level="info", reload=True)