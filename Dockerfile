FROM python:3.9
WORKDIR /user/src/app
RUN apt update
COPY . /user/src/app
RUN pip install -r requirements.txt
CMD [ "python", "main.py" ]