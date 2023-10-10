FROM python:3.8-slim-buster as base
FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN python -m pip install --no-cache-dir --prefix="/install" -r /requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN python -m pip install --no-cache-dir --prefix="/install" torch --extra-index-url https://download.pytorch.org/whl/cpu
FROM base
COPY --from=builder /install /usr/local/

COPY . /app
WORKDIR /app
ENV PYTHONIOENCODING=utf-8
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
EXPOSE 8080


CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]