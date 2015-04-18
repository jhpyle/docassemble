origdir=$PWD
pip uninstall -y docassemble.demo
pip uninstall -y docassemble.webapp
pip uninstall -y docassemble.base
pip uninstall -y docassemble
cd $origdir/docassemble && \
rm -rf dist build *egg-info && \
python setup.py install && \
cd $origdir/docassemble-base && \
rm -rf dist build *egg-info && \
python setup.py install && \
cd $origdir/docassemble-webapp && \
rm -rf dist build *egg-info && \
python setup.py install && \
cd $origdir/docassemble-demo && \
rm -rf dist build *egg-info && \
python setup.py install
cd $origdir
