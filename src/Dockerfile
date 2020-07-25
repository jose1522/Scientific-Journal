FROM python

RUN mkdir /src

# Set the working directory to /app
WORKDIR /src

# Copy the current directory contents into the container at /app
ADD . /src

# Install the dependencies
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools unixodbc-dev
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# run the command to start uWSGI
CMD ["uwsgi", "app.ini"]
