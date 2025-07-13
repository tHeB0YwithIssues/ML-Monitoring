FROM ubuntu

RUN apt-get update && \
    apt-get install -y stress-ng && \
    apt-get clean

CMD ["stress-ng", "--cpu", "8", "--cpu-load", "30","--io", "4", "--vm", "2", "--vm-bytes", "128M", "--fork", "4"]
