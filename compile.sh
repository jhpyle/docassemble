pythonhome=/usr/share/docassemble/local/bin
origdir=$PWD
for package in `ls -d docassemble* | sort -r | sed 's/_/./'`; do
    $pythonhome/pip uninstall -y $package
done
for package in `ls -d docassemble*`; do
    cd $origdir/$package && \
    rm -rf dist build *egg-info && \
    $pythonhome/python setup.py install || exit 1
done
cd $origdir
