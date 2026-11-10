FROM python:3.12-slim
WORKDIR /app
COPY server.py mcp_stdio.py ./
ENV PYTHONUNBUFFERED=1
CMD ["python", "server.py"]
