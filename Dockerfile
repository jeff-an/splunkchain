FROM splunk/splunk:latest
LABEL maintainer='jan@splunk.com'

WORKDIR /splunkchain

# Install system libraries
RUN sudo apt update; \
	sudo apt -y install python3;
RUN sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN sudo python3 get-pip.py

# Install python dependencies
COPY requirements.txt .
RUN sudo pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python3", "." ]
# ENTRYPOINT [ "/sbin/entrypoint.sh", "start-service", ">", "splunk.log", "2>&1", "&", "python3", ".", "&&", "fg" ]
