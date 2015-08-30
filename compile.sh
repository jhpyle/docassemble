origdir=$PWD
for package in `ls -d docassemble* | sort -r | sed 's/_/./'`; do
    pip uninstall -y $package
done
for package in `ls -d docassemble*`; do
    cd $origdir/$package && \
    rm -rf dist build *egg-info && \
    python setup.py install || exit 1
done
cd $origdir
