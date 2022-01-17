# Setup rust build container
FROM rust:bullseye AS rust_builder
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y make perl git && \
    git clone https://github.com/Findomain/Findomain.git && \
    cd Findomain && \
    cargo build --release

# Setup golang builder container
FROM golang:1-buster AS go_builder
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/OWASP/Amass/v3/...@master && \
    go get -u github.com/tomnomnom/assetfinder

# Build prod image
FROM python:3.9.9-slim-bullseye
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install git -y && \
    git -C /opt/ clone https://github.com/zPrototype/bugbounty_stuff.git && \
    cd /opt/bugbounty_stuff/subkiller && pip3 install -r requirements.txt
COPY --from=rust_builder /Findomain/target/release/findomain /usr/local/bin/
COPY --from=go_builder /go/bin/* /usr/local/bin/
WORKDIR /data
ENTRYPOINT ["python3", "/opt/bugbounty_stuff/subkiller/subkiller.py"]
