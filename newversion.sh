#! /bin/bash
{ bumpversion --config-file .bumpversion.cfg patch && git push --tags && ./pypi-publish.sh && ./publish.sh && wget -O /dev/null -q --post-data= https://registry.hub.docker.com/u/jhpyle/docassemble/trigger/464265b1-55c9-41bc-b7f8-6ac02544fc74/ && git push; } || echo "Failed"
