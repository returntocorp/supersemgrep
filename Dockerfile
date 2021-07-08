FROM returntocorp/semgrep-agent:v1

WORKDIR /supersemgrep

COPY poetry.lock pyproject.toml ./
RUN apk add --no-cache --virtual=.build-deps build-base cargo libffi-dev openssl-dev &&\
  poetry install --no-dev --no-root &&\
  apk del .build-deps &&\
  rm -rf /root/.cache/* /root/.cargo/* /tmp/*

COPY ./src/supersemgrep /supersemgrep/src/supersemgrep
RUN poetry install --no-dev

CMD [ "supersemgrep-agent" ]
