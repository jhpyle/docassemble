# Contributing

When contributing to this repository, please first discuss the change
you wish to make via issue, email, or any other method with the owner
of this repository before making a change.  The best way to contribute
a change is through a pull request.

If you want to add an additional feature, first consider if the
feature could be made available through an [add-on
package](https://docassemble.org/docs/packages.html).  If the feature
turns out to be universally useful, it can be incorporated later into
the core code.

## How to modify and test the core docassemble code

For instructions on how to test modificiations to the core code, see the
[workflow for making changes to the core docassemble code](https://docassemble.org/docs/development.html#core).

## How to contribute to the documentation

The documentation is written in GitHub Pages.  It is available in the
gh-pages branch of the GitHub repository.

## How to write a code example

Code examples appear in the documentation and in the "examples" area
of the Playground.  These come from interview YAML files that are
stored in `docassemble_base/docassemble/base/data/questions/examples`.

There is a script that automatically generates screenshots for the
code samples and carries over the YAML text into the documentation.
So if you want to contribute a code example, just add a YAML file to
`docassemble_base/docassemble/base/data/questions/examples`.

Each interview should begin with a `metadata` block like the
following:

    metadata:
      title: Test if user is logged in
      short title: Logged in
      documentation: "https://docassemble.org/docs/functions.html#user_logged_in"
      example start: 2
      example end: 5

The `documentation` should be a link to the documentation.  You can
see in the "examples" area of the Playground that each code example
has a link to the documentation; this is where that link comes from.

Most code examples are displayed as excerpts from the full interview
example.  The `example start` and `example end` metadata tags identify
the start and end blocks.  Note that the numbers start at zero, so the
first block in the YAML file (which is usually the `metadata` block)
is block 0.

If you want your code example to appear in the "examples" area of the
Playground, edit the
`docassemble_base/docassemble/base/data/questions/example-list.yml`
file and add a reference to your YAML file.

To add a code example to a page of the documentation, include a line
like the following:

    {% include side-by-side.html demo="user-logged-in" %}
