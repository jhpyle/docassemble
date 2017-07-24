#! /bin/bash

export ORIGUSER=$USER

su -c "rm -rf ~/.cache/pip && rm -rf docassemble/build docassemble/dist docassemble/docassemble.egg-info docassemble_base/build docassemble_base/dist docassemble_base/docassemble.base.egg-info docassemble_demo/build docassemble_demo/dist docassemble_demo/docassemble.demo.egg-info docassemble_webapp/build docassemble_webapp/dist docassemble_webapp/docassemble.demo.egg-info && ./Docker/config/save-db-schema.sh > docassemble_webapp/docassemble/webapp/data/db-schema.txt && ./Docker/config/extract_words.sh > docassemble_base/docassemble/base/data/sources/base-words.yml && chown ${ORIGUSER}.${ORIGUSER} docassemble_webapp/docassemble/webapp/data/db-schema.txt docassemble_base/docassemble/base/data/sources/base-words.yml && su -c '/bin/bash --init-file www-compile.sh -i' www-data" root
