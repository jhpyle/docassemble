# Docassemble Interview Logic

## Mental model: a checklist, not a flowchart

Every time a screen loads, docassemble re-evaluates the interview from the top. It runs `mandatory` and `initial` blocks in YAML order, and whenever it hits an undefined variable it pauses, finds and runs the block that defines that variable (asking the user a question or running a `code` block), then restarts from the beginning. This is **dependency satisfaction**.

Think of it as a checklist that is re-run on every screen load, not a linear sequence of steps. The "current question" is whatever the checklist discovers is still missing.

---

## `mandatory` — the entry point

All blocks are optional unless marked `mandatory: True`. Docassemble runs mandatory blocks in the order they appear in the YAML file. An already-completed mandatory block is skipped on subsequent runs.

`mandatory` can also be a Python expression; the block is treated as mandatory only when that expression is truthy:

```yaml
mandatory: favorite_fruit == 'apple'
question: What type of apple is your favorite?
fields:
  - Type: favorite_apple_type
```

**Best practice:** Use a single mandatory `code` block as an explicit outline of the interview, then let dependency satisfaction handle gathering variables:

```yaml
mandatory: True
code: |
  user.name.first
  if user.age_in_years() < 18:
    parental_consent
  final_screen
```

Each bare variable reference means "if this variable is undefined, stop and define it; otherwise continue." Tag every mandatory block with an `id` to avoid re-asking questions if you rearrange the YAML later.

---

## `initial` — runs on every screen load

An `initial: True` code block runs every time the screen loads, even after it has completed successfully. Use it to initialize session context (e.g., setting `user` based on the logged-in user). Do not use `initial` for anything that should only happen once.

---

## `objects` block — declaring objects

Use `objects` to initialize docassemble objects. This is the standard way to declare `DAList`, `Individual`, `Address`, and other objects. The block is processed when docassemble needs to define the listed variable:

```yaml
objects:
  - user: Individual
  - children: DAList.using(object_type=Individual, complete_attribute='complete')
  - address: Address
```

All objects used as interview variables must inherit from `DAObject`. Use the `.using()` method to set initial attributes inline:

```yaml
objects:
  - fruit: DAList.using(object_type=str, minimum_number=1, ask_number=True)
```

Prefer `objects` blocks over `code` blocks for initialization — docassemble needs the full variable name to be passed correctly, and `objects` handles that automatically.

---

## File organization: `include` and `modules`

### `include`

```yaml
include:
  - basic-questions.yml
  - docassemble.helloworld:questions.yml
```

`include` incorporates another YAML file's blocks at compile time, as if they appeared in place of the `include` block. Modifiers like `if` and `mandatory` have no effect on `include` — it cannot be made conditional. To reference a file from another package: `packagename:filename.yml`.

Because included blocks appear before the blocks in the including file, they have lower override priority (later = higher priority).

### `imports` and `modules`

```yaml
imports:
  - datetime          # equivalent to: import datetime
```

```yaml
modules:
  - .utils            # equivalent to: from .utils import *
```

Use `imports` for standard library or third-party modules you access by module name. Use `modules` for your own utility modules that export functions and classes. Define `__all__` in your module files to limit what `modules` imports.

---

## Dependency satisfaction in practice

When docassemble needs a variable it searches for the best block to define it, then runs that block. If the block itself needs another undefined variable, the search recurses. Non-mandatory blocks can appear in any order; their position relative to each other only matters when multiple blocks can define the same variable (see **Overriding** below).

Example — the mandatory block asks for `final_screen`; docassemble automatically discovers and asks everything `final_screen` refers to:

```yaml
mandatory: True
event: final_screen
question: |
  Your favorite fruit is ${ favorite_fruit }.
  % if favorite_fruit == 'grapes':
  You prefer ${ favorite_vineyard } grapes.
  % endif
---
question: What is your favorite fruit?
fields:
  - Fruit: favorite_fruit
---
question: Which vineyard is your favorite?
fields:
  - Vineyard: favorite_vineyard
```

If the user answers "apples," `favorite_vineyard` is never asked because it is never referenced in a code path that runs.

---

## Idempotency — the most common pitfall

Because code blocks can be **interrupted and restarted** whenever an undefined variable is encountered, a block may execute multiple times before it completes. Code that accumulates a value will double-count:

```yaml
# BAD — total_income is incremented each time this block restarts
mandatory: True
code: |
  total_income = total_income + benefits_income   # restarts here if benefits_income undefined
  total_income = total_income + net_business_income
```

Fix: initialise and compute atomically so re-running produces the same result:

```yaml
# GOOD
mandatory: True
code: |
  total_income = 0
  total_income += benefits_income
  total_income += net_business_income
```

Or better, keep calculation code in a separate non-mandatory block that assigns the variable in a single expression:

```yaml
code: |
  total_income = benefits_income + net_business_income
```

Similarly, side-effects (sending emails, storing data) must be guarded so they fire only once:

```yaml
mandatory: True
code: |
  user.email
  if not task_performed('welcome_email'):
    send_email(to=user, subject="Welcome", body=body_text, task='welcome_email')
  final_screen
```

---

## Conditional branching

### In a mandatory code block

Use normal Python `if` / `elif` / `else`. Referencing a variable that is undefined causes docassemble to seek its definition:

```yaml
mandatory: True
code: |
  if user.age_in_years() >= 60 or user.is_disabled:
    eligible_screen
  else:
    ineligible_screen
```

Docassemble short-circuits: if `user.age_in_years() >= 60` is true, `user.is_disabled` is never asked.

### Branching with `event` screens

Terminal screens (no Continue button) use `event`:

```yaml
event: ineligible_screen
question: Sorry, you do not qualify.
```

Referencing `ineligible_screen` in a code block causes docassemble to display that screen and stop.

---

## Overriding blocks

When multiple blocks can define the same variable, docassemble tries **later-defined blocks first**. This lets you override a question from an included library without editing that library:

```yaml
include:
  - question-library.yml   # defines user_wants_to_go_to_dance
---
# This later block supersedes the library question
question: Hey, want to dance?
yesno: user_wants_to_go_to_dance
```

---

## Key block-level specifiers

### `need`

Force docassemble to gather specific variables before processing a block, even if those variables are not mentioned in the block's content:

```yaml
need:
  - favorite_fruit
question: Your favorite apple is ${ favorite_apple }.
continue button field: fruit_verified
```

Use `post` to gather a variable *after* the block's own prerequisites:

```yaml
need:
  - favorite_vegetable
  - post:
      - favorite_fruit
```

### `depends on`

When listed variables change (e.g., via a review screen), invalidate this block's output so it is recomputed:

```yaml
depends on:
  - a
code: |
  b = a * 2
```

If the user later edits `a`, `b` is automatically undefined and recomputed.

### `reconsider`

- `reconsider: True` on a `code` block: forget the variables it sets on every screen load, forcing recomputation. Use when a computed variable must reflect information gathered after it was first computed.
- `reconsider: [var1, var2]` on a `question`: undefine those variables before showing the question, so they are looked up fresh.

```yaml
reconsider: True
code: |
  cat_food_cans_needed = number_of_cats * 4
```

### `undefine`

Undefine listed variables before showing a question (useful in review screens):

```yaml
undefine:
  - favorite_foods
question: What is your favorite fruit?
fields:
  - Favorite fruit: favorite_fruit
```

### `only sets`

Tell docassemble that this `code` block should only be consulted to define a specific variable, even though it may set others as side effects:

```yaml
only sets: total_income
code: |
  temp = []
  for item in income:
    if item.included:
      temp.append(item.value)
      if item.type == 'disability':
        has_benefits = True   # side effect, but not the purpose of this block
  total_income = sum(temp)
```

---

## Block search order summary

| Direction | Purpose |
|---|---|
| Top → bottom | Which `mandatory`/`initial` blocks to run, and in what order |
| Bottom → top | Which non-mandatory block to use to define a needed variable (later = higher priority) |

---

## Common patterns

### Explicit interview outline

```yaml
mandatory: True
code: |
  intro_screen
  user.name.first
  if applicant_is_eligible:
    document_screen
  else:
    rejection_screen
```

### One-time side effect

```yaml
mandatory: True
code: |
  user.email
  email_sent       # triggers the code block below exactly once
  final_screen
---
code: |
  send_email(to=user, subject="Welcome", body="...")
  email_sent = True
```

### Encoding legal rules as code

Write eligibility rules as Python, then let dependency satisfaction ask only the questions needed:

```yaml
code: |
  if relationship == 'Grandparent' \
     and willing_to_assume_responsibility \
     and (child_is_dependent or child_is_at_risk):
    has_standing = True
  else:
    has_standing = False
---
mandatory: True
code: |
  if has_standing:
    final_screen
  else:
    no_standing_screen
```

Docassemble will not ask `child_is_at_risk` if `willing_to_assume_responsibility` is `False`.

---

## `reset` and `on change`

### `reset` — unconditional recomputation on every screen load

```yaml
reset:
  - client_is_guilty
```

Variables listed in a `reset` block are undefined on every screen load, forcing recomputation. This is equivalent to applying `reconsider: True` to every code block that defines those variables. Use sparingly — it adds overhead on every page load.

### `on change` — react when a variable's value changes

```yaml
on change:
  married: |
    income.reset_gathered(mark_incomplete=True)
    undefine('income[i].amount')
```

The code runs when `married` changes value, and also when it is first initialized. Use `on change` when `depends on` is insufficient — for example, when you need to invalidate indexed attributes like `income[i].amount` where the index variable `i` is not in scope at change time.

`on change` code must run to completion without encountering any undefined variables. It runs before `modules` and `imports` blocks have loaded; standard docassemble utility functions (`undefine()`, `invalidate()`, etc.) are available.

---

## Groups: `DAList`, `DADict`, `DASet`

Docassemble provides three collection types that integrate with the dependency-satisfaction engine:

- **`DAList`** — ordered list, elements accessed by integer index
- **`DADict`** — key/value mapping, elements accessed by key
- **`DASet`** — unordered set of unique items

Use `objects` blocks (not plain Python `list`, `dict`, or `set`) to declare these so docassemble can gather them automatically.

### Gathering a `DAList`

```yaml
objects:
  - fruit: DAList
```

The gathering algorithm asks three types of questions in a loop:

1. `fruit.there_are_any` — "Is there at least one item?"
2. `fruit[i]` — "What is the item at index `i`?"
3. `fruit.there_is_another` — "Are there more items?"

After each item is added, docassemble undefines `fruit.there_is_another` and re-seeks it. When the user answers no, gathering is complete.

Write one question for `fruit[i]` using the special index variable `i`:

```yaml
question: Are there any fruits to add?
yesno: fruit.there_are_any
---
question: What fruit should be added?
fields:
  - Fruit: fruit[i]
---
question: So far the fruits include ${ fruit }. Are there others?
yesno: fruit.there_is_another
```

The index variable `i` is a **special variable** set automatically by docassemble. Never set `i` yourself. Never use `i` in `mandatory` or `initial` blocks.

Gathering is triggered implicitly when you iterate the list, call `.number()` or `.number_as_word()`, or include `${ fruit }` in a template. Trigger it explicitly with `fruit.gather()`.

### `complete_attribute` — gathering all attributes per item

When list items are objects with multiple attributes, set `complete_attribute='complete'` so docassemble finishes gathering every attribute for one item before moving on to the next:

```yaml
objects:
  - friend: DAList.using(object_type=Individual, complete_attribute='complete')
---
code: |
  friend[i].name.first
  friend[i].birthdate
  friend[i].favorite_animal
  friend[i].complete = True
```

This code block runs for each `friend[i]`, gathering all its attributes before the list moves to the next item. When the user later edits a list item via a `table`, docassemble undefines `.complete` and re-runs this block.

### Nested lists: index variables `i` and `j`

For a list within a list, use `i` for the outer index and `j` for the inner index:

```yaml
objects:
  - person: DAList.using(object_type=Individual, complete_attribute='complete')
  - person[i].child: DAList.using(object_type=Individual, complete_attribute='complete')
---
# defines person[i].complete — uses i only
code: |
  person[i].name.first
  person[i].child.gather()
  person[i].complete = True
---
# defines person[i].child[j].complete — uses both i and j
code: |
  person[i].child[j].name.first
  person[i].child[j].complete = True
```

Keep the two `code` blocks **separate**. If you mix `i` and `j` in the same block, docassemble will not set `j` when it is seeking `person[i].complete`, causing an error.

The index hierarchy is always `i` → `j` → `k`. A block that uses `j` must also reference `i`; a block that uses `k` must reference both `j` and `i`.

### `generic object` — reusable blocks across instances

Use `generic object: ClassName` with the special variable `x` to write one block that applies to any instance of that class, regardless of its nesting depth:

```yaml
generic object: Individual
objects:
  - x.allergy: DAList
---
generic object: Individual
question: Does ${ x } have any allergies?
yesno: x.allergy.there_are_any
---
generic object: Individual
question: What allergy does ${ x } have?
fields:
  - Allergy: x.allergy[i]
---
generic object: Individual
question: Does ${ x } have any other allergies?
yesno: x.allergy.there_is_another
```

Docassemble sets `x` to the appropriate instance (e.g., `person[0]` or `person[1].child[2]`) before running the block. This avoids writing separate questions for `person[i].allergy` and `person[i].child[j].allergy`.

### Gathering a `DADict`

Similar to `DAList`, but the gathering process also asks for a key via `.new_item_name`. In the value question, `i` is the key (not an integer):

```yaml
objects:
  - fruit: DADict
---
question: What fruit?
fields:
  - Name: fruit.new_item_name
---
question: How many seeds does ${ i } have?
fields:
  - Seeds: fruit[i]
---
question: Are there more fruits?
yesno: fruit.there_is_another
```

To set key and value in one question, set both `.new_item_name` and `.new_item_value` together in a single question block.

### Gathering a `DASet`

Like `DADict` but uses a single `.new_item` attribute:

```yaml
question: What item to add?
fields:
  - Item: colors.new_item
```

### For loops in Mako templates

Iterate over a gathered list inside question text with `% for` / `% endfor`:

```yaml
question: Summary
subquestion: |
  % for item in fruit:
  - ${ item }
  % endfor
```

Do not indent the text lines with spaces — Markdown treats indented text as a code block. The `% for` / `% endfor` directive lines themselves may be indented for readability but it is not required.
