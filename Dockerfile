FROM mgorny/gentoo-python
WORKDIR /pyproject2setuppy
COPY . /pyproject2setuppy
ENV LANG=C.UTF-8 FLIT_ROOT_INSTALL=1
RUN ["tox"]
