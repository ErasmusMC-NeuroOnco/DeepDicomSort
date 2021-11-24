FROM ubuntu:20.04

###############
## Install python and required packages
###############

## Install python and pip
RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install --no-install-recommends -y \
    build-essential\
    curl\
    ca-certificates\
    libssl-dev\
    libbz2-dev\
    libffi-dev\
    libncurses5-dev\
    libncursesw5-dev\
    libreadline-dev\
    libsqlite3-dev\
    llvm\
    make\
    openssl\
    python3-distutils\
    tk-dev\
    wget\
    xz-utils\
    zlib1g-dev\
    && rm -rf /var/lib/apt/lists/*

RUN wget https://www.python.org/ftp/python/3.6.7/Python-3.6.7.tgz \
    && tar -xzvf Python-3.6.7.tgz \
    && rm Python-3.6.7.tgz \
    && cd Python-3.6.7 \
    && ./configure \
    && make \
    && make install \
    && cd / \
    && rm -rf Python-3.6.7/


# Install pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3 get-pip.py


###############
## Install dcm2niix
###############

# The exact release used (v1.0.20190410) is not available in the official repository as a package
# We use the one that is closest to this release

RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install --no-install-recommends -y\
    wget\
    unzip\
    && wget https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20190902/dcm2niix_lnx.zip \
    && unzip dcm2niix_lnx.zip \
    && mv dcm2niix /usr/local/bin/dcm2niix \
    && rm dcm2niix* \
    && rm -rf /var/lib/apt/lists/*

###############
## Install fsl
###############


RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install --no-install-recommends -y \
    fsl-5.0-core \
    && rm -rf /var/lib/apt/lists/*

# ###############
# ## Set-up from repository
# ###############

RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y \
    git\
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/Svdvoort/DeepDicomSort.git \
    && cd DeepDicomSort \
    && pip3 install -r requirements.txt

#     && mv Data/brain_mask.nii.gz /DATA/ATLAS/ \
#     && mkdir -p /DATA/MODEL/ \
#     && mv Data/config_prognosais_model.yaml /DATA/MODEL/ \
#     && mv Scripts/custom_definitions.py /DATA/MODEL/\
#     && cd Trained_models \
#     && tar -xzvf prognosais_model.tar.gz \
#     && cp -r prognosais_model/  /DATA/MODEL/prognosais_model/ \
#     && rm prognosais_model.tar.gz \
#     && rm -r prognosais_model/ \
#     && cd .. \
#     && mv Docker/run_pipeline.sh / \
#     && chmod +x /run_pipeline.sh \
#     && mv Scripts/get_predictions.py / \
#     && mv Scripts/evaluate_model.py /

# ENTRYPOINT [ "/run_pipeline.sh" ]



