---
layout: docs
title: Docassemble Demo
short_title: Demo Steward
order: 10
---

# The Demo Steward

You can [run a simple Demo Steward](https://demo.docassemble.org?i=docassemble.demo:data/questions/questions.yml){:target="_blank"} to see the Docassemble Framework in action.

<a class="btn btn-primary btn-lg"
href="https://demo.docassemble.org?i=docassemble.demo:data/questions/questions.yml"
target="_blank">Run the Demo Steward</a>

The interface is based on [Bootstrap], which is both mobile-friendly
and desktop-friendly.  Try it out on a mobile device.

Note that the example Steward is not intended to make logical sense;
it is simply intended to demonstrate the features of
the Docassemble Framework.

100% of the [DALang] source code for the example Steward is listed below in
the form of two [YAML] files, which are annotated with comments.

When you are using the demonstration, you can click "Source" to see
the [DALang] source code that generated the question, along with a
review of the conditions that led to the question being asked.  You
can learn a lot about how to do things in DALang by clicking
"Source" and comparing the DALang source to the end result.  The
"Source" tab is only available because the demo [server] is configured
as a development [server] (by setting `debug: True` in the
[configuration file]).  End users will not see a "Source" tab.

# The DALang File for the Demo Steward

The [DALang] file that powers the Demo Steward, `questions.yml`, is
listed below.  Note that:

* It incorporates by reference another [DALang] file,
  `basic-questions.yml`, which specifies how certain common questions
  should be asked.  The content of this file is also listed below.
* The code is not entirely self-explanatory, but for computer code, it
  is pretty close to plain English.
* The questions and logic are not specified in any particular order.
  If the Demo Steward needs to get the value of a variable, it knows
  where to find it.  This makes things easier for the developer, who can
  organize the questions however he or she wants and use keyword
  searching to navigate.  Moreover, the developer can represent the
  underlying legal logic in modular, bite-size pieces.  A question or
  a bit of logic that a developer writes for one Steward can be
  packaged and reused in another Steward.

{% highlight yaml %}
metadata:
  title: |
    Demonstration Steward
  short title:
    Demo
  description: |
    This is a demonstration of the Docassemble Framework.
  authors:
    - name: Jonathan Pyle
      organization: none
  revision_date: 2017-05-26
comment: |
  A "metadata" block contains information about the Steward, such as
  the title of the Steward as displayed in the navigation bar.
---
interview help:
  heading: |
    % if interface() == 'sms':
    About this text messaging service
    % else:
    About this web site
    % endif
  content: |
    Answer each question.  At the end, you may be given a document
    that you can save.
    
    % if interface() == 'web':
    If you see a word written in green text, you can click on it to
    see more information about the word.  You can try this out here 
    to find out more about rhododendron plants.
    % endif
comment: |
  An "interview help" block adds text to the "Help" page of every
  question a Steward asks.  If the question has help text of its
  own, the "interview help" will appear after the question-specific
  help.

  This help screen displays different text depending on whether the
  web interface or the SMS interface is being used.
---
language: es
interview help:
  heading: Acerca de este sitio web
  content: |
    Conteste cada pregunta. Al final, se le puede dar un documento
    que puede ahorrar.
comment: |
  This Steward is not fully bilingual in Spanish, but this shows
  how you would provide a Spanish translation of the "interview help."
---
include:
  - basic-questions.yml
comment: |
  This loads some question definitions that are common to many Legal
  Stewards.  It also defines basic variables like "user" and sets
  the names of icons that you can use to "decorate" your Steward's questions.

  The "basic-questions.yml" comes from the docassemble.base Steward
  and is located in the directory docassemble/base/data/questions
  in that Steward's package.

  You can include question files from other Stewards by explicitly
  referring to their names.  For example,
  "docassemble.helloworld:questions.yml" refers to the file
  questions.yml in the docassemble/helloworld/data/questions
  directory of the package for the Steward docassemble.helloworld.
---
image sets:
  freepik:
    attribution: |
      Icon made by [Freepik](http://www.flaticon.com/authors/freepik)
    images:
      baby: crawling.svg
      people: users6.svg
      injury: accident3.svg
comment: |
  An "image sets" block defines the names of icons that you can use to
  "decorate" your Steward's questions.  Loading the "basic-questions.yml" file
  already defined a number of icons, but this block defines some more
  icons.

  Since most free icons available on the internet require attribution,
  the "image sets" block allows you to specify what attribution text
  to use for particular icons.  The web app shows the appropriate
  attribution text at the bottom of any page that uses one of the
  icons.
  
  Since this file, questions.yml, is in the Steward docassemble.demo,
  the image files referenced here are also in the package for the Steward docassemble.demo.
  The files are located in the directory
  docassemble/demo/data/static.
---
objects:
  - village_idiot: Individual
comment: |
  In a later question we will refer to the variable "village_idiot."
  This "objects" block creates the variable "village_idiot" and
  specifies that it is a DALang object of type "Individual."
---
auto terms:
  rhododendron: |
     A genus of shrubs or small trees, often having handsome
     evergreen leaves, and remarkable for the beauty of their
     flowers.
  custody order: |
    An order signed by a family court judge that says who gets to have
    what kind of custody over a child.
  complaint: |
    A document that you file in court to start a lawsuit.
  lawyer: |
    Someone with a license to practice law.
  plaintiff: |
    The person who starts a case.
  defendant: |
    The person who is on the defensive in a case.  In a lawsuit, the
    plaintiff sues the defendant.
comment: |
  Sometimes you will use vocabulary that the user may or may not know.
  Instead of interrupting the flow of your questions to define every
  term, you can define certain vocabulary words, and the Steward will
  turn them into hyperlinks wherever they appear.  When the user
  clicks on the hyperlink, a popup appears with the word's definition.
---
mandatory: True
code: |
  client.asset.new('checking account', 'savings account', 'stocks and bonds', 'automobiles')
  client.asset.gathered = True
  client.income.new('employment', 'self employment', 'SSI', 'TANF', 'rent', period=12)
  client.income.gathered = True
comment: |
  This Steward will ask whether the client has particular income and assets.

  The objects client.asset and client.income are DALang objects that function
  like Python "dictionaries."
  
  This code initializes the list of income and asset items.

  The attribute "gathered" is set to True because after being initialized with
  the given items, we want the list to be considered complete.  That is, we
  do not want the Steward to ask the user if there are any additional items
  to add.
  
  "Mandatory" sections like this one are evaluated in the order they
  appear in the question file.
---
initial: True
code: |
  set_language(user.language)
comment: |
  When providing multilingual Stewards, you need to tell the Steward
  what language it should use for the built-in words and expressions
  that the user will see.  This needs to be set up-front in "initial" code, which
  will run every time the screen loads.

  When the Steward first loads, user.language is undefined.  Therefore
  the Steward will ask the user a question in order to obtain a definition for
  user.language.  We will encounter this question below.
  
  "Mandatory" and "initial" sections are evaluated in the order they
  appear in the question file.  But "mandatory" sections are different because
  as soon as they run to completion, they will subsequently be skipped.
  "Initial" sections will always be run every time the screen loads.
---
mandatory: True
code: |
  need(user_saw_initial_screen)
  if user_understands_no_attorney_client_relationship == "understands":
    need(client_done)
  else:
    need(client_kicked_out)
comment: |
  This is the code that directs the question flow for the Steward.

  It runs after the user's language is set by the previous "initial" block.

  Note that there are no other "mandatory" or "initial" questions for this
  Steward.  This code block determines how the Steward will end.
  
  This code indicates to the system that we need to get to the
  endpoint "client_done."  There is a question elsewhere that contains
  "event: client_done."  The Steward will ask all the questions
  necessary to get the information need to pose that that final
  question to the user.

  However, if the answer to the question
  user_understands_no_attorney_client_relationship is not
  "understands," the Steward will looks for a question that sets the
  variable "client_kicked_out."  There is a question elsewhere that
  contains "event: client_kicked_out."

  This is the code that determines the entire path for the Steward,
  and yet it is very short, even though the Steward has many questions.
  That is because flow of an interview session on the Docassemble Framework is automatic.  The order
  in which questions are asked can vary depending on the user input.  In
  some interview sessions, a question is asked early by a Steward, and in another, it is asked
  later.  Questions are asked by the Steward if and when there is a necessity to
  gather information.

  There is one additional bit of the flow of interview sessions that is manual: the
  requirement of "user_saw_initial_screen."  This causes a "welcome" screen
  to be shown.  We always want this screen to be displayed first (at
  least as soon as we determine the user's language).
---
code: |
  if client not in case.plaintiff.elements and client.is_plaintiff:
    case.plaintiff.append(client)
  if client not in case.defendant.elements and not client.is_plaintiff and client.is_defendant:
    case.defendant.append(client)
  case.plaintiff.there_are_any = True
  case.defendant.there_are_any = True
comment: |
  This Steward relates to a court case.  It takes advantage of the
  basic-questions.yml file in the Steward docassemble.base.  This
  Steward file provides some functionality for Legal Stewards.

  For example, basic-questions.yml defines the objects "case" and "client."

  But in our Steward, what do we want to do with "case" and "client"?
  What is the relation of the client to the case?  Is the client the user,
  or a different person from the user?

  The purpose of the above code is to set initial values for the
  objects case.plaintiff and case.defendant.  These objects are
  DALang objects that function as Python lists.  They represent
  the plaintiffs and defendants in the case.

  This code will add the client as a plaintiff, or add the client as a
  defendant, depending on whether the client is a plaintiff or a
  defendant.  This code will trigger the asking of questions to
  determine whether the client is a plaintiff or a defendant, if those
  facts are unknown.  Elsewhere there is a question that defines the
  "is_plaintiff" attribute and another question that defines the
  "is_defendant" attribute.

  The end result of this code is to define the "there_are_any"
  attributes of the two lists.  Note that this code is not
  "mandatory."  It will be run when and if the Steward needs to know
  whether the lists are empty.  We set the attributes to True because
  all court cases need to have at least one plaintiff and at least one
  defendant.
---
event: client_kicked_out
progress: 100
question: |
  Sorry, you cannot proceed with the interview session.
subquestion: |
  You can only proceed with the interview session if you agree that your
  completion of the interview session with the Steward does not create an attorney-client
  relationship.

  % if user_understands_no_attorney_client_relationship == 'unsure':
  We suggest that you call us at 215-981-3800 to talk to us about the
  kinds of services we provide.
  % endif
decoration: exit
buttons:
  - Exit: exit
  - Restart: restart
comment: |
  This is an endpoint question (note that the only options are exiting
  or restarting).

  If the Steward was configured to show a progress bar, the progress
  bar would be set to 100% on this question.

  This question uses the "event" component.  "client_kicked_out" is a
  variable, just like any other variable, except that it is never
  defined, only sought.

  We saw above in the "mandatory" code block that if the user does not
  understand that no attorney-client relationship will be created, the
  "client_kicked_out" variable will be sought.  When that variable is
  sought, this question will be displayed to the user.

  This question also uses a "decoration."  This places an icon in the
  corner of the screen.  The image by the name of "exit" is defined
  in the basic-questions.yml file.
---
question: |
  Welcome to the Docassemble Framework Demonstration.
subquestion: |
  The following Steward is designed to demonstrate almost all of
  the Docassemble Framework's features.  At the end, you will be provided with a
  fake client letter and a fake pleading.

  % if interface() == 'web':
  In the navigation bar above, you can click "[Help]" to see the help
  text associated with the Steward and with the individual question
  (if any).  If "Help <i class="glyphicon glyphicon-star"></i>"
  appears in the navigation bar, that means help text specific to the
  question is available.

  Click "Source" to toggle the display of the DALang code used to
  generate the question.  (Note: the "Source" tab is available because
  this server is configured as a development server; end users would
  not see a "Source" tab.)
  % endif

  [Help]: ${ url_of('help') }
field: user_saw_initial_screen
buttons:
  - Ok, got it: True
comment: |
  This is the "splash screen" for the Steward.  The question is a
  multiple-choice question with one option.

  This example demonstrates that HTML can be combined with Markdown
  in the text of questions.  Here, we wanted to show a particular icon
  available in Bootstrap, so we inserted raw HTML.
---
generic object: Individual
question: |
  What language ${ x.do_question('speak') }?
field: x.language
choices:
  - English: en
  - Español: es
default: ${ language_from_browser() }
comment: |
  This is the first question that will be asked because there is
  an "initial" block above that needs the definition of user.language.

  This is a "generic object" question.  It is written in a "generic"
  way so that it will ask "What language do you speak?" or "What language
  does John Smith speak?" depending on whether "x" is the user or not.

  The language_from_browser() function sets the default choice to
  English or Spanish if the web server detects that the user's browser
  is set to either of these languages.  This method of determining the
  user's language is not 100% reliable, but it will save the user from
  making an extra click.
---
generic object: Individual
question: |
  ${ x.do_question('have', capitalize=True) } a support order?
subquestion: |
  If you aren't sure, look through your papers for a document that
  looks something like this.  If this document is signed by the judge,
  then you have a support order.
    
  [FILE sample-support-order.jpg, 100%]
yesno: x.has_support_order
comment: |
  This question illustrates how you can include images in your
  questions.  The file sample-support-order.jpg is part of the Steward
  docassemble.demo and it is stored in the package subdirectory
  docassemble/demo/data/static.  This is how you refer to a "static"
  file that exists within a Steward's subpackage.

  The "100%" indicates that the image width should fill the screen.
---
question: What form do you want to prepare?
decoration: document
buttons:
  - Custody Complaint:
      code: |
        law_category = "custody"
        pleading.type = "complaint"
        pleading.title = "Complaint for Custody"
    image: parentchild
  - Support Complaint:
      code: |
        law_category = "support"
        pleading.type = "complaint"
        pleading.title = "Complaint for Support"
    image: coins
comment: |
  This is an example of a multiple-choice question that runs Python
  code (as opposed to simply setting the value of a single variable).

  This example also shows how you can create square buttons with icons
  and labels: you just add an "image" value to the button item.
---
code: |
  if client_has_injury and injury_in_jurisdiction and \
     statute_of_limitations_ok:
    client_has_standing = True
  else:
    client_has_standing = False
comment: |
  This is an example of how a Steward can serve as a legal "expert
  system."  The variable "client_has_standing" (a legal concept) can
  be set using simple logical expressions in Python.  Legal concepts
  can be expressed as true/false variables and the law can be coded in
  logical expressions like these.

  Note that the "\" character at the end of a line is merely a
  formatting aid.  Python normally considers line breaks to indicate
  that a statement is finished.  The "\" character at the end of a
  line tells Python that the statement isn't finished yet.
---
question: Were you injured?
decoration: injury
yesno: client_has_injury
help:
  content: |
    An injury can take many forms.  It can be a physical injury or a
    purely financial injury.
  audio: schumann-clip-3.mp3
progress: 50
comment: |
  This question demonstrates how an audio file can be provided on the
  help screen of a question.
---
question: |
  What is the village idiot's name?
fields:
  - Somebody already mentioned: village_idiot
    datatype: object
    disable others: True
    choices:
      - case.plaintiff
      - case.defendant
  - First Name: village_idiot.name.first
  - Middle Name: village_idiot.name.middle
    required: False
  - Last Name: village_idiot.name.last
  - Suffix: village_idiot.name.suffix
    required: False
    code: name_suffix()
comment: |
  This question demonstrates the use of objects in a multiple choice
  question, as well as the feature of disabling fields when they are
  not necessary.  The question allows the user to indicate who the
  "village_idiot" is.  If the village idiot is a plaintiff or
  defendant, the user will be able to select the person's name from a
  list.  If the village idiot is not a plaintiff or defendant, the
  user can enter the person's name.  Either way, village_idiot will be
  an object.
---
question: |
  I understand that you live in ${ client.address.city }.
  Were you injured in ${ jurisdiction_state }?
yesno: injury_in_jurisdiction
---
question: When did your injury take place?
decoration: calendar
fields:
  - html: |
      The current date and time is <span class="mytime" id="today_time"></span>.
  - Date of Injury: injury_date
    datatype: date
css: |
  <style>
    .mytime {
       color: green;
    }
  </style>
script: |
  <script>
    $("#today_time").html(Date());
  </script>
comment: |
  You can embed raw HTML into a list of fields using the 'html' key.
  You can also expand the capabilities of what you do with this HTML by
  adding 'script' and 'css' keys.

  The text of 'script' is added to the bottom of the page, while the
  text of 'css' is added to the <head>.

  Note that you can use Mako templates in each of these components.
---
question: |
  Why do you think you deserve to win this case?
fields:
  - no label: explanation
    datatype: area
    hint: |
      I should win because . . .
---
code: |
  court.jurisdiction = ['US', 'state', 'PA', 'trial', 'Philadelphia County']
  jurisdiction_state = "Pennsylvania"
  jurisdiction_county = "Philadelphia"
comment: |
  This code sets some information about the current jurisdiction.  The
  Steward assumes that the legal case is in a Pennsylvania court.

  The court.jurisdiction variable uses a special format that is
  particular to the docassemble.base.legal module.  It is used to
  facilitate the use of "layers" of code, where there is a common
  layer of questions and code applicable at a federal level, another
  layer of questions and code applicable at a state level, another
  layer of questions and code applicable at a county level, etc.

  Note that this code is not "mandatory."  It will be called when and
  if the Steward needs to know any of these variables.
---
code: |
  if jurisdiction_state == "Pennsylvania":
      statute_of_limitations_years = 5
  else:
      statute_of_limitations_years = 2
---
code: |
  if jurisdiction_state == "Pennsylvania":
      if law_category == "custody" or law_category == "support":
          court.name = "Court of Common Pleas of " + \
          jurisdiction_county + " County, " + jurisdiction_state
---
code: |
  cutoff_date = current_datetime() - date_interval(years=statute_of_limitations_years)
  if as_datetime(injury_date) > cutoff_date:
      statute_of_limitations_ok = True
  else:
      statute_of_limitations_ok = False
comment: |
  This code uses some date/time functions to determine whether the
  date of the injury is within the statute of limitations period.

  The variable cutoff_date represents the latest date in the past when
  an injury could have occurred that would still be actionable under
  the statute of limitations.

  To calculate cutoff_date, we start with today's date and subtract a
  number of number of years given by the applicable statute of
  limitations.

  The number of years in the applicable statute of limitations period
  is the number stored in the variable statute_of_limitations_years.
---
generic object: Individual
decoration: home
question: |
  What is ${ x.possessive('home') } like?
fields:
  - Type of home: x.address.type
    datatype: radio
    shuffle: True
    choices:
      - Apartment
      - Leased house
      - Owned house
      - Mobile home
  - Amenities: x.address.amenities
    datatype: checkboxes
    code: |
      {u'chimney': u'Chimney', 'stove': 'Stove'}
  - note: |
      How would you describe the general *milieu* of ${ x.possessive('abode') }?
  - no label: x.address.milieu
    required: False
comment: |
  In this question, the type of home uses a "radio" selector.  The
  address type will be set to one of "Apartment," "Leased house,"
  "Owned house," or "Mobile home."  Because "shuffle" is true, the
  order of the choices will be random (different every time the page
  is loaded).

  The "amenities" of the home, by contrast, use a "checkbox" selector.
  This means that the variable will be defined not as text, but as a
  Python dictionary containing key/value pairs.  For example, if
  this question is asked regarding an Individual with the variable
  name "client," and the user selects "Chimney" only, the value of
  client.address.amenities will be a Python dictionary in which
  "chimney" is set to True and "stove" is set to False.

  The "amenities" field demonstrates that checkbox values and labels
  can be set using Python code.  The code needs to evaluate to a
  Python dictionary, where the values are the labels to be shown to
  the user and the keys are the keys that will be used in the
  resulting Python dictionary (x.address.amenities).

  The third "field" is not really a field; it is a "note."  This
  places text onto the screen.  The text can include Markdown and can
  be a Mako template.  In this case, the text introduces the fourth
  field, which is a text field with no label.  Since the label has the
  special value "no label," the field fills the width of the form.
---
generic object: Individual
decoration: home
question: |
  Where ${ x.do_question('live') }?
fields:
  - Address: x.address.address
  - Unit: x.address.unit
    required: False
    help: The apartment, suite, or unit number of the residence.
  - City: x.address.city
  - State: x.address.state
    code: states_list()
  - Zip: x.address.zip
    required: False
comment: |
  This question demonstrates fields that have the style of dropdown
  lists.  The values of a dropdown list can be generated with code
  that runs at the time the question is asked, or they can be
  hard-coded into the question itself.  In this case, we use the
  states_list() function to provide a list of U.S. states.
---
generic object: Individual
question: |
  Please upload one or more pictures of ${ x.yourself_or_name() }.
decoration: picture
fields:
  - A test file: x.picture
    datatype: files
comment: |
  You can accept file uploads from users by using the datatypes "file"
  (for a single file) or "files" (for one or more files).
---
generic object: Individual
question: |
  % if x.picture.number() > 1:
  Are these the pictures you uploaded?
  % else:
  Is this the picture you uploaded?
  % endif
subquestion: |  
  ${ x.picture }
yesno: x.picture_verified
comment: |
  This question demonstrates displaying a picture that a user has uploaded.
---
question: |
  On a scale of 1 to 10, how much hatred do you harbor toward
  ${ case.defendant }?
fields:
  no label: hatred_level
  datatype: range
  min: 1
  max: 10
---
def: kid_defs
mako: |
  <%def name="describe_as_adorable(person)"> \
  ${ person } is adorable. \
  </%def>
comment: |
  DALang uses the Mako templating system to expand variables
  within Markdown text.  Mako allows functions to be defined within
  source text using "def" constructs.  If you write Mako "def"
  functions, you may want to use them in more than one document.  This
  section shows how you can attach a name (e.g., kid_defs) to some
  Mako text, and an example below shows how an attachment can include
  this Mako text by referring to it by its name (kid_defs).

  Another way to write functions in DALang is to write methods
  that act on DALang objects, which you define in your objects.py
  file within your Steward.
---
comment: |
  This very long question is the Steward's main endpoint (it offers
  to define client_done, which was referred to in the mandatory code
  block above.  This question has two "attachment" documents.  Most of
  the Steward's questions are asked because they are needed by
  this question or one of its attachments.

  This question also demonstrates use of the "need" component to
  gather information about the case's plaintiffs and defendants up
  front.  This is not strictly necessary, because the case caption
  will cause those questions to be answered.  However, the "need"
  clause forces the Steward to gather the information up front, before
  it starts processing the question and its attachments.  This helps
  to direct the order of the questions in a more sensible fashion.
event: client_done
progress: 100
question: |
  % if client_has_standing:
    Congratulations!  You have a valid claim.
  % else:
    Sorry, you do not have a valid claim.
  % endif
decoration: finishline
subquestion: |
  Here is an advice letter and a pleading you can file.

  (Note: the options to see documents in Markdown and LaTeX format are
  hidden when the server is configured for production.
  End users will not see these options.)
help: |
  This is the end of the interview session, ${ client }.  You can exit or
  restart.

  I hope you enjoyed this interview session.
buttons:
  - Exit: exit
  - Restart: restart
attachments:
  - name: Advice Letter for ${ client }
    filename: Advice_letter_${ space_to_underscore(client) }
    description: |
      This is a *very* helpful advice letter.
    metadata:
      FirstHeaderRight: |
        Example, LLP [BR] 123 Main Street, Suite 1500 [BR] Philadelphia, PA 19102
      HeaderLeft: |
        ${ client } [BR] ${ today() } [BR] Page [PAGENUM]
      HeaderLines: "3"
      SingleSpacing: True
    content: |
      ${ today() }

      ${ client.address_block() }

      Dear ${ client.salutation() } ${ client.name.last }:

      Your marital status is ${ client.marital_status.lower() }.
      % if client.marital_status == 'Single' and village_idiot is not client:
      Perhaps you should marry ${ village_idiot }.
      % endif
      Your annual income is ${ currency(client.income.total()) }
      and the value of all you own is 
      ${ currency(client.asset.total()) }.  Your home is best described as
      a "${ client.address.type }."

      % if hatred_level > 8:
      You seem to dislike ${ case.defendant }.
      % endif

      % if client_has_standing:
      You have a valid claim.
      % else:
      Sorry, you do not have a valid claim.
      % endif

      Carles 8-bit polaroid, banjo bespoke Intelligentsia actually
      PBR&B hashtag. Asymmetrical banjo mustache fashion axe cardigan,
      polaroid literally taxidermy cornhole authentic 3 wolf moon yr
      meditation. Kale chips cliche distillery, stumptown mustache DIY
      hella cred. Cardigan church-key stumptown organic. IPhone street
      art leggings, art party 8-bit Blue Bottle mustache aesthetic
      selvage cold-pressed High Life semiotics Bushwick retro
      Banksy. Aesthetic hella mumblecore, readymade gluten-free
      locavore cliche keytar XOXO tote bag. Put a bird on it swag
      bicycle rights trust fund, hella small batch tousled church-key
      bitters Brooklyn normcore Portland gentrify keytar Austin.

      Semiotics DIY cronut, stumptown McSweeney's 90's plaid pork
      belly Brooklyn squid gentrify chillwave. Occupy forage irony
      banjo heirloom. Irony health goth gentrify, plaid hella Etsy 3
      wolf moon American Apparel chillwave Truffaut retro synth
      artisan wolf bitters. Williamsburg flannel VHS, quinoa banjo
      fingerstache plaid vinyl meditation. Banksy Vice salvia pickled,
      selvage stumptown narwhal artisan Bushwick tilde Portland
      keffiyeh Carles food truck. Master cleanse Echo Park cardigan,
      selvage health goth next level keffiyeh shabby chic hashtag
      aesthetic taxidermy Carles irony fixie. Hella organic swag pork
      belly Bushwick.

      Banh mi stumptown migas, raw denim iPhone distillery
      Pinterest Schlitz. Raw denim Marfa typewriter mustache PBR&B
      cold-pressed. Locavore crucifix occupy, quinoa actually pickled
      ugh ennui VHS normcore literally jean shorts cred
      post-ironic. Godard Pitchfork narwhal direct trade deep v
      drinking vinegar, fingerstache authentic listicle. Kitsch
      literally VHS readymade distillery tattooed. Aesthetic High Life
      shabby chic, typewriter swag plaid Etsy photo booth craft
      beer. Disrupt yr semiotics, wayfarers meh scenester tattooed
      keffiyeh fingerstache meditation chia roof party migas.

      Chambray art party craft beer pork belly health goth,
      locavore photo booth pickled. Cold-pressed gentrify street art,
      butcher direct trade salvia twee hashtag. Flannel semiotics wolf
      next level Tumblr gluten-free. Sustainable shabby chic migas
      Intelligentsia, swag synth meh lumbersexual gentrify. Gastropub
      lumbersexual Blue Bottle, +1 sustainable heirloom meditation
      Pitchfork deep v try-hard blog vinyl. Tofu banjo Kickstarter
      post-ironic cray tilde Tumblr, Marfa polaroid wolf. Schlitz
      selvage narwhal fanny pack, mustache scenester leggings cardigan
      Kickstarter street art polaroid fixie aesthetic PBR&B.

      Semiotics DIY cronut, stumptown McSweeney's 90's plaid pork
      belly Brooklyn squid gentrify chillwave. Occupy forage irony
      banjo heirloom. Irony health goth gentrify, plaid hella Etsy 3
      wolf moon American Apparel chillwave Truffaut retro synth
      artisan wolf bitters. Williamsburg flannel VHS, quinoa banjo
      fingerstache plaid vinyl meditation. Banksy Vice salvia pickled,
      selvage stumptown narwhal artisan Bushwick tilde Portland
      keffiyeh Carles food truck. Master cleanse Echo Park cardigan,
      selvage health goth next level keffiyeh shabby chic hashtag
      aesthetic taxidermy Carles irony fixie. Hella organic swag pork
      belly Bushwick.

      If you have any questions, you can call us at 215-391-9686.

      Sincerely,

      /s/

      John Smith, Attorney
  - name: ${ pleading.title }
    filename: ${ space_to_underscore(pleading.title) }
    metadata:
      FirstFooterCenter: "[HYPHEN] [PAGENUM] [HYPHEN]"
      FooterCenter: "[HYPHEN] [PAGENUM] [HYPHEN]"
      FirstFooterLeft: "${ pleading.title }"
      FooterLeft: "${ pleading.title }"
    usedefs:
      - kid_defs
    content: |
      ${ pleading.caption() }

      I am the ${ case.role_of(client) } in this case.
      % if client.child.number() > 0:
      I have ${ client.child.number_as_word() } ${ client.child.as_noun() }:

      % for child in client.child:
      #. ${ child }
      % endfor

      % for child in client.child:
      ${ describe_as_adorable(child) }
      % endfor
      Aren't children :baby: such a blessing?
      % if client.has_support_order:
      I already have a support order.
      % endif
      % endif

      <%
        index = 0
      %>
      % for party in case.parties():
      The ${ ordinal(index) } party in this case is ${ party },
      a ${ case.role_of(party) },
      % if party.child.number() > 0:
      who has the following ${ party.child.as_noun() }:

      % for child in party.child:
      * ${ child }
      % endfor

      % else:
      who has no children.
      % endif
      <%
        index += 1
      %>
      % endfor
      
      This petition should be granted.
      ${ fix_punctuation(explanation) }
      % if client.picture_verified:
      Look how cute I am:

      [FLUSHLEFT] ${ client.picture }
      % endif

      Chambray art party craft beer pork belly health goth, locavore
      photo booth pickled. Cold-pressed gentrify street art, butcher
      direct trade salvia twee hashtag. Flannel semiotics wolf next
      level Tumblr gluten-free. Sustainable shabby chic migas
      Intelligentsia, swag synth meh lumbersexual gentrify. Gastropub
      lumbersexual Blue Bottle, +1 sustainable heirloom meditation
      Pitchfork deep v try-hard blog vinyl. Tofu banjo Kickstarter
      post-ironic cray tilde Tumblr, Marfa polaroid wolf. Schlitz
      selvage narwhal fanny pack, mustache scenester leggings cardigan
      Kickstarter street art polaroid fixie aesthetic PBR&B.

      Please grant me the relief I request!

      [FLUSHLEFT] Respectfully submitted,

      % if client.signature_verified:
      [FLUSHLEFT] ${ client.signature.show(width='2in') }
      % else:
      [FLUSHLEFT] ${ blank_signature }
      % endif

      [FLUSHLEFT] ${ client }, ${ title_case(case.role_of(client)) }
---
language: es
question: |
  Bienvenido a la demostración Docassemble Framework.
subquestion: |
  La siguiente entrevista está diseñado para demostrar la casi
  totalidad de características de Docassemble Framework. Al final, se le
  proporcionará un carta cliente falso y un escrito falso.

  En la barra de navegación de arriba, puede hacer clic en "Ayuda"
  para ver el texto de ayuda asociado a la entrevista y con la
  pregunta individual. Si "Ayuda <i class="glyphicon
  glyphicon-star"></i>" aparece en la barra de navegación, eso
  significa que el texto de ayuda específica a la cuestión está
  disponible.

  Haga clic en "Fuente" para cambiar la visualización del código
  DALang utilizado para generar la pregunta.
  
  (This demonstration Steward is not fully bilingual in
  Spanish; only this page has.  The remainder of the interview session will
  fall back to using the available English versions of each question.)

field: user_saw_initial_screen
datatype: boolean
buttons:
  - Comprendo: True
comment: |
  This demonstration Steward is not available in Spanish, but this
  question and the question after it demonstrate how multi-lingual
  Stewards can be constructed.  This question offers to set
  "user_saw_initial_screen," just like a previous question block did,
  except that this question has a "language: es" component, indicating
  that this question should only be used if the current language (as
  set by the "initial" code block above using the set_language()
  function) is Spanish.
---
language: es
auto terms:
  cliente: |
    El cliente es la persona que está llenando este formulario
comment: |
  This demonstrates how vocabulary terms can be provided in a
  language other than the default language.
---
generic object: Individual
question: |
  What is ${ x.possessive('gender') }?
field: x.gender
choices:
  - "Male :male:": male
  - "Female :female:": female
  - Other: other
comment: |
  You can include "emoji-style" images by putting colons around an
  image name (as defined in an "images" block).  This feature works
  within labels as well as within question text.
---
generic object: Individual
question: |
  How much ${ x.do_question("make") } from ${ i }?
fields:
  - Amount: x.income[i].value
    datatype: currency
  - "": x.income[i].period
    datatype: number
    code: |
      period_list()
comment: |
  If you do not want a field to be labeled, you can use "" as the
  label name.

  The function period_list() provides a list of options (12 for "Per
  Month," 1 for "Per Year," and 52 for "Per Week").

  The datatype "currency" is like the datatype "number" except that
  causes the input field to be displayed with a locale-specific
  currency symbol.
---
generic object: Individual
question: |
  How much ${ x.do_question("make") } from employment?
decoration: bills
fields:
  - Employment Income: x.income['employment'].value
    datatype: currency
  - "": x.income['employment'].period
    datatype: number
    code: |
      period_list()
comment: |
  The previous question was a general question; this is a specific
  question that asks the question a certain way if the income type is
  "employment."  Although this question and the previous question are
  both capable of defining x.income['employment'].value, this one
  takes precedence because it is more specific.
  This is called precedence.

  The following questions are also specific cases.  The decorations
  are different for each question.
---
generic object: Individual
question: |
  How much ${ x.do_question("make") } from self-employment?
decoration: bills
fields:
  - Self-employment Income: x.income['self employment'].value
    datatype: currency
  - "": x.income['self employment'].period
    datatype: number
    code: |
      period_list()
---
generic object: Individual
question: |
  How much ${ x.do_question("make") } from SSI?
decoration: bills
fields:
  - SSI Income: x.income['SSI'].value
    datatype: currency
  - "": x.income['SSI'].period
    datatype: number
    code: |
      period_list()
---
generic object: Individual
question: |
  How much ${ x.do_question("make") } from cash assistance 
  (Temporary Assistance to Needy Families or TANF)?
decoration: bills
fields:
  - TANF Income: x.income['TANF'].value
    datatype: currency
  - "": x.income['TANF'].period
    datatype: number
    code: |
      period_list()
---
generic object: Individual
question: |
  How much ${ x.do_question("have") } in 
  ${ i }?
fields:
  - Amount: x.asset[i].value
    datatype: currency
---
generic object: Individual
question: |
  How much ${ x.do_question("have") } in 
  ${ x.pronoun_possessive("checking account") }?
decoration: piggybank
fields:
  - Amount in Checking Account: x.asset['checking account'].value
    datatype: currency
---
generic object: Individual
question: |
  How much ${ x.do_question("have") } in 
  ${ x.pronoun_possessive("savings account") }?
decoration: piggybank
fields:
  - Amount in Savings Account: x.asset['savings account'].value
    datatype: currency
---
generic object: Individual
question: |
  How much ${ x.do_question("have") } in stocks and bonds?
decoration: stocks
fields:
  - Amount in Stocks and Bonds: x.asset['stocks and bonds'].value
    datatype: currency
---
generic object: Individual
question: |
  ${ x.do_question("have", capitalize=True) } income from ${ i }?
yesno: x.income[i].exists
comment: |
  This question and the following questions ask the threshold question
  of whether the income or assets is applicable.  If it does not
  "exist," there is no need to ask for its value.
---
generic object: Individual
question: |
  What kinds of income ${ x.do_question("have") }?
decoration: bills
fields:
  - Employment: x.income['employment'].exists
    datatype: yesnowide
  - Self-employment: x.income['self employment'].exists
    datatype: yesnowide
  - SSI: x.income['SSI'].exists
    datatype: yesnowide
  - Cash assistance: x.income['TANF'].exists
    datatype: yesnowide
  - None of the above: x.no_income_exists
    datatype: yesnowide
    uncheck others: True
comment: |
  The datatype "yesnowide" is just like the data type "yesno" except
  that it fills the width of the form rather than aligning with other
  fields that use labels.
---
generic object: Individual
question: |
  ${ x.do_question("own", capitalize=True) } any ${ i }?
yesno: x.asset[i].exists
---
generic object: Individual
question: |
  What kinds of assets ${ x.do_question("own") }?
decoration: piggybank
fields:
  - Checking Account: x.asset['checking account'].exists
    datatype: yesnowide
  - Savings Account: x.asset['savings account'].exists
    datatype: yesnowide
  - Stocks and Bonds: x.asset['stocks and bonds'].exists
    datatype: yesnowide
...
{% endhighlight %}

# The basic-questions.yml File, Incorporated by Reference into the Demo Steward

Many of the questions asked in the demonstration Steward do not need
to be defined in the Steward's main source file because they are already
defined in the `basic-questions.yml` file.  Here is an annotated
guide to this file.

{% highlight yaml %}
---
---
metadata:
  description: |
    This question file contains questions that are common in
    law-related Stewards.  It also imports DALang functions,
    initializes a role system involving a "client" and an "advocate,"
    and defines objects including "client," "advocate," "case,"
    "spouse," "pleading," and "court."    
  authors:
    - name: Jonathan Pyle
      organization: none
  revision_date: 2018-09-21
comment: |
  A "metadata" block contains information about the Steward, such as
  the title of the Steward as displayed in the navigation bar.
---
modules:
  - docassemble.base.legal
comment: |
  A "modules" section imports class names and function names from
  a module.  The docassemble.base.legal module defines some
  object classes and functions that are useful for Legal Stewards.
  
  Using docassemble.base.legal in "modules" also has the effect of
  importing all of the class names and function names that are in
  docassemble.base.util.  So you never need to include both
  docassemble.base.legal and docassemble.base.util together in the
  same "modules" block.
---
default role: client
code: |
  if user_logged_in() and user_has_privilege('advocate'):
    user = advocate
    role = 'advocate'
  else:
    user = client
    role = 'client'
  set_info(user=user, role=role)
comment: |
  This is a special "initial block" that initializes the "roles" system
  for this Steward.  (This is an advanced feature.)
  
  The default user role is "client" and a secondary role is
  "advocate."  Unless a block has a "role" component, all questions
  will require the user to be a "client."  The user is assumed to have
  the role of "advocate" role for interview sessions with this Steward if the user is logged
  in and the user has "advocate" as one of his or her user roles.

  Many DALang functions and methods need to know who the user is.
  The set_info() function communicates that information to the
  DALang code.

  Since the code here is paired with the "default role" component,
  it is run as "initial" code, meaning that it is run every time
  the Steward processes this DALang (i.e., every time the screen
  loads).  This is important because in a multi-user interview, a
  "client" and an "advocate" could be a part of the same
  interview session with the same dictionary of variables at the same time.
  But they would need to see different things, so it isn't enough to just
  to use a variable for the Steward to keep track of the current
  user; this needs to be reconsidered every time the screen loads.
---
event: role_event
question: You are done for now.
subquestion: |
  % if 'advocate' in role_needed:
    An advocate needs to review your answers before you can proceed.

    Please remember the following link and come back to it when you
    receive notice to do so:

    [${ interview_url() }](${ interview_url() })
    
  % else:
    Thanks, the client needs to resume the interview session now.
  % endif
decoration: exit
buttons:
  - Exit: leave
comment: |
  This block is related to the "roles" system that was initialized in
  the previous block.  (This is an advanced feature.)

  When a Steward needs to ask a question that requires a role other
  than the role of the current user, it needs to display a special
  message for the user.  It does this by searching for a question that
  offers to define the variable "role_event," and displaying that
  question.  The question above is an example of such a question.  It
  will be displayed in the event of a "role change" because it
  contains the component "event: role_event."
---
objects:
  - case: Case
  - client: Individual
  - spouse: Individual
  - advocate: Individual
  - pleading: LegalFiling
  - court: Court
comment: |
  An "objects" section initializes variables that are DALang
  objects.  The object types here (Case, Individual, LegalFiling, and
  Court) are imported through the docassemble.base.legal module.
  (See the "modules" block above.)
---
mandatory: true
code: |
  case.court = court
  pleading.case = case
comment: |
  This code defines some basic relations among the objects created in
  the objects block of this DALang file.

  The objects created by the `objects` block do not have any
  connections among themselves, initially.  The Steward needs to
  make those connections.  This "mandatory" code block establishes
  those connections.

  These connections among objects are what allows you to write things
  like pleading.caption().  In order to write the caption for a
  pleading, it is necessary to know the case of which the pleading is
  a part and the court in which the case is filed.  The ".caption()"
  method only has access to the attributes of "pleading," but these
  connections allow the ".caption()" method to gain access to the case
  and the court.
---
image sets:
  freepik:
    attribution: |
      Icon made by [Freepik](http://www.flaticon.com/authors/freepik)
    images:
      bills: money146.svg
      children: children2.svg
      finishline: checkered12.svg
      gavel: court.svg
      gaveljudge: magistrate.svg
      home: home168.svg
      piggybank: savings1.svg
      scalesofjustice: judge1.svg
      stocks: increasing10.svg
      wallet: commerce.svg
      document: contract11.svg
      calendar: calendar146.svg
      picture: picture64.svg
      parentchild: man32.svg
      coins: coins36.svg
      exit: open203.svg
      man: silhouette21.svg
      person: silhouette21.svg
      woman: women13.svg
      girl: girl4.svg
      male: male244.svg
      female: female243.svg
      map: map32.svg
comment: |
  Here we define some icons for inclusion as decorations or emoji.
  These files are located in the docassemble.base package in the
  subdirectory docassemble/base/data/static.
---
generic object: Individual
question: |
  What is ${ x.possessive('date of birth') }?
fields:
  - Date of Birth: x.birthdate
    datatype: date
comment: |
  This question file defines a number of "generic" questions like
  these.  If your Steward refers to a variable called user.birthdate
  durring an interview session, it will first look for a question that sets "user.birthdate"
  specifically, but if it does not find it, it will look for a
  question for which the generic object property is set to the object
  type of the user object, which is Individual, and where the question
  offers to set the variable x.birthdate.
  
  It will find that question here.

  The question uses the possessive() method, which is a method of the
  Individual class.  The result is that the question will be "What is
  your date of birth?" if x is the user, but will otherwise ask "What
  is Jane Doe's date of birth?"

  By using "generic" questions, you can write a single question that
  works in a variety of circumstances.  This saves you from having to
  write multiple questions, and also helps ensure that if you want to
  make a global change to the way a question is asked, you can do so
  in one place.

  If you ever want to use a more specific question for a specific
  variable, you can.  For example, if your code calls for
  spouse.birthdate, you may to ask the question in a different way.
  (E.g., "What is the birthdate of your lovely spouse?  If you don't
  know this, you are in deep trouble!")  You would do this by defining
  a non-generic question that sets spouse.birthdate, in which case
  the Steward would use that question instead of the generic question.
  This is called precedence.
---
generic object: Individual
question: |
  What is ${ x.possessive('time zone') }?
fields:
  - Time Zone: x.timezone
    code: timezone_list()
---
generic object: Individual
question: |
  What is ${ x.possessive('Social Security Number') }?
fields:
  - Social Security Number: x.ssn
---
generic object: Individual
question: |
  ${ x.is_are_you(capitalize=True) } a defendant in this case?
yesno: x.is_defendant
---
generic object: Individual
field: x.marital_status
question: |
  What is ${ x.possessive('marital status') }?
choices:
  - Married: Married
  - Single: Single
  - Divorced: Divorced
  - Separated: Separated
comment: |
  This is an example of a multiple-choice question.  Each of the
  choices can be a key/value pair, or it can be a single text item.
  If the choice is a key/value pair, the key is the label that is
  shown to the user and value is the value to which the variable will
  be set.
---
field: user_understands_how_to_use_signature_feature
question: Instructions for signing your name
subquestion: |
  On the next screen, you will see a box in which you can sign your
  name using your mouse, track pad, or touch screen.  If you make a
  mistake, you can press "Clear" and try again.  For best results, try
  signing your name *slowly*.
---
generic object: Individual
question: |
  Sign your name
signature: x.signature
need:
  - x.name.first
  - user_understands_how_to_use_signature_feature
under: |
  ${ x.name }
comment: |
  A Steward can collect signatures from users, who can write their
  signature with their finger on a touchscreen device, or use a mouse
  or trackpad.  The signatures can be added to documents.
---
template: blank_signature
content: |
  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
comment: |
  This template can be used to insert into a document a blank line
  that someone might sign.
---
template: empty_signature
content: |
  \_\_\_[Your signature here]\_\_\_
comment: |
  This template can be used in place of a user's signature.  It is a
  good practice to show users where their signature would go on a
  document before asking the user for his or her signature.
---
generic object: Individual
question: |
  Is this ${ x.possessive('signature') }?
subquestion: |
  ${ x.signature.show() }
buttons:
  - "Yes":
      generic object: Individual
      code: |
        x.signature_verified = True
  - "No":
      generic object: Individual
      code: |
        x.signature_verified = False
  - "Let me try again":
      generic object: Individual
      code: |
        force_ask('x.signature')
comment: |
  This is an example of a multiple choice question where selecting an
  option causes code to be run.  Each multiple choice option contains
  an embedded block.
  
  Note that in order for an "embedded" code or question block to use
  the special variable "x," you need to declare a generic object
  within the embedded code or question.
---
generic object: Individual
question: |
  ${ x.is_are_you(capitalize=True) } a citizen of the United States?
yesno: x.is_citizen
---
field: user_understands_no_attorney_client_relationship
question: |
  Your use of this system does not mean that you have a lawyer.  Do
  you understand this?
buttons:
  - "I understand": understands
  - code: |
      [{'does not understand':"I do not understand"}, {'unsure':"I'm not sure"}]
comment: |
  You can specify whether you want multiple choices to appear as
  buttons by using the word "buttons" instead of the word "choices."

  Also, the example above shows how you can use Python code to
  generate the selections of multiple-choice question.  The code is
  evaluated at the time the question is asked.
---
generic object: Individual
question: |
  What is ${ x.possessive('e-mail address') }?
fields:
  - E-mail: x.email
    datatype: email
comment: |
  The datatype "email" presents a text box that is like ordinary text
  boxes except that validation is applied that checks to make sure the
  e-mail address is valid.  Also, on supporting mobile web browsers,
  there is a different keyboard option (e.g, the @ sign is readily
  available).
---
generic object: Individual
question: |
  What is ${ x.possessive('gender') }?
field: x.gender
choices:
  - Male: male
  - Female: female
  - Other: other
---
generic object: Individual
question: |
  What is ${ x.object_possessive('name') }?
fields:
  - First Name: x.name.first
    default: ${ x.first_name_hint() }
  - Middle Name: x.name.middle
    required: False
  - Last Name: x.name.last
    default: ${ x.last_name_hint() }
  - Suffix: x.name.suffix
    required: False
    code: |
      name_suffix()
comment: |
  If an object does not have a name yet, generic questions can refer
  to it by the name of the variable itself, using the method
  .object_possessive().  For example, suppose you create an object,
  case.judge, with the class of Individual.  If the name of case.judge
  is ever needed, the Steward will use the question above to ask "What
  is the name of the judge in the case?"  If the object is called
  user, it will ask "What is your name?"  If the object is called
  village_idiot, it will ask "What is the village idiot's name?"
---
generic list object: Individual
question: |
  What is the name of the ${ x[i].object_name() }?
fields:
  - First Name: x[i].name.first
  - Middle Name: x[i].name.middle
    required: False
  - Last Name: x[i].name.last
  - Suffix: x[i].name.suffix
    required: False
    code: |
      name_suffix()
comment: |
  Generic questions can also use indices, for example to fill out the
  names of a list of people.  (E.g., case.plaintiff.)

  This example also illustrates how the developer can control whether the
  user can leave a field blank.  By default, all fields are required,
  but the developer can add required: False to a field to indicate that
  the field can be left blank.
---
generic list object: Individual
question: |
  What is ${ x.possessive(ordinal(i) + " child") }'s name?
fields:
  - Somebody already mentioned: x.child[i]
    datatype: object
    disable others: True
    choices: case.all_known_people()
    exclude:
      - x
      - x.child
  - First Name: x.child[i].name.first
  - Middle Name: x.child[i].name.middle
    required: False
  - Last Name: x.child[i].name.last
    default: ${ x.name.last }
  - Suffix: x.child[i].name.suffix
    required: False
    code: |
      name_suffix()
comment: |
  This illustrates the use of the ".possessive()" method of the class
  Individual.  Depending on who x is, this question will ask different
  things:

  Example 1: What is your second child's name?

  Example 2: What is John Doe's first child's name?
---
generic object: DAList
question: |
  Are there any ${ x.as_noun(plural=True) }?
yesno: x.there_are_any
comment: |
  The attributes .there_are_any and .there_is_another are special
  attributes that are used in the gathering of "groups" of things
  by the Steward.
---
generic object: Individual
question: |
  ${ x.do_question('have', capitalize=True) } any children?
yesno: x.child.there_are_any
decoration: children
comment: |
  This illustrates the use of the ".do_question()" method of the class
  Individual.  Depending on who x is, this question will ask different
  things:

  Example 1: Do you have any children?

  Example 2: Does Jane Doe have any children?
---
generic object: DAList
question: |
  You have told me that there ${ x.does_verb("is") }
  ${ x.number_as_word() } ${ x.as_noun() }, ${ x }.
  Is there another ${ x.as_singular_noun() }?
yesno: x.there_is_another
comment: |
  It is possible to write highly generalized "generic" questions that
  use functions that ask questions of users based on variable names
  and linguistic variations of variable names.  For that reason, it is
  a good practice to give your variables meaningful, plain-English
  names.

  For example, if you create a PartyList called "plaintiff," this
  generic question will ask something like: "You have told me that
  there is one plaintiff, John Smith.  Is there another plaintiff?"
  This would not be possible if your variable name was something that
  only made sense to you, like "bad_guys_list_two."
---
generic object: Individual
question: |
  So far, you have told me about
  ${ x.possessive(x.child.number_as_word()) }
  ${ x.child.as_noun() }, ${ x.child }.
  ${ x.do_question('have', capitalize=True) } any other children?
yesno: x.child.there_is_another
decoration: children
comment: |
  This also illustrates the use of various methods of the class Individual.
  Depending on who x is, this question will ask different things:

  Example 1: So far, you have told me about John Doe's two children, 
  Sally Doe and Harold Doe.  Does John Doe have any other children?

  Example 2: So far, you have told me about your one child, Kathleen 
  Smith.  Do you have any other children?
---
generic object: Individual
question: |
  ${ x.is_are_you(capitalize=True) } a plaintiff in this case?
subquestion: |
  A "plaintiff" is a person who starts a case by filing a lawsuit
  against a person called a "defendant."  Plaintiffs and defendants
  are the "parties" in a case.
decoration: scalesofjustice
yesno: x.is_plaintiff
---
generic object: Individual
question: |
  Where ${ x.do_question('live') } in 
  ${ state_name(case.state) }?
fields:
  - Address: x.address.address
  - Unit: x.address.unit
    required: False
    help: The apartment, suite, or unit number of the residence.
  - City: x.address.city
  - State: x.address.state
    default: 
      code: |
        case.state
    code: |
      us.states.mapping('abbr', 'name')
  - Zip: x.address.zip
    required: False
---
generic object: Address
question: |
  In which county is
  ${ x.on_one_line() }
  located?
fields:
  - County: x.county
---
generic object: Address
sets: x.county
code: |
  x.geolocate()
comment: |
  This code block and the question before it illustrate the concept
  of "fallback" questions.  If the Steward needs the "county"
  attribute of an address, but finds that it is not defined, it will
  first run this code block, which "geolocates" the address.  That is,
  it goes on to the internet and runs the address through a
  geolocation service, which returns geographic information about the
  address.

  This code block uses the "sets" component to indicate that the code
  block offers sets the attribute "county."  Normally, you don't have
  to use "sets" with code blocks because the Steward can see by
  looking at the DALang code what variables the code will set.  In the case
  of the code "x.geolocate()," however, it is not apparent that the
  code is offering to set the "county" attribute.  Therefore we need
  to manually specify what the code block is offering to do so.

  It is significant that the code block merely "offers" to set these
  variables.  The "x.geolocate()" code might fail.  The user might put
  in an address that the geolocation service does not understand.  Or
  the geolocation service might be down at the time.  If that happens,
  the code block will run, but the attributes will not be set.

  If the variable that a code block offers to set is not actually set
  when the code is run, the Steward will look for another block that
  offers to set the variables.  In the case of the "county" attribute
  of an address, the question immediately preceding this one offers to
  set the "county" attribute.  It does so by asking the user a
  question, rather than by using a geolocation service.  This question
  serves as a "fallback" question.

  Note that when the Steward looks for a block that offers to set a
  variable, it starts at the end of the DALang and proceeds
  backward.  Therefore, the order in which these blocks appear in
  the DALang file is significant.
---
generic object: City
question: |
  In which county in
  ${ state_name(x.state) }
  is
  ${ x.city }
  located?
fields:
  - County: x.county
    hint: |
      e.g., Springfield County
---
generic object: City
sets: x.county
code: |
  x.geolocate()
comment: |

  Suppose you have an object "birthplace" of type "City."  A "City"
  object is a subtype of an "Address," and an "Address" is a type of
  "DAObject."  If your Steward needs a definition of
  birthplace.county, the Steward will first look for blocks that offer
  to define "birthplace.county," then for "generic object: City"
  blocks that offer to define "x.county," then for "generic object:
  Address" blocks that offer to define "x.county," then for "generic
  object: DAObject" blocks that offer to define "x.county."
  This is called precedence.

  Therefore, the "generic object: Address" code block is capable of
  defining "birthplace.county."  However, if we wish to have a
  fallback question that is "City"-specific, and we tag it with
  "generic object: City," this question will take priority over the
  "generic object: Address" code block.

  Therefore, in order to have a "City"-specific fallback question, we
  also need a "City"-specific code block.
---
generic object: Document
question: |
  Are you able to attach or take a picture of ${ x.title }?
yesno: x.able_to_attach
---
generic object: Document
question: |
  Please attach or take a picture of ${ x.title }.
fields:
  - label: |
      ${ capitalize(x.title) }
    field: x.file
    datatype: file
comment: |
  These two questions facilitate using the "Document" object type to
  gather uploaded documents if the user is able to upload the document.
---
generic object: Individual
question: |
  In what country ${ x.do_question('live') }?
fields:
  - Country: x.address.country
---
generic object: Individual
question: |
  In what neighborhood ${ x.do_question('live') }?
fields:
  - Neighborhood: x.address.neighborhood
---
generic object: Individual
question: |
  In what county ${ x.do_question('live') }?
fields:
  - County: x.address.county
---
generic object: Address
sets:
  - x.county
  - x.country
  - x.neighborhood
code: |
  x.geolocate()
comment: |
...
{% endhighlight %}

[Bootstrap]: https://en.wikipedia.org/wiki/Bootstrap_%28front-end_framework%29
[YAML]: https://en.wikipedia.org/wiki/YAML
[configuration file]: {{ site.baseurl }}/docs/config.html
[DALang]: {{ site.baseurl }}/docs/interviews.html#yaml
[server]: {{ site.baseurl }}/docs/installation.html