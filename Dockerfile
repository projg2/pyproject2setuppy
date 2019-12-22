FROM mgorny/gentoo-python
WORKDIR /pyproject2setuppy
COPY . /pyproject2setuppy
ENV LANG=C.UTF-8
RUN ["tox"]
