FROM python:3.11.7
ARG db_url=sqlite:///./api/logreef.db
ENV db_url=$db_url
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install psycopg2-binary
COPY ./api /code/api
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]