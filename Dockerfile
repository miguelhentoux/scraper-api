##
# STEP 1: Build build container
FROM python:3.10-slim-buster as builder
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1


# Install build dependencies and update packages
RUN : \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
       curl \
       gnupg2 \
       build-essential \
       python-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && :

# Install google cloud sdk
RUN echo "deb http://packages.cloud.google.com/apt cloud-sdk-bullseye main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y

# Setup user
RUN useradd -d /app -ms /bin/bash -u 1012 -g users runner
WORKDIR /app

# Define dependencies
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock

# Install and configure poetry to install from internal pypi.
RUN pip install --upgrade pip
RUN pip install poetry && \
    poetry config virtualenvs.in-project false && \
    poetry config virtualenvs.create false && \
    poetry show --outdated
RUN poetry install --no-dev


## STEP 2: Build runtime container
FROM python:3.10-slim-bullseye
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH /app/.local/bin:${PATH}

# Install pipeline dependencies and update packages
RUN : \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && :

RUN useradd -d /app -ms /bin/bash -u 1012 -g users runner
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# # Copy application/pipeline code
COPY ./scraper_api /app/scraper_api

# # Ensure `secrets` volume path is present
RUN mkdir /app/scraper_api/secrets

# FAST API Port
EXPOSE 8000


# # Cleanup.
RUN apt-get autoremove -y && apt-get autoclean -y && rm -rf /var/lib/apt/lists/*

CMD ["python", "-m", "uvicorn", "scraper_api.api.main:app", "--reload", "--port", "8000", "--host", "0.0.0.0"]