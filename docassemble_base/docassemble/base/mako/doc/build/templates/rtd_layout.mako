<!-- readthedocs add-in template -->

<%inherit file="/layout.mako"/>


<%block name="headers">

<link href='http://fonts.googleapis.com/css?family=Lato:400,700|Roboto+Slab:400,700' rel='stylesheet' type='text/css'>

<!-- RTD <head> via mako adapter -->
<script type="text/javascript">
    var doc_version = "${current_version}";
    var doc_slug = "${slug}";
    var static_root = "${pathto('_static', 1)}"

    // copied from:
    // https://github.com/rtfd/readthedocs.org/commit/edbbb4c753454cf20c128d4eb2fef60d740debaa#diff-2f70e8d9361202bfe3f378d2ff2c510bR8
    var READTHEDOCS_DATA = {
        project: "${slug}",
        version: "${current_version}",
        page: "${pagename}",
        theme: "${html_theme or ''}"
      };

</script>
<!-- end RTD <head> via mako adapter -->

    ${parent.headers()}

</%block>


${next.body()}

<%block name="footer">
    ${parent.footer()}
</%block>
