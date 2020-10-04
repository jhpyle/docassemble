[1mdiff --git a/CHANGELOG.md b/CHANGELOG.md[m
[1mindex be01a52e..7f9887f5 100644[m
[1m--- a/CHANGELOG.md[m
[1m+++ b/CHANGELOG.md[m
[36m@@ -1,5 +1,16 @@[m
 # Change Log[m
 [m
[32m+[m[32m## [1.1.80] - 2020-10-04[m
[32m+[m[32m### Added[m
[32m+[m[32m- The `middle_initial()` method of `Name`.[m
[32m+[m[32m### Changed[m
[32m+[m[32m- First input element on the screen is focused only if visible in the[m
[32m+[m[32m  viewport.[m
[32m+[m[32m- `[FILE ...]` can now be used with images declared in `images` or[m
[32m+[m[32m  `image sets`.[m
[32m+[m[32m### Fixed[m
[32m+[m[32m- Issue with floating point/integer numbers and input validation.[m
[32m+[m
 ## [1.1.79] - 2020-09-28[m
 ### Fixed[m
 - Problem with using `[TARGET]` inside of `right`.[m
[1mdiff --git a/docassemble_base/docassemble/base/filter.py b/docassemble_base/docassemble/base/filter.py[m
[1mindex 0ee5ef55..5edb1397 100644[m
[1m--- a/docassemble_base/docassemble/base/filter.py[m
[1m+++ b/docassemble_base/docassemble/base/filter.py[m
[36m@@ -554,10 +554,10 @@[m [mdef html_filter(text, status=None, question=None, embedder=None, default_image_w[m
     #     text = re.sub(r'\[FIELD ([^\]]+)\]', 'ERROR: FIELD cannot be used here', text)[m
     text = re.sub(r'\[TARGET ([^\]]+)\]', target_html, text)[m
     if docassemble.base.functions.this_thread.evaluation_context != 'docx':[m
[31m-        text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_url_string(x, emoji=True, question=question, external=external), text)[m
[31m-        text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', lambda x: image_url_string(x, question=question, external=external), text)[m
[31m-        text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_url_string(x, question=question, external=external), text)[m
[31m-        text = re.sub(r'\[FILE ([^,\]]+)\]', lambda x: image_url_string(x, question=question, default_image_width=default_image_width, external=external), text)[m
[32m+[m[32m        text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_url_string(x, emoji=True, question=question, external=external, status=status), text)[m
[32m+[m[32m        text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', lambda x: image_url_string(x, question=question, external=external, status=status), text)[m
[32m+[m[32m        text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_url_string(x, question=question, external=external, status=status), text)[m
[32m+[m[32m        text = re.sub(r'\[FILE ([^,\]]+)\]', lambda x: image_url_string(x, question=question, default_image_width=default_image_width, external=external, status=status), text)[m
         text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', qr_url_string, text)[m
         text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+)\]', qr_url_string, text)[m
         text = re.sub(r'\[QR ([^,\]]+)\]', qr_url_string, text)[m
[36m@@ -755,6 +755,8 @@[m [mdef image_as_rtf(match, question=None):[m
     if width == 'full':[m
         width_supplied = False[m
     file_reference = match.group(1)[m
[32m+[m[32m    if question and file_reference in question.interview.images:[m
[32m+[m[32m        file_reference = question.interview.images[file_reference].get_reference()[m
     file_info = server.file_finder(file_reference, convert={'svg': 'png', 'gif': 'png'}, question=question)[m
     if 'path' not in file_info:[m
         return ''[m
[36m@@ -903,7 +905,7 @@[m [mdef pixels_in(length):[m
     logmessage("Could not read " + str(length) + "\n")[m
     return(300)[m
 [m
[31m-def image_url_string(match, emoji=False, question=None, playground=False, default_image_width=None, external=False):[m
[32m+[m[32mdef image_url_string(match, emoji=False, question=None, playground=False, default_image_width=None, external=False, status=None):[m
     file_reference = match.group(1)[m
     try:[m
         width = match.group(2)[m
[36m@@ -922,9 +924,13 @@[m [mdef image_url_string(match, emoji=False, question=None, playground=False, defaul[m
             alt_text = ''[m
     else:[m
         alt_text = ''[m
[31m-    return image_url(file_reference, alt_text, width, emoji=emoji, question=question, playground=playground, external=external)[m
[32m+[m[32m    return image_url(file_reference, alt_text, width, emoji=emoji, question=question, playground=playground, external=external, status=status)[m
 [m
[31m-def image_url(file_reference, alt_text, width, emoji=False, question=None, playground=False, external=False):[m
[32m+[m[32mdef image_url(file_reference, alt_text, width, emoji=False, question=None, playground=False, external=False, status=None):[m
[32m+[m[32m    if question and file_reference in question.interview.images:[m
[32m+[m[32m        if status and question.interview.images[file_reference].attribution is not None:[m
[32m+[m[32m            status.attributions.add(question.interview.images[file_reference].attribution)[m
[32m+[m[32m        file_reference = question.interview.images[file_reference].get_reference()[m
     file_info = server.file_finder(file_reference, question=question)[m
     if 'mimetype' in file_info and file_info['mimetype']:[m
         if re.search(r'^audio', file_info['mimetype']):[m
[36m@@ -1024,6 +1030,8 @@[m [mdef convert_pixels(match):[m
 [m
 def image_include_string(match, emoji=False, question=None):[m
     file_reference = match.group(1)[m
[32m+[m[32m    if question and file_reference in question.interview.images:[m
[32m+[m[32m        file_reference = question.interview.images[file_reference].get_reference()[m
     try:[m
         width = match.group(2)[m
         assert width != 'None'[m
[36m@@ -1057,6 +1065,8 @@[m [mdef image_include_string(match, emoji=False, question=None):[m
 [m
 def image_include_docx(match, question=None):[m
     file_reference = match.group(1)[m
[32m+[m[32m    if question and file_reference in question.interview.images:[m
[32m+[m[32m        file_reference = question.interview.images[file_reference].get_reference()[m
     try:[m
         width = match.group(2)[m
         assert width != 'None'[m
[36m@@ -1612,6 +1622,8 @@[m [mdef replace_fields(string, status=None, embedder=None):[m
 [m
 def image_include_docx_template(match, question=None):[m
     file_reference = match.group(1)[m
[32m+[m[32m    if question and file_reference in question.interview.images:[m
[32m+[m[32m        file_reference = question.interview.images[file_reference].get_reference()[m
     try:[m
         width = match.group(2)[m
         assert width != 'None'[m
[1mdiff --git a/docassemble_base/docassemble/base/standardformatter.py b/docassemble_base/docassemble/base/standardformatter.py[m
[1mindex f9dde654..6d335a4f 100644[m
[1m--- a/docassemble_base/docassemble/base/standardformatter.py[m
[1m+++ b/docassemble_base/docassemble/base/standardformatter.py[m
[36m@@ -1054,7 +1054,7 @@[m [mdef as_html(status, url_for, debug, root, validation_rules, field_error, the_pro[m
                     for key in ('minlength', 'maxlength'):[m
                         if hasattr(field, 'extras') and key in field.extras and key in status.extras:[m
                             #sys.stderr.write("Adding validation rule for " + str(key) + "\n")[m
[31m-                            validation_rules['rules'][the_saveas][key] = int(status.extras[key][field.number])[m
[32m+[m[32m                            validation_rules['rules'][the_saveas][key] = int(float(status.extras[key][field.number]))[m
                             if key == 'minlength':[m
                                 validation_rules['messages'][the_saveas][key] = field.validation_message(key, status, word("You must type at least %s characters."), parameters=tuple([status.extras[key][field.number]]))[m
                             elif key == 'maxlength':[m
[36m@@ -1082,7 +1082,7 @@[m [mdef as_html(status, url_for, debug, root, validation_rules, field_error, the_pro[m
                                     checkbox_messages['checkatleast'] = field.validation_message('checkbox minlength', status, word("Please select one."))[m
                                 else:[m
                                     checkbox_messages['checkatleast'] = field.validation_message('checkbox minlength', status, word("Please select at least %s."), parameters=tuple([status.extras['minlength'][field.number]]))[m
[31m-                                if int(status.extras['minlength'][field.number]) > 0:[m
[32m+[m[32m                                if int(float(status.extras['minlength'][field.number])) > 0:[m
                                     if 'nota' not in status.extras:[m
                                         status.extras['nota'] = dict()[m
                                     status.extras['nota'][field.number] = False[m
[36m@@ -2437,9 +2437,9 @@[m [mdef input_for(status, field, wide=False, embedded=False):[m
             maximagesize = ''[m
             if 'max_image_size' in status.extras:[m
                 if status.extras['max_image_size']:[m
[31m-                    maximagesize = 'data-maximagesize="' + str(int(status.extras['max_image_size'])) + '" '[m
[32m+[m[32m                    maximagesize = 'data-maximagesize="' + str(int(float(status.extras['max_image_size']))) + '" '[m
             elif status.question.interview.max_image_size:[m
[31m-                maximagesize = 'data-maximagesize="' + str(int(status.question.interview.max_image_size)) + '" '[m
[32m+[m[32m                maximagesize = 'data-maximagesize="' + str(int(float(status.question.interview.max_image_size))) + '" '[m
             imagetype = ''[m
             if 'image_type' in status.extras:[m
                 if status.extras['image_type']:[m
[36m@@ -2489,7 +2489,7 @@[m [mdef input_for(status, field, wide=False, embedded=False):[m
                 output += '</span>'[m
         elif hasattr(field, 'inputtype') and field.inputtype == 'ajax':[m
             if defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)):[m
[31m-                if field.datatype in ('currency', 'number') and hasattr(field, 'extras') and 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step'] and int(status.extras['step'][field.number]) == float(status.extras['step'][field.number]):[m
[32m+[m[32m                if field.datatype in ('currency', 'number') and hasattr(field, 'extras') and 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step'] and int(float(status.extras['step'][field.number])) == float(status.extras['step'][field.number]):[m
                     defaultvalue = int(float(defaultvalue))[m
                 defaultstring = ' value=' + fix_double_quote(str(defaultvalue))[m
                 default_val = defaultvalue[m
[36m@@ -2528,7 +2528,7 @@[m [mdef input_for(status, field, wide=False, embedded=False):[m
                     the_date = format_datetime(defaultvalue, format='yyyy-MM-ddTHH:mm')[m
                     if the_date != word("Bad date"):[m
                         defaultvalue = the_date[m
[31m-                elif field.datatype in ('currency', 'number') and hasattr(field, 'extras') and 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step'] and int(status.extras['step'][field.number]) == float(status.extras['step'][field.number]):[m
[32m+[m[32m                elif field.datatype in ('currency', 'number') and hasattr(field, 'extras') and 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step'] and int(float(status.extras['step'][field.number])) == float(status.extras['step'][field.number]):[m
                     defaultvalue = int(float(defaultvalue))[m
                 defaultstring = ' value=' + fix_double_quote(str(defaultvalue))[m
             elif isinstance(defaultvalue, datetime.datetime):[m
[1mdiff --git a/docassemble_base/docassemble/base/util.py b/docassemble_base/docassemble/base/util.py[m
[1mindex ef1a972b..2be16e1e 100644[m
[1m--- a/docassemble_base/docassemble/base/util.py[m
[1m+++ b/docassemble_base/docassemble/base/util.py[m
[36m@@ -1280,6 +1280,9 @@[m [mclass Name(DAObject):[m
     def lastfirst(self):[m
         """This method is included for compatibility with other types of names."""[m
         return(self.text)[m
[32m+[m[32m    def middle_initial(self, with_period=True):[m
[32m+[m[32m        """This method is included for compatibility with other types of names."""[m
[32m+[m[32m        return('')[m
     def defined(self):[m
         """Returns True if the name has been defined.  Otherwise, returns False."""[m
         return hasattr(self, 'text')[m
[36m@@ -1310,12 +1313,12 @@[m [mclass IndividualName(Name):[m
         if not self.uses_parts:[m
             return super().full()[m
         names = [self.first][m
[31m-        if hasattr(self, 'middle') and len(self.middle):[m
[32m+[m[32m        if hasattr(self, 'middle'):[m
             if middle is False or middle is None:[m
                 pass[m
             elif middle == 'initial':[m
[31m-                names.append(self.middle[0] + '.')[m
[31m-            else:[m
[32m+[m[32m                names.append(self.middle_initial())[m
[32m+[m[32m            elif len(self.middle):[m
                 names.append(self.middle)[m
         if hasattr(self, 'last') and len(self.last):[m
             names.append(self.last)[m
[36m@@ -1344,6 +1347,14 @@[m [mclass IndividualName(Name):[m
         if hasattr(self, 'middle') and self.middle:[m
             output += " " + self.middle[0] + '.'[m
         return output[m
[32m+[m[32m    def middle_initial(self, with_period=True):[m
[32m+[m[32m        """Returns the middle initial, or the empty string if the name does not have a middle component."""[m
[32m+[m[32m        if len(self.middle) == 0:[m
[32m+[m[32m            return ''[m
[32m+[m[32m        if with_period:[m
[32m+[m[32m            return self.middle[0] + '.'[m
[32m+[m[32m        else:[m
[32m+[m[32m            return self.middle[0] + '.'[m
 [m
 class Address(DAObject):[m
     """A geographic address."""[m
[1mdiff --git a/docassemble_webapp/docassemble/webapp/server.py b/docassemble_webapp/docassemble/webapp/server.py[m
[1mindex 7bfef753..d04174db 100644[m
[1m--- a/docassemble_webapp/docassemble/webapp/server.py[m
[1m+++ b/docassemble_webapp/docassemble/webapp/server.py[m
[36m@@ -40,6 +40,7 @@[m [mSTRICT_MODE = daconfig.get('restrict input variables', False)[m
 PACKAGE_PROTECTION = daconfig.get('package protection', True)[m
 [m
 HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)[m
[32m+[m[32mGITHUB_BRANCH = daconfig.get('github default branch name', 'main')[m
 request_active = True[m
 [m
 default_playground_yaml = """metadata:[m
[36m@@ -2872,10 +2873,10 @@[m [mdef install_zip_package(packagename, file_number):[m
     db.session.commit()[m
     return[m
 [m
[31m-def install_git_package(packagename, giturl, branch=None):[m
[32m+[m[32mdef install_git_package(packagename, giturl, branch):[m
     #logmessage("install_git_package: " + packagename + " " + str(giturl))[m
     if branch is None or str(branch).lower().strip() in ('none', ''):[m
[31m-        branch = 'master'[m
[32m+[m[32m        branch = GITHUB_BRANCH[m
     if Package.query.filter_by(name=packagename).first() is None and Package.query.filter_by(giturl=giturl).with_for_update().first() is None:[m
         package_auth = PackageAuth(user_id=current_user.id)[m
         package_entry = Package(name=packagename, giturl=giturl, package_auth=package_auth, version=1, active=True, type='git', upload=None, limitation=None, gitbranch=branch)[m
[36m@@ -9480,7 +9481,10 @@[m [mdef index(action_argument=None, refer=None):[m
             $(this).addClass("dainvisible");[m
             $(".da-first-delete").removeClass("dainvisible");[m
             rationalizeListCollect();[m
[31m-            $('div[data-collectnum="' + num + '"]').find('input, textarea, select').first().focus();[m
[32m+[m[32m            var elem = $('div[data-collectnum="' + num + '"]').find('input, textarea, select').first();[m
[32m+[m[32m            if ($(elem).visible()){[m
[32m+[m[32m              $(elem).focus();[m
[32m+[m[32m            }[m
           }[m
           return false;[m
         });[m
[36m@@ -9794,7 +9798,7 @@[m [mdef index(action_argument=None, refer=None):[m
         if (!daJsEmbed){[m
           setTimeout(function(){[m
             var firstInput = $("#daform .da-field-container").not(".da-field-container-note").first().find("input, textarea, select").filter(":visible").first();[m
[31m-            if (firstInput.length > 0){[m
[32m+[m[32m            if (firstInput.length > 0 && $(firstInput).visible()){[m
               $(firstInput).focus();[m
               var inputType = $(firstInput).attr('type');[m
               if ($(firstInput).prop('tagName') != 'SELECT' && inputType != "checkbox" && inputType != "radio" && inputType != "hidden" && inputType != "submit" && inputType != "file" && inputType != "range" && inputType != "number" && inputType != "date" && inputType != "time"){[m
[36m@@ -9811,7 +9815,7 @@[m [mdef index(action_argument=None, refer=None):[m
             }[m
             else {[m
               var firstButton = $("#danavbar-collapse .nav-link").filter(':visible').first();[m
[31m-              if (firstButton.length > 0){[m
[32m+[m[32m              if (firstButton.length > 0 && $(firstButton).visible()){[m
                 setTimeout(function(){[m
                   $(firstButton).focus();[m
                   $(firstButton).blur();[m
[36m@@ -13976,6 +13980,15 @@[m [mdef update_package():[m
         del session['taskwait'][m
     #pip.utils.logging._log_state = threading.local()[m
     #pip.utils.logging._log_state.indentation = 0[m
[32m+[m[32m    if request.method == 'GET' and app.config['USE_GITHUB'] and r.get('da:using_github:userid:' + str(current_user.id)) is not None:[m
[32m+[m[32m        storage = RedisCredStorage(app='github')[m
[32m+[m[32m        credentials = storage.get()[m
[32m+[m[32m        if not credentials or credentials.invalid:[m
[32m+[m[32m            state_string = random_string(16)[m
[32m+[m[32m            session['github_next'] = json.dumps(dict(state=state_string, path='playground_packages', arguments=request.args))[m
[32m+[m[32m            flow = get_github_flow()[m
[32m+[m[32m            uri = flow.step1_get_authorize_url(state=state_string)[m
[32m+[m[32m            return redirect(uri)[m
     form = UpdatePackageForm(request.form)[m
     form.gitbranch.choices = [('', "Not applicable")][m
     if form.gitbranch.data:[m
[36m@@ -14002,9 +14015,9 @@[m [mdef update_package():[m
                         db.session.commit()[m
                     if existing_package.type == 'git' and existing_package.giturl is not None:[m
                         if existing_package.gitbranch:[m
[31m-                            install_git_package(target, existing_package.giturl, branch=existing_package.gitbranch)[m
[32m+[m[32m                            install_git_package(target, existing_package.giturl, existing_package.gitbranch)[m
                         else:[m
[31m-                            install_git_package(target, existing_package.giturl)[m
[32m+[m[32m                            install_git_package(target, existing_package.giturl, get_master_branch(existing_package.giturl))[m
                     elif existing_package.type == 'pip':[m
                         if existing_package.name == 'docassemble.webapp' and existing_package.limitation and not limitation:[m
                             existing_package.limitation = None[m
[36m@@ -14044,6 +14057,8 @@[m [mdef update_package():[m
             if form.giturl.data:[m
                 giturl = form.giturl.data.strip()[m
                 branch = form.gitbranch.data.strip()[m
[32m+[m[32m                if not branch:[m
[32m+[m[32m                    branch = get_master_branch(giturl)[m
                 packagename = re.sub(r'/*$', '', giturl)[m
                 packagename = re.sub(r'^git+', '', packagename)[m
                 packagename = re.sub(r'#.*', '', packagename)[m
[36m@@ -14051,10 +14066,7 @@[m [mdef update_package():[m
                 packagename = re.sub(r'.*/', '', packagename)[m
                 packagename = re.sub(r'^docassemble-', 'docassemble.', packagename)[m
                 if user_can_edit_package(giturl=giturl) and user_can_edit_package(pkgname=packagename):[m
[31m-                    if branch:[m
[31m-                        install_git_package(packagename, giturl, branch=branch)[m
[31m-                    else:[m
[31m-                        install_git_package(packagename, giturl)[m
[32m+[m[32m                    install_git_package(packagename, giturl, branch)[m
                     result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s())[m
                     session['taskwait'] = result.id[m
                     return redirect(url_for('update_package_wait'))[m
[36m@@ -14083,7 +14095,7 @@[m [mdef update_package():[m
     form.giturl.data = None[m
     extra_js = """[m
     <script>[m
[31m-      var default_branch = """ + json.dumps(branch if branch else 'master') + """;[m
[32m+[m[32m      var default_branch = """ + json.dumps(branch if branch else 'null') + """;[m
       function get_branches(){[m
         var elem = $("#gitbranch");[m
         elem.empty();[m
[36m@@ -14100,11 +14112,22 @@[m [mdef update_package():[m
           if (data.success){[m
             var n = data.result.length;[m
             if (n > 0){[m
[32m+[m[32m              var default_to_use = default_branch;[m
[32m+[m[32m              var to_try = [default_branch, """ + json.dumps(GITHUB_BRANCH) + """, 'master', 'main'];[m
[32m+[m[32m            outer:[m
[32m+[m[32m              for (var j = 0; j < 4; j++){[m
[32m+[m[32m                for (var i = 0; i < n; i++){[m
[32m+[m[32m                  if (data.result[i].name == to_try[j]){[m
[32m+[m[32m                    default_to_use = to_try[j];[m
[32m+[m[32m                    break outer;[m
[32m+[m[32m                  }[m
[32m+[m[32m                }[m
[32m+[m[32m              }[m
               elem.empty();[m
               for (var i = 0; i < n; i++){[m
                 opt = $("<option><\/option>");[m
                 opt.attr("value", data.result[i].name).text(data.result[i].name);[m
[31m-                if (data.result[i].name == default_branch){[m
[32m+[m[32m                if (data.result[i].name == default_to_use){[m
                   opt.prop('selected', true);[m
                 }[m
                 $(elem).append(opt);[m
[36m@@ -14156,6 +14179,12 @@[m [mdef update_package():[m
     response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'[m
     return response[m
 [m
[32m+[m[32mdef get_master_branch(giturl):[m
[32m+[m[32m    try:[m
[32m+[m[32m        return get_repo_info(giturl).get('default_branch', GITHUB_BRANCH)[m
[32m+[m[32m    except:[m
[32m+[m[32m        return GITHUB_BRANCH[m
[32m+[m
 # @app.route('/testws', methods=['GET', 'POST'])[m
 # def test_websocket():[m
 #     script = '<script type="text/javascript" src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>' + """<script type="text/javascript" charset="utf-8">[m
[36m@@ -14213,6 +14242,7 @@[m [mdef create_playground_package():[m
         branch_is_new = True[m
     else:[m
         branch_is_new = False[m
[32m+[m[32m    force_branch_creation = False[m
     if app.config['USE_GITHUB']:[m
         github_auth = r.get('da:using_github:userid:' + str(current_user.id))[m
     else:[m
[36m@@ -14437,13 +14467,14 @@[m [mdef create_playground_package():[m
                 git_prefix = "GIT_SSH=" + ssh_script.name + " "[m
                 ssh_url = commit_repository.get('ssh_url', None)[m
                 github_url = commit_repository.get('html_url', None)[m
[32m+[m[32m                commit_branch = commit_repository.get('default_branch', GITHUB_BRANCH)[m
                 if ssh_url is None:[m
                     raise DAError("create_playground_package: could not obtain ssh_url for package")[m
                 output = ''[m
                 if branch:[m
                     branch_option = '-b ' + str(branch) + ' '[m
                 else:[m
[31m-                    branch_option = '-b master '[m
[32m+[m[32m                    branch_option = '-b ' + commit_branch + ' '[m
                 tempbranch = 'playground' + random_string(5)[m
                 packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))[m
                 the_user_name = str(current_user.first_name) + " " + str(current_user.last_name)[m
[36m@@ -14471,6 +14502,7 @@[m [mdef create_playground_package():[m
                     except subprocess.CalledProcessError as err:[m
                         output += err.output.decode()[m
                         raise DAError("create_playground_package: error running git config user.email.  " + output)[m
[32m+[m[32m                    output += "Doing git add README.MD\n"[m
                     try:[m
                         output += subprocess.check_output(["git", "add", "README.md"], cwd=packagedir, stderr=subprocess.STDOUT).decode()[m
                     except subprocess.CalledProcessError as err:[m
[36m@@ -14482,15 +14514,21 @@[m [mdef create_playground_package():[m
                     except subprocess.CalledProcessError as err:[m
                         output += err.output.decode()[m
                         raise DAError("create_playground_package: error running git commit -m \"first commit\".  " + output)[m
[31m-                    output += "Doing git remote add origin " + ssh_url + "\n"[m
[32m+[m[32m                    output += "Doing git branch -M " + commit_branch + "\n"[m
[32m+[m[32m                    try:[m
[32m+[m[32m                        output += subprocess.check_output(["git", "branch", "-M", commit_branch], cwd=packagedir, stderr=subprocess.STDOUT).decode()[m
[32m+[m[32m                    except subprocess.CalledProcessError as err:[m
[32m+[m[32m                        output += err.output.decode()[m
[32m+[m[32m                        raise DAError("create_playground_package: error running git branch -M " + commit_branch + ".  " + output)[m
[32m+[m[32m                    output += "Doing git remote add origin " + ssh_url + "\n"[m[41m                        [m
                     try:[m
                         output += subprocess.check_output(["git", "remote", "add", "origin", ssh_url], cwd=packagedir, stderr=subprocess.STDOUT).decode()[m
                     except subprocess.CalledProcessError as err:[m
                         output += err.output.decode()[m
                         raise DAError("create_playground_package: error running git remote add origin.  " + output)[m
[31m-                    output += "Doing " + git_prefix + "git push -u origin master\n"[m
[32m+[m[32m                    output += "Doing " + git_prefix + "git push -u origin " + commit_branch + "\n"[m
                     try:[m
[31m-                        output += subprocess.check_output(git_prefix + "git push -u origin master", cwd=packagedir, stderr=subprocess.STDOUT, shell=True).decode()[m
[32m+[m[32m                        output += subprocess.check_output(git_prefix + "git push -u origin " + commit_branch, cwd=packagedir, stderr=subprocess.STDOUT, shell=True).decode()[m
                     except subprocess.CalledProcessError as err:[m
                         output += err.output.decode()[m
                         raise DAError("create_playground_package: error running first git push.  " + output)[m
[36m@@ -14529,6 +14567,13 @@[m [mdef create_playground_package():[m
                     except subprocess.CalledProcessError as err:[m
                         output += err.output.decode()[m
                         raise DAError("create_playground_package: error running git config user.email.  " + output)[m
[32m+[m[32m                    output += "Trying git checkout " + commit_branch + "\n"[m
[32m+[m[32m                    try:[m
[32m+[m[32m                        output += subprocess.check_output(["git", "checkout", commit_branch], cwd=packagedir, stderr=subprocess.STDOUT).decode()[m
[32m+[m[32m                    except subprocess.CalledProcessError as err:[m
[32m+[m[32m                        output += commit_branch + " is a new branch\n"[m
[32m+[m[32m                        force_branch_creation = True[m
[32m+[m[32m                        branch = commit_branch[m
                 output += "Doing git checkout -b " + tempbranch + "\n"[m
                 try:[m
                     output += subprocess.check_output(git_prefix + "git checkout -b " + tempbranch, cwd=packagedir, stderr=subprocess.STDOUT, shell=True).decode()[m
[36m@@ -14556,8 +14601,8 @@[m [mdef create_playground_package():[m
                 if branch:[m
                     the_branch = branch[m
                 else:[m
[31m-                    the_branch = 'master'[m
[31m-                if branch_is_new and the_branch != 'master':[m
[32m+[m[32m                    the_branch = commit_branch[m
[32m+[m[32m                if force_branch_creation or (branch_is_new and the_branch != commit_branch):[m
                     output += "Doing git checkout -b " + the_branch + "\n"[m
                     try:[m
                         output += subprocess.check_output(git_prefix + "git checkout -b " + the_branch, cwd=packagedir, stderr=subprocess.STDOUT, shell=True).decode()[m
[36m@@ -14565,24 +14610,18 @@[m [mdef create_playground_package():[m
                         output += err.output.decode()[m
                         raise DAError("create_playground_package: error running git checkout.  " + output)[m
                 else:[m
[31m-                    output += "Doing git checkout " + the_branch + "\n"[m
[31m-                    try:[m
[31m-                        output += subprocess.check_output(git_prefix + "git checkout " + the_branch, cwd=packagedir, stderr=subprocess.STDOUT, shell=True).decode()[m
[31m-                    except subprocess.CalledProcessError as err:[m
[31m-                        output += err.output.decode()[m
[31m-                        raise DAError("create_playground_package: error running git checkout.  " + output)[m
                     output += "Doing git merge --squash " + tempbranch + "\n"[m
                     try:[m
                         output += subprocess.check_output(git_prefix + "git merge --squash " + tempbranch, cwd=packagedir, stderr=subprocess.STDOUT, shell=True).decode()[m
                     except subprocess.CalledProcessError as err:[m
                         output += err.output.decode()[m
[31m-                        raise DAError("create_playground_package: error running git merge.  " + output)[m
[32m+[m[32m                        raise DAError("create_playground_package: error running git merge --squash " + tempbranch + ".  " + output)[m
                     output += "Doing git commit\n"[m
                     try:[m
                         output += subprocess.check_output(["git", "commit", "-am", str(commit_message)], cwd=packagedir, stderr=subprocess.STDOUT).decode()[m
                     except subprocess.CalledProcessError as err:[m
                         output += err.output.decode()[m
[31m-                        raise DAError("create_playground_package: error running git commit.  " + output)[m
[32m+[m[32m                        raise DAError("create_playground_package: error running git commit -am " + str(commit_message) + ".  " + output)[m
                 if False:[m
                     try:[m
                         output += subprocess.check_output(["git", "remote", "add", "origin", ssh_url], cwd=packagedir, stderr=subprocess.STDOUT).decode()[m
[36m@@ -16971,7 +17010,7 @@[m [mdef pull_playground_package():[m
     branch = request.args.get('branch')[m
     extra_js = """[m
     <script>[m
[31m-      var default_branch = """ + json.dumps(branch if branch else 'master') + """;[m
[32m+[m[32m      var default_branch = """ + json.dumps(branch if branch else GITHUB_BRANCH) + """;[m
       function get_branches(){[m
         var elem = $("#github_branch");[m
         elem.empty();[m
[36m@@ -16988,11 +17027,22 @@[m [mdef pull_playground_package():[m
           if (data.success){[m
             var n = data.result.length;[m
             if (n > 0){[m
[32m+[m[32m              var default_to_use = default_branch;[m
[32m+[m[32m              var to_try = [default_branch, """ + json.dumps(GITHUB_BRANCH) + """, 'master', 'main'];[m
[32m+[m[32m            outer:[m
[32m+[m[32m              for (var j = 0; j < 4; j++){[m
[32m+[m[32m                for (var i = 0; i < n; i++){[m
[32m+[m[32m                  if (data.result[i].name == to_try[j]){[m
[32m+[m[32m                    default_to_use = to_try[j];[m
[32m+[m[32m                    break outer;[m
[32m+[m[32m                  }[m
[32m+[m[32m                }[m
[32m+[m[32m              }[m
               elem.empty();[m
               for (var i = 0; i < n; i++){[m
                 opt = $("<option><\/option>");[m
                 opt.attr("value", data.result[i].name).text(data.result[i].name);[m
[31m-                if (data.result[i].name == default_branch){[m
[32m+[m[32m                if (data.result[i].name == default_to_use){[m
                   opt.prop('selected', true);[m
                 }[m
                 $(elem).append(opt);[m
[36m@@ -17011,19 +17061,55 @@[m [mdef pull_playground_package():[m
     response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'[m
     return response[m
 [m
[31m-@app.route('/get_git_branches', methods=['GET'])[m
[31m-@login_required[m
[31m-@roles_required(['developer', 'admin'])[m
[31m-def get_git_branches():[m
[31m-    if not app.config['ENABLE_PLAYGROUND']:[m
[31m-        return ('File not found', 404)[m
[31m-    if 'url' not in request.args:[m
[31m-        return ('File not found', 404)[m
[32m+[m[32mdef get_branches_of_repo(giturl):[m
[32m+[m[32m    repo_name = re.sub(r'/*$', '', giturl)[m
[32m+[m[32m    m = re.search(r'//(.+):x-oauth-basic@github.com', repo_name)[m
[32m+[m[32m    if m:[m
[32m+[m[32m        access_token = m.group(1)[m
[32m+[m[32m    else:[m
[32m+[m[32m        access_token = None[m
[32m+[m[32m    repo_name = re.sub(r'^http.*github.com/', '', repo_name)[m
[32m+[m[32m    repo_name = re.sub(r'.*@github.com:', '', repo_name)[m
[32m+[m[32m    repo_name = re.sub(r'.git$', '', repo_name)[m
     if app.config['USE_GITHUB']:[m
         github_auth = r.get('da:using_github:userid:' + str(current_user.id))[m
     else:[m
         github_auth = None[m
[31m-    repo_name = re.sub(r'/*$', '', request.args['url'].strip())[m
[32m+[m[32m    if github_auth and access_token is None:[m
[32m+[m[32m        storage = RedisCredStorage(app='github')[m
[32m+[m[32m        credentials = storage.get()[m
[32m+[m[32m        if not credentials or credentials.invalid:[m
[32m+[m[32m            http = httplib2.Http()[m
[32m+[m[32m        else:[m
[32m+[m[32m            http = credentials.authorize(httplib2.Http())[m
[32m+[m[32m    else:[m
[32m+[m[32m        http = httplib2.Http()[m
[32m+[m[32m    the_url = "https://api.github.com/repos/" + repo_name + '/branches'[m
[32m+[m[32m    branches = list()[m
[32m+[m[32m    if access_token:[m
[32m+[m[32m        resp, content = http.request(the_url, "GET", headers=dict(Authorization="token " + access_token))[m
[32m+[m[32m    else:[m
[32m+[m[32m        resp, content = http.request(the_url, "GET")[m
[32m+[m[32m    if int(resp['status']) == 200:[m
[32m+[m[32m        branches.extend(json.loads(content.decode()))[m
[32m+[m[32m        while True:[m
[32m+[m[32m            next_link = get_next_link(resp)[m
[32m+[m[32m            if next_link:[m
[32m+[m[32m                if access_token:[m
[32m+[m[32m                    resp, content = http.request(next_link, "GET", headers=dict(Authorization="token " + access_token))[m
[32m+[m[32m                else:[m
[32m+[m[32m                    resp, content = http.request(next_link, "GET")[m
[32m+[m[32m                if int(resp['status']) != 200:[m
[32m+[m[32m                    raise Exception(repo_name + " fetch failed")[m
[32m+[m[32m                else:[m
[32m+[m[32m                    branches.extend(json.loads(content.decode()))[m
[32m+[m[32m            else:[m
[32m+[m[32m                break[m
[32m+[m[32m        return branches[m
[32m+[m[32m    raise Exception(the_url + " fetch failed on first try; got " + str(resp['status']))[m
[32m+[m
[32m+[m[32mdef get_repo_info(giturl):[m
[32m+[m[32m    repo_name = re.sub(r'/*$', '', giturl)[m
     m = re.search(r'//(.+):x-oauth-basic@github.com', repo_name)[m
     if m:[m
         access_token = m.group(1)[m
[36m@@ -17032,41 +17118,42 @@[m [mdef get_git_branches():[m
     repo_name = re.sub(r'^http.*github.com/', '', repo_name)[m
     repo_name = re.sub(r'.*@github.com:', '', repo_name)[m
     repo_name = re.sub(r'.git$', '', repo_name)[m
[31m-    try:[m
[31m-        if github_auth and access_token is None:[m
[31m-            storage = RedisCredStorage(app='github')[m
[31m-            credentials = storage.get()[m
[31m-            if not credentials or credentials.invalid:[m
[31m-                return jsonify(dict(success=False, reason="bad credentials"))[m
[31m-            http = credentials.authorize(httplib2.Http())[m
[31m-        else:[m
[32m+[m[32m    if app.config['USE_GITHUB']:[m
[32m+[m[32m        github_auth = r.get('da:using_github:userid:' + str(current_user.id))[m
[32m+[m[32m    else:[m
[32m+[m[32m        github_auth = None[m
[32m+[m[32m    if github_auth and access_token is None:[m
[32m+[m[32m        storage = RedisCredStorage(app='github')[m
[32m+[m[32m        credentials = storage.get()[m
[32m+[m[32m        if not credentials or credentials.invalid:[m
             http = httplib2.Http()[m
[31m-        the_url = "https://api.github.com/repos/" + repo_name + '/branches'[m
[31m-        branches = list()[m
[31m-        if access_token:[m
[31m-            resp, content = http.request(the_url, "GET", headers=dict(Authorization="token " + access_token))[m
         else:[m
[31m-            resp, content = http.request(the_url, "GET")[m
[31m-        if int(resp['status']) == 200:[m
[31m-            branches.extend(json.loads(content.decode()))[m
[31m-            while True:[m
[31m-                next_link = get_next_link(resp)[m
[31m-                if next_link:[m
[31m-                    if access_token:[m
[31m-                        resp, content = http.request(next_link, "GET", headers=dict(Authorization="token " + access_token))[m
[31m-                    else:[m
[31m-                        resp, content = http.request(next_link, "GET")[m
[31m-                    if int(resp['status']) != 200:[m
[31m-                        return jsonify(dict(success=False, reason=repo_name + " fetch failed"))[m
[31m-                    else:[m
[31m-                        branches.extend(json.loads(content.decode()))[m
[31m-                else:[m
[31m-                    break[m
[31m-            return jsonify(dict(success=True, result=branches))[m
[31m-        return jsonify(dict(success=False, reason=the_url + " fetch failed on first try; got " + str(resp['status'])))[m
[32m+[m[32m            http = credentials.authorize(httplib2.Http())[m
[32m+[m[32m    else:[m
[32m+[m[32m        http = httplib2.Http()[m
[32m+[m[32m    the_url = "https://api.github.com/repos/" + repo_name[m
[32m+[m[32m    branches = list()[m
[32m+[m[32m    if access_token:[m
[32m+[m[32m        resp, content = http.request(the_url, "GET", headers=dict(Authorization="token " + access_token))[m
[32m+[m[32m    else:[m
[32m+[m[32m        resp, content = http.request(the_url, "GET")[m
[32m+[m[32m    if int(resp['status']) == 200:[m
[32m+[m[32m        return(json.loads(content.decode()))[m
[32m+[m[32m    raise Exception(the_url + " fetch failed on first try; got " + str(resp['status']))[m
[32m+[m
[32m+[m[32m@app.route('/get_git_branches', methods=['GET'])[m
[32m+[m[32m@login_required[m
[32m+[m[32m@roles_required(['developer', 'admin'])[m
[32m+[m[32mdef get_git_branches():[m
[32m+[m[32m    if not app.config['ENABLE_PLAYGROUND']:[m
[32m+[m[32m        return ('File not found', 404)[m
[32m+[m[32m    if 'url' not in request.args:[m
[32m+[m[32m        return ('File not found', 404)[m
[32m+[m[32m    giturl = request.args['url'].strip()[m
[32m+[m[32m    try:[m
[32m+[m[32m        return jsonify(dict(success=True, result=get_branches_of_repo(giturl)))[m
     except Exception as err:[m
         return jsonify(dict(success=False, reason=str(err)))[m
[31m-    return jsonify(dict(success=False))[m
 [m
 def get_user_repositories(http):[m
     repositories = list()[m
[36m@@ -17190,6 +17277,15 @@[m [mdef playground_packages():[m
             can_publish_to_github = False[m
     else:[m
         can_publish_to_github = None[m
[32m+[m[32m    if can_publish_to_github and request.method == 'GET':[m
[32m+[m[32m        storage = RedisCredStorage(app='github')[m
[32m+[m[32m        credentials = storage.get()[m
[32m+[m[32m        if not credentials or credentials.invalid:[m
[32m+[m[32m            state_string = random_string(16)[m
[32m+[m[32m            session['github_next'] = json.dumps(dict(state=state_string, path='playground_packages', arguments=request.args))[m
[32m+[m[32m            flow = get_github_flow()[m
[32m+[m[32m            uri = flow.step1_get_authorize_url(state=state_string)[m
[32m+[m[32m            return redirect(uri)[m
     show_message = true_or_false(request.args.get('show_message', True))[m
     github_message = None[m
     pypi_message = None[m
[36m@@ -18014,10 +18110,16 @@[m [mdef playground_packages():[m
         branch_choices.append((br['name'], br['name']))[m
     if branch and branch in branch_names:[m
         form.github_branch.data = branch[m
[32m+[m[32m        default_branch = branch[m
     elif 'master' in branch_names:[m
         form.github_branch.data = 'master'[m
[32m+[m[32m        default_branch = 'master'[m
[32m+[m[32m    elif 'main' in branch_names:[m
[32m+[m[32m        form.github_branch.data = 'main'[m
[32m+[m[32m        default_branch = 'main'[m
[32m+[m[32m    else:[m
[32m+[m[32m        default_branch = GITHUB_BRANCH[m
     form.github_branch.choices = branch_choices[m
[31m-    default_branch = branch if branch else 'master'[m
     if form.author_name.data in ('', None) and current_user.first_name and current_user.last_name:[m
         form.author_name.data = current_user.first_name + " " + current_user.last_name[m
     if form.author_email.data in ('', None) and current_user.email:[m
[36m@@ -19558,7 +19660,7 @@[m [mdef playground_css_bundle():[m
 def js_bundle():[m
     base_path = pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.webapp'), os.path.join('docassemble', 'webapp', 'static'))[m
     output = ''[m
[31m-    for parts in [['app', 'jquery.min.js'], ['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['popper', 'umd', 'popper.min.js'], ['popper', 'umd', 'tooltip.min.js'], ['bootstrap', 'js', 'bootstrap.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.js'], ['app', 'socket.io.min.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js']]:[m
[32m+[m[32m    for parts in [['app', 'jquery.min.js'], ['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['app', 'jquery.visible.js'], ['popper', 'umd', 'popper.min.js'], ['popper', 'umd', 'tooltip.min.js'], ['bootstrap', 'js', 'bootstrap.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.js'], ['app', 'socket.io.min.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js']]:[m
         with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:[m
             output += fp.read()[m
         output += "\n"[m
[36m@@ -19588,7 +19690,7 @@[m [mdef js_admin_bundle():[m
 def js_bundle_wrap():[m
     base_path = pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.webapp'), os.path.join('docassemble', 'webapp', 'static'))[m
     output = '(function($) {'[m
[31m-    for parts in [['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['popper', 'umd', 'popper.min.js'], ['popper', 'umd', 'tooltip.min.js'], ['bootstrap', 'js', 'bootstrap.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.js'], ['app', 'socket.io.min.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js']]:[m
[32m+[m[32m    for parts in [['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['app', 'jquery.visible.js'], ['popper', 'umd', 'popper.min.js'], ['popper', 'umd', 'tooltip.min.js'], ['bootstrap', 'js', 'bootstrap.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.js'], ['app', 'socket.io.min.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js']]:[m
         with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:[m
             output += fp.read()[m
         output += "\n"[m
[36m@@ -19599,7 +19701,7 @@[m [mdef js_bundle_wrap():[m
 def js_bundle_no_query():[m
     base_path = pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.webapp'), os.path.join('docassemble', 'webapp', 'static'))[m
     output = ''[m
[31m-    for parts in [['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['popper', 'umd', 'popper.min.js'], ['popper', 'umd', 'tooltip.min.js'], ['bootstrap', 'js', 'bootstrap.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.js'], ['app', 'socket.io.min.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js']]:[m
[32m+[m[32m    for parts in [['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['app', 'jquery.visible.js'], ['popper', 'umd', 'popper.min.js'], ['popper', 'umd', 'tooltip.min.js'], ['bootstrap', 'js', 'bootstrap.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.js'], ['app', 'socket.io.min.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js']]:[m
         with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:[m
             output += fp.read()[m
         output += "\n"[m
[36m@@ -23953,9 +24055,9 @@[m [mdef api_package():[m
             if existing_package is not None:[m
                 if existing_package.type == 'git' and existing_package.giturl is not None:[m
                     if existing_package.gitbranch:[m
[31m-                        install_git_package(target, existing_package.giturl, branch=existing_package.gitbranch)[m
[32m+[m[32m                        install_git_package(target, existing_package.giturl, existing_package.gitbranch)[m
                     else:[m
[31m-                        install_git_package(target, existing_package.giturl)[m
[32m+[m[32m                        install_git_package(target, existing_package.giturl, get_master_branch(existing_package.giturl))[m
                 elif existing_package.type == 'pip':[m
                     if existing_package.name == 'docassemble.webapp' and existing_package.limitation:[m
                         existing_package.limitation = None[m
[36m@@ -23966,6 +24068,8 @@[m [mdef api_package():[m
         if 'github_url' in post_data:[m
             github_url = post_data['github_url'][m
             branch = post_data.get('branch', None)[m
[32m+[m[32m            if branch is None:[m
[32m+[m[32m                branch = get_master_branch(github_url)[m
             packagename = re.sub(r'/*$', '', github_url)[m
             packagename = re.sub(r'^git+', '', packagename)[m
             packagename = re.sub(r'#.*', '', packagename)[m
[36m@@ -23973,10 +24077,7 @@[m [mdef api_package():[m
             packagename = re.sub(r'.*/', '', packagename)[m
             packagename = re.sub(r'^docassemble-', 'docassemble.', packagename)[m
             if user_can_edit_package(giturl=github_url) and user_can_edit_package(pkgname=packagename):[m
[31m-                if branch:[m
[31m-                    install_git_package(packagename, github_url, branch=branch)[m
[31m-                else:[m
[31m-                    install_git_package(packagename, github_url)[m
[32m+[m[32m                install_git_package(packagename, github_url, branch)[m
                 result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s())[m
                 return jsonify_task(result)[m
             else:[m
[1mdiff --git a/docassemble_webapp/docassemble/webapp/static/app/app.css b/docassemble_webapp/docassemble/webapp/static/app/app.css[m
[1mindex 2c77910b..95a2b9b8 100644[m
[1m--- a/docassemble_webapp/docassemble/webapp/static/app/app.css[m
[1m+++ b/docassemble_webapp/docassemble/webapp/static/app/app.css[m
[36m@@ -2274,3 +2274,13 @@[m [mtr:first-child .datableup, tr:last-child .databledown {[m
 body.da-pad-for-footer {[m
   margin-bottom: 60px;[m
 }[m
[32m+[m
[32m+[m[32minput::-webkit-outer-spin-button,[m
[32m+[m[32minput::-webkit-inner-spin-button {[m
[32m+[m[32m  -webkit-appearance: none;[m
[32m+[m[32m  margin: 0;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32minput[type=number] {[m
[32m+[m[32m  -moz-appearance: textfield;[m
[32m+[m[32m}[m
[1mdiff --git a/docassemble_webapp/docassemble/webapp/static/app/bundle.css b/docassemble_webapp/docassemble/webapp/static/app/bundle.css[m
[1mindex c013f1a9..8c1a26fc 100644[m
[1m--- a/docassemble_webapp/docassemble/webapp/static/app/bundle.css[m
[1m+++ b/docassemble_webapp/docassemble/webapp/static/app/bundle.css[m
[36m@@ -2120,7 +2120,7 @@[m [mdiv.danavbar {[m
 }[m
 [m
 .dayesnospacing + .dayesnospacing {[m
[31m-    margin-top: -15px;[m
[32m+[m[32m    margin-top: -1.0rem;[m
 }[m
 [m
 .dainterviewhaserror {[m
[36m@@ -2755,3 +2755,13 @@[m [mbody.da-pad-for-footer {[m
   margin-bottom: 60px;[m
 }[m
 [m
[32m+[m[32minput::-webkit-outer-spin-button,[m
[32m+[m[32minput::-webkit-inner-spin-button {[m
[32m+[m[32m  -webkit-appearance: none;[m
[32m+[m[32m  margin: 0;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32minput[type=number] {[m
[32m+[m[32m  -moz-appearance: textfield;[m
[32m+[m[32m}[m
[32m+[m
[1mdiff --git a/docassemble_webapp/docassemble/webapp/static/app/bundle.js b/docassemble_webapp/docassemble/webapp/static/app/bundle.js[m
[1mindex f21b6769..2d9b1ef6 100644[m
[1m--- a/docassemble_webapp/docassemble/webapp/static/app/bundle.js[m
[1m+++ b/docassemble_webapp/docassemble/webapp/static/app/bundle.js[m
[36m@@ -9,6 +9,90 @@[m
  * https://jqueryvalidation.org/[m
  * Copyright (c) 2020 Jörn Zaefferer; Licensed MIT */[m
 !function(a){"function"==typeof define&&define.amd?define(["jquery","./jquery.validate.min"],a):"object"==typeof module&&module.exports?module.exports=a(require("jquery")):a(jQuery)}(function(a){return function(){function b(a){return a.replace(/<.[^<>]*?>/g," ").replace(/&nbsp;|&#160;/gi," ").replace(/[.(),;:!?%#$'\"_+=\/\-“”’]*/g,"")}a.validator.addMethod("maxWords",function(a,c,d){return this.optional(c)||b(a).match(/\b\w+\b/g).length<=d},a.validator.format("Please enter {0} words or less.")),a.validator.addMethod("minWords",function(a,c,d){return this.optional(c)||b(a).match(/\b\w+\b/g).length>=d},a.validator.format("Please enter at least {0} words.")),a.validator.addMethod("rangeWords",function(a,c,d){var e=b(a),f=/\b\w+\b/g;return this.optional(c)||e.match(f).length>=d[0]&&e.match(f).length<=d[1]},a.validator.format("Please enter between {0} and {1} words."))}(),a.validator.addMethod("abaRoutingNumber",function(a){var b=0,c=a.split(""),d=c.length;if(9!==d)return!1;for(var e=0;e<d;e+=3)b+=3*parseInt(c[e],10)+7*parseInt(c[e+1],10)+parseInt(c[e+2],10);return 0!==b&&b%10===0},"Please enter a valid routing number."),a.validator.addMethod("accept",function(b,c,d){var e,f,g,h="string"==typeof d?d.replace(/\s/g,""):"image/*",i=this.optional(c);if(i)return i;if("file"===a(c).attr("type")&&(h=h.replace(/[\-\[\]\/\{\}\(\)\+\?\.\\\^\$\|]/g,"\\$&").replace(/,/g,"|").replace(/\/\*/g,"/.*"),c.files&&c.files.length))for(g=new RegExp(".?("+h+")$","i"),e=0;e<c.files.length;e++)if(f=c.files[e],!f.type.match(g))return!1;return!0},a.validator.format("Please enter a value with a valid mimetype.")),a.validator.addMethod("alphanumeric",function(a,b){return this.optional(b)||/^\w+$/i.test(a)},"Letters, numbers, and underscores only please"),a.validator.addMethod("bankaccountNL",function(a,b){if(this.optional(b))return!0;if(!/^[0-9]{9}|([0-9]{2} ){3}[0-9]{3}$/.test(a))return!1;var c,d,e,f=a.replace(/ /g,""),g=0,h=f.length;for(c=0;c<h;c++)d=h-c,e=f.substring(c,c+1),g+=d*e;return g%11===0},"Please specify a valid bank account number"),a.validator.addMethod("bankorgiroaccountNL",function(b,c){return this.optional(c)||a.validator.methods.bankaccountNL.call(this,b,c)||a.validator.methods.giroaccountNL.call(this,b,c)},"Please specify a valid bank or giro account number"),a.validator.addMethod("bic",function(a,b){return this.optional(b)||/^([A-Z]{6}[A-Z2-9][A-NP-Z1-9])(X{3}|[A-WY-Z0-9][A-Z0-9]{2})?$/.test(a.toUpperCase())},"Please specify a valid BIC code"),a.validator.addMethod("cifES",function(a,b){"use strict";function c(a){return a%2===0}if(this.optional(b))return!0;var d,e,f,g,h=new RegExp(/^([ABCDEFGHJKLMNPQRSUVW])(\d{7})([0-9A-J])$/gi),i=a.substring(0,1),j=a.substring(1,8),k=a.substring(8,9),l=0,m=0,n=0;if(9!==a.length||!h.test(a))return!1;for(d=0;d<j.length;d++)e=parseInt(j[d],10),c(d)?(e*=2,n+=e<10?e:e-9):m+=e;return l=m+n,f=(10-l.toString().substr(-1)).toString(),f=parseInt(f,10)>9?"0":f,g="JABCDEFGHI".substr(f,1).toString(),i.match(/[ABEH]/)?k===f:i.match(/[KPQS]/)?k===g:k===f||k===g},"Please specify a valid CIF number."),a.validator.addMethod("cnhBR",function(a){if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;var b,c,d,e,f,g,h=0,i=0;if(b=a.charAt(0),new Array(12).join(b)===a)return!1;for(e=0,f=9,g=0;e<9;++e,--f)h+=+(a.charAt(e)*f);for(c=h%11,c>=10&&(c=0,i=2),h=0,e=0,f=1,g=0;e<9;++e,++f)h+=+(a.charAt(e)*f);return d=h%11,d>=10?d=0:d-=i,String(c).concat(d)===a.substr(-2)},"Please specify a valid CNH number"),a.validator.addMethod("cnpjBR",function(a,b){"use strict";if(this.optional(b))return!0;if(a=a.replace(/[^\d]+/g,""),14!==a.length)return!1;if("00000000000000"===a||"11111111111111"===a||"22222222222222"===a||"33333333333333"===a||"44444444444444"===a||"55555555555555"===a||"66666666666666"===a||"77777777777777"===a||"88888888888888"===a||"99999999999999"===a)return!1;for(var c=a.length-2,d=a.substring(0,c),e=a.substring(c),f=0,g=c-7,h=c;h>=1;h--)f+=d.charAt(c-h)*g--,g<2&&(g=9);var i=f%11<2?0:11-f%11;if(i!==parseInt(e.charAt(0),10))return!1;c+=1,d=a.substring(0,c),f=0,g=c-7;for(var j=c;j>=1;j--)f+=d.charAt(c-j)*g--,g<2&&(g=9);return i=f%11<2?0:11-f%11,i===parseInt(e.charAt(1),10)},"Please specify a CNPJ value number"),a.validator.addMethod("cpfBR",function(a,b){"use strict";if(this.optional(b))return!0;if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;var c,d,e,f,g=0;if(c=parseInt(a.substring(9,10),10),d=parseInt(a.substring(10,11),10),e=function(a,b){var c=10*a%11;return 10!==c&&11!==c||(c=0),c===b},""===a||"00000000000"===a||"11111111111"===a||"22222222222"===a||"33333333333"===a||"44444444444"===a||"55555555555"===a||"66666666666"===a||"77777777777"===a||"88888888888"===a||"99999999999"===a)return!1;for(f=1;f<=9;f++)g+=parseInt(a.substring(f-1,f),10)*(11-f);if(e(g,c)){for(g=0,f=1;f<=10;f++)g+=parseInt(a.substring(f-1,f),10)*(12-f);return e(g,d)}return!1},"Please specify a valid CPF number"),a.validator.addMethod("creditcard",function(a,b){if(this.optional(b))return"dependency-mismatch";if(/[^0-9 \-]+/.test(a))return!1;var c,d,e=0,f=0,g=!1;if(a=a.replace(/\D/g,""),a.length<13||a.length>19)return!1;for(c=a.length-1;c>=0;c--)d=a.charAt(c),f=parseInt(d,10),g&&(f*=2)>9&&(f-=9),e+=f,g=!g;return e%10===0},"Please enter a valid credit card number."),a.validator.addMethod("creditcardtypes",function(a,b,c){if(/[^0-9\-]+/.test(a))return!1;a=a.replace(/\D/g,"");var d=0;return c.mastercard&&(d|=1),c.visa&&(d|=2),c.amex&&(d|=4),c.dinersclub&&(d|=8),c.enroute&&(d|=16),c.discover&&(d|=32),c.jcb&&(d|=64),c.unknown&&(d|=128),c.all&&(d=255),1&d&&(/^(5[12345])/.test(a)||/^(2[234567])/.test(a))?16===a.length:2&d&&/^(4)/.test(a)?16===a.length:4&d&&/^(3[47])/.test(a)?15===a.length:8&d&&/^(3(0[012345]|[68]))/.test(a)?14===a.length:16&d&&/^(2(014|149))/.test(a)?15===a.length:32&d&&/^(6011)/.test(a)?16===a.length:64&d&&/^(3)/.test(a)?16===a.length:64&d&&/^(2131|1800)/.test(a)?15===a.length:!!(128&d)},"Please enter a valid credit card number."),a.validator.addMethod("currency",function(a,b,c){var d,e="string"==typeof c,f=e?c:c[0],g=!!e||c[1];return f=f.replace(/,/g,""),f=g?f+"]":f+"]?",d="^["+f+"([1-9]{1}[0-9]{0,2}(\\,[0-9]{3})*(\\.[0-9]{0,2})?|[1-9]{1}[0-9]{0,}(\\.[0-9]{0,2})?|0(\\.[0-9]{0,2})?|(\\.[0-9]{1,2})?)$",d=new RegExp(d),this.optional(b)||d.test(a)},"Please specify a valid currency"),a.validator.addMethod("dateFA",function(a,b){return this.optional(b)||/^[1-4]\d{3}\/((0?[1-6]\/((3[0-1])|([1-2][0-9])|(0?[1-9])))|((1[0-2]|(0?[7-9]))\/(30|([1-2][0-9])|(0?[1-9]))))$/.test(a)},a.validator.messages.date),a.validator.addMethod("dateITA",function(a,b){var c,d,e,f,g,h=!1,i=/^\d{1,2}\/\d{1,2}\/\d{4}$/;return i.test(a)?(c=a.split("/"),d=parseInt(c[0],10),e=parseInt(c[1],10),f=parseInt(c[2],10),g=new Date(Date.UTC(f,e-1,d,12,0,0,0)),h=g.getUTCFullYear()===f&&g.getUTCMonth()===e-1&&g.getUTCDate()===d):h=!1,this.optional(b)||h},a.validator.messages.date),a.validator.addMethod("dateNL",function(a,b){return this.optional(b)||/^(0?[1-9]|[12]\d|3[01])[\.\/\-](0?[1-9]|1[012])[\.\/\-]([12]\d)?(\d\d)$/.test(a)},a.validator.messages.date),a.validator.addMethod("extension",function(a,b,c){return c="string"==typeof c?c.replace(/,/g,"|"):"png|jpe?g|gif",this.optional(b)||a.match(new RegExp("\\.("+c+")$","i"))},a.validator.format("Please enter a value with a valid extension.")),a.validator.addMethod("giroaccountNL",function(a,b){return this.optional(b)||/^[0-9]{1,7}$/.test(a)},"Please specify a valid giro account number"),a.validator.addMethod("greaterThan",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-greaterThan-blur").length&&e.addClass("validate-greaterThan-blur").on("blur.validate-greaterThan",function(){a(c).valid()}),b>e.val()},"Please enter a greater value."),a.validator.addMethod("greaterThanEqual",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-greaterThanEqual-blur").length&&e.addClass("validate-greaterThanEqual-blur").on("blur.validate-greaterThanEqual",function(){a(c).valid()}),b>=e.val()},"Please enter a greater value."),a.validator.addMethod("iban",function(a,b){if(this.optional(b))return!0;var c,d,e,f,g,h,i,j,k,l=a.replace(/ /g,"").toUpperCase(),m="",n=!0,o="",p="",q=5;if(l.length<q)return!1;if(c=l.substring(0,2),h={AL:"\\d{8}[\\dA-Z]{16}",AD:"\\d{8}[\\dA-Z]{12}",AT:"\\d{16}",AZ:"[\\dA-Z]{4}\\d{20}",BE:"\\d{12}",BH:"[A-Z]{4}[\\dA-Z]{14}",BA:"\\d{16}",BR:"\\d{23}[A-Z][\\dA-Z]",BG:"[A-Z]{4}\\d{6}[\\dA-Z]{8}",CR:"\\d{17}",HR:"\\d{17}",CY:"\\d{8}[\\dA-Z]{16}",CZ:"\\d{20}",DK:"\\d{14}",DO:"[A-Z]{4}\\d{20}",EE:"\\d{16}",FO:"\\d{14}",FI:"\\d{14}",FR:"\\d{10}[\\dA-Z]{11}\\d{2}",GE:"[\\dA-Z]{2}\\d{16}",DE:"\\d{18}",GI:"[A-Z]{4}[\\dA-Z]{15}",GR:"\\d{7}[\\dA-Z]{16}",GL:"\\d{14}",GT:"[\\dA-Z]{4}[\\dA-Z]{20}",HU:"\\d{24}",IS:"\\d{22}",IE:"[\\dA-Z]{4}\\d{14}",IL:"\\d{19}",IT:"[A-Z]\\d{10}[\\dA-Z]{12}",KZ:"\\d{3}[\\dA-Z]{13}",KW:"[A-Z]{4}[\\dA-Z]{22}",LV:"[A-Z]{4}[\\dA-Z]{13}",LB:"\\d{4}[\\dA-Z]{20}",LI:"\\d{5}[\\dA-Z]{12}",LT:"\\d{16}",LU:"\\d{3}[\\dA-Z]{13}",MK:"\\d{3}[\\dA-Z]{10}\\d{2}",MT:"[A-Z]{4}\\d{5}[\\dA-Z]{18}",MR:"\\d{23}",MU:"[A-Z]{4}\\d{19}[A-Z]{3}",MC:"\\d{10}[\\dA-Z]{11}\\d{2}",MD:"[\\dA-Z]{2}\\d{18}",ME:"\\d{18}",NL:"[A-Z]{4}\\d{10}",NO:"\\d{11}",PK:"[\\dA-Z]{4}\\d{16}",PS:"[\\dA-Z]{4}\\d{21}",PL:"\\d{24}",PT:"\\d{21}",RO:"[A-Z]{4}[\\dA-Z]{16}",SM:"[A-Z]\\d{10}[\\dA-Z]{12}",SA:"\\d{2}[\\dA-Z]{18}",RS:"\\d{18}",SK:"\\d{20}",SI:"\\d{15}",ES:"\\d{20}",SE:"\\d{20}",CH:"\\d{5}[\\dA-Z]{12}",TN:"\\d{20}",TR:"\\d{5}[\\dA-Z]{17}",AE:"\\d{3}\\d{16}",GB:"[A-Z]{4}\\d{14}",VG:"[\\dA-Z]{4}\\d{16}"},g=h[c],"undefined"!=typeof g&&(i=new RegExp("^[A-Z]{2}\\d{2}"+g+"$",""),!i.test(l)))return!1;for(d=l.substring(4,l.length)+l.substring(0,4),j=0;j<d.length;j++)e=d.charAt(j),"0"!==e&&(n=!1),n||(m+="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".indexOf(e));for(k=0;k<m.length;k++)f=m.charAt(k),p=""+o+f,o=p%97;return 1===o},"Please specify a valid IBAN"),a.validator.addMethod("integer",function(a,b){return this.optional(b)||/^-?\d+$/.test(a)},"A positive or negative non-decimal number please"),a.validator.addMethod("ipv4",function(a,b){return this.optional(b)||/^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$/i.test(a)},"Please enter a valid IP v4 address."),a.validator.addMethod("ipv6",function(a,b){return this.optional(b)||/^((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(([0-9A-Fa-f]{1,4}:){0,5}:((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(::([0-9A-Fa-f]{1,4}:){0,5}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))$/i.test(a)},"Please enter a valid IP v6 address."),a.validator.addMethod("lessThan",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-lessThan-blur").length&&e.addClass("validate-lessThan-blur").on("blur.validate-lessThan",function(){a(c).valid()}),b<e.val()},"Please enter a lesser value."),a.validator.addMethod("lessThanEqual",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-lessThanEqual-blur").length&&e.addClass("validate-lessThanEqual-blur").on("blur.validate-lessThanEqual",function(){a(c).valid()}),b<=e.val()},"Please enter a lesser value."),a.validator.addMethod("lettersonly",function(a,b){return this.optional(b)||/^[a-z]+$/i.test(a)},"Letters only please"),a.validator.addMethod("letterswithbasicpunc",function(a,b){return this.optional(b)||/^[a-z\-.,()'"\s]+$/i.test(a)},"Letters or punctuation only please"),a.validator.addMethod("maxfiles",function(b,c,d){return!!this.optional(c)||!("file"===a(c).attr("type")&&c.files&&c.files.length>d)},a.validator.format("Please select no more than {0} files.")),a.validator.addMethod("maxsize",function(b,c,d){if(this.optional(c))return!0;if("file"===a(c).attr("type")&&c.files&&c.files.length)for(var e=0;e<c.files.length;e++)if(c.files[e].size>d)return!1;return!0},a.validator.format("File size must not exceed {0} bytes each.")),a.validator.addMethod("maxsizetotal",function(b,c,d){if(this.optional(c))return!0;if("file"===a(c).attr("type")&&c.files&&c.files.length)for(var e=0,f=0;f<c.files.length;f++)if(e+=c.files[f].size,e>d)return!1;return!0},a.validator.format("Total size of all files must not exceed {0} bytes.")),a.validator.addMethod("mobileNL",function(a,b){return this.optional(b)||/^((\+|00(\s|\s?\-\s?)?)31(\s|\s?\-\s?)?(\(0\)[\-\s]?)?|0)6((\s|\s?\-\s?)?[0-9]){8}$/.test(a)},"Please specify a valid mobile number"),a.validator.addMethod("mobileRU",function(a,b){var c=a.replace(/\(|\)|\s+|-/g,"");return this.optional(b)||c.length>9&&/^((\+7|7|8)+([0-9]){10})$/.test(c)},"Please specify a valid mobile number"),a.validator.addMethod("mobileUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?|0)7(?:[1345789]\d{2}|624)\s?\d{3}\s?\d{3})$/)},"Please specify a valid mobile number"),a.validator.addMethod("netmask",function(a,b){return this.optional(b)||/^(254|252|248|240|224|192|128)\.0\.0\.0|255\.(254|252|248|240|224|192|128|0)\.0\.0|255\.255\.(254|252|248|240|224|192|128|0)\.0|255\.255\.255\.(254|252|248|240|224|192|128|0)/i.test(a)},"Please enter a valid netmask."),a.validator.addMethod("nieES",function(a,b){"use strict";if(this.optional(b))return!0;var c,d=new RegExp(/^[MXYZ]{1}[0-9]{7,8}[TRWAGMYFPDXBNJZSQVHLCKET]{1}$/gi),e="TRWAGMYFPDXBNJZSQVHLCKET",f=a.substr(a.length-1).toUpperCase();return a=a.toString().toUpperCase(),!(a.length>10||a.length<9||!d.test(a))&&(a=a.replace(/^[X]/,"0").replace(/^[Y]/,"1").replace(/^[Z]/,"2"),c=9===a.length?a.substr(0,8):a.substr(0,9),e.charAt(parseInt(c,10)%23)===f)},"Please specify a valid NIE number."),a.validator.addMethod("nifES",function(a,b){"use strict";return!!this.optional(b)||(a=a.toUpperCase(),!!a.match("((^[A-Z]{1}[0-9]{7}[A-Z0-9]{1}$|^[T]{1}[A-Z0-9]{8}$)|^[0-9]{8}[A-Z]{1}$)")&&(/^[0-9]{8}[A-Z]{1}$/.test(a)?"TRWAGMYFPDXBNJZSQVHLCKE".charAt(a.substring(8,0)%23)===a.charAt(8):!!/^[KLM]{1}/.test(a)&&a[8]==="TRWAGMYFPDXBNJZSQVHLCKE".charAt(a.substring(8,1)%23)))},"Please specify a valid NIF number."),a.validator.addMethod("nipPL",function(a){"use strict";if(a=a.replace(/[^0-9]/g,""),10!==a.length)return!1;for(var b=[6,5,7,2,3,4,5,6,7],c=0,d=0;d<9;d++)c+=b[d]*a[d];var e=c%11,f=10===e?0:e;return f===parseInt(a[9],10)},"Please specify a valid NIP number."),a.validator.addMethod("nisBR",function(a){var b,c,d,e,f,g=0;if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;for(c=parseInt(a.substring(10,11),10),b=parseInt(a.substring(0,10),10),e=2;e<12;e++)f=e,10===e&&(f=2),11===e&&(f=3),g+=b%10*f,b=parseInt(b/10,10);return d=g%11,d=d>1?11-d:0,c===d},"Please specify a valid NIS/PIS number"),a.validator.addMethod("notEqualTo",function(b,c,d){return this.optional(c)||!a.validator.methods.equalTo.call(this,b,c,d)},"Please enter a different value, values must not be the same."),a.validator.addMethod("nowhitespace",function(a,b){return this.optional(b)||/^\S+$/i.test(a)},"No white space please"),a.validator.addMethod("pattern",function(a,b,c){return!!this.optional(b)||("string"==typeof c&&(c=new RegExp("^(?:"+c+")$")),c.test(a))},"Invalid format."),a.validator.addMethod("phoneNL",function(a,b){return this.optional(b)||/^((\+|00(\s|\s?\-\s?)?)31(\s|\s?\-\s?)?(\(0\)[\-\s]?)?|0)[1-9]((\s|\s?\-\s?)?[0-9]){8}$/.test(a)},"Please specify a valid phone number."),a.validator.addMethod("phonePL",function(a,b){a=a.replace(/\s+/g,"");var c=/^(?:(?:(?:\+|00)?48)|(?:\(\+?48\)))?(?:1[2-8]|2[2-69]|3[2-49]|4[1-68]|5[0-9]|6[0-35-9]|[7-8][1-9]|9[145])\d{7}$/;return this.optional(b)||c.test(a)},"Please specify a valid phone number"),a.validator.addMethod("phonesUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?|0)(?:1\d{8,9}|[23]\d{9}|7(?:[1345789]\d{8}|624\d{6})))$/)},"Please specify a valid uk phone number"),a.validator.addMethod("phoneUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?)|(?:\(?0))(?:\d{2}\)?\s?\d{4}\s?\d{4}|\d{3}\)?\s?\d{3}\s?\d{3,4}|\d{4}\)?\s?(?:\d{5}|\d{3}\s?\d{3})|\d{5}\)?\s?\d{4,5})$/)},"Please specify a valid phone number"),a.validator.addMethod("phoneUS",function(a,b){return a=a.replace(/\s+/g,""),this.optional(b)||a.length>9&&a.match(/^(\+?1-?)?(\([2-9]([02-9]\d|1[02-9])\)|[2-9]([02-9]\d|1[02-9]))-?[2-9]\d{2}-?\d{4}$/)},"Please specify a valid phone number"),a.validator.addMethod("postalcodeBR",function(a,b){return this.optional(b)||/^\d{2}.\d{3}-\d{3}?$|^\d{5}-?\d{3}?$/.test(a)},"Informe um CEP válido."),a.validator.addMethod("postalCodeCA",function(a,b){return this.optional(b)||/^[ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVWXYZ] *\d[ABCEGHJKLMNPRSTVWXYZ]\d$/i.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postalcodeIT",function(a,b){return this.optional(b)||/^\d{5}$/.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postalcodeNL",function(a,b){return this.optional(b)||/^[1-9][0-9]{3}\s?[a-zA-Z]{2}$/.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postcodeUK",function(a,b){return this.optional(b)||/^((([A-PR-UWYZ][0-9])|([A-PR-UWYZ][0-9][0-9])|([A-PR-UWYZ][A-HK-Y][0-9])|([A-PR-UWYZ][A-HK-Y][0-9][0-9])|([A-PR-UWYZ][0-9][A-HJKSTUW])|([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY]))\s?([0-9][ABD-HJLNP-UW-Z]{2})|(GIR)\s?(0AA))$/i.test(a)},"Please specify a valid UK postcode"),a.validator.addMethod("require_from_group",function(b,c,d){var e=a(d[1],c.form),f=e.eq(0),g=f.data("valid_req_grp")?f.data("valid_req_grp"):a.extend({},this),h=e.filter(function(){return g.elementValue(this)}).length>=d[0];return f.data("valid_req_grp",g),a(c).data("being_validated")||(e.data("being_validated",!0),e.each(function(){g.element(this)}),e.data("being_validated",!1)),h},a.validator.format("Please fill at least {0} of these fields.")),a.validator.addMethod("skip_or_fill_minimum",function(b,c,d){var e=a(d[1],c.form),f=e.eq(0),g=f.data("valid_skip")?f.data("valid_skip"):a.extend({},this),h=e.filter(function(){return g.elementValue(this)}).length,i=0===h||h>=d[0];return f.data("valid_skip",g),a(c).data("being_validated")||(e.data("being_validated",!0),e.each(function(){g.element(this)}),e.data("being_validated",!1)),i},a.validator.format("Please either skip these fields or fill at least {0} of them.")),a.validator.addMethod("stateUS",function(a,b,c){var d,e="undefined"==typeof c,f=!e&&"undefined"!=typeof c.caseSensitive&&c.caseSensitive,g=!e&&"undefined"!=typeof c.includeTerritories&&c.includeTerritories,h=!e&&"undefined"!=typeof c.includeMilitary&&c.includeMilitary;return d=g||h?g&&h?"^(A[AEKLPRSZ]|C[AOT]|D[CE]|FL|G[AU]|HI|I[ADLN]|K[SY]|LA|M[ADEINOPST]|N[CDEHJMVY]|O[HKR]|P[AR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])$":g?"^(A[KLRSZ]|C[AOT]|D[CE]|FL|G[AU]|HI|I[ADLN]|K[SY]|LA|M[ADEINOPST]|N[CDEHJMVY]|O[HKR]|P[AR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])$":"^(A[AEKLPRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])$":"^(A[KLRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])$",d=f?new RegExp(d):new RegExp(d,"i"),this.optional(b)||d.test(a)},"Please specify a valid state"),a.validator.addMethod("strippedminlength",function(b,c,d){return a(b).text().length>=d},a.validator.format("Please enter at least {0} characters")),a.validator.addMethod("time",function(a,b){return this.optional(b)||/^([01]\d|2[0-3]|[0-9])(:[0-5]\d){1,2}$/.test(a)},"Please enter a valid time, between 00:00 and 23:59"),a.validator.addMethod("time12h",function(a,b){return this.optional(b)||/^((0?[1-9]|1[012])(:[0-5]\d){1,2}(\ ?[AP]M))$/i.test(a)},"Please enter a valid time in 12-hour am/pm format"),a.validator.addMethod("url2",function(a,b){return this.optional(b)||/^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)*(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(a)},a.validator.messages.url),a.validator.addMethod("vinUS",function(a){if(17!==a.length)return!1;var b,c,d,e,f,g,h=["A","B","C","D","E","F","G","H","J","K","L","M","N","P","R","S","T","U","V","W","X","Y","Z"],i=[1,2,3,4,5,6,7,8,1,2,3,4,5,7,9,2,3,4,5,6,7,8,9],j=[8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2],k=0;for(b=0;b<17;b++){if(e=j[b],d=a.slice(b,b+1),8===b&&(g=d),isNaN(d)){for(c=0;c<h.length;c++)if(d.toUpperCase()===h[c]){d=i[c],d*=e,isNaN(g)&&8===c&&(g=h[c]);break}}else d*=e;k+=d}return f=k%11,10===f&&(f="X"),f===g},"The specified vehicle identification number (VIN) is invalid."),a.validator.addMethod("zipcodeUS",function(a,b){return this.optional(b)||/^\d{5}(-\d{4})?$/.test(a)},"The specified US ZIP Code is invalid"),a.validator.addMethod("ziprange",function(a,b){return this.optional(b)||/^90[2-5]\d\{2\}-\d{4}$/.test(a)},"Your ZIP-code must be in the range 902xx-xxxx to 905xx-xxxx"),a});[m
[32m+[m[32m(function($){[m
[32m+[m
[32m+[m[32m    /**[m
[32m+[m[32m     * Copyright 2012, Digital Fusion[m
[32m+[m[32m     * Licensed under the MIT license.[m
[32m+[m[32m     * http://teamdf.com/jquery-plugins/license/[m
[32m+[m[32m     *[m
[32m+[m[32m     * @author Sam Sehnert[m
[32m+[m[32m     * @desc A small plugin that checks whether elements are within[m
[32m+[m[32m     *       the user visible viewport of a web browser.[m
[32m+[m[32m     *       can accounts for vertical position, horizontal, or both[m
[32m+[m[32m     */[m
[32m+[m[32m    var $w=$(window);[m
[32m+[m[32m    $.fn.visible = function(partial,hidden,direction,container){[m
[32m+[m
[32m+[m[32m        if (this.length < 1)[m
[32m+[m[32m            return;[m
[32m+[m[41m	[m
[32m+[m	[32m// Set direction default to 'both'.[m
[32m+[m	[32mdirection = direction || 'both';[m
[32m+[m[41m	    [m
[32m+[m[32m        var $t          = this.length > 1 ? this.eq(0) : this,[m
[32m+[m						[32misContained = typeof container !== 'undefined' && container !== null,[m
[32m+[m						[32m$c				  = isContained ? $(container) : $w,[m
[32m+[m						[32mwPosition        = isContained ? $c.position() : 0,[m
[32m+[m[32m            t           = $t.get(0),[m
[32m+[m[32m            vpWidth     = $c.outerWidth(),[m
[32m+[m[32m            vpHeight    = $c.outerHeight(),[m
[32m+[m[32m            clientSize  = hidden === true ? t.offsetWidth * t.offsetHeight : true;[m
[32m+[m
[32m+[m[32m        if (typeof t.getBoundingClientRect === 'function'){[m
[32m+[m
[32m+[m[32m            // Use this native browser method, if available.[m
[32m+[m[32m            var rec = t.getBoundingClientRect(),[m
[32m+[m[32m                tViz = isContained ?[m
[32m+[m												[32mrec.top - wPosition.top >= 0 && rec.top < vpHeight + wPosition.top :[m
[32m+[m												[32mrec.top >= 0 && rec.top < vpHeight,[m
[32m+[m[32m                bViz = isContained ?[m
[32m+[m												[32mrec.bottom - wPosition.top > 0 && rec.bottom <= vpHeight + wPosition.top :[m
[32m+[m												[32mrec.bottom > 0 && rec.bottom <= vpHeight,[m
[32m+[m[32m                lViz = isContained ?[m
[32m+[m												[32mrec.left - wPosition.left >= 0 && rec.left < vpWidth + wPosition.left :[m
[32m+[m												[32mrec.left >= 0 && rec.left <  vpWidth,[m
[32m+[m[32m                rViz = isContained ?[m
[32m+[m												[32mrec.right - wPosition.left > 0  && rec.right < vpWidth + wPosition.left  :[m
[32m+[m												[32mrec.right > 0 && rec.right <= vpWidth,[m
[32m+[m[32m                vVisible   = partial ? tViz || bViz : tViz && bViz,[m
[32m+[m[32m                hVisible   = partial ? lViz || rViz : lViz && rViz,[m
[32m+[m		[32mvVisible = (rec.top < 0 && rec.bottom > vpHeight) ? true : vVisible,[m
[32m+[m[32m                hVisible = (rec.left < 0 && rec.right > vpWidth) ? true : hVisible;[m
[32m+[m
[32m+[m[32m            if(direction === 'both')[m
[32m+[m[32m                return clientSize && vVisible && hVisible;[m
[32m+[m[32m            else if(direction === 'vertical')[m
[32m+[m[32m                return clientSize && vVisible;[m
[32m+[m[32m            else if(direction === 'horizontal')[m
[32m+[m[32m                return clientSize && hVisible;[m
[32m+[m[32m        } else {[m
[32m+[m
[32m+[m[32m            var viewTop 				= isContained ? 0 : wPosition,[m
[32m+[m[32m                viewBottom      = viewTop + vpHeight,[m
[32m+[m[32m                viewLeft        = $c.scrollLeft(),[m
[32m+[m[32m                viewRight       = viewLeft + vpWidth,[m
[32m+[m[32m                position          = $t.position(),[m
[32m+[m[32m                _top            = position.top,[m
[32m+[m[32m                _bottom         = _top + $t.height(),[m
[32m+[m[32m                _left           = position.left,[m
[32m+[m[32m                _right          = _left + $t.width(),[m
[32m+[m[32m                compareTop      = partial === true ? _bottom : _top,[m
[32m+[m[32m                compareBottom   = partial === true ? _top : _bottom,[m
[32m+[m[32m                compareLeft     = partial === true ? _right : _left,[m
[32m+[m[32m                compareRight    = partial === true ? _left : _right;[m
[32m+[m
[32m+[m[32m            if(direction === 'both')[m
[32m+[m[32m                return !!clientSize && ((compareBottom <= viewBottom) && (compareTop >= viewTop)) && ((compareRight <= viewRight) && (compareLeft >= viewLeft));[m
[32m+[m[32m            else if(direction === 'vertical')[m
[32m+[m[32m                return !!clientSize && ((compareBottom <= viewBottom) && (compareTop >= viewTop));[m
[32m+[m[32m            else if(direction === 'horizontal')[m
[32m+[m[32m                return !!clientSize && ((compareRight <= viewRight) && (compareLeft >= viewLeft));[m
[32m+[m[32m        }[m
[32m+[m[32m    };[m
[32m+[m
[32m+[m[32m})(jQuery);[m
[32m+[m
 /*[m
  Copyright (C) Federico Zivolo 2019[m
  Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).[m
[1mdiff --git a/docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.js b/docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.js[m
[1mindex 88dfed06..07640e88 100644[m
[1m--- a/docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.js[m
[1m+++ b/docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.js[m
[36m@@ -6,6 +6,90 @@[m
  * https://jqueryvalidation.org/[m
  * Copyright (c) 2020 Jörn Zaefferer; Licensed MIT */[m
 !function(a){"function"==typeof define&&define.amd?define(["jquery","./jquery.validate.min"],a):"object"==typeof module&&module.exports?module.exports=a(require("jquery")):a(jQuery)}(function(a){return function(){function b(a){return a.replace(/<.[^<>]*?>/g," ").replace(/&nbsp;|&#160;/gi," ").replace(/[.(),;:!?%#$'\"_+=\/\-“”’]*/g,"")}a.validator.addMethod("maxWords",function(a,c,d){return this.optional(c)||b(a).match(/\b\w+\b/g).length<=d},a.validator.format("Please enter {0} words or less.")),a.validator.addMethod("minWords",function(a,c,d){return this.optional(c)||b(a).match(/\b\w+\b/g).length>=d},a.validator.format("Please enter at least {0} words.")),a.validator.addMethod("rangeWords",function(a,c,d){var e=b(a),f=/\b\w+\b/g;return this.optional(c)||e.match(f).length>=d[0]&&e.match(f).length<=d[1]},a.validator.format("Please enter between {0} and {1} words."))}(),a.validator.addMethod("abaRoutingNumber",function(a){var b=0,c=a.split(""),d=c.length;if(9!==d)return!1;for(var e=0;e<d;e+=3)b+=3*parseInt(c[e],10)+7*parseInt(c[e+1],10)+parseInt(c[e+2],10);return 0!==b&&b%10===0},"Please enter a valid routing number."),a.validator.addMethod("accept",function(b,c,d){var e,f,g,h="string"==typeof d?d.replace(/\s/g,""):"image/*",i=this.optional(c);if(i)return i;if("file"===a(c).attr("type")&&(h=h.replace(/[\-\[\]\/\{\}\(\)\+\?\.\\\^\$\|]/g,"\\$&").replace(/,/g,"|").replace(/\/\*/g,"/.*"),c.files&&c.files.length))for(g=new RegExp(".?("+h+")$","i"),e=0;e<c.files.length;e++)if(f=c.files[e],!f.type.match(g))return!1;return!0},a.validator.format("Please enter a value with a valid mimetype.")),a.validator.addMethod("alphanumeric",function(a,b){return this.optional(b)||/^\w+$/i.test(a)},"Letters, numbers, and underscores only please"),a.validator.addMethod("bankaccountNL",function(a,b){if(this.optional(b))return!0;if(!/^[0-9]{9}|([0-9]{2} ){3}[0-9]{3}$/.test(a))return!1;var c,d,e,f=a.replace(/ /g,""),g=0,h=f.length;for(c=0;c<h;c++)d=h-c,e=f.substring(c,c+1),g+=d*e;return g%11===0},"Please specify a valid bank account number"),a.validator.addMethod("bankorgiroaccountNL",function(b,c){return this.optional(c)||a.validator.methods.bankaccountNL.call(this,b,c)||a.validator.methods.giroaccountNL.call(this,b,c)},"Please specify a valid bank or giro account number"),a.validator.addMethod("bic",function(a,b){return this.optional(b)||/^([A-Z]{6}[A-Z2-9][A-NP-Z1-9])(X{3}|[A-WY-Z0-9][A-Z0-9]{2})?$/.test(a.toUpperCase())},"Please specify a valid BIC code"),a.validator.addMethod("cifES",function(a,b){"use strict";function c(a){return a%2===0}if(this.optional(b))return!0;var d,e,f,g,h=new RegExp(/^([ABCDEFGHJKLMNPQRSUVW])(\d{7})([0-9A-J])$/gi),i=a.substring(0,1),j=a.substring(1,8),k=a.substring(8,9),l=0,m=0,n=0;if(9!==a.length||!h.test(a))return!1;for(d=0;d<j.length;d++)e=parseInt(j[d],10),c(d)?(e*=2,n+=e<10?e:e-9):m+=e;return l=m+n,f=(10-l.toString().substr(-1)).toString(),f=parseInt(f,10)>9?"0":f,g="JABCDEFGHI".substr(f,1).toString(),i.match(/[ABEH]/)?k===f:i.match(/[KPQS]/)?k===g:k===f||k===g},"Please specify a valid CIF number."),a.validator.addMethod("cnhBR",function(a){if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;var b,c,d,e,f,g,h=0,i=0;if(b=a.charAt(0),new Array(12).join(b)===a)return!1;for(e=0,f=9,g=0;e<9;++e,--f)h+=+(a.charAt(e)*f);for(c=h%11,c>=10&&(c=0,i=2),h=0,e=0,f=1,g=0;e<9;++e,++f)h+=+(a.charAt(e)*f);return d=h%11,d>=10?d=0:d-=i,String(c).concat(d)===a.substr(-2)},"Please specify a valid CNH number"),a.validator.addMethod("cnpjBR",function(a,b){"use strict";if(this.optional(b))return!0;if(a=a.replace(/[^\d]+/g,""),14!==a.length)return!1;if("00000000000000"===a||"11111111111111"===a||"22222222222222"===a||"33333333333333"===a||"44444444444444"===a||"55555555555555"===a||"66666666666666"===a||"77777777777777"===a||"88888888888888"===a||"99999999999999"===a)return!1;for(var c=a.length-2,d=a.substring(0,c),e=a.substring(c),f=0,g=c-7,h=c;h>=1;h--)f+=d.charAt(c-h)*g--,g<2&&(g=9);var i=f%11<2?0:11-f%11;if(i!==parseInt(e.charAt(0),10))return!1;c+=1,d=a.substring(0,c),f=0,g=c-7;for(var j=c;j>=1;j--)f+=d.charAt(c-j)*g--,g<2&&(g=9);return i=f%11<2?0:11-f%11,i===parseInt(e.charAt(1),10)},"Please specify a CNPJ value number"),a.validator.addMethod("cpfBR",function(a,b){"use strict";if(this.optional(b))return!0;if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;var c,d,e,f,g=0;if(c=parseInt(a.substring(9,10),10),d=parseInt(a.substring(10,11),10),e=function(a,b){var c=10*a%11;return 10!==c&&11!==c||(c=0),c===b},""===a||"00000000000"===a||"11111111111"===a||"22222222222"===a||"33333333333"===a||"44444444444"===a||"55555555555"===a||"66666666666"===a||"77777777777"===a||"88888888888"===a||"99999999999"===a)return!1;for(f=1;f<=9;f++)g+=parseInt(a.substring(f-1,f),10)*(11-f);if(e(g,c)){for(g=0,f=1;f<=10;f++)g+=parseInt(a.substring(f-1,f),10)*(12-f);return e(g,d)}return!1},"Please specify a valid CPF number"),a.validator.addMethod("creditcard",function(a,b){if(this.optional(b))return"dependency-mismatch";if(/[^0-9 \-]+/.test(a))return!1;var c,d,e=0,f=0,g=!1;if(a=a.replace(/\D/g,""),a.length<13||a.length>19)return!1;for(c=a.length-1;c>=0;c--)d=a.charAt(c),f=parseInt(d,10),g&&(f*=2)>9&&(f-=9),e+=f,g=!g;return e%10===0},"Please enter a valid credit card number."),a.validator.addMethod("creditcardtypes",function(a,b,c){if(/[^0-9\-]+/.test(a))return!1;a=a.replace(/\D/g,"");var d=0;return c.mastercard&&(d|=1),c.visa&&(d|=2),c.amex&&(d|=4),c.dinersclub&&(d|=8),c.enroute&&(d|=16),c.discover&&(d|=32),c.jcb&&(d|=64),c.unknown&&(d|=128),c.all&&(d=255),1&d&&(/^(5[12345])/.test(a)||/^(2[234567])/.test(a))?16===a.length:2&d&&/^(4)/.test(a)?16===a.length:4&d&&/^(3[47])/.test(a)?15===a.length:8&d&&/^(3(0[012345]|[68]))/.test(a)?14===a.length:16&d&&/^(2(014|149))/.test(a)?15===a.length:32&d&&/^(6011)/.test(a)?16===a.length:64&d&&/^(3)/.test(a)?16===a.length:64&d&&/^(2131|1800)/.test(a)?15===a.length:!!(128&d)},"Please enter a valid credit card number."),a.validator.addMethod("currency",function(a,b,c){var d,e="string"==typeof c,f=e?c:c[0],g=!!e||c[1];return f=f.replace(/,/g,""),f=g?f+"]":f+"]?",d="^["+f+"([1-9]{1}[0-9]{0,2}(\\,[0-9]{3})*(\\.[0-9]{0,2})?|[1-9]{1}[0-9]{0,}(\\.[0-9]{0,2})?|0(\\.[0-9]{0,2})?|(\\.[0-9]{1,2})?)$",d=new RegExp(d),this.optional(b)||d.test(a)},"Please specify a valid currency"),a.validator.addMethod("dateFA",function(a,b){return this.optional(b)||/^[1-4]\d{3}\/((0?[1-6]\/((3[0-1])|([1-2][0-9])|(0?[1-9])))|((1[0-2]|(0?[7-9]))\/(30|([1-2][0-9])|(0?[1-9]))))$/.test(a)},a.validator.messages.date),a.validator.addMethod("dateITA",function(a,b){var c,d,e,f,g,h=!1,i=/^\d{1,2}\/\d{1,2}\/\d{4}$/;return i.test(a)?(c=a.split("/"),d=parseInt(c[0],10),e=parseInt(c[1],10),f=parseInt(c[2],10),g=new Date(Date.UTC(f,e-1,d,12,0,0,0)),h=g.getUTCFullYear()===f&&g.getUTCMonth()===e-1&&g.getUTCDate()===d):h=!1,this.optional(b)||h},a.validator.messages.date),a.validator.addMethod("dateNL",function(a,b){return this.optional(b)||/^(0?[1-9]|[12]\d|3[01])[\.\/\-](0?[1-9]|1[012])[\.\/\-]([12]\d)?(\d\d)$/.test(a)},a.validator.messages.date),a.validator.addMethod("extension",function(a,b,c){return c="string"==typeof c?c.replace(/,/g,"|"):"png|jpe?g|gif",this.optional(b)||a.match(new RegExp("\\.("+c+")$","i"))},a.validator.format("Please enter a value with a valid extension.")),a.validator.addMethod("giroaccountNL",function(a,b){return this.optional(b)||/^[0-9]{1,7}$/.test(a)},"Please specify a valid giro account number"),a.validator.addMethod("greaterThan",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-greaterThan-blur").length&&e.addClass("validate-greaterThan-blur").on("blur.validate-greaterThan",function(){a(c).valid()}),b>e.val()},"Please enter a greater value."),a.validator.addMethod("greaterThanEqual",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-greaterThanEqual-blur").length&&e.addClass("validate-greaterThanEqual-blur").on("blur.validate-greaterThanEqual",function(){a(c).valid()}),b>=e.val()},"Please enter a greater value."),a.validator.addMethod("iban",function(a,b){if(this.optional(b))return!0;var c,d,e,f,g,h,i,j,k,l=a.replace(/ /g,"").toUpperCase(),m="",n=!0,o="",p="",q=5;if(l.length<q)return!1;if(c=l.substring(0,2),h={AL:"\\d{8}[\\dA-Z]{16}",AD:"\\d{8}[\\dA-Z]{12}",AT:"\\d{16}",AZ:"[\\dA-Z]{4}\\d{20}",BE:"\\d{12}",BH:"[A-Z]{4}[\\dA-Z]{14}",BA:"\\d{16}",BR:"\\d{23}[A-Z][\\dA-Z]",BG:"[A-Z]{4}\\d{6}[\\dA-Z]{8}",CR:"\\d{17}",HR:"\\d{17}",CY:"\\d{8}[\\dA-Z]{16}",CZ:"\\d{20}",DK:"\\d{14}",DO:"[A-Z]{4}\\d{20}",EE:"\\d{16}",FO:"\\d{14}",FI:"\\d{14}",FR:"\\d{10}[\\dA-Z]{11}\\d{2}",GE:"[\\dA-Z]{2}\\d{16}",DE:"\\d{18}",GI:"[A-Z]{4}[\\dA-Z]{15}",GR:"\\d{7}[\\dA-Z]{16}",GL:"\\d{14}",GT:"[\\dA-Z]{4}[\\dA-Z]{20}",HU:"\\d{24}",IS:"\\d{22}",IE:"[\\dA-Z]{4}\\d{14}",IL:"\\d{19}",IT:"[A-Z]\\d{10}[\\dA-Z]{12}",KZ:"\\d{3}[\\dA-Z]{13}",KW:"[A-Z]{4}[\\dA-Z]{22}",LV:"[A-Z]{4}[\\dA-Z]{13}",LB:"\\d{4}[\\dA-Z]{20}",LI:"\\d{5}[\\dA-Z]{12}",LT:"\\d{16}",LU:"\\d{3}[\\dA-Z]{13}",MK:"\\d{3}[\\dA-Z]{10}\\d{2}",MT:"[A-Z]{4}\\d{5}[\\dA-Z]{18}",MR:"\\d{23}",MU:"[A-Z]{4}\\d{19}[A-Z]{3}",MC:"\\d{10}[\\dA-Z]{11}\\d{2}",MD:"[\\dA-Z]{2}\\d{18}",ME:"\\d{18}",NL:"[A-Z]{4}\\d{10}",NO:"\\d{11}",PK:"[\\dA-Z]{4}\\d{16}",PS:"[\\dA-Z]{4}\\d{21}",PL:"\\d{24}",PT:"\\d{21}",RO:"[A-Z]{4}[\\dA-Z]{16}",SM:"[A-Z]\\d{10}[\\dA-Z]{12}",SA:"\\d{2}[\\dA-Z]{18}",RS:"\\d{18}",SK:"\\d{20}",SI:"\\d{15}",ES:"\\d{20}",SE:"\\d{20}",CH:"\\d{5}[\\dA-Z]{12}",TN:"\\d{20}",TR:"\\d{5}[\\dA-Z]{17}",AE:"\\d{3}\\d{16}",GB:"[A-Z]{4}\\d{14}",VG:"[\\dA-Z]{4}\\d{16}"},g=h[c],"undefined"!=typeof g&&(i=new RegExp("^[A-Z]{2}\\d{2}"+g+"$",""),!i.test(l)))return!1;for(d=l.substring(4,l.length)+l.substring(0,4),j=0;j<d.length;j++)e=d.charAt(j),"0"!==e&&(n=!1),n||(m+="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".indexOf(e));for(k=0;k<m.length;k++)f=m.charAt(k),p=""+o+f,o=p%97;return 1===o},"Please specify a valid IBAN"),a.validator.addMethod("integer",function(a,b){return this.optional(b)||/^-?\d+$/.test(a)},"A positive or negative non-decimal number please"),a.validator.addMethod("ipv4",function(a,b){return this.optional(b)||/^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$/i.test(a)},"Please enter a valid IP v4 address."),a.validator.addMethod("ipv6",function(a,b){return this.optional(b)||/^((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(([0-9A-Fa-f]{1,4}:){0,5}:((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(::([0-9A-Fa-f]{1,4}:){0,5}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))$/i.test(a)},"Please enter a valid IP v6 address."),a.validator.addMethod("lessThan",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-lessThan-blur").length&&e.addClass("validate-lessThan-blur").on("blur.validate-lessThan",function(){a(c).valid()}),b<e.val()},"Please enter a lesser value."),a.validator.addMethod("lessThanEqual",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-lessThanEqual-blur").length&&e.addClass("validate-lessThanEqual-blur").on("blur.validate-lessThanEqual",function(){a(c).valid()}),b<=e.val()},"Please enter a lesser value."),a.validator.addMethod("lettersonly",function(a,b){return this.optional(b)||/^[a-z]+$/i.test(a)},"Letters only please"),a.validator.addMethod("letterswithbasicpunc",function(a,b){return this.optional(b)||/^[a-z\-.,()'"\s]+$/i.test(a)},"Letters or punctuation only please"),a.validator.addMethod("maxfiles",function(b,c,d){return!!this.optional(c)||!("file"===a(c).attr("type")&&c.files&&c.files.length>d)},a.validator.format("Please select no more than {0} files.")),a.validator.addMethod("maxsize",function(b,c,d){if(this.optional(c))return!0;if("file"===a(c).attr("type")&&c.files&&c.files.length)for(var e=0;e<c.files.length;e++)if(c.files[e].size>d)return!1;return!0},a.validator.format("File size must not exceed {0} bytes each.")),a.validator.addMethod("maxsizetotal",function(b,c,d){if(this.optional(c))return!0;if("file"===a(c).attr("type")&&c.files&&c.files.length)for(var e=0,f=0;f<c.files.length;f++)if(e+=c.files[f].size,e>d)return!1;return!0},a.validator.format("Total size of all files must not exceed {0} bytes.")),a.validator.addMethod("mobileNL",function(a,b){return this.optional(b)||/^((\+|00(\s|\s?\-\s?)?)31(\s|\s?\-\s?)?(\(0\)[\-\s]?)?|0)6((\s|\s?\-\s?)?[0-9]){8}$/.test(a)},"Please specify a valid mobile number"),a.validator.addMethod("mobileRU",function(a,b){var c=a.replace(/\(|\)|\s+|-/g,"");return this.optional(b)||c.length>9&&/^((\+7|7|8)+([0-9]){10})$/.test(c)},"Please specify a valid mobile number"),a.validator.addMethod("mobileUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?|0)7(?:[1345789]\d{2}|624)\s?\d{3}\s?\d{3})$/)},"Please specify a valid mobile number"),a.validator.addMethod("netmask",function(a,b){return this.optional(b)||/^(254|252|248|240|224|192|128)\.0\.0\.0|255\.(254|252|248|240|224|192|128|0)\.0\.0|255\.255\.(254|252|248|240|224|192|128|0)\.0|255\.255\.255\.(254|252|248|240|224|192|128|0)/i.test(a)},"Please enter a valid netmask."),a.validator.addMethod("nieES",function(a,b){"use strict";if(this.optional(b))return!0;var c,d=new RegExp(/^[MXYZ]{1}[0-9]{7,8}[TRWAGMYFPDXBNJZSQVHLCKET]{1}$/gi),e="TRWAGMYFPDXBNJZSQVHLCKET",f=a.substr(a.length-1).toUpperCase();return a=a.toString().toUpperCase(),!(a.length>10||a.length<9||!d.test(a))&&(a=a.replace(/^[X]/,"0").replace(/^[Y]/,"1").replace(/^[Z]/,"2"),c=9===a.length?a.substr(0,8):a.substr(0,9),e.charAt(parseInt(c,10)%23)===f)},"Please specify a valid NIE number."),a.validator.addMethod("nifES",function(a,b){"use strict";return!!this.optional(b)||(a=a.toUpperCase(),!!a.match("((^[A-Z]{1}[0-9]{7}[A-Z0-9]{1}$|^[T]{1}[A-Z0-9]{8}$)|^[0-9]{8}[A-Z]{1}$)")&&(/^[0-9]{8}[A-Z]{1}$/.test(a)?"TRWAGMYFPDXBNJZSQVHLCKE".charAt(a.substring(8,0)%23)===a.charAt(8):!!/^[KLM]{1}/.test(a)&&a[8]==="TRWAGMYFPDXBNJZSQVHLCKE".charAt(a.substring(8,1)%23)))},"Please specify a valid NIF number."),a.validator.addMethod("nipPL",function(a){"use strict";if(a=a.replace(/[^0-9]/g,""),10!==a.length)return!1;for(var b=[6,5,7,2,3,4,5,6,7],c=0,d=0;d<9;d++)c+=b[d]*a[d];var e=c%11,f=10===e?0:e;return f===parseInt(a[9],10)},"Please specify a valid NIP number."),a.validator.addMethod("nisBR",function(a){var b,c,d,e,f,g=0;if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;for(c=parseInt(a.substring(10,11),10),b=parseInt(a.substring(0,10),10),e=2;e<12;e++)f=e,10===e&&(f=2),11===e&&(f=3),g+=b%10*f,b=parseInt(b/10,10);return d=g%11,d=d>1?11-d:0,c===d},"Please specify a valid NIS/PIS number"),a.validator.addMethod("notEqualTo",function(b,c,d){return this.optional(c)||!a.validator.methods.equalTo.call(this,b,c,d)},"Please enter a different value, values must not be the same."),a.validator.addMethod("nowhitespace",function(a,b){return this.optional(b)||/^\S+$/i.test(a)},"No white space please"),a.validator.addMethod("pattern",function(a,b,c){return!!this.optional(b)||("string"==typeof c&&(c=new RegExp("^(?:"+c+")$")),c.test(a))},"Invalid format."),a.validator.addMethod("phoneNL",function(a,b){return this.optional(b)||/^((\+|00(\s|\s?\-\s?)?)31(\s|\s?\-\s?)?(\(0\)[\-\s]?)?|0)[1-9]((\s|\s?\-\s?)?[0-9]){8}$/.test(a)},"Please specify a valid phone number."),a.validator.addMethod("phonePL",function(a,b){a=a.replace(/\s+/g,"");var c=/^(?:(?:(?:\+|00)?48)|(?:\(\+?48\)))?(?:1[2-8]|2[2-69]|3[2-49]|4[1-68]|5[0-9]|6[0-35-9]|[7-8][1-9]|9[145])\d{7}$/;return this.optional(b)||c.test(a)},"Please specify a valid phone number"),a.validator.addMethod("phonesUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?|0)(?:1\d{8,9}|[23]\d{9}|7(?:[1345789]\d{8}|624\d{6})))$/)},"Please specify a valid uk phone number"),a.validator.addMethod("phoneUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?)|(?:\(?0))(?:\d{2}\)?\s?\d{4}\s?\d{4}|\d{3}\)?\s?\d{3}\s?\d{3,4}|\d{4}\)?\s?(?:\d{5}|\d{3}\s?\d{3})|\d{5}\)?\s?\d{4,5})$/)},"Please specify a valid phone number"),a.validator.addMethod("phoneUS",function(a,b){return a=a.replace(/\s+/g,""),this.optional(b)||a.length>9&&a.match(/^(\+?1-?)?(\([2-9]([02-9]\d|1[02-9])\)|[2-9]([02-9]\d|1[02-9]))-?[2-9]\d{2}-?\d{4}$/)},"Please specify a valid phone number"),a.validator.addMethod("postalcodeBR",function(a,b){return this.optional(b)||/^\d{2}.\d{3}-\d{3}?$|^\d{5}-?\d{3}?$/.test(a)},"Informe um CEP válido."),a.validator.addMethod("postalCodeCA",function(a,b){return this.optional(b)||/^[ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVWXYZ] *\d[ABCEGHJKLMNPRSTVWXYZ]\d$/i.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postalcodeIT",function(a,b){return this.optional(b)||/^\d{5}$/.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postalcodeNL",function(a,b){return this.optional(b)||/^[1-9][0-9]{3}\s?[a-zA-Z]{2}$/.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postcodeUK",function(a,b){return this.optional(b)||/^((([A-PR-UWYZ][0-9])|([A-PR-UWYZ][0-9][0-9])|([A-PR-UWYZ][A-HK-Y][0-9])|([A-PR-UWYZ][A-HK-Y][0-9][0-9])|([A-PR-UWYZ][0-9][A-HJKSTUW])|([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY]))\s?([0-9][ABD-HJLNP-UW-Z]{2})|(GIR)\s?(0AA))$/i.test(a)},"Please specify a valid UK postcode"),a.validator.addMethod("require_from_group",function(b,c,d){var e=a(d[1],c.form),f=e.eq(0),g=f.data("valid_req_grp")?f.data("valid_req_grp"):a.extend({},this),h=e.filter(function(){return g.elementValue(this)}).length>=d[0];return f.data("valid_req_grp",g),a(c).data("being_validated")||(e.data("being_validated",!0),e.each(function(){g.element(this)}),e.data("being_validated",!1)),h},a.validator.format("Please fill at least {0} of these fields.")),a.validator.addMethod("skip_or_fill_minimum",function(b,c,d){var e=a(d[1],c.form),f=e.eq(0),g=f.data("valid_skip")?f.data("valid_skip"):a.extend({},this),h=e.filter(function(){return g.elementValue(this)}).length,i=0===h||h>=d[0];return f.data("valid_skip",g),a(c).data("being_validated")||(e.data("being_validated",!0),e.each(function(){g.element(this)}),e.data("being_validated",!1)),i},a.validator.format("Please either skip these fields or fill at least {0} of them.")),a.validator.addMethod("stateUS",function(a,b,c){var d,e="undefined"==typeof c,f=!e&&"undefined"!=typeof c.caseSensitive&&c.caseSensitive,g=!e&&"undefined"!=typeof c.includeTerritories&&c.includeTerritories,h=!e&&"undefined"!=typeof c.includeMilitary&&c.includeMilitary;return d=g||h?g&&h?"^(A[AEKLPRSZ]|C[AOT]|D[CE]|FL|G[AU]|HI|I[ADLN]|K[SY]|LA|M[ADEINOPST]|N[CDEHJMVY]|O[HKR]|P[AR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])$":g?"^(A[KLRSZ]|C[AOT]|D[CE]|FL|G[AU]|HI|I[ADLN]|K[SY]|LA|M[ADEINOPST]|N[CDEHJMVY]|O[HKR]|P[AR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])$":"^(A[AEKLPRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])$":"^(A[KLRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])$",d=f?new RegExp(d):new RegExp(d,"i"),this.optional(b)||d.test(a)},"Please specify a valid state"),a.validator.addMethod("strippedminlength",function(b,c,d){return a(b).text().length>=d},a.validator.format("Please enter at least {0} characters")),a.validator.addMethod("time",function(a,b){return this.optional(b)||/^([01]\d|2[0-3]|[0-9])(:[0-5]\d){1,2}$/.test(a)},"Please enter a valid time, between 00:00 and 23:59"),a.validator.addMethod("time12h",function(a,b){return this.optional(b)||/^((0?[1-9]|1[012])(:[0-5]\d){1,2}(\ ?[AP]M))$/i.test(a)},"Please enter a valid time in 12-hour am/pm format"),a.validator.addMethod("url2",function(a,b){return this.optional(b)||/^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)*(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(a)},a.validator.messages.url),a.validator.addMethod("vinUS",function(a){if(17!==a.length)return!1;var b,c,d,e,f,g,h=["A","B","C","D","E","F","G","H","J","K","L","M","N","P","R","S","T","U","V","W","X","Y","Z"],i=[1,2,3,4,5,6,7,8,1,2,3,4,5,7,9,2,3,4,5,6,7,8,9],j=[8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2],k=0;for(b=0;b<17;b++){if(e=j[b],d=a.slice(b,b+1),8===b&&(g=d),isNaN(d)){for(c=0;c<h.length;c++)if(d.toUpperCase()===h[c]){d=i[c],d*=e,isNaN(g)&&8===c&&(g=h[c]);break}}else d*=e;k+=d}return f=k%11,10===f&&(f="X"),f===g},"The specified vehicle identification number (VIN) is invalid."),a.validator.addMethod("zipcodeUS",function(a,b){return this.optional(b)||/^\d{5}(-\d{4})?$/.test(a)},"The specified US ZIP Code is invalid"),a.validator.addMethod("ziprange",function(a,b){return this.optional(b)||/^90[2-5]\d\{2\}-\d{4}$/.test(a)},"Your ZIP-code must be in the range 902xx-xxxx to 905xx-xxxx"),a});[m
[32m+[m[32m(function($){[m
[32m+[m
[32m+[m[32m    /**[m
[32m+[m[32m     * Copyright 2012, Digital Fusion[m
[32m+[m[32m     * Licensed under the MIT license.[m
[32m+[m[32m     * http://teamdf.com/jquery-plugins/license/[m
[32m+[m[32m     *[m
[32m+[m[32m     * @author Sam Sehnert[m
[32m+[m[32m     * @desc A small plugin that checks whether elements are within[m
[32m+[m[32m     *       the user visible viewport of a web browser.[m
[32m+[m[32m     *       can accounts for vertical position, horizontal, or both[m
[32m+[m[32m     */[m
[32m+[m[32m    var $w=$(window);[m
[32m+[m[32m    $.fn.visible = function(partial,hidden,direction,container){[m
[32m+[m
[32m+[m[32m        if (this.length < 1)[m
[32m+[m[32m            return;[m
[32m+[m[41m	[m
[32m+[m	[32m// Set direction default to 'both'.[m
[32m+[m	[32mdirection = direction || 'both';[m
[32m+[m[41m	    [m
[32m+[m[32m        var $t          = this.length > 1 ? this.eq(0) : this,[m
[32m+[m						[32misContained = typeof container !== 'undefined' && container !== null,[m
[32m+[m						[32m$c				  = isContained ? $(container) : $w,[m
[32m+[m						[32mwPosition        = isContained ? $c.position() : 0,[m
[32m+[m[32m            t           = $t.get(0),[m
[32m+[m[32m            vpWidth     = $c.outerWidth(),[m
[32m+[m[32m            vpHeight    = $c.outerHeight(),[m
[32m+[m[32m            clientSize  = hidden === true ? t.offsetWidth * t.offsetHeight : true;[m
[32m+[m
[32m+[m[32m        if (typeof t.getBoundingClientRect === 'function'){[m
[32m+[m
[32m+[m[32m            // Use this native browser method, if available.[m
[32m+[m[32m            var rec = t.getBoundingClientRect(),[m
[32m+[m[32m                tViz = isContained ?[m
[32m+[m												[32mrec.top - wPosition.top >= 0 && rec.top < vpHeight + wPosition.top :[m
[32m+[m												[32mrec.top >= 0 && rec.top < vpHeight,[m
[32m+[m[32m                bViz = isContained ?[m
[32m+[m												[32mrec.bottom - wPosition.top > 0 && rec.bottom <= vpHeight + wPosition.top :[m
[32m+[m												[32mrec.bottom > 0 && rec.bottom <= vpHeight,[m
[32m+[m[32m                lViz = isContained ?[m
[32m+[m												[32mrec.left - wPosition.left >= 0 && rec.left < vpWidth + wPosition.left :[m
[32m+[m												[32mrec.left >= 0 && rec.left <  vpWidth,[m
[32m+[m[32m                rViz = isContained ?[m
[32m+[m												[32mrec.right - wPosition.left > 0  && rec.right < vpWidth + wPosition.left  :[m
[32m+[m												[32mrec.right > 0 && rec.right <= vpWidth,[m
[32m+[m[32m                vVisible   = partial ? tViz || bViz : tViz && bViz,[m
[32m+[m[32m                hVisible   = partial ? lViz || rViz : lViz && rViz,[m
[32m+[m		[32mvVisible = (rec.top < 0 && rec.bottom > vpHeight) ? true : vVisible,[m
[32m+[m[32m                hVisible = (rec.left < 0 && rec.right > vpWidth) ? true : hVisible;[m
[32m+[m
[32m+[m[32m            if(direction === 'both')[m
[32m+[m[32m                return clientSize && vVisible && hVisible;[m
[32m+[m[32m            else if(direction === 'vertical')[m
[32m+[m[32m                return clientSize && vVisible;[m
[32m+[m[32m            else if(direction === 'horizontal')[m
[32m+[m[32m                return clientSize && hVisible;[m
[32m+[m[32m        } else {[m
[32m+[m
[32m+[m[32m            var viewTop 				= isContained ? 0 : wPosition,[m
[32m+[m[32m                viewBottom      = viewTop + vpHeight,[m
[32m+[m[32m                viewLeft        = $c.scrollLeft(),[m
[32m+[m[32m                viewRight       = viewLeft + vpWidth,[m
[32m+[m[32m                position          = $t.position(),[m
[32m+[m[32m                _top            = position.top,[m
[32m+[m[32m                _bottom         = _top + $t.height(),[m
[32m+[m[32m                _left           = position.left,[m
[32m+[m[32m                _right          = _left + $t.width(),[m
[32m+[m[32m                compareTop      = partial === true ? _bottom : _top,[m
[32m+[m[32m                compareBottom   = partial === true ? _top : _bottom,[m
[32m+[m[32m                compareLeft     = partial === true ? _right : _left,[m
[32m+[m[32m                compareRight    = partial === true ? _left : _right;[m
[32m+[m
[32m+[m[32m            if(direction === 'both')[m
[32m+[m[32m                return !!clientSize && ((compareBottom <= viewBottom) && (compareTop >= viewTop)) && ((compareRight <= viewRight) && (compareLeft >= viewLeft));[m
[32m+[m[32m            else if(direction === 'vertical')[m
[32m+[m[32m                return !!clientSize && ((compareBottom <= viewBottom) && (compareTop >= viewTop));[m
[32m+[m[32m            else if(direction === 'horizontal')[m
[32m+[m[32m                return !!clientSize && ((compareRight <= viewRight) && (compareLeft >= viewLeft));[m
[32m+[m[32m        }[m
[32m+[m[32m    };[m
[32m+[m
[32m+[m[32m})(jQuery);[m
[32m+[m
 /*[m
  Copyright (C) Federico Zivolo 2019[m
  Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).[m
[1mdiff --git a/docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.js b/docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.js[m
[1mindex 4a72dac7..54685d19 100644[m
[1m--- a/docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.js[m
[1m+++ b/docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.js[m
[36m@@ -6,6 +6,90 @@[m
  * https://jqueryvalidation.org/[m
  * Copyright (c) 2020 Jörn Zaefferer; Licensed MIT */[m
 !function(a){"function"==typeof define&&define.amd?define(["jquery","./jquery.validate.min"],a):"object"==typeof module&&module.exports?module.exports=a(require("jquery")):a(jQuery)}(function(a){return function(){function b(a){return a.replace(/<.[^<>]*?>/g," ").replace(/&nbsp;|&#160;/gi," ").replace(/[.(),;:!?%#$'\"_+=\/\-“”’]*/g,"")}a.validator.addMethod("maxWords",function(a,c,d){return this.optional(c)||b(a).match(/\b\w+\b/g).length<=d},a.validator.format("Please enter {0} words or less.")),a.validator.addMethod("minWords",function(a,c,d){return this.optional(c)||b(a).match(/\b\w+\b/g).length>=d},a.validator.format("Please enter at least {0} words.")),a.validator.addMethod("rangeWords",function(a,c,d){var e=b(a),f=/\b\w+\b/g;return this.optional(c)||e.match(f).length>=d[0]&&e.match(f).length<=d[1]},a.validator.format("Please enter between {0} and {1} words."))}(),a.validator.addMethod("abaRoutingNumber",function(a){var b=0,c=a.split(""),d=c.length;if(9!==d)return!1;for(var e=0;e<d;e+=3)b+=3*parseInt(c[e],10)+7*parseInt(c[e+1],10)+parseInt(c[e+2],10);return 0!==b&&b%10===0},"Please enter a valid routing number."),a.validator.addMethod("accept",function(b,c,d){var e,f,g,h="string"==typeof d?d.replace(/\s/g,""):"image/*",i=this.optional(c);if(i)return i;if("file"===a(c).attr("type")&&(h=h.replace(/[\-\[\]\/\{\}\(\)\+\?\.\\\^\$\|]/g,"\\$&").replace(/,/g,"|").replace(/\/\*/g,"/.*"),c.files&&c.files.length))for(g=new RegExp(".?("+h+")$","i"),e=0;e<c.files.length;e++)if(f=c.files[e],!f.type.match(g))return!1;return!0},a.validator.format("Please enter a value with a valid mimetype.")),a.validator.addMethod("alphanumeric",function(a,b){return this.optional(b)||/^\w+$/i.test(a)},"Letters, numbers, and underscores only please"),a.validator.addMethod("bankaccountNL",function(a,b){if(this.optional(b))return!0;if(!/^[0-9]{9}|([0-9]{2} ){3}[0-9]{3}$/.test(a))return!1;var c,d,e,f=a.replace(/ /g,""),g=0,h=f.length;for(c=0;c<h;c++)d=h-c,e=f.substring(c,c+1),g+=d*e;return g%11===0},"Please specify a valid bank account number"),a.validator.addMethod("bankorgiroaccountNL",function(b,c){return this.optional(c)||a.validator.methods.bankaccountNL.call(this,b,c)||a.validator.methods.giroaccountNL.call(this,b,c)},"Please specify a valid bank or giro account number"),a.validator.addMethod("bic",function(a,b){return this.optional(b)||/^([A-Z]{6}[A-Z2-9][A-NP-Z1-9])(X{3}|[A-WY-Z0-9][A-Z0-9]{2})?$/.test(a.toUpperCase())},"Please specify a valid BIC code"),a.validator.addMethod("cifES",function(a,b){"use strict";function c(a){return a%2===0}if(this.optional(b))return!0;var d,e,f,g,h=new RegExp(/^([ABCDEFGHJKLMNPQRSUVW])(\d{7})([0-9A-J])$/gi),i=a.substring(0,1),j=a.substring(1,8),k=a.substring(8,9),l=0,m=0,n=0;if(9!==a.length||!h.test(a))return!1;for(d=0;d<j.length;d++)e=parseInt(j[d],10),c(d)?(e*=2,n+=e<10?e:e-9):m+=e;return l=m+n,f=(10-l.toString().substr(-1)).toString(),f=parseInt(f,10)>9?"0":f,g="JABCDEFGHI".substr(f,1).toString(),i.match(/[ABEH]/)?k===f:i.match(/[KPQS]/)?k===g:k===f||k===g},"Please specify a valid CIF number."),a.validator.addMethod("cnhBR",function(a){if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;var b,c,d,e,f,g,h=0,i=0;if(b=a.charAt(0),new Array(12).join(b)===a)return!1;for(e=0,f=9,g=0;e<9;++e,--f)h+=+(a.charAt(e)*f);for(c=h%11,c>=10&&(c=0,i=2),h=0,e=0,f=1,g=0;e<9;++e,++f)h+=+(a.charAt(e)*f);return d=h%11,d>=10?d=0:d-=i,String(c).concat(d)===a.substr(-2)},"Please specify a valid CNH number"),a.validator.addMethod("cnpjBR",function(a,b){"use strict";if(this.optional(b))return!0;if(a=a.replace(/[^\d]+/g,""),14!==a.length)return!1;if("00000000000000"===a||"11111111111111"===a||"22222222222222"===a||"33333333333333"===a||"44444444444444"===a||"55555555555555"===a||"66666666666666"===a||"77777777777777"===a||"88888888888888"===a||"99999999999999"===a)return!1;for(var c=a.length-2,d=a.substring(0,c),e=a.substring(c),f=0,g=c-7,h=c;h>=1;h--)f+=d.charAt(c-h)*g--,g<2&&(g=9);var i=f%11<2?0:11-f%11;if(i!==parseInt(e.charAt(0),10))return!1;c+=1,d=a.substring(0,c),f=0,g=c-7;for(var j=c;j>=1;j--)f+=d.charAt(c-j)*g--,g<2&&(g=9);return i=f%11<2?0:11-f%11,i===parseInt(e.charAt(1),10)},"Please specify a CNPJ value number"),a.validator.addMethod("cpfBR",function(a,b){"use strict";if(this.optional(b))return!0;if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;var c,d,e,f,g=0;if(c=parseInt(a.substring(9,10),10),d=parseInt(a.substring(10,11),10),e=function(a,b){var c=10*a%11;return 10!==c&&11!==c||(c=0),c===b},""===a||"00000000000"===a||"11111111111"===a||"22222222222"===a||"33333333333"===a||"44444444444"===a||"55555555555"===a||"66666666666"===a||"77777777777"===a||"88888888888"===a||"99999999999"===a)return!1;for(f=1;f<=9;f++)g+=parseInt(a.substring(f-1,f),10)*(11-f);if(e(g,c)){for(g=0,f=1;f<=10;f++)g+=parseInt(a.substring(f-1,f),10)*(12-f);return e(g,d)}return!1},"Please specify a valid CPF number"),a.validator.addMethod("creditcard",function(a,b){if(this.optional(b))return"dependency-mismatch";if(/[^0-9 \-]+/.test(a))return!1;var c,d,e=0,f=0,g=!1;if(a=a.replace(/\D/g,""),a.length<13||a.length>19)return!1;for(c=a.length-1;c>=0;c--)d=a.charAt(c),f=parseInt(d,10),g&&(f*=2)>9&&(f-=9),e+=f,g=!g;return e%10===0},"Please enter a valid credit card number."),a.validator.addMethod("creditcardtypes",function(a,b,c){if(/[^0-9\-]+/.test(a))return!1;a=a.replace(/\D/g,"");var d=0;return c.mastercard&&(d|=1),c.visa&&(d|=2),c.amex&&(d|=4),c.dinersclub&&(d|=8),c.enroute&&(d|=16),c.discover&&(d|=32),c.jcb&&(d|=64),c.unknown&&(d|=128),c.all&&(d=255),1&d&&(/^(5[12345])/.test(a)||/^(2[234567])/.test(a))?16===a.length:2&d&&/^(4)/.test(a)?16===a.length:4&d&&/^(3[47])/.test(a)?15===a.length:8&d&&/^(3(0[012345]|[68]))/.test(a)?14===a.length:16&d&&/^(2(014|149))/.test(a)?15===a.length:32&d&&/^(6011)/.test(a)?16===a.length:64&d&&/^(3)/.test(a)?16===a.length:64&d&&/^(2131|1800)/.test(a)?15===a.length:!!(128&d)},"Please enter a valid credit card number."),a.validator.addMethod("currency",function(a,b,c){var d,e="string"==typeof c,f=e?c:c[0],g=!!e||c[1];return f=f.replace(/,/g,""),f=g?f+"]":f+"]?",d="^["+f+"([1-9]{1}[0-9]{0,2}(\\,[0-9]{3})*(\\.[0-9]{0,2})?|[1-9]{1}[0-9]{0,}(\\.[0-9]{0,2})?|0(\\.[0-9]{0,2})?|(\\.[0-9]{1,2})?)$",d=new RegExp(d),this.optional(b)||d.test(a)},"Please specify a valid currency"),a.validator.addMethod("dateFA",function(a,b){return this.optional(b)||/^[1-4]\d{3}\/((0?[1-6]\/((3[0-1])|([1-2][0-9])|(0?[1-9])))|((1[0-2]|(0?[7-9]))\/(30|([1-2][0-9])|(0?[1-9]))))$/.test(a)},a.validator.messages.date),a.validator.addMethod("dateITA",function(a,b){var c,d,e,f,g,h=!1,i=/^\d{1,2}\/\d{1,2}\/\d{4}$/;return i.test(a)?(c=a.split("/"),d=parseInt(c[0],10),e=parseInt(c[1],10),f=parseInt(c[2],10),g=new Date(Date.UTC(f,e-1,d,12,0,0,0)),h=g.getUTCFullYear()===f&&g.getUTCMonth()===e-1&&g.getUTCDate()===d):h=!1,this.optional(b)||h},a.validator.messages.date),a.validator.addMethod("dateNL",function(a,b){return this.optional(b)||/^(0?[1-9]|[12]\d|3[01])[\.\/\-](0?[1-9]|1[012])[\.\/\-]([12]\d)?(\d\d)$/.test(a)},a.validator.messages.date),a.validator.addMethod("extension",function(a,b,c){return c="string"==typeof c?c.replace(/,/g,"|"):"png|jpe?g|gif",this.optional(b)||a.match(new RegExp("\\.("+c+")$","i"))},a.validator.format("Please enter a value with a valid extension.")),a.validator.addMethod("giroaccountNL",function(a,b){return this.optional(b)||/^[0-9]{1,7}$/.test(a)},"Please specify a valid giro account number"),a.validator.addMethod("greaterThan",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-greaterThan-blur").length&&e.addClass("validate-greaterThan-blur").on("blur.validate-greaterThan",function(){a(c).valid()}),b>e.val()},"Please enter a greater value."),a.validator.addMethod("greaterThanEqual",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-greaterThanEqual-blur").length&&e.addClass("validate-greaterThanEqual-blur").on("blur.validate-greaterThanEqual",function(){a(c).valid()}),b>=e.val()},"Please enter a greater value."),a.validator.addMethod("iban",function(a,b){if(this.optional(b))return!0;var c,d,e,f,g,h,i,j,k,l=a.replace(/ /g,"").toUpperCase(),m="",n=!0,o="",p="",q=5;if(l.length<q)return!1;if(c=l.substring(0,2),h={AL:"\\d{8}[\\dA-Z]{16}",AD:"\\d{8}[\\dA-Z]{12}",AT:"\\d{16}",AZ:"[\\dA-Z]{4}\\d{20}",BE:"\\d{12}",BH:"[A-Z]{4}[\\dA-Z]{14}",BA:"\\d{16}",BR:"\\d{23}[A-Z][\\dA-Z]",BG:"[A-Z]{4}\\d{6}[\\dA-Z]{8}",CR:"\\d{17}",HR:"\\d{17}",CY:"\\d{8}[\\dA-Z]{16}",CZ:"\\d{20}",DK:"\\d{14}",DO:"[A-Z]{4}\\d{20}",EE:"\\d{16}",FO:"\\d{14}",FI:"\\d{14}",FR:"\\d{10}[\\dA-Z]{11}\\d{2}",GE:"[\\dA-Z]{2}\\d{16}",DE:"\\d{18}",GI:"[A-Z]{4}[\\dA-Z]{15}",GR:"\\d{7}[\\dA-Z]{16}",GL:"\\d{14}",GT:"[\\dA-Z]{4}[\\dA-Z]{20}",HU:"\\d{24}",IS:"\\d{22}",IE:"[\\dA-Z]{4}\\d{14}",IL:"\\d{19}",IT:"[A-Z]\\d{10}[\\dA-Z]{12}",KZ:"\\d{3}[\\dA-Z]{13}",KW:"[A-Z]{4}[\\dA-Z]{22}",LV:"[A-Z]{4}[\\dA-Z]{13}",LB:"\\d{4}[\\dA-Z]{20}",LI:"\\d{5}[\\dA-Z]{12}",LT:"\\d{16}",LU:"\\d{3}[\\dA-Z]{13}",MK:"\\d{3}[\\dA-Z]{10}\\d{2}",MT:"[A-Z]{4}\\d{5}[\\dA-Z]{18}",MR:"\\d{23}",MU:"[A-Z]{4}\\d{19}[A-Z]{3}",MC:"\\d{10}[\\dA-Z]{11}\\d{2}",MD:"[\\dA-Z]{2}\\d{18}",ME:"\\d{18}",NL:"[A-Z]{4}\\d{10}",NO:"\\d{11}",PK:"[\\dA-Z]{4}\\d{16}",PS:"[\\dA-Z]{4}\\d{21}",PL:"\\d{24}",PT:"\\d{21}",RO:"[A-Z]{4}[\\dA-Z]{16}",SM:"[A-Z]\\d{10}[\\dA-Z]{12}",SA:"\\d{2}[\\dA-Z]{18}",RS:"\\d{18}",SK:"\\d{20}",SI:"\\d{15}",ES:"\\d{20}",SE:"\\d{20}",CH:"\\d{5}[\\dA-Z]{12}",TN:"\\d{20}",TR:"\\d{5}[\\dA-Z]{17}",AE:"\\d{3}\\d{16}",GB:"[A-Z]{4}\\d{14}",VG:"[\\dA-Z]{4}\\d{16}"},g=h[c],"undefined"!=typeof g&&(i=new RegExp("^[A-Z]{2}\\d{2}"+g+"$",""),!i.test(l)))return!1;for(d=l.substring(4,l.length)+l.substring(0,4),j=0;j<d.length;j++)e=d.charAt(j),"0"!==e&&(n=!1),n||(m+="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".indexOf(e));for(k=0;k<m.length;k++)f=m.charAt(k),p=""+o+f,o=p%97;return 1===o},"Please specify a valid IBAN"),a.validator.addMethod("integer",function(a,b){return this.optional(b)||/^-?\d+$/.test(a)},"A positive or negative non-decimal number please"),a.validator.addMethod("ipv4",function(a,b){return this.optional(b)||/^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$/i.test(a)},"Please enter a valid IP v4 address."),a.validator.addMethod("ipv6",function(a,b){return this.optional(b)||/^((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(([0-9A-Fa-f]{1,4}:){0,5}:((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(::([0-9A-Fa-f]{1,4}:){0,5}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))$/i.test(a)},"Please enter a valid IP v6 address."),a.validator.addMethod("lessThan",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-lessThan-blur").length&&e.addClass("validate-lessThan-blur").on("blur.validate-lessThan",function(){a(c).valid()}),b<e.val()},"Please enter a lesser value."),a.validator.addMethod("lessThanEqual",function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-lessThanEqual-blur").length&&e.addClass("validate-lessThanEqual-blur").on("blur.validate-lessThanEqual",function(){a(c).valid()}),b<=e.val()},"Please enter a lesser value."),a.validator.addMethod("lettersonly",function(a,b){return this.optional(b)||/^[a-z]+$/i.test(a)},"Letters only please"),a.validator.addMethod("letterswithbasicpunc",function(a,b){return this.optional(b)||/^[a-z\-.,()'"\s]+$/i.test(a)},"Letters or punctuation only please"),a.validator.addMethod("maxfiles",function(b,c,d){return!!this.optional(c)||!("file"===a(c).attr("type")&&c.files&&c.files.length>d)},a.validator.format("Please select no more than {0} files.")),a.validator.addMethod("maxsize",function(b,c,d){if(this.optional(c))return!0;if("file"===a(c).attr("type")&&c.files&&c.files.length)for(var e=0;e<c.files.length;e++)if(c.files[e].size>d)return!1;return!0},a.validator.format("File size must not exceed {0} bytes each.")),a.validator.addMethod("maxsizetotal",function(b,c,d){if(this.optional(c))return!0;if("file"===a(c).attr("type")&&c.files&&c.files.length)for(var e=0,f=0;f<c.files.length;f++)if(e+=c.files[f].size,e>d)return!1;return!0},a.validator.format("Total size of all files must not exceed {0} bytes.")),a.validator.addMethod("mobileNL",function(a,b){return this.optional(b)||/^((\+|00(\s|\s?\-\s?)?)31(\s|\s?\-\s?)?(\(0\)[\-\s]?)?|0)6((\s|\s?\-\s?)?[0-9]){8}$/.test(a)},"Please specify a valid mobile number"),a.validator.addMethod("mobileRU",function(a,b){var c=a.replace(/\(|\)|\s+|-/g,"");return this.optional(b)||c.length>9&&/^((\+7|7|8)+([0-9]){10})$/.test(c)},"Please specify a valid mobile number"),a.validator.addMethod("mobileUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?|0)7(?:[1345789]\d{2}|624)\s?\d{3}\s?\d{3})$/)},"Please specify a valid mobile number"),a.validator.addMethod("netmask",function(a,b){return this.optional(b)||/^(254|252|248|240|224|192|128)\.0\.0\.0|255\.(254|252|248|240|224|192|128|0)\.0\.0|255\.255\.(254|252|248|240|224|192|128|0)\.0|255\.255\.255\.(254|252|248|240|224|192|128|0)/i.test(a)},"Please enter a valid netmask."),a.validator.addMethod("nieES",function(a,b){"use strict";if(this.optional(b))return!0;var c,d=new RegExp(/^[MXYZ]{1}[0-9]{7,8}[TRWAGMYFPDXBNJZSQVHLCKET]{1}$/gi),e="TRWAGMYFPDXBNJZSQVHLCKET",f=a.substr(a.length-1).toUpperCase();return a=a.toString().toUpperCase(),!(a.length>10||a.length<9||!d.test(a))&&(a=a.replace(/^[X]/,"0").replace(/^[Y]/,"1").replace(/^[Z]/,"2"),c=9===a.length?a.substr(0,8):a.substr(0,9),e.charAt(parseInt(c,10)%23)===f)},"Please specify a valid NIE number."),a.validator.addMethod("nifES",function(a,b){"use strict";return!!this.optional(b)||(a=a.toUpperCase(),!!a.match("((^[A-Z]{1}[0-9]{7}[A-Z0-9]{1}$|^[T]{1}[A-Z0-9]{8}$)|^[0-9]{8}[A-Z]{1}$)")&&(/^[0-9]{8}[A-Z]{1}$/.test(a)?"TRWAGMYFPDXBNJZSQVHLCKE".charAt(a.substring(8,0)%23)===a.charAt(8):!!/^[KLM]{1}/.test(a)&&a[8]==="TRWAGMYFPDXBNJZSQVHLCKE".charAt(a.substring(8,1)%23)))},"Please specify a valid NIF number."),a.validator.addMethod("nipPL",function(a){"use strict";if(a=a.replace(/[^0-9]/g,""),10!==a.length)return!1;for(var b=[6,5,7,2,3,4,5,6,7],c=0,d=0;d<9;d++)c+=b[d]*a[d];var e=c%11,f=10===e?0:e;return f===parseInt(a[9],10)},"Please specify a valid NIP number."),a.validator.addMethod("nisBR",function(a){var b,c,d,e,f,g=0;if(a=a.replace(/([~!@#$%^&*()_+=`{}\[\]\-|\\:;'<>,.\/? ])+/g,""),11!==a.length)return!1;for(c=parseInt(a.substring(10,11),10),b=parseInt(a.substring(0,10),10),e=2;e<12;e++)f=e,10===e&&(f=2),11===e&&(f=3),g+=b%10*f,b=parseInt(b/10,10);return d=g%11,d=d>1?11-d:0,c===d},"Please specify a valid NIS/PIS number"),a.validator.addMethod("notEqualTo",function(b,c,d){return this.optional(c)||!a.validator.methods.equalTo.call(this,b,c,d)},"Please enter a different value, values must not be the same."),a.validator.addMethod("nowhitespace",function(a,b){return this.optional(b)||/^\S+$/i.test(a)},"No white space please"),a.validator.addMethod("pattern",function(a,b,c){return!!this.optional(b)||("string"==typeof c&&(c=new RegExp("^(?:"+c+")$")),c.test(a))},"Invalid format."),a.validator.addMethod("phoneNL",function(a,b){return this.optional(b)||/^((\+|00(\s|\s?\-\s?)?)31(\s|\s?\-\s?)?(\(0\)[\-\s]?)?|0)[1-9]((\s|\s?\-\s?)?[0-9]){8}$/.test(a)},"Please specify a valid phone number."),a.validator.addMethod("phonePL",function(a,b){a=a.replace(/\s+/g,"");var c=/^(?:(?:(?:\+|00)?48)|(?:\(\+?48\)))?(?:1[2-8]|2[2-69]|3[2-49]|4[1-68]|5[0-9]|6[0-35-9]|[7-8][1-9]|9[145])\d{7}$/;return this.optional(b)||c.test(a)},"Please specify a valid phone number"),a.validator.addMethod("phonesUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?|0)(?:1\d{8,9}|[23]\d{9}|7(?:[1345789]\d{8}|624\d{6})))$/)},"Please specify a valid uk phone number"),a.validator.addMethod("phoneUK",function(a,b){return a=a.replace(/\(|\)|\s+|-/g,""),this.optional(b)||a.length>9&&a.match(/^(?:(?:(?:00\s?|\+)44\s?)|(?:\(?0))(?:\d{2}\)?\s?\d{4}\s?\d{4}|\d{3}\)?\s?\d{3}\s?\d{3,4}|\d{4}\)?\s?(?:\d{5}|\d{3}\s?\d{3})|\d{5}\)?\s?\d{4,5})$/)},"Please specify a valid phone number"),a.validator.addMethod("phoneUS",function(a,b){return a=a.replace(/\s+/g,""),this.optional(b)||a.length>9&&a.match(/^(\+?1-?)?(\([2-9]([02-9]\d|1[02-9])\)|[2-9]([02-9]\d|1[02-9]))-?[2-9]\d{2}-?\d{4}$/)},"Please specify a valid phone number"),a.validator.addMethod("postalcodeBR",function(a,b){return this.optional(b)||/^\d{2}.\d{3}-\d{3}?$|^\d{5}-?\d{3}?$/.test(a)},"Informe um CEP válido."),a.validator.addMethod("postalCodeCA",function(a,b){return this.optional(b)||/^[ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVWXYZ] *\d[ABCEGHJKLMNPRSTVWXYZ]\d$/i.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postalcodeIT",function(a,b){return this.optional(b)||/^\d{5}$/.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postalcodeNL",function(a,b){return this.optional(b)||/^[1-9][0-9]{3}\s?[a-zA-Z]{2}$/.test(a)},"Please specify a valid postal code"),a.validator.addMethod("postcodeUK",function(a,b){return this.optional(b)||/^((([A-PR-UWYZ][0-9])|([A-PR-UWYZ][0-9][0-9])|([A-PR-UWYZ][A-HK-Y][0-9])|([A-PR-UWYZ][A-HK-Y][0-9][0-9])|([A-PR-UWYZ][0-9][A-HJKSTUW])|([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY]))\s?([0-9][ABD-HJLNP-UW-Z]{2})|(GIR)\s?(0AA))$/i.test(a)},"Please specify a valid UK postcode"),a.validator.addMethod("require_from_group",function(b,c,d){var e=a(d[1],c.form),f=e.eq(0),g=f.data("valid_req_grp")?f.data("valid_req_grp"):a.extend({},this),h=e.filter(function(){return g.elementValue(this)}).length>=d[0];return f.data("valid_req_grp",g),a(c).data("being_validated")||(e.data("being_validated",!0),e.each(function(){g.element(this)}),e.data("being_validated",!1)),h},a.validator.format("Please fill at least {0} of these fields.")),a.validator.addMethod("skip_or_fill_minimum",function(b,c,d){var e=a(d[1],c.form),f=e.eq(0),g=f.data("valid_skip")?f.data("valid_skip"):a.extend({},this),h=e.filter(function(){return g.elementValue(this)}).length,i=0===h||h>=d[0];return f.data("valid_skip",g),a(c).data("being_validated")||(e.data("being_validated",!0),e.each(function(){g.element(this)}),e.data("being_validated",!1)),i},a.validator.format("Please either skip these fields or fill at least {0} of them.")),a.validator.addMethod("stateUS",function(a,b,c){var d,e="undefined"==typeof c,f=!e&&"undefined"!=typeof c.caseSensitive&&c.caseSensitive,g=!e&&"undefined"!=typeof c.includeTerritories&&c.includeTerritories,h=!e&&"undefined"!=typeof c.includeMilitary&&c.includeMilitary;return d=g||h?g&&h?"^(A[AEKLPRSZ]|C[AOT]|D[CE]|FL|G[AU]|HI|I[ADLN]|K[SY]|LA|M[ADEINOPST]|N[CDEHJMVY]|O[HKR]|P[AR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])$":g?"^(A[KLRSZ]|C[AOT]|D[CE]|FL|G[AU]|HI|I[ADLN]|K[SY]|LA|M[ADEINOPST]|N[CDEHJMVY]|O[HKR]|P[AR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])$":"^(A[AEKLPRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])$":"^(A[KLRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])$",d=f?new RegExp(d):new RegExp(d,"i"),this.optional(b)||d.test(a)},"Please specify a valid state"),a.validator.addMethod("strippedminlength",function(b,c,d){return a(b).text().length>=d},a.validator.format("Please enter at least {0} characters")),a.validator.addMethod("time",function(a,b){return this.optional(b)||/^([01]\d|2[0-3]|[0-9])(:[0-5]\d){1,2}$/.test(a)},"Please enter a valid time, between 00:00 and 23:59"),a.validator.addMethod("time12h",function(a,b){return this.optional(b)||/^((0?[1-9]|1[012])(:[0-5]\d){1,2}(\ ?[AP]M))$/i.test(a)},"Please enter a valid time in 12-hour am/pm format"),a.validator.addMethod("url2",function(a,b){return this.optional(b)||/^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)*(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(a)},a.validator.messages.url),a.validator.addMethod("vinUS",function(a){if(17!==a.length)return!1;var b,c,d,e,f,g,h=["A","B","C","D","E","F","G","H","J","K","L","M","N","P","R","S","T","U","V","W","X","Y","Z"],i=[1,2,3,4,5,6,7,8,1,2,3,4,5,7,9,2,3,4,5,6,7,8,9],j=[8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2],k=0;for(b=0;b<17;b++){if(e=j[b],d=a.slice(b,b+1),8===b&&(g=d),isNaN(d)){for(c=0;c<h.length;c++)if(d.toUpperCase()===h[c]){d=i[c],d*=e,isNaN(g)&&8===c&&(g=h[c]);break}}else d*=e;k+=d}return f=k%11,10===f&&(f="X"),f===g},"The specified vehicle identification number (VIN) is invalid."),a.validator.addMethod("zipcodeUS",function(a,b){return this.optional(b)||/^\d{5}(-\d{4})?$/.test(a)},"The specified US ZIP Code is invalid"),a.validator.addMethod("ziprange",function(a,b){return this.optional(b)||/^90[2-5]\d\{2\}-\d{4}$/.test(a)},"Your ZIP-code must be in the range 902xx-xxxx to 905xx-xxxx"),a});[m
[32m+[m[32m(function($){[m
[32m+[m
[32m+[m[32m    /**[m
[32m+[m[32m     * Copyright 2012, Digital Fusion[m
[32m+[m[32m     * Licensed under the MIT license.[m
[32m+[m[32m     * http://teamdf.com/jquery-plugins/license/[m
[32m+[m[32m     *[m
[32m+[m[32m     * @author Sam Sehnert[m
[32m+[m[32m     * @desc A small plugin that checks whether elements are within[m
[32m+[m[32m     *       the user visible viewport of a web browser.[m
[32m+[m[32m     *       can accounts for vertical position, horizontal, or both[m
[32m+[m[32m     */[m
[32m+[m[32m    var $w=$(window);[m
[32m+[m[32m    $.fn.visible = function(partial,hidden,direction,container){[m
[32m+[m
[32m+[m[32m        if (this.length < 1)[m
[32m+[m[32m            return;[m
[32m+[m[41m	[m
[32m+[m	[32m// Set direction default to 'both'.[m
[32m+[m	[32mdirection = direction || 'both';[m
[32m+[m[41m	    [m
[32m+[m[32m        var $t          = this.length > 1 ? this.eq(0) : this,[m
[32m+[m						[32misContained = typeof container !== 'undefined' && container !== null,[m
[32m+[m						[32m$c				  = isContained ? $(container) : $w,[m
[32m+[m						[32mwPosition        = isContained ? $c.position() : 0,[m
[32m+[m[32m            t           = $t.get(0),[m
[32m+[m[32m            vpWidth     = $c.outerWidth(),[m
[32m+[m[32m            vpHeight    = $c.outerHeight(),[m
[32m+[m[32m            clientSize  = hidden === true ? t.offsetWidth * t.offsetHeight : true;[m
[32m+[m
[32m+[m[32m        if (typeof t.getBoundingClientRect === 'function'){[m
[32m+[m
[32m+[m[32m            // Use this native browser method, if available.[m
[32m+[m[32m            var rec = t.getBoundingClientRect(),[m
[32m+[m[32m                tViz = isContained ?[m
[32m+[m												[32mrec.top - wPosition.top >= 0 && rec.top < vpHeight + wPosition.top :[m
[32m+[m												[32mrec.top >= 0 && rec.top < vpHeight,[m
[32m+[m[32m                bViz = isContained ?[m
[32m+[m												[32mrec.bottom - wPosition.top > 0 && rec.bottom <= vpHeight + wPosition.top :[m
[32m+[m												[32mrec.bottom > 0 && rec.bottom <= vpHeight,[m
[32m+[m[32m                lViz = isContained ?[m
[32m+[m												[32mrec.left - wPosition.left >= 0 && rec.left < vpWidth + wPosition.left :[m
[32m+[m												[32mrec.left >= 0 && rec.left <  vpWidth,[m
[32m+[m[32m                rViz = isContained ?[m
[32m+[m												[32mrec.right - wPosition.left > 0  && rec.right < vpWidth + wPosition.left  :[m
[32m+[m												[32mrec.right > 0 && rec.right <= vpWidth,[m
[32m+[m[32m                vVisible   = partial ? tViz || bViz : tViz && bViz,[m
[32m+[m[32m                hVisible   = partial ? lViz || rViz : lViz && rViz,[m
[32m+[m		[32mvVisible = (rec.top < 0 && rec.bottom > vpHeight) ? true : vVisible,[m
[32m+[m[32m                hVisible = (rec.left < 0 && rec.right > vpWidth) ? true : hVisible;[m
[32m+[m
[32m+[m[32m            if(direction === 'both')[m
[32m+[m[32m                return clientSize && vVisible && hVisible;[m
[32m+[m[32m            else if(direction === 'vertical')[m
[32m+[m[32m                return clientSize && vVisible;[m
[32m+[m[32m            else if(direction === 'horizontal')[m
[32m+[m[32m                return clientSize && hVisible;[m
[32m+[m[32m        } else {[m
[32m+[m
[32m+[m[32m            var viewTop 				= isContained ? 0 : wPosition,[m
[32m+[m[32m                viewBottom      = viewTop + vpHeight,[m
[32m+[m[32m                viewLeft        = $c.scrollLeft(),[m
[32m+[m[32m                viewRight       = viewLeft + vpWidth,[m
[32m+[m[32m                position          = $t.position(),[m
[32m+[m[32m                _top            = position.top,[m
[32m+[m[32m                _bottom         = _top + $t.height(),[m
[32m+[m[32m                _left           = position.left,[m
[32m+[m[32m                _right          = _left + $t.width(),[m
[32m+[m[32m                compareTop      = partial === true ? _bottom : _top,[m
[32m+[m[32m                compareBottom   = partial === true ? _top : _bottom,[m
[32m+[m[32m                compareLeft     = partial === true ? _right : _left,[m
[32m+[m[32m                compareRight    = partial === true ? _left : _right;[m
[32m+[m
[32m+[m[32m            if(direction === 'both')[m
[32m+[m[32m                return !!clientSize && ((compareBottom <= viewBottom) && (compareTop >= viewTop)) && ((compareRight <= viewRight) && (compareLeft >= viewLeft));[m
[32m+[m[32m            else if(direction === 'vertical')[m
[32m+[m[32m                return !!clientSize && ((compareBottom <= viewBottom) && (compareTop >= viewTop));[m
[32m+[m[32m            else if(direction === 'horizontal')[m
[32m+[m[32m                return !!clientSize && ((compareRight <= viewRight) && (compareLeft >= viewLeft));[m
[32m+[m[32m        }[m
[32m+[m[32m    };[m
[32m+[m
[32m+[m[32m})(jQuery);[m
[32m+[m
 /*[m
  Copyright (C) Federico Zivolo 2019[m
  Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).[m
