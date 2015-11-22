<html xmlns="http://www.w3.org/1999/xhtml">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
<head>
<title><%block name="head_title">Mako Templates for Python</%block></title>

<!-- begin iterate through sphinx environment css_files -->
% for cssfile in self.attr.default_css_files + css_files:
    <link rel="stylesheet" href="${pathto(cssfile, 1)}" type="text/css" />
% endfor
<!-- end iterate through sphinx environment css_files -->

<%block name="headers">
</%block>


</head>
<body>
    <div id="wrap">
    <div class="rightbar">

    <div class="slogan">
    Hyperfast and lightweight templating for the Python platform.
    </div>

    % if toolbar:
    <div class="toolbar">
    <a href="${site_base}/">Home</a>
    &nbsp; | &nbsp;
    <a href="${site_base}/community.html">Community</a>
    &nbsp; | &nbsp;
    <a href="${pathto('index')}">Documentation</a>
    &nbsp; | &nbsp;
    <a href="${site_base}/download.html">Download</a>
    </div>
    % endif

    </div>

    <a href="${site_base}/"><img src="${pathto('_static/makoLogo.png', 1)}" /></a>

    <hr/>

    ${next.body()}
<div class="clearfix">
<%block name="footer">
<hr/>

<div class="copyright">Website content copyright &copy; by Michael Bayer.
    All rights reserved.  Mako and its documentation are licensed
    under the MIT license.  mike(&)zzzcomputing.com</div>
</%block>
</div>
</div>
</body>
</html>
