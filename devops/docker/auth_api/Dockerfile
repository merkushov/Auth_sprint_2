FROM python:3.9 AS base

LABEL maintainer="Victor Merkushov <merkushov.victor@gmail.com>"

RUN apt-get -y update \
    && apt-get install -y apt-utils gcc musl-dev libpq-dev

ARG uid=1000
ARG gid=1000

ENV USER=authapi
ENV GROUP=authapi
ENV HOMEDIR=/home/${USER}
ENV APP_HOME=/usr/src/auth_app
ENV APP_TEST=/usr/src/auth_app_tests
ENV APP_REQUIREMENTS=/usr/src/app_requirements
ENV PATH="/home/${USER}/.local/bin:${PATH}"
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/auth_app/src"

RUN mkdir ${APP_HOME}
RUN mkdir ${APP_REQUIREMENTS}
WORKDIR ${APP_HOME}

# Create an unpribileged user
RUN groupadd -g $gid ${GROUP} && \
    useradd -d ${HOMEDIR} -s /bin/bash -u $uid -g $gid ${USER} && \
    mkdir ${HOMEDIR} && \
    chown -R ${USER}:${GROUP} ${HOMEDIR}

COPY --chown=${USER}:${GROUP} devops/auth_api/requirements ${APP_REQUIREMENTS}

USER ${USER}

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN /usr/local/bin/python -m pip install -r "${APP_REQUIREMENTS}/base.txt"

# -----------------------------------------------------------------------------
# production environment
# -----------------------------------------------------------------------------

FROM base AS production

USER root

COPY --chown=${USER}:${GROUP} src ${APP_HOME}

USER ${USER}

RUN /usr/local/bin/python -m pip install -r "${APP_REQUIREMENTS}/prod.txt"

WORKDIR ${APP_HOME}

# -----------------------------------------------------------------------------
# functional tests environment
# -----------------------------------------------------------------------------

FROM base AS test

USER root

RUN apt-get install -y iputils-ping vim curl

RUN mkdir ${APP_TEST}
RUN chown ${USER}:${GROUP} ${APP_TEST}

COPY --chown=${USER}:${GROUP} src ${APP_HOME}
COPY --chown=${USER}:${GROUP} tests ${APP_TEST}

USER ${USER}

RUN /usr/local/bin/python -m pip install -r "${APP_REQUIREMENTS}/test.txt"

WORKDIR ${APP_HOME}

# -----------------------------------------------------------------------------
# development environment
# -----------------------------------------------------------------------------

FROM base AS develop

USER root

WORKDIR ${APP_HOME}/src

RUN apt-get install -y vim make curl git tree jq iputils-ping

USER ${USER}

RUN /usr/local/bin/python -m pip install -r "${APP_REQUIREMENTS}/dev.txt"

# Fording local host users ssh keys to access the repository.
# SSH key is forwarded through Docker-compose as a Secret.
RUN mkdir -m 700 ${HOMEDIR}/.ssh
