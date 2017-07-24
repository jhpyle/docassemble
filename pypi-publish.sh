rm -rf docassemble/build docassemble/dist docassemble/docassemble.egg-info docassemble_base/build docassemble_base/dist docassemble_base/docassemble.base.egg-info docassemble_demo/build docassemble_demo/dist docassemble_demo/docassemble.demo.egg-info docassemble_webapp/build docassemble_webapp/dist docassemble_webapp/docassemble.demo.egg-info
cd ~/da/docassemble
python setup.py sdist || exit 1
#twine register --repository 'pypi' `find dist -path "*.gz"` || exit 1
twine upload --repository 'pypi' dist/* || exit 1
cd ~/da/docassemble_base
python setup.py sdist || exit 1
#twine register --repository 'pypi' `find dist -path "*.gz"` || exit 1
twine upload --repository 'pypi' dist/* || exit 1
cd ~/da/docassemble_demo
python setup.py sdist || exit 1
#twine register --repository 'pypi' `find dist -path "*.gz"` || exit 1
twine upload --repository 'pypi' dist/* || exit 1
cd ~/da/docassemble_webapp
python setup.py sdist || exit 1
#twine register --repository 'pypi' `find dist -path "*.gz"` || exit 1
twine upload --repository 'pypi' dist/* || exit 1
cd ~/da
rm -rf docassemble/build docassemble/dist docassemble/docassemble.egg-info docassemble_base/build docassemble_base/dist docassemble_base/docassemble.base.egg-info docassemble_demo/build docassemble_demo/dist docassemble_demo/docassemble.demo.egg-info docassemble_webapp/build docassemble_webapp/dist docassemble_webapp/docassemble.demo.egg-info
