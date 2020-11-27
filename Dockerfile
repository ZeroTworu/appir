FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app

RUN apt-get update -y && apt-get install -y g++ gconf-service libasound2 libatk1.0-0 libcairo2 \
    libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 \
    libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils firefox-esr wget

# install chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

RUN ln -s /app/drivers/geckodriver /usr/bin/geckodriver
RUN ln -s /app/drivers/chromedriver /usr/bin/chromedriver

ADD poetry.lock /app/
ADD pyproject.toml /app/

RUN pip3 install --upgrade pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false --local
RUN poetry install --no-dev

ADD . /app/

ENV PYTHONPATH=/app

CMD ["python", "wsgi.py"]
EXPOSE 5000
