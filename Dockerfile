FROM python:3.14-slim  

WORKDIR /internship_task

# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Install curl for Docker healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip 

COPY requirements.txt  /internship_task/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /internship_task/

EXPOSE 8000

CMD ["sh","entrypoint.sh"]