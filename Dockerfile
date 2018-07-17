FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY setup.py ./
COPY pychain/ ./pychain/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install -e .

CMD [ "python", "-u", "./pychain/gucci_main.py", "up" ]
