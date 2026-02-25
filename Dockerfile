FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends fonts-noto-cjk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY generate_image.py create_slides.py create_pptx.py ./

ENTRYPOINT ["python"]
