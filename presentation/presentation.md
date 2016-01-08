Hi, my name is Jonathan Pyle and I am an attorney with Philadelphia
Legal Assistance, and I have a background in computer programming.

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
sufficiently powerful and flexible to do all these things.

So I wrote my own.  The result is called docassemble.  It is a web
application that asks questions of users and then does things on the
basis of that information, like assembling PDF files and Word files,
sending e-mails, interacting with APIs, sending the user to another
web site, or storing information in a database.

Interview authors can write their own interviews, and clients can run
them by clicking on a link on their mobile phone or computer.  It's
100% free and open-source.

Some of the features:

* Developed with a mobile-first approach.  Thanks to the Bootstrap
  framework, it looks great on any mobile device, and also looks great
  on a computer monitor.
* It does document assembly, like HotDocs.  It uses a templating
  system called Mako, which means you have the full power of Python, a
  general purpose programming language, in your templates.
* It supports electronic signatures.  Using the touch screen, users
  can sign their name using their finger, and then the signature can
  be inserted into an assembled document.
* It handles document uploads.  While assembling a letter to a
  landlord about housing conditions, the user can take a picture with
  her phone, and then the photograph will be inserted into the body of
  her letter.
* It has built-in text-to-speech capability.  So users with low
  literacy can click the play button and their phone will read the text
  of each question out loud.
* Also, interview authors can easily embed their own audio or video
  content directly into interviews, as well as images, such as icon
  buttons.
* It has built-in capability for drawing Google Maps, as well as for
  taking user-supplied addresses and figuring out the latitude,
  longitude, and county.
* It is designed from the ground up to handle interviews in multiple
  languages and different countries.  All of the elements of the
  application, including the labels on buttons, can be converted into
  any language.

To create an interview, you write a text file, in a format called
YAML, which stands for YAML ain't markup language.  You express logic
using Python code.  You express formatting of text using Markdown, a
popular markup language.  Document assembly templates are written the
same way as questions, with the same syntax.

The most powerful feature is that it automatically figures out what
questions to ask the user and the order in which to ask them.  All
that the author needs to do is specify an end goal for the interview,
such as a document to be assembled, and make sure there are questions
to gather each piece of relevant information that might be needed
along the way.

For example, you can write things like this in a template:

If the client has standing and if the jurisdiction is proper, the
client has a valid claim, or not.

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

This is what makes it a good expert system platform for law.  As a
lawyer, I think in terms of statutes and regulations, multi-part tests
from common law, and legal terms that have definitions you look up in
another place.  That is how things are done in the docassemble system:
you express legal knowledge by writing snippets of Python code that
reference variables, which are in turn defined by other bits of Python
code, or by asking the user a question.

You might think I'm crazy to expect lawyers to write snippets of
Python code.  But it's the programming language that is closest to
plain English, and it's the language that nine year olds learn to
program in.  At the same time, Python is also a powerful,
general-purpose language in which anything can be done.  It is simple
for the uninitiated but imposes no limits on professionals.

Docassemble even uses what's called object-oriented programming.  That
sounds complicated, but it actually makes programming easier and more
intuitive.

    ---
    question: Organizations that can help you
    subquestion: ${ map_of(user, organizations_handling(problem=legal_problem, county=user.address.county)) }
    sets: map_of_organizations
    ---

For example, with the power of objects, you can write a single line of
code that draws a map of the user's location and the locations
of legal services organizations that handle her legal problem in her
county.

This also makes creating document templates much faster.  You don't
have to reinvent any wheels.  For example, you can put a case caption
into a document by writing nothing more than `pleading.caption()`.
This allows lawyers to practice at the top of their license as they
are creating forms, delegating all the mundane concepts to the
computer.

When we develop client-facing tools, we can't work in a vacuum: we
need to collaborate, and package work product for easy replication,
and keep track of versions of work product.  This can be challenging,
but solutions to these problems have already evolved in the
open-source community, in systems like GitHub.  So I've incorporated
these best practices into docassemble.

Interviews are actually Python add-on packages that get posted to
GitHub.  So if someone in California who I've never met has developed
really good plain-language questions for family law interviews, I can
incorporate her questions by reference by including her package, and
the latest version of her work will install automatically.  Then I
only need to write questions that are unique to my project or that I
want to ask differently.

Since everything is in text files, translation into other languages is
easy: just give someone the file and have them turn the English into
Spanish.  There can be a learning curve to working with text files,
but when you can use tools like search and replace and copy and paste,
you can do complicated things very quickly.

It's also fully scalable.  This means that whether you have ten
thousand users a day or ten users a day, or if you just want to run it
on your laptop, it's no problem.  You can install docassemble in a
multi-server configuration with load balancing and automatic scaling
in a matter of minutes on Amazon Web Services, without ever seeing a
command line.

I encourage you to try it out.  It is fully documented on
docassemble.org, where you can find a demo and a tutorial.  With a
developer account you can write test interviews directly in the web
browser.  I think you'll find that it is a system that allows you to
go from idea to implementation in a matter of days.

If you want to learn more about this system, feel free to contact me.
