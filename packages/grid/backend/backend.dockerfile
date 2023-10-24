ARG PYTHON_VERSION="3.11"
ARG TZ="Etc/UTC"
ARG USER="syftuser"
ARG UID=1000
ARG USER_GRP=$USER:$USER
ARG HOME="/home/$USER"
ARG SYFT_WORKDIR="$HOME/app"

# ==================== [BUILD STEP] Python Dev Base ==================== #

FROM cgr.dev/chainguard/wolfi-base as python_dev

ARG PYTHON_VERSION
ARG TZ
ARG USER
ARG UID

# Setup Python DEV
RUN apk update && \
    apk add build-base gcc tzdata python-$PYTHON_VERSION-dev py$PYTHON_VERSION-pip && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    adduser -D -u $UID $USER

# ==================== [BUILD STEP] Install Syft Dependency ==================== #

FROM python_dev as syft_deps

ARG SYFT_WORKDIR
ARG USER_GRP
ARG USER
ARG HOME
ARG UID

USER $USER
WORKDIR $SYFT_WORKDIR
ENV PATH=$PATH:$HOME/.local/bin

# copy skeleton to do package install
COPY --chown=$USER_GRP syft/setup.py ./syft/setup.py
COPY --chown=$USER_GRP syft/setup.cfg ./syft/setup.cfg
COPY --chown=$USER_GRP syft/pyproject.toml ./syft/pyproject.toml
COPY --chown=$USER_GRP syft/MANIFEST.in ./syft/MANIFEST.in
COPY --chown=$USER_GRP syft/src/syft/VERSION ./syft/src/syft/VERSION
COPY --chown=$USER_GRP syft/src/syft/capnp ./syft/src/syft/capnp

# Install all dependencies together here to avoid any version conflicts across pkgs
RUN --mount=type=cache,target=$HOME/.cache/,rw,uid=$UID \
    pip install --user pip-autoremove jupyterlab==4.0.7 -e ./syft/ && \
    pip-autoremove ansible ansible-core -y

# ==================== [Final] Setup Syft Server ==================== #

FROM cgr.dev/chainguard/wolfi-base as backend

# inherit from global
ARG PYTHON_VERSION
ARG TZ
ARG SYFT_WORKDIR
ARG USER_GRP
ARG USER
ARG HOME

# Setup Python
RUN apk update && \
    apk add --no-cache tzdata bash python-$PYTHON_VERSION py$PYTHON_VERSION-pip && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    rm -rf /var/cache/apk/* && \
    adduser -D -u 1000 $USER && \
    mkdir -p /var/log/pygrid $HOME/data/creds $HOME/data/db $HOME/.cache $HOME/.local && \
    chown -R $USER_GRP /var/log/pygrid $HOME/

USER $USER
WORKDIR $SYFT_WORKDIR

# Update environment variables
ENV PATH=$PATH:$HOME/.local/bin \
    PYTHONPATH=$SYFT_WORKDIR \
    APPDIR=$SYFT_WORKDIR \
    NODE_NAME="default_node_name" \
    NODE_TYPE="domain" \
    SERVICE_NAME="backend" \
    RELEASE="production" \
    DEV_MODE="False" \
    CONTAINER_HOST="docker" \
    PORT=80\
    HTTP_PORT=80 \
    HTTPS_PORT=443 \
    DOMAIN_CONNECTION_PORT=3030 \
    IGNORE_TLS_ERRORS="False" \
    DEFAULT_ROOT_EMAIL="info@openmined.org" \
    DEFAULT_ROOT_PASSWORD="changethis" \
    STACK_API_KEY="changeme" \
    MONGO_HOST="localhost" \
    MONGO_PORT="27017" \
    MONGO_USERNAME="root" \
    MONGO_PASSWORD="example" \
    CREDENTIALS_PATH="$HOME/data/creds/credentials.json"

# Copy pre-built jupyterlab, syft dependencies
COPY --chown=$USER_GRP --from=syft_deps $HOME/.local $HOME/.local

# copy grid
COPY --chown=$USER_GRP grid/backend/grid ./grid

# copy syft
COPY --chown=$USER_GRP syft/ ./syft/

CMD ["bash", "./grid/start.sh"]
