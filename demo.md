---
layout: page
title: Demo
---

[Run a simple demonstration] to see what the standard web interface
looks like.

The interface is based on [Bootstrap], which is both mobile-friendly
and desktop-friendly.  Try it out on a mobile device.

Keep in mind that this system is under active development.  The
example interview is not intended to make logical sense as an
interview; it is simply intended to demonstrate the features of
docassemble.

## The demo YAML file

The YAML file that generates the interview is listed below.  Note that:

* It incorporates by reference another YAML file, which specifies how
  basic questions should be asked.
* The code is not entirely self-explanatory, but for computer code, it
  is pretty close to plain English.
* Note that complicated processes, such as a series of questions that
  gather the names of the user's children, can be specified in a few
  lines of code.
* Most of the bits of logic are not specified in any particular order.
  If docassemble needs to get the value of a variable, it knows where
  to find it.  This makes things easier for the author, who can
  organize the code however he or she wants.  Moreover, the author can
  address the underlying legal logic in modular, bite-size pieces.
  The logic does not have to be placed into a specific structure in an
  interview or a document.  The bits of logic can be packaged and
  reused in a variety of contexts.

{% highlight yaml %}
metadata:
  description: |
    This is a demonstration of the docassemble system.
  authors:
    - name: Jonathan Pyle
      organization: Example, Inc.
  revision_date: 2015-09-28
comment: |
  A "metadata" block contains information about the YAML file, such as
  the name of the author.
---
interview help:
  heading: About this web site
  content: |
    Answer each question.  At the end, you may be given a document that you
    can save.

    If you see a word written in green text, you can click on it to
    see more information about the word.  You can try this out by here
    to find out more about rhododendron plants.
comment: |
  An "interview help" block adds text to the "Help" page of every
  question in the interview.  If the question has help text of its
  own, the "interview help" will appear after the question-specific
  help.
---
include:
  - basic-questions.yml
comment: |
  This loads some question definitions that are common to many legal
  interviews.  It also defines basic variables like "user" and sets the
  names of icons that you can use to "decorate" your questions.

  The "basic-questions.yml" file is in the docassemble.base package, in the
  directory docassemble/base/data/questions.

  You can include question files from other packages by explicitly referring
  to their package names.  E.g., "docassemble.helloworld:questions.yml" refers
  to the file questions.yml in the docassemble/helloworld/data/questions directory.
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
  "decorate" your questions.  Loading the "basic-questions.yml" file
  already defined a number of icons, but this block defines some more
  icons.

  Since this file, questions.yml, is in the docassemble.demo package, the
  image files referenced here are also in the docassemble.demo package.  The
  files are located in the directory docassemble/demo/data/static.

  Since most free icons available on the internet require attribution,
  the "image sets" block allows you to specify what attribution text
  to use for particular icons.  The web app shows the appropriate
  attribution text at the bottom of any page that uses one of the
  icons.
---
imports:
  - datetime
  - dateutil.relativedelta
  - dateutil.parser
  - us
comment: |
  This loads some Python modules that we will need in the interview.
---
objects:
  - village_idiot: Individual
comment: |
  In a question below we will refer to the variable "village_idiot."
  This "objects" block creates the variable "village_idiot" and
  specifies that it is an object of type "Individual."  It is
  important to define objects early on in your interview, before any
  "mandatory" code blocks.
---
terms:
  rhododendron: |
     A genus of shrubs or small trees, often having handsome
     evergreen leaves, and remarkable for the beauty of their
     flowers.
  custody order: |
    An order signed by a family court judge that says who gets to have what
    kind of custody over a child.
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
  term, you can define certain vocabulary words, and docassemble will
  turn them into hyperlinks wherever they appear.  When the user
  clicks on the hyperlink, a popup appears with the word's definition.
---
mandatory: True
code: |
  if user_understands_no_attorney_client_relationship == "understands":
    need(user_done)
  else:
    need(user_kicked_out)
comment: |
  This is the code that directs the flow of the interview.  It
  indicates to the system that we need to get to the endpoint
  "user_done."  There is a question below that "sets" the variable
  "user_done."  Docassemble will ask all the questions necessary to
  get the information need to pose that that final question to the
  user.

  However, if the answer to the question
  user_understands_no_attorney_client_relationship is not
  "understands," the interview will looks for a question that sets the
  variable "user_kicked_out."
  
  "Mandatory" sections like this one are evaluated in the order they appear
  in the question file.
---
progress: 100
question: |
  Sorry, you cannot proceed with the interview.
subquestion: |
  You can only proceed with the interview if you agree that your
  completion of the interview does not create an attorney-client
  relationship.

  % if user_understands_no_attorney_client_relationship == 'unsure':
  We suggest that you call us at 215-981-3800 to talk to us about the
  kinds of services we provide.
  % endif
decoration: exit
buttons:
  - Exit: exit
  - Restart: restart
sets: user_kicked_out
comment: |
  If docassemble is configured to show a progress bar, the progress bar will
  be set to 100% on this question, which is an endpoint question (since the only
  options are exiting or restarting).
---
question: |
  Do you have a support order?
subquestion: |
  If you aren't sure, look through your papers for a document that looks
  something like this.  If this document is signed by the judge, then
  you have a support order.
    
  [IMAGE docassemble.demo:sample-support-order.jpg, 100%]
yesno: user.has_support_order
comment: |
  This question illustrates how you can include images in your questions.
  The file sample-support-order.jpg is stored in the docassemble.demo package
  in the subdirectory docassemble/demo/data/static.  This is how you refer to
  a "static" file that exists within a docassemble subpackage.
---
question: What form do you want to prepare?
decoration: document
sets:
  - pleading.title
  - law_category
  - pleading.type
buttons:
  - "Custody Complaint":
      code: |
        law_category = "custody"
        pleading.type = "complaint"
        pleading.title = "Complaint for Custody"
    image: parentchild
  - "Support Complaint":
      code: |
        law_category = "support"
        pleading.type = "complaint"
        pleading.title = "Complaint for Support"
    image: coins
comment: |
  This is an example of a multiple-choice question that runs Python
  code (as opposed to simply setting the value of a single variable.
  Questions that run Python code need to include a list of the
  variables that the code "sets," because docassemble is not able to
  determine these variables automatically, as it usually can.

  This example also shows how you can create square buttons with icons
  and labels: you just add an "image" value to the button item.
---
comment: |
  The following seven lines of code ask all the necessary questions to
  gather the names of the plaintiffs in the case, when the user may
  not be a plaintiff.
code: |
  case.plaintiff.gathering = True
  if user_is_plaintiff and user not in case.plaintiff:
    case.plaintiff.add(user)
  if case.plaintiff.number_gathered() == 0:
    newplaintiff = case.plaintiff.addObject(Individual)
  while case.plaintiff.there_is_another:
    newplaintiff = case.plaintiff.addObject(Individual)
    del case.plaintiff.there_is_another
  case.plaintiff.gathering = False
  case.plaintiff.gathered = True
---
comment: |
  This code will ask the user if he or she is a defendant, so long as the user
  is not already a plaintiff.  Then it will ask for the names of the defendants.
code: |
  case.defendant.gathering = True
  if user not in case.defendant and not user_is_plaintiff and user_is_defendant:
    case.defendant.add(user)
  if case.defendant.number_gathered() == 0:
    newdefendant = case.defendant.addObject(Individual)
  while case.defendant.there_is_another:
    newdefendant = case.defendant.addObject(Individual)
    del case.defendant.there_is_another
  case.defendant.gathering = False
  case.defendant.gathered = True
---
comment: |
  This code gathers the names of the children of all of the parties.
code: |
  people = [user]
  people.extend(case.parties())
  for indiv in people:
    indiv.child.gathered
---
comment: |
  This is an example of how docassemble can serve as an "expert system."
  The variable "user_has_standing" (a legal concept) can be set using simple
  logical expressions in Python.
code: |
  if user_has_injury and injury_in_jurisdiction and statute_of_limitations_ok:
    user_has_standing = True
  else:
    user_has_standing = False
---
question: Were you injured?
decoration: injury
yesno: user_has_injury
help: |
  An injury can take many forms.  It can be a physical injury or a
  purely financial injury.
progress: 50
---
question: |
  I understand that you live in ${ user.address.city }.
  Were you injured in ${ jurisdiction.state }?
yesno: injury_in_jurisdiction
---
question: When did your injury take place?
decoration: calendar
fields:
  - Date of Injury: injury_date
    datatype: date
---
comment: |
  This code gathers information about the user's income and assets if necessary.
code: |
  user.asset.gathering = True
  user.income.gathering = True
  assets_to_ask_about = ['checking', 'savings', 'stocksbonds']
  income_to_ask_about = ['employment', 'selfemployment', 'ssi', 'tanf']
  for asset_item in assets_to_ask_about:
    user.asset.new(asset_item, period=12)
  for income_item in income_to_ask_about:
    user.income.new(income_item, period=12)
  user.asset.gathering = False
  user.income.gathering = False
  user.asset.gathered = True
  user.income.gathered = True
---
question: |
  Why do you think you deserve to win this case?
fields:
  - "Reason you should win": explanation
    datatype: area
    hint: |
      I should win because . . .
---
code: |
  if user.address.address and retry_address:
    retry_address = False
    force_ask('user.address.address')
comment: |
  This is an example of how the "force_ask" function can be used to
  ask a question that has already been asked.
---
question: Would you like to enter your address yet again?
yesno: retry_address
---
code: |
  jurisdiction.state = "Pennsylvania"
  jurisdiction.county = "Philadelphia"
---
code: |
  if jurisdiction.state == "Pennsylvania":
      statute_of_limitations_years = 5
  else:
      statute_of_limitations_years = 2
---
code: |
  if jurisdiction.state == "Pennsylvania":
      if law_category == "custody" or law_category == "support":
          court.name = "Court of Common Pleas of " + jurisdiction.county + " County"
---
comment: |
  This block uses some Python functions to determine whether the date of the
  injury is within the statute of limitations period.
code: |
  cutoff = datetime.datetime.now() - dateutil.relativedelta.relativedelta(years=statute_of_limitations_years)
  if dateutil.parser.parse(injury_date) > cutoff:
      statute_of_limitations_ok = True
  else:
      statute_of_limitations_ok = False
---
generic object: Individual
decoration: home
question: |
  Where ${ x.do_question('live') }?
fields:
  - Type of home: x.address.type
    choices:
      - Apartment
      - Leased house
      - Owned house
      - Mobile home
  - Address: x.address.address
  - Unit: x.address.unit
    required: false
    help: The apartment, suite, or unit number of the residence.
  - City: x.address.city
  - State: x.address.state
    code: |
      us.states.mapping('abbr', 'name')
  - Zip: x.address.zip
    required: false
comment: |
  This question demonstrates fields that have the style of dropdown
  lists.  The values of a dropdown list can be generated with code
  that runs at the time the question is asked, or they can be
  hard-coded into the question itself.  The code here gets a list of
  U.S. states from a helpful Python module called "us."  Note that we
  imported this module earlier.
---
question: Please upload one or more pictures.
decoration: picture
fields:
  - A test file: user.picture
    datatype: files
comment: |
  You can accept files from users by using the datatype of "file."
---
comment: |
  This is how you can display a picture that a user has uploaded.
question: |
  % if user.picture.number() > 1:
  Are these the pictures you uploaded?
  % else:
  Is this the picture you uploaded?
  % endif
subquestion: |  
  ${ user.picture.show() }
yesno: user.picture_verified
---
comment: |
  docassemble uses the Mako templating system to expand variables
  within Markdown text.  Mako allows functions to be defined within
  source text using "def" constructs.  If you write Mako "def"
  functions, you may want to use them in more than one document.  This
  section shows how you can attach a name (e.g., kid_defs) to some
  Mako text, and an example below shows how an attachment can include
  this Mako text by referring to it by its name (kid_defs).

  Another way to write functions in docassemble is to write methods
  that act on docassemble objects, which you define in your objects.py
  file within your package.
def: kid_defs
mako: |
  <%def name="describe_as_adorable(person)"> \
  ${ person } is adorable. \
  </%def>
---
comment: |
  The following question is the interview's main endpoint.  This
  question has two attachment documents.  Most of the questions in the
  interview are asked because they are needed by this question or one
  of its attachments.

  This section demonstrates use of the "need" clause to gather
  information about the case's plaintiffs and defendants up front.
  This is not strictly necessary, because the case caption will cause
  those questions to be answered.  However, the "need" clause forces
  docassemble to gather the information up front, before it starts
  processing the question and its attachments.  This helps to direct
  the order of the questions in a more sensible fashion.
sets: user_done
need:
  - case.plaintiff.gathered
  - case.defendant.gathered
question: |
  % if user_has_standing:
    Congratulations!  You have a valid claim.
  % else:
    Sorry, you do not have a valid claim.
  % endif
subquestion: |
  Here is an advice letter and a pleading you can file.
decoration: finishline
buttons:
  - Exit: exit
  - Restart: restart
attachments:
  - name: Advice Letter for ${ user }
    content: |
      ${ today() }

      ${ user.address_block() }

      Dear ${ user.salutation() } ${ user.name.last }:

      Your marital status is ${ user.marital_status.lower() }.
      % if user.marital_status == 'Single':
        Perhaps you should marry ${ village_idiot }.
      % endif
      Your annual income is ${ currency(user.income.total()) }
      and the value of all you own is ${ currency(user.asset.total()) }.

      % if user_has_standing:
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
    metadata:
      FirstHeaderRight: "Philadelphia Legal Assistance [NEWLINE] 718 Arch Street, Suite 300N [NEWLINE] Philadelphia, PA 19106"
      HeaderLeft: "${ user } [NEWLINE] ${ today() } [NEWLINE] Page [PAGENUM]"
      HeaderLines: "3"
      SingleSpacing: true
    filename: Advice_letter_${ space_to_underscore(user) }
  - name: ${ pleading.title }
    defs:
      - kid_defs
    content: |
      ${ pleading.caption() }

      I am the ${ case.role_of(user) } in this case.
      % if user.child.number() > 0:
      I have ${ user.child.number_as_word() } ${ user.child.as_noun() }:

      % for child in user.child:
      #. ${ child }
      % endfor

      % for child in user.child:
      ${ describe_as_adorable(child) }
      % endfor
      Aren't children such a blessing?
      % if user.has_support_order:
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
      
      This petition should be granted.  ${ explanation }
      % if user.picture_verified:
      Look how cute I am:

      ${ user.picture.show() }
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

      % if user.signature_verified:
      [FLUSHLEFT] ${ user.signature.show(width='2in') }
      % else:
      [FLUSHLEFT] ${ blank_signature }
      % endif

      [FLUSHLEFT] ${ user }, ${ titlecase(case.role_of(user)) }
    metadata:
      FirstFooterCenter: "[HYPHEN] [PAGENUM] [HYPHEN]"
      FooterCenter: "[HYPHEN] [PAGENUM] [HYPHEN]"
      FirstFooterLeft: "${ pleading.title }"
      FooterLeft: "${ pleading.title }"
    filename: ${ space_to_underscore(pleading.title) }
help: |
  This is the end of the interview, ${ user }.  You can exit or restart.

  I hope you enjoyed this interview.
progress: 100
...
{% endhighlight %}

## The basic-questions.yaml file

Many of the questions are defined in the `basic-questions.yaml` file.
Here is an annotated guide to how this file works.

{% highlight yaml %}
metadata:
  description: >-
    These are basic questions common to a lot of different scenarios
  authors:
    - name: Jonathan Pyle
      organization: Example, Inc.
  revision_date: 2015-09-28
comment: >-
  A "metadata" section contains information about who wrote the
  YAML file and how it is intended to be used.
---
modules:
  - docassemble.base.legal
comment: >-
  A "modules" section imports functions from Python modules.  The
  basic building blocks of docassemble variables are defined in the
  docassemble.legal module.
---
objects:
  - case: Case
  - user: Individual
  - spouse: Individual
  - pleading: LegalFiling
  - jurisdiction: Jurisdiction
  - court: Court
comment: >-
  An "objects" section defines variables that are Python objects.  The
  object types here are defined in the docassemble.legal module.
---
mandatory: True
code: |
  court.jurisdiction = jurisdiction
  case.court = court
  pleading.case = case
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
comment: |
  Here we pre-define some icon files so that we can easily refer to
  them later.  These files are located in the docassemble.base package
  in the subdirectory docassemble/base/data/static.
---
question: Are you the defendant?
yesno: user_is_defendant
comment: |
  After defining the basic variables, we define some standard questions.
---
field: user.marital_status
question: How would you describe yourself?
choices:
  - Married
  - Single
  - Divorced
  - Separated
---
field: user_understands_how_to_use_signature_feature
question: Instructions for signing your name
subquestion: |
  On the next screen, you will see a box in which you can sign your
  name using your mouse, track pad, or touch screen.  If you make a
  mistake, you can press "Clear" and try again.  For best results, try
  signing your name *slowly*.
buttons:
  - Continue: continue
---
comment: |
  docassemble can collect signatures from users, who can write their
  signature with their finger on a touchscreen device, or use a mouse
  or trackpad.  The signatures can be added to documents.
question: |
  Please sign your name below.
signature: user.signature
need: user_understands_how_to_use_signature_feature
under: |
  ${ user.name }
---
template: blank_signature
content: |
  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
---
template: empty_signature
content: |
  \_\_\_[Your signature here]\_\_\_
---
question: |
  Is this your signature?
subquestion: |  
  ${ user.signature.show() }
sets:
  - user.signature_verified
buttons:
  - "Yes":
      code: |
        user.signature_verified = True
  - "No":
      code: |
        user.signature_verified = False
  - "Let me try again":
      code: |
        answers = dict()
        remove('user.signature')
---
question: Are you a citizen of the United States?
yesno: user.is_citizen
---
field: user_understands_no_attorney_client_relationship
question: >-
  Your use of this system does not mean that you have a lawyer.  Do
  you understand this?
buttons:
  - "I understand": understands
  - code: |
      [{'does not understand':"I do not understand"}, {'unsure':"I'm not sure"}]
comment: |
  You can specify whether you want the multiple choices to appear as
  buttons by using the word "buttons" instead of the word "choices."
  Also, the example below shows how you can use Python code to
  generate the selections of multiple-choice question.  The code is
  evaluated at the time the question is asked.
---
generic object: Individual
question: >-
  What is ${ x.possessive('date of birth') }?
fields:
  - Date of birth: x.birthdate
    datatype: date
comment: |
  docassemble allows you to write "generic" questions.  For example,
  if your code uses a variable called user.birthdate, docassemble will
  first look for a question that sets user.birthdate specifically, but
  if it does not find it, it will look for a question for which the
  generic object property is set to the object type of the user
  object, which is Individual, and where the question sets the
  variable x.birthdate.
  
  It will find that question here.  The question uses the possessive
  function, which is a method of the Individual class.  The result is
  that the question will be "What is your date of birth?" if x is the
  user, but will otherwise ask "What is Jane Doe's date of birth?"
---
generic object: Individual
question: >-
  What is ${ x.possessive('e-mail address') }?
fields:
  - E-mail: x.email
    datatype: email
---
generic object: Individual
question: >-
  What is ${ x.possessive('gender') }?
field: x.gender
choices:
  - Male: male
  - Female: female
  - Other: other
comment: |
  By using "generic" questions, you can write a single question that
  works in a variety of circumstances, saving you a lot of time.  And
  if you ever want to use a more specific question for a specific
  variable, you can.  For example, if your code calls for
  spouse.birthdate, you may to ask the question in a different way.
  (E.g., "What is the birthdate of your lovely spouse?  If you don't
  know this, you are in deep trouble!")  You would do this by defining
  a non-generic question that sets spouse.birthdate, in which case
  docassemble would use that question instead of the generic question.
---
generic object: Individual
question: |
  What is ${ x.object_possessive('name') }?
fields:
  - First Name: x.name.first
  - Middle Name: x.name.middle
    required: False
  - Last Name: x.name.last
comment: |
  If the object does not have a name yet, generic questions can refer
  to it by the name of the variable itself.  For example, suppose you
  create an object, case.judge, with the class of Individual.  If the
  name of case.judge is ever needed, docassemble will use the question
  below to ask "What is the name of the judge in the case?"  If the
  object is called user, it will ask "What is your name?"  If the
  object is called village_idiot, it will ask "What is the village
  idiot's name?"
---
generic list object: Individual
question: |
  What is the name of the ${ ordinal(i) } ${ x.object_name() }?
fields:
  - First Name: x[i].name.first
  - Middle Name: x[i].name.middle
    required: False
  - Last Name: x[i].name.last
comment: |
  Generic questions can also use indices, for example to fill out the
  names of a list of people.  (E.g., case.plaintiff.)

  This example also illustates how the author can control whether the
  user can leave a field blank.  By default, all fields are required,
  but the author can add required: False to a field to indicate that
  the field can be left blank.
---
generic list object: Individual
question: |
  What is ${ x.possessive(ordinal(i) + " child") }'s name?
fields:
  - First Name: x.child[i].name.first
  - Middle Name: x.child[i].name.middle
    required: False
  - Last Name: x.child[i].name.last
    default: ${ x.name.last }
comment: |
  Example 1: What is your second child's name?
  Example 2: What is John Doe's first child's name?
---
comment: |
  As you can see in the following examples, it can get a little bit
  complicated to use lots of functions within questions.  However, it
  ultimately saves you a lot of trouble, because without the
  functions, you would have to define multiple different questions to
  ask the same thing in different contexts.
generic object: Individual
code: |
  x.child.gathering = True
  if x.has_children:
    if x.child.number_gathered() == 0:
      newchild = x.child.addObject(Individual)
    while x.has_other_children:
      newchild = x.child.addObject(Individual)
      del x.has_other_children
  x.child.gathering = False
  x.child.gathered = True
---
generic object: Individual
question: >-
  ${ x.do_question('have', capitalize=True) } any children?
yesno: x.has_children
decoration: children
comment: |
  Example 1: Do you have any children?
  Example 2: Does Jane Doe have any children?
---
generic object: Individual
question: |
  So far, you have told me about
  ${ x.possessive(x.child.number_gathered_as_word()) }
  ${ x.child.as_noun() }, ${ x.child }.
  ${ x.do_question('have', capitalize=True) } any other children?
yesno: x.has_other_children
decoration: children
comment: |
  Example 1: So far, you have told me about John Doe's two children, 
  Sally Doe and Harold Doe.  Does John Doe have any other children?

  Example 2: So far, you have told me about your one child, Kathleen 
  Smith.  Do you have any other children?
---
generic object: PartyList
question: |
  You have told me that there ${ x.does_verb("is", ) }
  ${ x.number_gathered_as_word() } ${ x.as_noun() }, ${ x }.  Is there another
  ${ x.as_singular_noun() }?
yesno: x.there_is_another
---
question: Are you a plaintiff in this case?
subquestion: |
  A "plaintiff" is a person who starts a case by filing a lawsuit
  against a person called a "defendant."  Plaintiffs and defendants
  are the "parties" in a case.
decoration: scalesofjustice
yesno: user_is_plaintiff
---
comment: |
  Here are some standard questions that ask about a person's income
  and assets.  These examples illustrate that if you do not want a
  field to be labeled, you can use "" as the label name.
generic object: Individual
question: How much ${ x.do_question("make") } from employment?
decoration: bills
fields:
  - Income: x.income.employment.value
    datatype: currency
  - "": x.income.employment.period
    code: |
      period_list()
---
generic object: Individual
question: How much ${ x.do_question("make") } from self-employment?
decoration: bills
fields:
  - Income: x.income.selfemployment.value
    datatype: currency
  - "": x.income.selfemployment.period
    code: |
      period_list()
---
generic object: Individual
question: How much ${ x.do_question("make") } from SSI?
decoration: bills
fields:
  - Income: x.income.ssi.value
    datatype: currency
  - "": x.income.ssi.period
    code: |
      period_list()
---
generic object: Individual
question: How much ${ x.do_question("make") } from cash assistance (Temporary Assistance to Needy Families or TANF)?
decoration: bills
fields:
  - Income: x.income.tanf.value
    datatype: currency
  - "": x.income.tanf.period
    code: |
      period_list()
---
generic object: Individual
question: How much ${ x.do_question("have") } in ${ x.pronoun_possessive("checking account") }?
decoration: piggybank
fields:
  - Amount: x.asset.checking.value
    datatype: currency
---
generic object: Individual
question: How much ${ x.do_question("have") } in ${ x.pronoun_possessive("savings account") }?
decoration: piggybank
fields:
  - Amount: x.asset.savings.value
    datatype: currency
---
generic object: Individual
question: How much ${ x.do_question("have") } in stocks and bonds?
decoration: stocks
fields:
  - Amount: x.asset.stocksbonds.value
    datatype: currency
---
generic object: Individual
question: What kinds of income ${ x.do_question("have") }?
decoration: bills
fields:
  - Employment: x.income.employment.exists
    datatype: yesno
  - Self-employment: x.income.selfemployment.exists
    datatype: yesno
  - SSI: x.income.ssi.exists
    datatype: yesno
  - Cash assistance: x.income.tanf.exists
    datatype: yesno
---
generic object: Individual
question: What kinds of assets ${ x.do_question("own") }?
decoration: piggybank
fields:
  - Checking Account: x.asset.checking.exists
    datatype: yesno
  - Savings Account: x.asset.savings.exists
    datatype: yesno
  - Stocks and Bonds: x.asset.stocksbonds.exists
    datatype: yesno
...
{% endhighlight %}

[Run a simple demonstration]: https://docassemble.org/demo?i%3Ddocassemble.demo:data/questions/questions.yml
[Bootstrap]: http://bootstrapdocs.com/v2.0.2/docs/index.html
