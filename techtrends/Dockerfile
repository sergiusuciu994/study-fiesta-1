FROM python:2.7
LABEL maintainer="Sergiu Suciu"
COPY ./techtrends/* /app
WORKDIR /app
RUN ls -ltr
RUN pip install -r requirements.txt
RUN python init_db.py
EXPOSE 3111
CMD [ "python", "app.py" ]
