I came back from the TIG conference last year very excited about the
possibilities for expert systems, and for moving beyond on-line intake
to generalized client portals, the endpoints of which might include
document assembly, referral, checklists, legal information, as well as
on-line intake.  I believe we need such systems because in order to
provide "some form of meaningful legal assistance" to everyone, we
need to make sure that computers are doing as much as they can
possibly do.

But when I researched the available technologies for implementing
these client-facing systems, I couldn't find any system that was
sufficiently powerful and flexible.

So I wrote my own.  The result is called docassemble.  It is a web
application that asks questions of users and then does things on the
basis of that information, like assembling PDF files and Word files,
sending e-mails, retreiving information from a wiki and presenting it
to the user, or storing information in a database.

Interview authors can write their own interviews, which clients can
run by clicking on a link on their mobile phone or computer.

The system is 100% free and open-source.  You can download it on
GitHub.  It is licensed under the MIT License, which means that anyone
can use it and modify it, even companies that want to use it to make a
profit.

Some of the features:

* Developed with a mobile-first approach.  Looks great on any mobile
  device, and also looks great on a computer monitor.  Uses Bootstrap
  framework.
* It does document assembly, like HotDocs.  It uses a Python-based
  templating system called Mako.  So you have the full power of a
  general purpose programming language in your templates.
* It supports electronic signatures.  Using the touch screen, users
  can sign their name using their finger, and then the signature can
  be inserted into an assembled document, which the user can download
  either as a PDF or a Microsoft Word file.
* It handles document uploads.  For example, suppose we want clients
  to be able to assemble form letters to their landlords about housing
  conditions.  In the middle of the interview, the user can take a
  picture with her phone, for example of a broken window, and then the
  photograph will be inserted into the body of the letter.  Or,
  clients can assemble a family law pleading on their cell phone,
  attaching screenshots of threatening text messages as exhibits to
  the pleading.
* It has built-in text-to-speech capability.  So users with low
  literacy can click a play button and their phone will read the text
  of each question out loud.
* Interview authors can easily embed their own audio or video content
  directly into interviews, as well as images, such as icon buttons.
* It has built-in capability for drawing Google Maps.
* It is designed from the ground up to handle interviews in multiple
  languages and different countries.

    ---
    question: What form do you want to prepare?
    decoration: document
    field: form_to_prepare
    buttons:
      - Custody Complaint: custody
        image: parentchild
      - Support Complaint: support
        image: coins
    ---

To create a docassemble interview, you write a text file, in a format
called YAML, which stands for YAML ain't markup language.  Document
assembly templates are written the same way.  Logic is expressed using
Python code.  Formatting of text is expressed using Markdown, a
popular markup language.

The most powerful feature of docassemble is that it automatically
figures out what questions to ask and the order in which to ask them.
All that the interview author needs to do is 1) specify the end goal of
the interview, such as a document to be assembled, and 2) make sure there
is a question to gather each piece of relevant information that might
be needed along the way.  The system will figure out what questions
are necessary to ask in order to get to the end result.

For example, you can write things like this in a template:

    % if client_has_standing and jurisdiction_is_proper:
    Congratulations, you have a valid claim.
    % else:
    Sorry, you do not have a valid claim.
    % endif

The variable `client_has_standing` is a legal concept that can be
expressed using simple Python code:

    ---
    code: |
      if client_was_injured and defendant_caused_injury:
         client_has_standing = True
      else:
         client_has_standing = False
    ---

This depends on two variables, which can be gathered from the user by
writing something like this:

    ---
    question: Were you injured?
    yesno: client_was_injured
    ---
    question: Did ${ defendant } cause your injury?
    yesno: defendant_caused_injury
    ---

The system will figure out automatically what questions to ask, and
will not ask any unnecessary questions.

This is what makes it a good expert system platform for law.  As a
lawyer, I think in terms of statutes and regulations, multi-part tests
from common law, and legal terms that have definitions you look up in
another place, such as the definitions section of a statute.

That is how things are done in the docassemble system: you express
legal knowledge by writing bits of Python code that reference
variables, which are in turn defined by other bits of Python code.

You might think it's crazy to expect lawyers to learn Python.  Well,
it's the programming language that is closest to plain English, and
the language used to introduce programming to nine year olds.  To
write an interview in docassemble you do not need to know much beyond
the if/then/else statement.

But Python is also a powerful, general-purpose language in which
anything can be done.  It is simple for the uninitiated but imposes no
limits.  Docassemble uses object-oriented programming.  That sounds
complicated, but it actually makes life easier.

    ---
    question: Organizations that can help you
    subquestion: ${ map_of(user, organizations_handling(problem=legal_problem, county=user.address.county)) }
    sets: map_of_organizations
    ---

For example, this shows a map of the user's location and the locations
of legal services organizations that handle her legal problem in her
county.  This is simple, only because we are using objects.

Docassemble incorporates the best practices of open source software
development.  Problems of multi-author collaboration, code sharing,
code packaging, and version tracking, have really good solutions in
the open source community, and docassemble uses those solutions.
Docassemble interviews are Python packages that get posted to GitHub.
So if someone in California who I've never met has developed really
good plain-language questions for family law interviews, I can
incorporate her work by reference, and I will always be able to get
the latest version of those questions just by upgrading.

Since everything is in text files, translation into other languages is
easy: just give someone the file and have them turn the English into
Spanish.

It's also fully scalable.  Whether you have ten thousand users a day
or ten users a day, or if you just want to run it on your laptop, it's
all no problem.  You can install docassemble in a fully scalable
multi-server configuration on Amazon Web Services with load balancing
and auto scaling, all without ever using the command line.
