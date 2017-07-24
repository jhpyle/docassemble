rm -rf docassemble/build docassemble/dist docassemble/docassemble.egg-info docassemble_base/build docassemble_base/dist docassemble_base/docassemble.base.egg-info docassemble_demo/build docassemble_demo/dist docassemble_demo/docassemble.demo.egg-info docassemble_webapp/build docassemble_webapp/dist docassemble_webapp/docassemble.demo.egg-info
tar --exclude-from=.gitignore -zcf ~/downloadda/docassemble.tar.gz docassemble/
tar --exclude-from=.gitignore -zcf ~/downloadda/docassemble-base.tar.gz docassemble_base/
tar --exclude-from=.gitignore -zcf ~/downloadda/docassemble-demo.tar.gz docassemble_demo/
tar --exclude-from=.gitignore -zcf ~/downloadda/docassemble-webapp.tar.gz docassemble_webapp/
rsync -au ~/downloadda/*.gz jpyle@litigationdatabase.org:da/ 
