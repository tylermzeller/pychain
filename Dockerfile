FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY core/*.py ./

CMD [ "python", "-u", "./gucci_main.py", "up" ]
