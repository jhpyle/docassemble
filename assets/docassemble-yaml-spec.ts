/**
 * Docassemble Interview YAML Specification
 * =========================================
 *
 * A docassemble interview file is a YAML file containing one or more
 * "documents" (blocks) separated by `---`. Each block is a YAML mapping
 * (dict). Docassemble lowercases all top-level keys before processing, so
 * `Question`, `question`, and `QUESTION` are all treated identically.
 *
 * The Interview class in parse.py parses blocks in order. Each block is
 * passed to Question.__init__(). Some blocks configure the interview
 * globally (e.g. `features`, `metadata`, `include`) and are not added to
 * the question queue. Others define "questions" that docassemble can ask
 * when it needs to define a variable.
 *
 * Mako syntax (${...}, % if ..., etc.) is available in most string
 * fields. Jinja2 syntax ({{ ... }}, {% ... %}) is available in DOCX
 * templates.
 */

// ---------------------------------------------------------------------------
// Primitive building blocks
// ---------------------------------------------------------------------------

/**
 * A string that may contain Mako template expressions such as:
 *   
 *   % if condition:
 *   Hello, ${ planet }!
 *   % endif
 *   <%doc>do not translate</%doc>
 *
 * Used wherever docassemble says the value is "plain text" that is
 * rendered at runtime. It is used for most labels that appear in the
 * front end, among other uses.
 */
type MakoString = string;

/**
 * A Python expression string. Used where docassemble calls compile(value,
 * ..., 'eval'). The expression is evaluated in the context of the
 * interview's variable store.
 *
 * Examples: "True", "user.age >= 18", "len(witnesses) > 0"
 */
type PythonExpression = string;

/**
 * A Python statement block. Used where docassemble calls compile(value,
 * ..., 'exec'). Multi-line code using block literal `|` in YAML.
 */
type PythonCode = string;

/**
 * A Python identifier (variable name). Must match [^\d][A-Za-z0-9_]*.
 * Can include attribute access (user.name.first) and list indexing (items[i]).
 */
type VariableName = string;

/**
 * A Bootstrap color name accepted in button/color fields.
 */
type BootstrapColor =
  | "primary"
  | "secondary"
  | "success"
  | "danger"
  | "warning"
  | "info"
  | "light"
  | "dark"
  | "link";

// ---------------------------------------------------------------------------
// Flexible "value or code" types used throughout
// ---------------------------------------------------------------------------

/**
 * A value that can be either a static Mako string or a `{code: expr}`
 * dict that is evaluated as a Python expression at runtime.
 *
 * This pattern appears in: `show if`, `default`, `valid formats`, etc.
 * When code is used, the dict must have exactly one key: "code".
 */
type MakoOrCode = MakoString | { code: PythonExpression };

/**
 * A boolean that can optionally be expressed as a Python expression string.
 * If a string, it is compiled with 'eval' and the result treated as bool.
 * Examples: true, false, "user.age >= 18"
 */
type BoolOrExpr = boolean | PythonExpression;

// ---------------------------------------------------------------------------
// Common block-level modifiers (applicable to many block types)
// ---------------------------------------------------------------------------

/**
 * Modifiers that can appear on most question blocks. They do not define
 * the question type but modify its behavior or metadata.
 */
interface CommonModifiers {
  /**
   * Unique identifier for this block. Used for supersedes/order directives,
   * forget_result_of(), and debugging. Must be unique within the interview.
   * Value is converted to string via str(data['id']).strip().
   */
  id?: string;

  /**
   * Google Analytics page-view identifier for this question.
   * Treated as a MakoString evaluated at display time.
   */
  "ga id"?: MakoString;

  /**
   * Segment analytics identifier for this question.
   */
  "segment id"?: MakoString;

  /**
   * Segment analytics configuration for this question.
   * Must be a dict with optional keys `id` (string) and
   * `arguments` (dict of string->scalar values).
   */
  segment?: {
    id?: MakoString;
    arguments?: Record<string, string | number | boolean>;
  };

  /**
   * If true (or a Python expression evaluating to true), this block is
   * always evaluated by the interview logic before any other blocks.
   * Can only be used on question, code, objects, attachment, data, and
   * data from code blocks. Cannot be combined with `initial`.
   *
   * true | false | PythonExpression
   */
  mandatory?: BoolOrExpr;

  /**
   * A language code (e.g. "en", "es"). Overrides the source file's default
   * language for this block. Used for localized questions.
   */
  language?: string;

  /**
   * One or more IDs that this block supersedes in priority ordering.
   * If a string, treated as a list of one. Each item is converted to string.
   */
  supersedes?: string | string[];

  /**
   * Marks the block as applicable only if all the Python expressions in
   * the list evaluate to true. Each item is a PythonExpression string.
   * Also accepts a single string (treated as a list of one).
   */
  if?: PythonExpression | PythonExpression[];

  /**
   * Declares which variables this block defines, for blocks where
   * scan_for_variables would not detect them automatically.
   * Disables automatic variable scanning.
   * String or list of strings.
   */
  sets?: VariableName | VariableName[];

  /**
   * When present, docassemble will not auto-scan the block for variable
   * names it defines. Useful for performance or when auto-scan gives wrong
   * results. Default: true (auto-scan enabled).
   */
  "scan for variables"?: boolean;

  /**
   * Overrides the variables that docassemble believes this block defines.
   * When used, scan_for_variables is also set to false. String or list.
   */
  "only sets"?: VariableName | VariableName[];

  /**
   * The role(s) required to see this question. String or list of strings.
   * Used in multi-user interviews. If the current user does not have any
   * of these roles, the question is skipped.
   */
  role?: string | string[];

  /**
   * A Python expression to evaluate before asking this question.
   * Forces the listed variables to be defined (evaluated for side effects).
   * String: a single Python expression.
   * List: multiple Python expressions.
   * Dict item with {pre: ...} or {post: ...}: evaluated before or after
   * the question is shown. Both can appear together.
   *
   * Example:
   *   need: user.name.first
   *   need:
   *     - user.age
   *     - post: user.email
   */
  need?:
    | PythonExpression
    | (
        | PythonExpression
        | { pre?: PythonExpression | PythonExpression[] }
        | { post?: PythonExpression | PythonExpression[] }
        | {
            pre?: PythonExpression | PythonExpression[];
            post?: PythonExpression | PythonExpression[];
          }
      )[];

  /**
   * List of variable names that, when changed, cause this block's output
   * variables to be invalidated. String or list of strings.
   */
  "depends on"?: VariableName | VariableName[];

  /**
   * After this block runs, mark the listed variables for re-evaluation.
   * true: reconsider all variables defined by this block.
   * false: do not reconsider any.
   * string: reconsider the named variable.
   * list of strings: reconsider each named variable.
   */
  reconsider?: boolean | VariableName | VariableName[];

  /**
   * After this block runs, undefine the listed variables.
   * String or list of strings.
   */
  undefine?: VariableName | VariableName[];

  /**
   * A Python expression used to choose among multiple blocks with the
   * same `id`. The block whose `order` expression evaluates to the
   * numerically lowest result is used first.
   * (Note: `order` as a standalone block type is different; see OrderBlock.)
   */
  // order is handled as OrderBlock below

  /**
   * Definitions from a `def` block to include in the Mako namespace.
   * String (single def name) or list of strings.
   */
  usedefs?: string | string[];

  /**
   * If set to false or to Python code that evaluates to false,
   * prevents the user from pressing the back button on this
   * screen. Default: true (back button allowed).
   */
  "prevent going back"?: boolean | null | PythonExpression;

  /**
   * Controls whether the back button appears on this question.
   * true: always show back button.
   * false: never show back button.
   * null: use interview default.
   * PythonExpression string: evaluated at display time.
   */
  "back button"?: boolean | null | PythonExpression;

  /**
   * An integer (0-100) representing how far along in the interview the
   * user is when this question is shown. Null resets the progress bar.
   * Used with the progress bar feature.
   */
  progress?: number | null;

  /**
   * The name of the navigation section this question belongs to.
   * Evaluated as a MakoString. Only valid on question blocks.
   */
  section?: MakoString;

  /**
   * Inline CSS text to inject into the page for this question.
   * Must be a plain text string. Mako is not supported.
   */
  css?: string;

  /**
   * Inline JavaScript text to inject into the page for this question.
   * Must be a plain text string. Mako is not supported.
   */
  script?: string;

  /**
   * The action name to call when the browser periodically "checks in"
   * (polls the server). Used for live-updating questions.
   * Must be a plain text string (the name of an action/event).
   */
  "check in"?: string;

  /**
   * When true, the question screen reloads automatically after the
   * specified number of seconds. Evaluated as a MakoString (number).
   * E.g.: reload: 10 (reload after 10 seconds).
   * false or 0 disables reload.
   */
  reload?: MakoString | number | boolean;

  /**
   * Breadcrumb text for this question. Shown in the browser tab title
   * or as a short navigation indicator. Evaluated as a MakoString.
   */
  breadcrumb?: MakoString;

  /**
   * Buttons to show below the question's main action buttons.
   * When clicked, these buttons trigger an action (like url_action).
   * Can be a static list or a {code: expr} dict.
   *
   * Static list form: list of ActionButtonSpec dicts.
   * Code form: { code: "python_expr" } - expression must return a list
   *   of dicts with at minimum `action` and `label` keys.
   */
  "action buttons"?:
    | ActionButtonSpec[]
    | { code: PythonExpression };

  /**
   * Custom metadata for this question. Any YAML structure is allowed.
   * Mako is supported in text values. Accessible via the question's
   * JSON representation.
   */
  "question metadata"?: unknown;

  /**
   * A CSS class name to add to the <body> of the question screen.
   * Evaluated as a MakoString. Only valid with a `question` key present.
   */
  "css class"?: MakoString;

  /**
   * CSS class for Markdown-generated <table> elements in this question.
   * Comma-separated for table and thead classes:
   *   "table table-bordered, thead-dark"
   * Only valid with a `question` key present.
   */
  "table css class"?: MakoString;

  /**
   * Sets the target variable (for template blocks). Plain text.
   * Can only be used with a `template` block.
   */
  target?: string;

  /**
   * A comment. If the block contains ONLY a `comment` key, the block is
   * ignored entirely (no question is added to the queue).
   */
  comment?: string;

  /**
   * Mako code validated via the `code` block to run after the form
   * is submitted. If the code raises a DAValidationError, the form
   * is re-shown with the error message. Must be a string (Python code).
   */
  "validation code"?: PythonCode;

  /**
   * Restricts which variables can be set by this block. When present,
   * only the listed variables (or those passing the Python expression)
   * may be saved.
   * String list: explicit variable names.
   * PythonExpression: evaluated; result must be a list of variable names.
   */
  "allowed to set"?: VariableName[] | PythonExpression;

  /**
   * A Python expression controlling visibility of the "Continue" button.
   * If the expression evaluates to true, the button is hidden.
   * Only valid with a `question` key.
   */
  "hide continue button"?: PythonExpression;

  /**
   * A Python expression controlling whether the "Continue" button is
   * disabled (greyed out but still visible).
   * Only valid with a `question` key.
   */
  "disable continue button"?: PythonExpression;
}

/**
 * An individual action button specification for the `action buttons` key.
 */
interface ActionButtonSpec {
  /** Required. The action name or URL to invoke. Mako is supported. */
  action: MakoString;

  /** Required. The visible label on the button. Mako is supported. */
  label: MakoString;

  /**
   * Bootstrap color of the button. Default: "primary". Mako is supported.
   */
  color?: BootstrapColor | MakoString;

  /**
   * Font Awesome icon name (without the `fa-` prefix). Mako is supported.
   */
  icon?: MakoString;

  /**
   * Where to place the button: "before" (before the main buttons) or
   * omit/null for after. Mako is supported.
   */
  placement?: "before" | MakoString;

  /**
   * Additional CSS class for the button element. Mako is supported.
   */
  "css class"?: MakoString;

  /**
   * If true, open the link/action in a new window/tab.
   * Can also be a string (_blank, _self, etc.).
   */
  "new window"?: boolean | string;

  /**
   * A Python expression; if it evaluates to a false value the button
   * is omitted from the display.
   */
  "show if"?: PythonExpression;

  /**
   * If true, discard any prior incomplete actions before starting this one.
   * Default: false.
   */
  "forget prior"?: boolean;

  /**
   * Key/value pairs passed as arguments to the action. Values can be
   * strings (Mako-rendered) or other scalars.
   */
  arguments?: Record<string, MakoString | number | boolean>;
}

// ---------------------------------------------------------------------------
// Screen text fields (appear on question blocks)
// ---------------------------------------------------------------------------

interface ScreenTextFields {
  /**
   * The main question text. Required for all question-type blocks.
   * Rendered as Markdown + Mako.
   * At most one of: yesno, noyes, yesnomaybe, noyesmaybe, fields, buttons,
   * choices, dropdown, combobox, signature, review may accompany it.
   */
  question: MakoString;

  /**
   * Secondary question text shown below the main question, above the inputs.
   * Rendered as Markdown + Mako.
   */
  subquestion?: MakoString;

  /**
   * Text shown below the buttons (after the form area). Markdown + Mako.
   */
  under?: MakoString;

  /**
   * Text shown above the question (before the question heading).
   * Markdown + Mako.
   */
  pre?: MakoString;

  /**
   * Text shown below everything on the screen. Markdown + Mako.
   */
  post?: MakoString;

  /**
   * Text shown on the right side of the screen (or below on small screens).
   * Markdown + Mako. Consider using features.centered: false with this.
   */
  right?: MakoString;

  /**
   * Help text for this question. Shown when the user clicks the help tab
   * or help button.
   * Can be a plain string or a dict with keys:
   *   content (required), label, heading, audio, video.
   */
  help?: MakoString | QuestionHelpSpec;

  /**
   * Audio file(s) to associate with the question area.
   * String or list of strings (filenames or package:path references).
   */
  audio?: MakoString | MakoString[];

  /**
   * Video file(s) or embed URL(s) to associate with the question area.
   * String or list of strings.
   */
  video?: MakoString | MakoString[];

  /**
   * Decoration image(s) to show alongside the question.
   * Can be:
   *   - A plain string: the name of an image defined in an images block.
   *   - A dict: {image: "name"} (or with extra keys).
   *   - A list of strings or dicts.
   */
  decoration?: string | { image: string } | (string | { image: string })[];

  /**
   * Terms to define for this question only (hover-popup definitions).
   * Dict form: { "term": "definition", ... }
   * List form: list of single-key dicts { "term": "definition" }
   * Multi-phrase form: { phrases: ["t1","t2"], definition: "..." }
   */
  terms?: Record<string, MakoString> | TermItem[];

  /**
   * Same as `terms` but automatically wraps matching text in the question
   * with hover-popup links, without requiring explicit {term} syntax.
   */
  "auto terms"?: Record<string, MakoString> | TermItem[];

  /**
   * The label for the "Continue" button on this question.
   * Cannot be used with yesno, noyes, yesnomaybe, noyesmaybe, or buttons.
   * Evaluated as a MakoString.
   */
  "continue button label"?: MakoString;

  /**
   * The Bootstrap color of the "Continue" button.
   * Evaluated as a MakoString.
   */
  "continue button color"?: MakoString | BootstrapColor;

  /**
   * The label for the back button appearing within the question body
   * (when question back button feature is enabled).
   * Evaluated as a MakoString.
   */
  "back button label"?: MakoString;

  /**
   * The label for the back button in the upper-left corner of the screen.
   * Evaluated as a MakoString.
   */
  "corner back button label"?: MakoString;
}

interface QuestionHelpSpec {
  /** Required if using dict form for help. Markdown + Mako. */
  content: MakoString;
  /** Optional label for the help tab or button. Mako string. */
  label?: MakoString;
  /** Optional heading inside the help panel. Mako string. */
  heading?: MakoString;
  /** Audio file(s) for the help panel. String or list of strings. */
  audio?: MakoString | MakoString[];
  /** Video file(s) for the help panel. String or list of strings. */
  video?: MakoString | MakoString[];
}

interface TermItem {
  /** Multiple phrases that all map to the same definition. */
  phrases: string[];
  /** The definition text. Mako string. */
  definition: MakoString;
}

// ---------------------------------------------------------------------------
// Question block variants
// ---------------------------------------------------------------------------

/**
 * A yes/no question. Sets the named variable to True (yesno) or
 * to False (noyes) when "Yes" is clicked, and the opposite when "No" is clicked.
 * Exactly one of yesno/noyes/yesnomaybe/noyesmaybe may be present.
 * The value must be a plain variable name string.
 */
type YesNoBlock = CommonModifiers &
  ScreenTextFields & {
    yesno: VariableName;
  };

type NoYesBlock = CommonModifiers &
  ScreenTextFields & {
    noyes: VariableName;
  };

/**
 * Like yesno but adds a third "I don't know" option that sets the
 * variable to None.
 */
type YesNoMaybeBlock = CommonModifiers &
  ScreenTextFields & {
    yesnomaybe: VariableName;
  };

type NoYesMaybeBlock = CommonModifiers &
  ScreenTextFields & {
    noyesmaybe: VariableName;
  };

/**
 * A multiple-choice question using clickable buttons.
 * Requires `field` (the variable to set) or `continue button field`.
 * The choices list is the buttons.
 */
type ButtonsBlock = CommonModifiers &
  ScreenTextFields & {
    buttons: ChoiceList;
    /**
     * The variable to be set when a button is clicked.
     * Required unless `event` is used.
     */
    field?: VariableName;
    /**
     * If true, the order of the choices is randomized. Default: false.
     */
    shuffle?: boolean;
    /** The datatype of the variable to be set. */
    datatype?: FieldDatatype;
    /**
     * Custom validation messages for this field.
     * Dict of validation rule name -> message string.
     */
    "validation messages"?: Record<string, MakoString>;
  };

/**
 * A multiple-choice question using radio buttons + Continue.
 * Requires `field`.
 */
type ChoicesBlock = CommonModifiers &
  ScreenTextFields & {
    choices: ChoiceList;
    field?: VariableName;
    "continue button field"?: VariableName;
    shuffle?: boolean;
    /**
     * Default value pre-selected in the radio list. Mako string.
     */
    default?: MakoString;
    datatype?: FieldDatatype;
    "validation messages"?: Record<string, MakoString>;
  };

/**
 * A multiple-choice dropdown question. Same structure as choices but
 * renders as an HTML <select> element.
 */
type DropdownBlock = CommonModifiers &
  ScreenTextFields & {
    dropdown: ChoiceList;
    field?: VariableName;
    "continue button field"?: VariableName;
    shuffle?: boolean;
    default?: MakoString;
    datatype?: FieldDatatype;
    "validation messages"?: Record<string, MakoString>;
  };

/**
 * A multiple-choice combobox question. Allows the user to either pick
 * from the list or type a custom value.
 */
type ComboboxBlock = CommonModifiers &
  ScreenTextFields & {
    combobox: ChoiceList;
    field?: VariableName;
    "continue button field"?: VariableName;
    shuffle?: boolean;
    default?: MakoString;
    datatype?: FieldDatatype;
    "validation messages"?: Record<string, MakoString>;
  };

/**
 * A signature capture question. The named variable is set to a DAFile
 * image of the user's drawn signature.
 */
type SignatureBlock = CommonModifiers &
  ScreenTextFields & {
    signature: VariableName;
    /**
     * Whether the signature is required. Default: true.
     * Can be a Python expression string.
     */
    required?: BoolOrExpr;
    /** Color of the pen (e.g. "black", "#000000"). Mako string. */
    "pen color"?: MakoString;
  };

/**
 * A "continue button field" question with no other input.
 * The named variable is set to True when the user clicks Continue.
 * Can also be combined with `fields` to add a continue button to a
 * multi-field form that sets a separate variable to True.
 */
type ContinueButtonFieldBlock = CommonModifiers &
  ScreenTextFields & {
    "continue button field": VariableName;
  };

/**
 * A multi-field question. `fields` contains a list of FieldSpec items.
 */
type FieldsBlock = CommonModifiers &
  ScreenTextFields & {
    fields: FieldSpec[] | { code: PythonExpression };
    /**
     * If present, set this variable to True when the user clicks Continue.
     * Used in combination with fields to track question completion.
     */
    "continue button field"?: VariableName;
    /**
     * If true, show "Add another" button after this fields screen,
     * allowing the user to re-enter the screen to add more items to a list.
     * Can also be a dict with enable, label, is final, allow append,
     * allow delete, and add another label subkeys.
     * Only valid when `fields` is present.
     */
    "list collect"?: boolean | PythonExpression | ListCollectSpec;
    /**
     * Custom validation messages for this question's fields.
     * Dict of validation rule name -> message string.
     */
    "validation messages"?: Record<string, MakoString>;
  };

interface ListCollectSpec {
  /**
   * Whether to show the list collect behavior at all.
   * PythonExpression or boolean.
   */
  enable?: BoolOrExpr;
  /** Label for the "collect" button. Mako string. */
  label?: MakoString;
  /** Whether this is the "final" collection item. Python expression. */
  "is final"?: PythonExpression;
  /** Whether to allow appending (adding more items). Python expression. */
  "allow append"?: PythonExpression;
  /** Whether to allow deleting items. Python expression. */
  "allow delete"?: PythonExpression;
  /** Label for the "add another" button. Mako string. */
  "add another label"?: MakoString;
}

/**
 * A "review" question displays variables already collected and lets the
 * user go back and change them. Requires `question`.
 * The review list is like the fields list but with different semantics.
 */
type ReviewBlock = CommonModifiers &
  ScreenTextFields & {
    review: ReviewFieldSpec[];
    /**
     * If present, set this variable to True when the user clicks the
     * resume button. Required if the block is mandatory.
     */
    "continue button field"?: VariableName;
    /**
     * The label for the Resume button (defaults to "Resume"). Mako string.
     * Only valid on review blocks.
     */
    "resume button label"?: MakoString;
    /**
     * The Bootstrap color of the Resume button. Mako string.
     */
    "resume button color"?: MakoString | BootstrapColor;
    /**
     * If false, do not skip undefined variables in the review list.
     * Default: true (skip undefined). Only valid on review blocks.
     */
    "skip undefined"?: boolean;
    /**
     * If set, render the review as a table with the given CSS class string.
     * E.g.: "table table-borderless"
     * true uses "table table-borderless" as default class.
     */
    tabular?: boolean | MakoString;
  };

/**
 * An event question. Shown when a special event occurs in the interview.
 * Can be combined with `question` (and optionally `buttons`) but not with
 * `field`, `fields`, `yesno`, or `noyes`.
 * The named event triggers this question to be shown.
 */
type EventBlock = CommonModifiers &
  Partial<ScreenTextFields> & {
    event: VariableName | VariableName[];
    buttons?: ChoiceList;
    shuffle?: boolean;
  };

// ---------------------------------------------------------------------------
// Choice list format (for buttons, choices, dropdown, combobox)
// ---------------------------------------------------------------------------

/**
 * A list of choices for multiple-choice questions and buttons.
 *
 * Each item can be:
 *   1. A plain string: used as both the label and the value.
 *   2. A single-key dict { "Label": value }: label->value mapping.
 *   3. A dict with keys `label` and `value` (and optionally other modifiers).
 *   4. A dict with key `code`: a Python expression returning a list of choices.
 *      The expression returns a list of:
 *        - dicts { value: label, ... }
 *        - two-element lists [value, label]
 *        - plain strings (label == value)
 *        - dicts with keys `label`, `value`, `default`, `help`, `image`, etc.
 *
 * Special "command" values for buttons (no `field` needed):
 *   restart, new_session, exit, logout, exit_logout, leave,
 *   continue, refresh, signin
 *
 * For `exit` with a redirect:
 *   - Restart: restart
 *   - Exit to URL:  { Exit: exit, url: "https://..." }
 */
type ChoiceItem =
  | string
  | Record<string, unknown>
  | ChoiceItemDict
  | { code: PythonExpression };

interface ChoiceItemDict {
  /** The visible label. Mako string. */
  label?: MakoString;
  /** The value stored in the variable. Any scalar. */
  value?: unknown;
  /**
   * URL to redirect to when this item represents an "exit" action.
   * Mako string.
   */
  url?: MakoString;
  /** Bootstrap color for this choice's button/badge. */
  color?: BootstrapColor | MakoString;
  /** Additional CSS class for this choice's button. Mako string. */
  "css class"?: MakoString;
  /** Image name (from images/image sets) to decorate this choice. */
  image?: string;
  /** Help text for this choice (popover). Mako string. */
  help?: MakoString;
  /** If false, exclude this choice from the list. Python expression. */
  "show if"?: PythonExpression;
  /** If true, pre-select this choice. */
  default?: boolean;
  /** Embedded question block run when this choice is selected. */
  question?: unknown; // Full QuestionBlock structure, nested
  /** Embedded code block run when this choice is selected. */
  code?: PythonCode;
}

type ChoiceList = ChoiceItem[];

// ---------------------------------------------------------------------------
// fields: individual field spec
// ---------------------------------------------------------------------------

/**
 * The complete set of standard datatypes for the `datatype` key in a field.
 */
type FieldDatatype =
  | "text"      // Single-line text input (default)
  | "area"      // Multi-line textarea (shorthand for input type: area)
  | "password"  // Password input
  | "hidden"    // Hidden field (shorthand for input type: hidden)
  | "email"     // Email address input
  | "date"      // Date picker
  | "time"      // Time picker
  | "datetime"  // Combined date+time picker
  | "integer"   // Integer input
  | "number"    // Floating point number input
  | "float"     // Same as number
  | "currency"  // Currency input (shows symbol)
  | "range"     // Slider (requires min and max)
  | "file"      // Single file upload
  | "files"     // Multiple file upload
  | "camera"    // Image-only file upload
  | "user"      // User-facing camera (front camera hint)
  | "environment" // Environment-facing camera (rear camera hint)
  | "camcorder" // Video file upload
  | "microphone" // Audio file upload
  | "yesno"     // Checkbox that sets True/False
  | "noyes"     // Checkbox that sets False/True (inverted)
  | "yesnowide" // Full-width yes/no checkbox
  | "noyeswide" // Full-width noyes checkbox
  | "yesnoradio" // Radio buttons for yes/no
  | "noyesradio" // Radio buttons for noyes (inverted)
  | "yesnomaybe" // Radio buttons for yes/no/maybe
  | "noyesmaybe" // Radio buttons for noyes/maybe (inverted)
  | "checkboxes" // Checkbox group (sets DADict of bool values)
  | "multiselect" // Multi-select <select> element (sets DADict)
  | "object"    // Single-select from existing objects
  | "object_radio" // Radio button select from existing objects
  | "object_checkboxes" // Checkbox select from existing objects
  | "object_multiselect" // Multi-select from existing objects
  | "ml"        // Machine learning text classification
  | "mlarea"    // Machine learning textarea (shorthand)
  | "raw"       // Raw text input (HTML not sanitized)
  | "radio"     // Shorthand: input type: radio
  | "dropdown"  // Shorthand: input type: dropdown
  | "combobox"  // Shorthand: input type: combobox
  | "datalist"  // Shorthand: input type: datalist
  | "ajax"      // Shorthand: input type: ajax
  | "pulldown"  // Alias for dropdown
  | string;     // Custom datatypes declared in Python modules

/**
 * The input type for multiple-choice fields within `fields`.
 * Controls the UI widget while datatype controls storage format.
 */
type FieldInputType =
  | "area"      // Multi-line textarea
  | "dropdown"  // Dropdown select
  | "radio"     // Radio button list
  | "datalist"  // HTML5 datalist combo
  | "combobox"  // JavaScript combobox
  | "ajax"      // Ajax-powered combobox
  | "hidden"    // Hidden input (JavaScript-populated)
  | "pulldown"; // Alias for dropdown

/**
 * A "show if" or "hide if" specifier for a field.
 *
 * Method 1 (JavaScript-based, depends on other fields on screen):
 *   { variable: "other_field_var", is: "expected_value" }
 * Method 2 (shorthand for boolean on-screen field):
 *   "other_yesno_variable"  (shown when truthy)
 * Method 3 (server-side Python):
 *   { code: "python_expression" }
 */
type ShowIfSpec =
  | { variable: VariableName; is: MakoString }
  | { code: PythonExpression }
  | VariableName;

/**
 * A field specification within the `fields` list. Each field dict must
 * have exactly one of:
 *   - A non-reserved key whose value is a variable name (label: varname form)
 *   - `label` + `field` (explicit form)
 *   - `note`, `html`, or `raw html` (display-only, no variable)
 *   - `code` (as the only key, generates sub-fields from Python expression)
 *
 * Reserved modifier keys are distinguished from label keys by name.
 */
interface FieldSpec {
  // --- Variable declaration (one of these must be present) ---

  /**
   * Explicit label for this field. Must be accompanied by `field`.
   * Mako string. "no label" is a special value for a wider unlabeled field.
   */
  label?: MakoString;

  /**
   * Explicit variable name. Must be accompanied by `label`.
   */
  field?: VariableName;

  /**
   * Display-only note text (Markdown + Mako). No variable is set.
   * Mutually exclusive with `html` and `raw html`.
   */
  note?: MakoString;

  /**
   * Display-only raw HTML. No variable is set.
   * Mutually exclusive with `note` and `raw html`.
   */
  html?: MakoString;

  /**
   * Display-only raw HTML inserted without wrapping element.
   * No variable is set.
   */
  "raw html"?: MakoString;

  /**
   * Generates sub-fields from a Python expression returning a list of
   * field dicts. If this is the only key, no variable is set by this
   * entry; the sub-fields are used instead.
   * Can also appear as part of a choices field (use `choices: {code: ...}`)
   */
  code?: PythonExpression;

  // --- Field modifiers ---

  /**
   * The data type of the input. See FieldDatatype.
   * Default: "text"
   */
  datatype?: FieldDatatype;

  /**
   * The input widget type. Used when datatype is a storage type but
   * you want a specific UI widget.
   */
  "input type"?: FieldInputType;

  /**
   * Whether this field is required. Default: true for most types.
   * false: field is optional.
   * PythonExpression string: evaluated at display time.
   */
  required?: BoolOrExpr;

  /**
   * If true or a truthy Python expression, disables the field.
   * The variable will not be set when the user submits the form.
   */
  disabled?: BoolOrExpr;

  /**
   * Default value for the field. Evaluated as a MakoString.
   * Also accepts {code: "python_expr"} for code-computed defaults.
   * For checkbox fields, can be a list or dict.
   */
  default?: MakoString | { code: PythonExpression } | unknown;

  /**
   * Placeholder ("hint") text shown inside the input before the user types.
   * Mako string.
   */
  hint?: MakoString;

  /**
   * Help text shown as a popover next to this field. Mako string.
   */
  help?: MakoString;

  /**
   * Conditional visibility (server-side or client-side).
   * See ShowIfSpec for the three forms.
   */
  "show if"?: ShowIfSpec;

  /**
   * Conditional hiding (opposite of show if).
   * Same forms as show if. Cannot be combined with show if.
   */
  "hide if"?: ShowIfSpec;

  /**
   * Conditionally disable (grey out) the field based on another field's value.
   * Same forms as show if, except {code: ...} is NOT supported.
   * Cannot be combined with show if or hide if.
   */
  "disable if"?: Omit<ShowIfSpec, { code: string }>;

  /**
   * Conditionally enable the field based on another field's value.
   * Same forms as disable if.
   * Cannot be combined with show if or hide if.
   */
  "enable if"?: Omit<ShowIfSpec, { code: string }>;

  /**
   * JavaScript expression for show/hide. Uses val('varname') function.
   * String only. Cannot be combined with non-js show if/hide if.
   */
  "js show if"?: string;

  /**
   * JavaScript expression for hide. Opposite of js show if.
   */
  "js hide if"?: string;

  /**
   * JavaScript expression for disabling field. Cannot be combined with
   * js show if or js hide if.
   */
  "js disable if"?: string;

  /**
   * JavaScript expression for enabling field.
   */
  "js enable if"?: string;

  /**
   * When set to True or a list of variable names, disabling this field
   * also disables other fields. Cannot be used with file/range/multiselect/
   * checkboxes/camera/user/environment/camcorder/microphone/
   * object_multiselect/object_checkboxes.
   */
  "disable others"?: boolean | VariableName[];

  /**
   * Makes this checkbox uncheck all other yesno/yesnowide/noyes/noyeswide
   * checkboxes on the screen ("None of the above" behavior).
   * true or a list of variable names.
   * Only valid with datatype: yesno/yesnowide/noyes/noyeswide.
   */
  "uncheck others"?: boolean | VariableName[];

  /**
   * Makes this checkbox check all other yesno/yesnowide/noyes/noyeswide
   * checkboxes on the screen ("All of the above" behavior).
   * true or a list of variable names.
   * Only valid with datatype: yesno/yesnowide/noyes/noyeswide.
   */
  "check others"?: boolean | VariableName[];

  /**
   * List of choices for multiple-choice fields.
   * Must be present if datatype is: object, object_radio, object_checkboxes,
   * object_multiselect, checkboxes, multiselect.
   * Can be a list of:
   *   - plain strings (label == value)
   *   - { "Label": value } dicts
   *   - { label: "...", value: ..., default: bool, help: "..." } dicts
   * For object datatypes, items are Python expressions resolving to objects.
   */
  choices?:
    | ChoiceItem[]
    | string // Python expression for object datatypes
    | { code: PythonExpression };

  /**
   * Python expression to generate the choices list dynamically.
   * Used instead of `choices` for computed choice lists.
   * The expression must evaluate to one of:
   *   - list of { value: label } dicts
   *   - list of [value, label] pairs
   *   - list of plain strings
   *   - list of { label, value, default, help, image } dicts
   * Note: `choices: { code: expr }` is equivalent to using `code: expr`
   * at the field level.
   */
  // code?: PythonExpression; (already declared above)

  /**
   * Items to exclude from the choices list. Python expression or list.
   * Only valid when `code` is used to generate choices.
   */
  exclude?: PythonExpression | PythonExpression[];

  /**
   * "None of the above" option for checkboxes/object_checkboxes/object_radio.
   * true: add default "None of the above" option.
   * false: suppress "None of the above".
   * MakoString: custom label for the none-of-the-above option.
   * For checkboxes, default is true. For object_radio, default is false.
   */
  "none of the above"?: boolean | MakoString;

  /**
   * "All of the above" option for checkboxes/object_checkboxes.
   * true: add default "All of the above" option.
   * false: suppress it (default).
   * MakoString: custom label.
   */
  "all of the above"?: boolean | MakoString;

  /**
   * If true, randomize order of choices. Default: false.
   */
  shuffle?: boolean;

  /**
   * Minimum value for number/currency/range fields (passed to jQuery Validate).
   * For range fields, required. Mako string.
   */
  min?: MakoString | number;

  /**
   * Maximum value for number/currency/range fields.
   * For range fields, required. Mako string.
   */
  max?: MakoString | number;

  /**
   * Minimum length/character count for text fields, or minimum number of
   * checkboxes checked. Mako string.
   */
  minlength?: MakoString | number;

  /**
   * Maximum length/character count or maximum checkboxes. Mako string.
   */
  maxlength?: MakoString | number;

  /**
   * Step size for number/range fields. Mako string.
   */
  step?: MakoString | number;

  /**
   * Scale for range fields. "logarithmic" is the only special value.
   */
  scale?: "logarithmic" | MakoString;

  /**
   * Currency symbol override for currency fields.
   * Mako string. E.g.: "€"
   */
  "currency symbol"?: MakoString;

  /**
   * Number of rows for `area` or `multiselect`/`object_multiselect` fields.
   * Integer or Python expression string (compiled with 'eval').
   */
  rows?: number | PythonExpression;

  /**
   * For file upload fields: reduce uploaded images to at most this many pixels.
   * Integer or Python expression.
   */
  "maximum image size"?: number | PythonExpression;

  /**
   * For file upload fields: the format to convert uploaded images to.
   * "jpeg", "jpg", "bmp", or "png". Or a Python expression.
   */
  "image upload type"?: "jpeg" | "jpg" | "bmp" | "png" | PythonExpression;

  /**
   * For file upload fields: MIME type accept string for the <input accept>.
   * Python expression (e.g. "\"image/*\"").
   */
  accept?: PythonExpression;

  /**
   * For file upload fields: CSS class for the file input element.
   * Mako string. "None" disables the Bootstrap File Input plugin.
   */
  "file css class"?: MakoString;

  /**
   * Whether uploaded files persist after the session ends.
   * true/false or Python expression.
   */
  persistent?: BoolOrExpr;

  /**
   * Whether uploaded files are private (only accessible by the uploader).
   * true/false or Python expression. Default: true (private).
   */
  private?: BoolOrExpr;

  /**
   * Email addresses or user IDs allowed to access uploaded files.
   * String, list of strings/ints, or {code: expr}.
   */
  "allow users"?:
    | string
    | (string | number)[]
    | { code: PythonExpression };

  /**
   * Privilege names (role names) allowed to access uploaded files.
   * String, list of strings, or {code: expr}.
   */
  "allow privileges"?:
    | string
    | string[]
    | { code: PythonExpression };

  /**
   * For ml/mlarea fields: the machine learning group/model to use.
   * Mako string.
   */
  using?: MakoString;

  /**
   * For ml/mlarea fields: whether to use the input for training.
   * true/false or Python expression.
   */
  "keep for training"?: BoolOrExpr;

  /**
   * For object datatypes: a Python expression returning a function that
   * generates the label for each object in the choices list.
   */
  "object labeler"?: PythonExpression;

  /**
   * Python expression returning a function that generates help text
   * for each item in the choices list.
   */
  "help generator"?: PythonExpression;

  /**
   * Python expression returning a function that generates an image
   * for each item in the choices list.
   */
  "image generator"?: PythonExpression;

  /**
   * For ajax fields: the action name to call when the user types.
   * Required when input type is ajax.
   */
  action?: string;

  /**
   * For ajax fields: minimum number of characters before triggering.
   * Must be an integer >= 2. Default: 4.
   */
  "trigger at"?: number;

  /**
   * Address autocomplete configuration.
   * true/false: enable/disable.
   * PythonExpression: evaluated for enable/disable.
   * dict: Google Maps Places API configuration.
   */
  "address autocomplete"?: boolean | PythonExpression | Record<string, unknown>;

  /**
   * If true (or a truthy Python expression), position the label above
   * the field instead of to the left.
   */
  "label above field"?: boolean | PythonExpression;

  /**
   * If true (or a truthy Python expression), use Bootstrap floating labels.
   */
  "floating label"?: boolean | PythonExpression;

  /**
   * Bootstrap grid width for this field (1-12). Puts adjacent fields
   * side by side. Integer or Python expression string.
   * Can also be a dict with keys: width, label width, offset, start, end, breakpoint.
   */
  grid?: number | PythonExpression | GridSpec;

  /**
   * Grid width for items within a radio/checkbox list.
   * Integer or dict with keys: width, breakpoint.
   */
  "item grid"?: number | ItemGridSpec;

  /**
   * Whether to show the label and field on one row (inline).
   * Mako string (boolean expression).
   */
  inline?: MakoString;

  /**
   * Width of the inline field. Mako string.
   */
  "inline width"?: MakoString;

  /**
   * Additional CSS class for the input element. Mako string.
   */
  "css class"?: MakoString;

  /**
   * Text to display below this field (contextual guidance). Mako string.
   */
  "under text"?: MakoString;

  /**
   * Per-field validation messages (overrides defaults).
   * Dict of validation rule name -> message string.
   */
  "validation messages"?: Record<string, MakoString>;

  /**
   * Server-side validation code. Python expression returning true or raising
   * DAValidationError. Must return a boolean.
   */
  validate?: PythonExpression;

  /**
   * Group name for grouping radio/checkbox choices visually.
   * Mako string.
   */
  group?: MakoString;

  /**
   * Logical group for related fields (CSS/JS grouping).
   * Mako string.
   */
  // group is already declared above

  /**
   * Custom metadata for this field. Any YAML structure is allowed.
   * Mako supported in text values. Accessible in JSON representation.
   */
  "field metadata"?: unknown;

  // Catch-all: any other key is treated as the field label,
  // with its value as the variable name.
  [label: string]: unknown;
}

interface GridSpec {
  /** Width of the field (1-12). Integer or Python expression. */
  width: number | PythonExpression;
  /** Width of the label (1-12). Integer or Python expression. */
  "label width"?: number | PythonExpression;
  /** Offset (1-12). Integer or Python expression. */
  offset?: number | PythonExpression;
  /** If true, start a new Bootstrap row with this field. */
  start?: boolean | PythonExpression;
  /** If true, end the current Bootstrap row after this field. */
  end?: boolean | PythonExpression;
  /** Bootstrap responsive breakpoint (xs/sm/md/lg/xl/xxl). Mako string. */
  breakpoint?: MakoString;
}

interface ItemGridSpec {
  /** Width of each item (1-12). Integer or Python expression. */
  width: number | PythonExpression;
  /** Bootstrap responsive breakpoint. Mako string. */
  breakpoint?: MakoString;
}

// ---------------------------------------------------------------------------
// review: individual review field spec
// ---------------------------------------------------------------------------

/**
 * A field specification within the `review` list.
 * Each item describes one entry in the review screen.
 *
 * Forms:
 *   1. { "Label": "variable_name" } - show/edit a single variable
 *   2. { "Label": ["var1", "var2"] } - show/edit multiple variables
 *   3. { label: "...", field: "var" } or { label: "...", fields: [...] }
 *   4. { note: "..." } or { html: "..." } or { raw html: "..." } - display only
 *   5. { button: "Label" } - a button (like a note but styled as a button)
 *   6. { show if: "var" } or { show if: ["var1", "var2"] } - conditional
 */
interface ReviewFieldSpec {
  /**
   * Explicit label for this review item. Must be accompanied by `field`.
   * Mako string.
   */
  label?: MakoString;

  /**
   * Single variable to review. Must be accompanied by `label`.
   */
  field?: VariableName;

  /**
   * Multiple variables to review together. Must be accompanied by `label`.
   */
  fields?: (VariableName | ReviewActionSpec)[];

  /**
   * Display note text. No variable is associated.
   */
  note?: MakoString;

  /**
   * Display HTML text. No variable is associated.
   */
  html?: MakoString;

  /**
   * Display raw HTML. No variable is associated.
   */
  "raw html"?: MakoString;

  /**
   * A button that acts like a note but with button styling.
   * Clicking it triggers the `action` specified.
   */
  button?: MakoString;

  /**
   * An action to run when the user clicks on this review item.
   * Plain text: the name of the action.
   */
  action?: string;

  /**
   * Show this review item only if the listed variable(s) are defined.
   * String or list of strings.
   */
  "show if"?: VariableName | VariableName[];

  /**
   * Additional CSS class for this review item row.
   */
  "css class"?: MakoString;

  /**
   * Help text for this review item.
   */
  help?: MakoString;

  // Catch-all: other keys are treated as label: variable_or_list
  [label: string]: unknown;
}

/**
 * Special action specs within a review field/fields list.
 * These appear as dict items in the list of variables to review.
 */
type ReviewActionSpec =
  | { undefine: VariableName[] }
  | { invalidate: VariableName[] }
  | { recompute: VariableName[] }
  | { "follow up": VariableName[] }
  | { set: Array<Record<VariableName, unknown>> }
  | { action: string; arguments: Record<string, unknown> };

// ---------------------------------------------------------------------------
// Code block
// ---------------------------------------------------------------------------

/**
 * A code block contains Python code that is executed when docassemble
 * needs to define variables the code sets.
 *
 * `mandatory: True` or `initial: True` can be added to make the code run
 * unconditionally or at the start of every screen respectively.
 *
 * `event` can be combined with `code` to make a code block that runs when
 * a named event is triggered.
 */
interface CodeBlock extends Omit<CommonModifiers, "mandatory"> {
  /**
   * Python code to execute. Multi-line code uses YAML block literal `|`.
   * The code can define variables, call functions, etc.
   */
  code: PythonCode;

  /**
   * Triggers this block unconditionally or conditionally.
   * true: always execute first in every screen evaluation pass.
   * false/null: not mandatory.
   * PythonExpression: execute when condition is true.
   * Cannot be combined with `initial`.
   */
  mandatory?: BoolOrExpr;

  /**
   * Marks this code as "initial": run at the start of every screen load.
   * true: always run before anything else.
   * false/null: not initial.
   * PythonExpression: run when condition is true.
   * Cannot be combined with `mandatory`.
   */
  initial?: BoolOrExpr;

  /**
   * When combined with code, makes an event handler.
   * The code runs when the named event is triggered.
   */
  event?: VariableName | VariableName[];

  /**
   * Set the default role(s) for the interview (used in multi-user interviews).
   * Can be combined with code.
   * String or list of strings.
   */
  "default role"?: string | string[];
}

// ---------------------------------------------------------------------------
// Template block
// ---------------------------------------------------------------------------

/**
 * A template block defines a DATemplate variable with Markdown + Mako content.
 * The variable can be referenced in attachments or displayed in question text.
 *
 * If `content file` is used instead of `content`, the content is loaded from
 * a file. `content file` can be a filename string, list of filenames (concatenated),
 * or { code: "python_expression" } for code-computed filename.
 */
interface TemplateBlock extends CommonModifiers {
  /**
   * The variable name to assign the template content to.
   */
  template: VariableName;

  /**
   * The Markdown + Mako content of the template body.
   * Mutually exclusive with `content file` (though content file is
   * converted to content at parse time).
   */
  content?: MakoString;

  /**
   * Path to a Markdown file (in the package's templates folder) to use
   * as the content. String, list of strings (concatenated), or
   * { code: "python_expression" } for runtime filename.
   */
  "content file"?: MakoString | MakoString[] | { code: PythonExpression };

  /**
   * Subject line of the template (for email use).
   * Mako string. Used as the `subject` attribute of the DATemplate.
   */
  subject?: MakoString;

  /**
   * Target for this template: the name of a variable that should be updated
   * when this template is re-rendered. Plain text.
   * Only valid with `template`.
   */
  target?: string;
}

// ---------------------------------------------------------------------------
// Table block
// ---------------------------------------------------------------------------

/**
 * A table block defines a variable that displays as an HTML table when
 * referenced in a question. All three keys (table, rows, columns) are required.
 */
interface TableBlock extends CommonModifiers {
  /**
   * The variable name to assign the table to. Plain text.
   */
  table: VariableName;

  /**
   * Python expression that evaluates to an iterable (DAList, DADict, etc.).
   * Each element becomes a row. The iteration variable is available as
   * `row_item` and the index as `row_index` in column expressions.
   */
  rows: PythonExpression;

  /**
   * List of column definitions. Each column is a dict with either:
   *   { header: "Label", cell: "python_expr" }
   *   or { "Label": "python_expr" } (shorthand)
   */
  columns: Array<
    | { header: MakoString; cell: PythonExpression }
    | Record<string, PythonExpression>
  >;

  /**
   * Whether to require that the DAList/DADict is fully gathered before
   * showing the table. Default: true.
   * false: show the table even if not all items are gathered.
   */
  "require gathered"?: boolean;

  /**
   * Whether to show incomplete (not-yet-gathered) items in the table.
   * Default: false. Only used when require gathered is false.
   */
  "show incomplete"?: boolean;

  /**
   * Whether to add edit/delete buttons to each row.
   * true: add edit and delete buttons.
   * false: no buttons.
   * list of strings: add edit buttons for the listed attribute names.
   */
  edit?: boolean | string[];

  /**
   * Whether to add delete buttons (but not edit buttons) to each row.
   * Only used if `edit` is not set.
   */
  "delete buttons"?: boolean;

  /**
   * Whether to add reorder buttons to each row.
   * Only used when edit is set or delete buttons is set.
   */
  "allow reordering"?: boolean;

  /**
   * Whether to ask for confirmation before deleting a row.
   */
  confirm?: boolean;

  /**
   * The attribute name used as the read-only marker. Plain text.
   * If an item has this attribute set to true, it cannot be edited/deleted.
   */
  "read only"?: string;

  /**
   * Header text for the edit/action column. Mako string.
   * Default: "Actions".
   */
  "edit header"?: MakoString;

  /**
   * Text or behavior for empty tables.
   * true (default): show default "There are no items" message.
   * false: show nothing.
   * MakoString: show custom message.
   */
  "show if empty"?: boolean | MakoString;

  /**
   * Label for N/A values. Plain text.
   * Default: "n/a"
   */
  "not available label"?: string;

  /**
   * Whether to indent the table. Default: false.
   */
  indent?: boolean;

  /**
   * Python expression to sort the rows. Expression receives `row_item`.
   */
  "sort key"?: PythonExpression;

  /**
   * Python expression for sort direction. Default: False (ascending).
   */
  "sort reverse"?: PythonExpression;

  /**
   * Python expression to filter rows. Rows where the expression evaluates
   * to false are hidden.
   */
  filter?: PythonExpression;
}

// ---------------------------------------------------------------------------
// Attachment blocks
// ---------------------------------------------------------------------------

/**
 * An attachment block assembles a document (PDF, DOCX, RTF, etc.) and
 * makes it available for download or emailing.
 *
 * `attachment` (singular) accepts either a single AttachmentSpec dict or
 * a string (Markdown content, minimal form).
 * `attachments` (plural) accepts a list of AttachmentSpec dicts.
 * `attachment code` and `attachments code` accept a Python expression
 * that returns a list of attachment specification dicts.
 *
 * An attachment block requires a `question` to display the assembled
 * documents to the user.
 */
type AttachmentBlock = CommonModifiers &
  ScreenTextFields & {
    attachment?: AttachmentSpec | AttachmentSpec[] | string;
    attachments?: AttachmentSpec[];
    "attachment code"?: PythonExpression;
    "attachments code"?: PythonExpression;

    /**
     * Whether to offer the email option to the user. Default: true.
     */
    "allow emailing"?: boolean;

    /**
     * Whether to offer the download option. Default: true.
     */
    "allow downloading"?: boolean;

    /**
     * Default email subject when emailing attachments. Mako string.
     */
    "email subject"?: MakoString;

    /**
     * Default email body when emailing attachments. Mako string.
     */
    "email body"?: MakoString;

    /**
     * A Python expression returning an email template object to use
     * for the email.
     */
    "email template"?: PythonExpression;

    /**
     * Default email address for sending. Mako string.
     */
    "email address default"?: MakoString;

    /**
     * Always include editable (source) files in the download. Default: false.
     */
    "always include editable files"?: boolean;

    /**
     * Whether to include the attachment notice. Default: true.
     */
    "include attachment notice"?: boolean;

    /**
     * Whether to include the download tab. Default: true.
     */
    "include download tab"?: boolean;

    /**
     * Whether to describe the file types available for download.
     */
    "describe file types"?: boolean;

    /**
     * If true, the attachment list is not auto-generated; the interview
     * developer must manually display it.
     */
    "manual attachment list"?: boolean;

    /**
     * Filename for a ZIP archive containing all attachments. Mako string.
     */
    "zip filename"?: MakoString;
  };

/**
 * A single attachment specification within an `attachments` list or
 * the value of `attachment`.
 *
 * The attachment can be:
 *   - A Markdown content document (using `content` or `content file`)
 *   - A PDF form fill (using `pdf template file` + `fields`)
 *   - A DOCX template (using `docx template file`)
 *   - Other formats via `valid formats`
 */
interface AttachmentSpec {
  /**
   * The display name of the document. Mako string.
   * Default: "Document"
   */
  name?: MakoString;

  /**
   * The filename (without extension) for the downloaded file. Mako string.
   * Default: derived from name.
   */
  filename?: MakoString;

  /**
   * Description of the document. Mako string. Used in some templates.
   */
  description?: MakoString;

  /**
   * The variable name to store the assembled document (DAFile).
   * If omitted, a temporary internal variable is used.
   */
  "variable name"?: VariableName;

  /**
   * Markdown + Mako content of the document.
   * Mutually exclusive with `content file` and `docx template file`.
   */
  content?: MakoString;

  /**
   * Path to a Markdown file to use as content.
   * String, list of strings, or {code: "python_expression"}.
   */
  "content file"?:
    | MakoString
    | MakoString[]
    | { code: PythonExpression };

  /**
   * Output formats to generate. Default: ["*"] (all supported formats).
   *
   * Possible values:
   *   "pdf", "rtf", "docx", "tex", "html", "md", "raw",
   *   "rtf to docx" (converts RTF to DOCX via Word)
   * String or list of strings. Also accepts {code: "python_expr"}.
   *
   * Special: ["raw"] with a content file that has an extension generates
   * a file of that type.
   */
  "valid formats"?:
    | string
    | string[]
    | { code: PythonExpression };

  /**
   * Path to a PDF template file with form fields to fill.
   * When used, `fields` (or `field code`, `field variables`, etc.) define
   * the values for the PDF form fields.
   * Mutually exclusive with `docx template file`.
   */
  "pdf template file"?: MakoString;

  /**
   * Path(s) to a DOCX template file to populate using Jinja2 syntax.
   * When used, variables are passed automatically (field_mode: auto)
   * unless `fields` is specified explicitly.
   * String, list of strings, or {code: "python_expression"}.
   * Mutually exclusive with `pdf template file`.
   */
  "docx template file"?:
    | MakoString
    | MakoString[]
    | { code: PythonExpression };

  /**
   * Field values for PDF/DOCX template files.
   * For PDF: dict or list of dicts mapping form field names to values.
   * For DOCX: dict or list mapping Jinja2 variable names to values.
   * If omitted for DOCX, all interview variables are passed automatically.
   *
   * Dict form: { "PDF Field Name": "value", ... }
   * List form: [ { "field1": "val1" }, { "field2": code_expr }, ... ]
   *
   * Values can be Mako strings or dicts with a "code" key.
   */
  fields?: Record<string, MakoOrCode> | Array<Record<string, MakoOrCode>>;

  /**
   * A Python expression for additional field values (for PDF/DOCX).
   * Result is merged with `fields`.
   */
  code?: PythonExpression;

  /**
   * List of variable names whose values are automatically used as field
   * values. Each name must be a simple identifier.
   */
  "field variables"?: VariableName[];

  /**
   * Like `field variables` but values are used as raw Python without
   * Mako rendering.
   */
  "raw field variables"?: VariableName[];

  /**
   * List of dicts mapping field names to Python expressions.
   * E.g.: [{fieldname: python_expr}]
   */
  "field code"?: Array<Record<string, PythonExpression>>;

  /**
   * Whether to update cross-references in DOCX files.
   * true/false or Python expression.
   */
  "update references"?: BoolOrExpr;

  /**
   * Whether to skip undefined variables in Mako templates instead of
   * raising an error. true/false or Python expression.
   * Default: false.
   */
  "skip undefined"?: BoolOrExpr;

  /**
   * PDF metadata (author, title, subject, keywords, etc.).
   * Dict of key -> string or list of strings.
   */
  metadata?: Record<string, MakoString | MakoString[] | boolean>;

  /**
   * A LaTeX/RTF/other template file for non-PDF non-DOCX output.
   */
  "template file"?: string;

  /**
   * An RTF template file.
   */
  "rtf template file"?: string;

  /**
   * A DOCX reference file for DOCX styling.
   */
  "docx reference file"?: string;

  /**
   * Initial YAML files for the document assembly context.
   * String or list of strings (package:path references).
   */
  "initial yaml"?: string | string[];

  /**
   * Additional YAML files for the document assembly context.
   * String or list of strings.
   */
  "additional yaml"?: string | string[];

  /**
   * Definitions from `def` blocks to include in the Mako context.
   * String (single def name) or list of strings.
   */
  usedefs?: string | string[];

  /**
   * The language to use for rendering this attachment.
   */
  language?: string;

  /**
   * Whether to output in PDF/A format.
   * true/false or Python expression.
   */
  "pdf/a"?: BoolOrExpr;

  /**
   * Whether to use pdftk for PDF processing.
   * true/false or Python expression.
   */
  pdftk?: BoolOrExpr;

  /**
   * Whether to produce a tagged PDF. true/false or Python expression.
   */
  "tagged pdf"?: BoolOrExpr;

  /**
   * Whether to enable redaction. true/false or Python expression.
   */
  redact?: BoolOrExpr;

  /**
   * Whether the PDF form should remain editable.
   * Python expression evaluated to bool.
   */
  editable?: PythonExpression;

  /**
   * The value for checkbox export in PDF forms. Must be a string.
   * Only valid with `pdf template file`.
   */
  "checkbox export value"?: string;

  /**
   * Number of decimal places for numeric PDF form fields.
   * Integer or string.
   */
  "decimal places"?: number | string;

  /**
   * Password for opening the generated PDF.
   */
  password?: MakoString;

  /**
   * Owner password for the generated PDF.
   */
  "owner password"?: MakoString;

  /**
   * Password for the DOCX template file (if encrypted).
   */
  "template password"?: MakoString;

  /**
   * Whether the file persists after the session ends.
   * true/false or Python expression.
   */
  persistent?: BoolOrExpr;

  /**
   * Whether the file is private.
   * true/false or Python expression. Default: true.
   */
  private?: BoolOrExpr;

  /**
   * Users allowed to access the file. String, list, or {code: expr}.
   */
  "allow users"?:
    | string
    | number
    | (string | number)[]
    | { code: PythonExpression };

  /**
   * Privilege names allowed to access the file. String, list, or {code: expr}.
   */
  "allow privileges"?:
    | string
    | string[]
    | { code: PythonExpression };

  /**
   * Hyperlink style for the document ("word" or "markdown").
   */
  "hyperlink style"?: MakoString;

  /**
   * Font to use for rendering (e.g. for PDF generation from Markdown).
   */
  "rendering font"?: MakoString;

  /**
   * Whether to output a "raw" document (no conversion).
   * true: use the file extension of the content file as the format.
   */
  raw?: boolean;

  /**
   * Manual mapping of page numbers to Python expressions.
   * Dict where keys are alphanumeric strings and values are Python expressions.
   * Used for low-level PDF manipulation.
   */
  manual?: Record<string, PythonExpression>;

  /**
   * Python expression for manual attachment processing.
   */
  "manual code"?: PythonExpression;
}

// ---------------------------------------------------------------------------
// Objects block
// ---------------------------------------------------------------------------

/**
 * An `objects` block initializes one or more Python objects.
 * Each item in the list maps a variable name to a Python class name.
 *
 * Example:
 *   objects:
 *     - user: Individual
 *     - client: Person
 */
interface ObjectsBlock extends CommonModifiers {
  /**
   * List of dicts, each mapping a variable name to a class name.
   * { "variable_name": "ClassName" }
   * The class must be importable in the docassemble context.
   */
  objects: Array<Record<VariableName, string>>;
}

// ---------------------------------------------------------------------------
// Objects from file block
// ---------------------------------------------------------------------------

/**
 * An `objects from file` block loads Python objects from a YAML or JSON file.
 */
interface ObjectsFromFileBlock extends CommonModifiers {
  /**
   * List of dicts mapping variable names to source file references.
   * { "variable_name": "package:data/sources/file.yml" }
   */
  "objects from file": Array<Record<VariableName, MakoString>>;

  /**
   * Whether to use the objects in the file as Python objects.
   * true (default): use as Python objects.
   * false: use as plain dicts.
   * "objects": use a special nested object format.
   * Python expression: evaluated at runtime.
   */
  "use objects"?: boolean | "objects" | PythonExpression;
}

// ---------------------------------------------------------------------------
// Data block
// ---------------------------------------------------------------------------

/**
 * A `data` block defines a variable from a static YAML data structure.
 * The structure is converted to Python primitives or docassemble objects.
 */
interface DataBlock extends CommonModifiers {
  /**
   * The variable name to assign the data to.
   */
  "variable name": VariableName;

  /**
   * The data to assign. Any YAML structure is allowed.
   */
  data: unknown;

  /**
   * Whether to convert the data to Python objects.
   * false (default): keep as plain Python dicts/lists.
   * true: convert to docassemble objects where possible.
   * "objects": use special nested object conversion.
   */
  "use objects"?: boolean | "objects";

  /**
   * Marks the data as gathered (for DAList/DADict variables).
   * true (default): set .gathered = True.
   * false: do not set .gathered.
   * Python expression: evaluated to determine gathered status.
   */
  gathered?: BoolOrExpr;
}

/**
 * A `data from code` block defines a variable from a YAML structure
 * where values are Python expressions evaluated at runtime.
 */
interface DataFromCodeBlock extends CommonModifiers {
  /**
   * The variable name to assign the data to.
   */
  "variable name": VariableName;

  /**
   * The data structure where values are Python expressions.
   * Values are evaluated as Python expressions.
   */
  "data from code": unknown;

  /** Same as DataBlock.use_objects */
  "use objects"?: boolean | "objects";

  /** Same as DataBlock.gathered */
  gathered?: BoolOrExpr;
}

// ---------------------------------------------------------------------------
// Initial / metadata blocks (not added to question queue)
// ---------------------------------------------------------------------------

/**
 * A `features` block configures global interview-wide settings.
 * Must not be combined with other block types. Not added to question queue.
 */
interface FeaturesBlock {
  features: FeaturesSpec;
  /** Optional comment. */
  comment?: string;
}

interface FeaturesSpec {
  /**
   * Whether to show a progress bar. Default: false.
   */
  "progress bar"?: boolean;

  /**
   * Whether to show the percentage in the progress bar.
   */
  "show progress bar percentage"?: boolean;

  /**
   * Whether the progress bar value can decrease (go backwards).
   */
  "progress can go backwards"?: boolean;

  /**
   * How the progress bar is calculated.
   * "DANav": based on navigation sections.
   */
  "progress bar method"?: string;

  /**
   * A multiplier (0 < x < 1) for the progress bar calculation.
   */
  "progress bar multiplier"?: number;

  /**
   * Whether to show a navigation bar. true/false or "horizontal".
   */
  navigation?: boolean | "horizontal";

  /**
   * Whether to show navigation on small screens.
   * true, false, or "dropdown".
   */
  "small screen navigation"?: boolean | "dropdown";

  /**
   * Whether to center the question content. Default: true.
   */
  centered?: boolean;

  /**
   * Whether to use a wide side-by-side layout.
   */
  "wide side by side"?: boolean;

  /**
   * Whether to show a back button within the question body.
   */
  "question back button"?: boolean;

  /**
   * Whether to show a question help button within the question body.
   */
  "question help button"?: boolean;

  /**
   * Whether to show a back button in the navigation bar.
   */
  "navigation back button"?: boolean;

  /**
   * Go full screen on mobile when the user starts interacting.
   * true: always go full screen.
   * false: never.
   * Other values: trigger condition.
   */
  "go full screen"?: boolean | unknown;

  /**
   * Maximum pixels for uploaded images before they are scaled down.
   * Evaluated as a Python expression (can reference interview variables).
   */
  "maximum image size"?: number | PythonExpression;

  /**
   * Default image upload type: "jpeg", "jpg", "bmp", "png".
   */
  "image upload type"?: string;

  /**
   * Whether to enable debug mode for this interview. Default: server setting.
   */
  debug?: boolean;

  /**
   * Whether to cache assembled documents. Default: server setting.
   */
  "cache documents"?: boolean;

  /**
   * Maximum loop iterations in interview logic. Integer.
   */
  "loop limit"?: number;

  /**
   * Maximum recursion depth in interview logic. Integer.
   */
  "recursion limit"?: number;

  /**
   * Whether to produce PDF/A output by default. Default: false.
   */
  "pdf/a"?: boolean;

  /**
   * Whether to use pdftk for PDF processing. Default: server setting.
   */
  pdftk?: boolean;

  /**
   * Whether to produce tagged PDFs. Default: false.
   */
  "tagged pdf"?: boolean;

  /**
   * Bootstrap theme file to load for this interview.
   * Path relative to the package's static/bootstrap directory.
   */
  "bootstrap theme"?: string;

  /**
   * Whether to use an inverse (dark) navbar. Default: false.
   */
  "inverse navbar"?: boolean;

  /**
   * How to trigger popovers: "hover" or "click". Default: "hover".
   */
  "popover trigger"?: "hover" | "click";

  /**
   * Bootstrap color for review buttons.
   */
  "review button color"?: BootstrapColor | string;

  /**
   * Font Awesome icon for review buttons.
   */
  "review button icon"?: string;

  /**
   * Whether to disable analytics. Default: false (analytics enabled).
   */
  "disable analytics"?: boolean;

  /**
   * Whether to hide the navbar. Default: false.
   */
  "hide navbar"?: boolean;

  /**
   * Whether to hide the standard menu. Default: false.
   */
  "hide standard menu"?: boolean;

  /**
   * Whether to position labels above fields by default.
   */
  "labels above fields"?: boolean;

  /**
   * Whether to suppress browser autofill.
   */
  "suppress autofill"?: boolean;

  /**
   * Whether to use Bootstrap floating labels by default.
   */
  "floating labels"?: boolean;

  /**
   * Whether to send question data to the browser.
   */
  "send question data"?: boolean;

  /**
   * Custom datatypes to load JavaScript for.
   * String or list of strings.
   */
  "custom datatypes to load"?: string | string[];

  /**
   * How often the browser checks in with the server (milliseconds).
   * 0 to disable. Minimum 1000 if not 0.
   */
  "checkin interval"?: number;

  /**
   * Whether to hide the corner interface (e.g. the spinning indicator).
   */
  "hide corner interface"?: boolean;

  /**
   * JavaScript files to load for this interview.
   * String or list of strings (package:path or URL).
   */
  javascript?: string | string[];

  /**
   * CSS files to load for this interview.
   * String or list of strings.
   */
  css?: string | string[];

  /**
   * Whether to use a "catchall" block to handle undefined variables.
   */
  "use catchall"?: boolean;

  /**
   * Maximum width of table columns in pixels.
   */
  "table width"?: number;

  /**
   * Default minimum date for date fields.
   * Parsed as a date string.
   */
  "default date min"?: string;

  /**
   * Default maximum date for date fields.
   * Parsed as a date string.
   */
  "default date max"?: string;

  /**
   * Auto Jinja filter expression(s) applied to DOCX Jinja2 context.
   * String or list of strings (Python expressions).
   */
  "auto jinja filter"?: string | string[];
}

/**
 * A `metadata` block provides interview-level metadata.
 * Must not be combined with other block types. Not added to question queue.
 */
interface MetadataBlock {
  metadata: MetadataSpec;
  comment?: string;
}

interface MetadataSpec {
  /**
   * Title shown in the interview list and browser title.
   * Plain text (no Mako).
   */
  title?: string;

  /**
   * Short title for the navigation bar (small screens).
   */
  "short title"?: string;

  /**
   * URL the title links to.
   */
  "title url"?: string;

  /**
   * Whether the title URL opens in a new window. Default: true.
   */
  "title url opens in other window"?: boolean;

  /**
   * Subtitle (visible in the Available Interviews list, not on screen).
   */
  subtitle?: string;

  /**
   * Custom HTML for the logo area (replaces title).
   */
  logo?: string;

  /**
   * Custom HTML for the logo on small screens.
   */
  "short logo"?: string;

  /**
   * Default language for this interview (overrides server default).
   */
  "default language"?: string;

  /**
   * URL to redirect to when the user clicks the exit link.
   */
  "exit url"?: string;

  /**
   * Whether the exit link exits ("exit") or leaves ("leave").
   */
  "exit link"?: "exit" | "leave";

  /**
   * Label for the exit link.
   */
  "exit label"?: string;

  /**
   * Custom navigation bar HTML.
   */
  "navigation bar html"?: string;

  /**
   * Version of the interview.
   */
  version?: string | number;

  /**
   * Author name(s).
   */
  authors?: string | string[] | Array<{ name: string; organization?: string }>;

  /**
   * Institution/organization name.
   */
  institution?: string;

  // Any other custom metadata fields are allowed.
  [key: string]: unknown;
}

/**
 * A `default language` block sets the default language for all subsequent
 * blocks in the file.
 */
interface DefaultLanguageBlock {
  "default language": string;
  comment?: string;
}

/**
 * An `include` block loads another YAML file into the interview.
 * String or list of strings. Filenames can be:
 *   - Simple filename (looks in current package's data/questions/ folder)
 *   - "package:data/questions/file.yml" (cross-package reference)
 */
interface IncludeBlock {
  include: string | string[];
  comment?: string;
}

/**
 * A `modules` block imports Python modules into the interview's namespace.
 * String or list of strings (module names, e.g. "docassemble.demo.legal").
 */
interface ModulesBlock {
  modules: string | string[];
  comment?: string;
}

/**
 * An `imports` block imports Python modules (like `import module` in Python).
 * Unlike `modules` (which uses `from module import *`), `imports` uses
 * `import module`. String or list of strings.
 */
interface ImportsBlock {
  imports: string | string[];
  comment?: string;
}

/**
 * A `reset` block causes listed variables to be undefined before the
 * interview logic runs on each screen load.
 * String or list of strings.
 */
interface ResetBlock {
  reset: string | string[];
  comment?: string;
}

/**
 * A `terms` block (standalone, without `question`) defines interview-wide
 * hover-popup term definitions. Terms in {braces} in question text will
 * be linked to popups.
 *
 * Dict form: { "term": "definition", ... }
 * List form: list of single-key dicts or {phrases: [...], definition: ...}
 */
interface StandaloneTermsBlock {
  terms: Record<string, MakoString> | TermItem[];
  language?: string;
  comment?: string;
}

/**
 * An `auto terms` block (standalone) like `terms` but auto-links
 * matching text without requiring explicit {braces}.
 */
interface StandaloneAutoTermsBlock {
  "auto terms": Record<string, MakoString> | TermItem[];
  language?: string;
  comment?: string;
}

/**
 * An `interview help` block defines global help text for the interview.
 * Shown when the user clicks the help tab.
 */
interface InterviewHelpBlock {
  "interview help": MakoString | InterviewHelpSpec;
  language?: string;
  comment?: string;
}

interface InterviewHelpSpec {
  /** Required. The help content. Mako string. */
  content: MakoString;
  /** Optional heading. Mako string. */
  heading?: MakoString;
  /** Optional label. Mako string. */
  label?: MakoString;
  /** Audio file(s). String or list. */
  audio?: MakoString | MakoString[];
  /** Video file(s). String or list. */
  video?: MakoString | MakoString[];
}

/**
 * A `default screen parts` block defines interview-wide default values
 * for screen parts (pre, post, title, etc.). Values are Mako strings
 * evaluated on every screen load. Setting a value to null removes it.
 */
interface DefaultScreenPartsBlock {
  "default screen parts": Record<string, MakoString | null>;
  language?: string;
  comment?: string;
}

/**
 * A `default validation messages` block defines interview-wide custom
 * validation error messages for jQuery Validation Plugin rules.
 * Keys are validation rule names; values are message strings.
 */
interface DefaultValidationMessagesBlock {
  "default validation messages": Record<string, string>;
  language?: string;
  comment?: string;
}

/**
 * A `sections` block defines the navigation sections for the interview.
 * Used with the progress bar/navigation features.
 *
 * The list can contain strings or dicts. Dict form:
 *   { "Section Name": [ subsection_list ] }  (with subsections)
 *   { "key": "Section Name" }  (key/value)
 */
interface SectionsBlock {
  sections: Array<string | Record<string, unknown>>;
  /**
   * Language for these sections. Default: interview default language.
   */
  language?: string;
  /**
   * Whether sections are revealed progressively as the user advances.
   * Only valid with sections.
   */
  progressive?: boolean;
  /**
   * Whether subsections auto-open when the parent is selected.
   * Only valid with sections.
   */
  "auto open"?: boolean;
  comment?: string;
}

/**
 * An `on change` block defines Python code to run when specific variables
 * change. Must be the only key (besides any internal keys).
 *
 * Keys are variable names; values are Python code to execute when that
 * variable changes.
 */
interface OnChangeBlock {
  "on change": Record<VariableName, PythonCode>;
  comment?: string;
}

/**
 * A `machine learning storage` block specifies the JSON file used to
 * store machine learning data for this interview.
 * Must be a file ending in .json in a package's data/sources/ folder.
 */
interface MachineLearningStorageBlock {
  "machine learning storage": string;
  comment?: string;
}

/**
 * A `translations` block specifies translation files to load.
 * Each item must be a filename ending in .xlsx, .xlf, or .xliff,
 * in a package's data/sources/ folder.
 */
interface TranslationsBlock {
  translations: string[];
  comment?: string;
}

/**
 * An `images` block defines image shortcuts for use in `decoration` fields
 * and image references throughout the interview.
 *
 * Dict form (no attribution):
 *   images:
 *     calendar: calendar.png
 *     map: map.png
 *
 * Dict form (with sets):
 *   images:
 *     calendar: { images: { calendar: calendar.png }, attribution: "..." }
 */
interface ImagesBlock {
  images: Record<string, string | { images: Record<string, string>; attribution?: string }>;
  comment?: string;
}

/**
 * An `image sets` block defines named sets of images, each with optional
 * attribution text.
 *
 * image sets:
 *   setname:
 *     images:
 *       name: filename.png
 *     attribution: "Photo by ..."
 */
interface ImageSetsBlock {
  "image sets": Record<
    string,
    {
      images:
        | Record<string, string>
        | Array<Record<string, string>>;
      attribution?: string;
    }
  >;
  comment?: string;
}

/**
 * A `def` block defines a reusable Mako template definition.
 * Referenced by `usedefs` in other blocks.
 *
 * mako: the template text(s) to define.
 * String or list of strings.
 */
interface DefBlock {
  def: string;
  mako: string | string[];
  comment?: string;
}

/**
 * An `order` block specifies the priority ordering of blocks by ID.
 * Must contain only `order` (and optionally `comment`).
 * The list items are block IDs; earlier IDs have higher priority.
 */
interface OrderBlock {
  order: string[];
  comment?: string;
}

/**
 * An `attachment options` block specifies default options for all
 * attachments in the interview.
 * Value is a dict or list of dicts.
 */
interface AttachmentOptionsBlock {
  "attachment options": AttachmentOptionSpec | AttachmentOptionSpec[];
  comment?: string;
}

interface AttachmentOptionSpec {
  "initial yaml"?: string | string[];
  "additional yaml"?: string | string[];
  "template file"?: string;
  "rtf template file"?: string;
  "docx reference file"?: string;
  metadata?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Response / action blocks
// ---------------------------------------------------------------------------

/**
 * A `response` block sends a raw HTTP response to the browser instead of
 * showing a question. Useful for API endpoints or file downloads.
 */
interface ResponseBlock extends CommonModifiers {
  /**
   * The response body. Mako string.
   */
  response?: MakoString;

  /**
   * Content type header. Mako string. Default: "text/plain; charset=utf-8".
   */
  "content type"?: MakoString;

  /**
   * HTTP response code. Integer. Default: 200.
   */
  "response code"?: number;

  /**
   * Include all interview variables as JSON. Cannot be combined with response.
   */
  all_variables?: boolean;

  /**
   * Include internal interview variables in all_variables output.
   */
  include_internal?: boolean;

  /**
   * Send a null (empty) response. Cannot be combined with response.
   */
  "null response"?: boolean;

  /**
   * Send a binary response. The value is a Python expression evaluating
   * to a bytes object. Cannot be combined with response.
   */
  binaryresponse?: PythonExpression;

  /**
   * Sleep for this many seconds before sending the response.
   * Number.
   */
  sleep?: number;
}

/**
 * A `response filename` block sends a file from the server as the response.
 */
interface ResponseFilenameBlock extends CommonModifiers {
  /**
   * The filename (or DAFile object) to send as the response.
   */
  "response filename": MakoString;

  /**
   * Content type override. Mako string.
   */
  "content type"?: MakoString;
}

/**
 * A `redirect url` block redirects the browser to a URL.
 */
interface RedirectBlock extends CommonModifiers {
  /**
   * The URL to redirect to. Mako string.
   */
  "redirect url": MakoString;
}

/**
 * A `backgroundresponse` block sends a background task response.
 * Used in conjunction with background_action().
 */
interface BackgroundResponseBlock extends CommonModifiers {
  /**
   * The response value (any Python value via PythonExpression).
   */
  backgroundresponse: unknown;
}

/**
 * An `action` block runs a background action and returns its response.
 * The value is the action identifier.
 */
interface ActionBlock extends CommonModifiers {
  action: string;
}

/**
 * A `command` block performs a special navigation action.
 * These replace the need to use the command() function in code.
 */
interface CommandBlock extends CommonModifiers {
  command:
    | "exit"
    | "logout"
    | "exit_logout"
    | "continue"
    | "restart"
    | "leave"
    | "refresh"
    | "signin"
    | "register"
    | "new_session"
    | "interview_exit"
    | "wait";
}

// ---------------------------------------------------------------------------
// Default role (used in multi-user interviews)
// ---------------------------------------------------------------------------

/**
 * A `default role` block can be standalone (not added to question queue)
 * or combined with a `code` block to set the default role conditionally.
 */
interface DefaultRoleBlock {
  "default role": string | string[];
  /**
   * If present, combines default role with code execution.
   * The code is run initially to set the role.
   */
  code?: PythonCode;
  initial?: BoolOrExpr;
  comment?: string;
}

// ---------------------------------------------------------------------------
// Require block (deprecated/advanced)
// ---------------------------------------------------------------------------

/**
 * A `require` block specifies a list of Python expressions that must all
 * be true for the interview to proceed. If any is false, the `orelse`
 * block is shown instead.
 * This is a legacy feature. Using `code` blocks with `command()` is preferred.
 */
interface RequireBlock {
  require: PythonExpression[];
  orelse: Omit<AnyQuestionBlock, "require">;
}

// ---------------------------------------------------------------------------
// Generic object modifier
// ---------------------------------------------------------------------------

/**
 * The `generic object` modifier makes a block apply generically to any
 * object of the specified class. The placeholder `x` refers to the object.
 * Index variables `i`, `j`, `k`, etc. refer to list indices.
 *
 * Example:
 *   generic object: Individual
 *   question: What is ${ x }'s first name?
 *   fields:
 *     - First name: x.name.first
 */
type GenericObjectModifier =
  | { "generic object": string } // Apply to any object of this class
  | { "generic list object": string }; // Apply to objects in a list of this class

// ---------------------------------------------------------------------------
// Standalone comment block
// ---------------------------------------------------------------------------

/**
 * A block containing only a `comment` key is completely ignored by
 * docassemble. It is not added to the question queue and has no effect.
 */
interface CommentOnlyBlock {
  comment: string;
}

// ---------------------------------------------------------------------------
// Union type of all block types
// ---------------------------------------------------------------------------

/**
 * The complete union of all valid docassemble block types.
 *
 * A YAML document (separated by ---) must be one of these block types.
 * Docassemble determines the block type by examining which keys are present.
 *
 * Key detection order (approximate, from parse.py):
 *   1. features        -> FeaturesBlock (not queued)
 *   2. default language -> DefaultLanguageBlock (not queued)
 *   3. on change       -> OnChangeBlock (not queued)
 *   4. sections        -> SectionsBlock (not queued)
 *   5. machine learning storage -> MachineLearningStorageBlock (not queued)
 *   6. translations    -> TranslationsBlock (not queued)
 *   7. metadata        -> MetadataBlock (not queued)
 *   8. modules         -> ModulesBlock (queued as 'modules' type)
 *   9. reset           -> ResetBlock (queued as 'reset' type)
 *  10. imports         -> ImportsBlock (queued as 'imports' type)
 *  11. terms (standalone) -> StandaloneTermsBlock (not queued)
 *  12. auto terms (standalone) -> StandaloneAutoTermsBlock (not queued)
 *  13. default role    -> DefaultRoleBlock (not queued unless + code)
 *  14. role            -> part of any question block
 *  15. include         -> IncludeBlock (not queued; included immediately)
 *  16. image sets      -> ImageSetsBlock (not queued)
 *  17. images          -> ImagesBlock (not queued)
 *  18. def             -> DefBlock (not queued)
 *  19. interview help  -> InterviewHelpBlock (not queued)
 *  20. default screen parts -> DefaultScreenPartsBlock (not queued)
 *  21. default validation messages -> DefaultValidationMessagesBlock (not queued)
 *  22. objects from file -> ObjectsFromFileBlock
 *  23. data + variable name -> DataBlock
 *  24. data from code + variable name -> DataFromCodeBlock
 *  25. objects         -> ObjectsBlock
 *  26. order           -> OrderBlock (not queued)
 *  27. attachment options -> AttachmentOptionsBlock (not queued)
 *  28. attachment/attachments -> AttachmentBlock (queued as 'attachments')
 *  29. response        -> ResponseBlock
 *  30. binaryresponse  -> ResponseBlock
 *  31. all_variables   -> ResponseBlock
 *  32. response filename -> ResponseFilenameBlock
 *  33. redirect url    -> RedirectBlock
 *  34. null response   -> ResponseBlock
 *  35. action          -> ActionBlock
 *  36. backgroundresponse -> BackgroundResponseBlock
 *  37. command         -> CommandBlock
 *  38. table + rows + columns -> TableBlock
 *  39. template + content -> TemplateBlock
 *  40. code            -> CodeBlock
 *  41. yesno           -> YesNoBlock
 *  42. noyes           -> NoYesBlock
 *  43. yesnomaybe      -> YesNoMaybeBlock
 *  44. noyesmaybe      -> NoYesMaybeBlock
 *  45. choices         -> ChoicesBlock
 *  46. buttons         -> ButtonsBlock
 *  47. dropdown        -> DropdownBlock
 *  48. combobox        -> ComboboxBlock
 *  49. signature       -> SignatureBlock
 *  50. review          -> ReviewBlock
 *  51. fields          -> FieldsBlock
 *  52. continue button field -> ContinueButtonFieldBlock
 *  53. event           -> EventBlock
 *  54. question (only) -> "dead end" question (no fields)
 *  55. comment (only)  -> CommentOnlyBlock (not queued)
 *  56. require         -> RequireBlock
 *
 * Note: Many blocks can coexist (e.g., `question` + `fields` + `attachment`),
 * but only one "primary input directive" is allowed per block. The mutually
 * exclusive set is: yesno, noyes, yesnomaybe, noyesmaybe, fields, buttons,
 * choices, dropdown, combobox, signature, review. Exactly one of these may
 * appear in a block that contains `question`.
 */
type AnyBlock =
  // Non-question blocks (not added to question queue):
  | FeaturesBlock
  | DefaultLanguageBlock
  | IncludeBlock
  | ModulesBlock
  | ImportsBlock
  | ResetBlock
  | MetadataBlock
  | ImageSetsBlock
  | ImagesBlock
  | DefBlock
  | InterviewHelpBlock
  | DefaultScreenPartsBlock
  | DefaultValidationMessagesBlock
  | SectionsBlock
  | OnChangeBlock
  | MachineLearningStorageBlock
  | TranslationsBlock
  | StandaloneTermsBlock
  | StandaloneAutoTermsBlock
  | DefaultRoleBlock
  | AttachmentOptionsBlock
  | OrderBlock
  | CommentOnlyBlock
  // Question blocks (added to question queue):
  | YesNoBlock
  | NoYesBlock
  | YesNoMaybeBlock
  | NoYesMaybeBlock
  | ButtonsBlock
  | ChoicesBlock
  | DropdownBlock
  | ComboboxBlock
  | SignatureBlock
  | ContinueButtonFieldBlock
  | FieldsBlock
  | ReviewBlock
  | EventBlock
  | CodeBlock
  | TemplateBlock
  | TableBlock
  | ObjectsBlock
  | ObjectsFromFileBlock
  | DataBlock
  | DataFromCodeBlock
  | AttachmentBlock
  | ResponseBlock
  | ResponseFilenameBlock
  | RedirectBlock
  | BackgroundResponseBlock
  | ActionBlock
  | CommandBlock
  | RequireBlock;

// Convenience alias for blocks that produce a question screen:
type AnyQuestionBlock =
  | YesNoBlock
  | NoYesBlock
  | YesNoMaybeBlock
  | NoYesMaybeBlock
  | ButtonsBlock
  | ChoicesBlock
  | DropdownBlock
  | ComboboxBlock
  | SignatureBlock
  | ContinueButtonFieldBlock
  | FieldsBlock
  | ReviewBlock
  | EventBlock
  | AttachmentBlock;

/**
 * A complete interview file is a list of blocks (YAML documents separated by ---).
 */
type InterviewFile = AnyBlock[];

// ---------------------------------------------------------------------------
// Additional notes on key behaviors and constraints
// ---------------------------------------------------------------------------

/*
 * KEY BEHAVIORS DERIVED FROM parse.py
 * =====================================
 *
 * 1. KEY NORMALIZATION
 *    All top-level keys are lowercased before processing. So `Question`,
 *    `QUESTION`, and `question` are all treated as `question`.
 *
 * 2. MUTUAL EXCLUSIVITY
 *    At most one of: yesno, noyes, yesnomaybe, noyesmaybe, fields, buttons,
 *    choices, dropdown, combobox, signature, review
 *    may appear in a single block. If more than one is present, a DASourceError
 *    is raised.
 *
 * 3. QUESTION REQUIRED WITH INPUT DIRECTIVES
 *    If any of the above input directives are present, `question` MUST also
 *    be present, unless `event` is used (event can appear without question).
 *
 * 4. QUESTION + CODE MUTUAL EXCLUSION
 *    A block cannot have both `question` and `code`. They are mutually exclusive.
 *
 * 5. MANDATORY vs INITIAL
 *    `mandatory` and `initial` cannot appear in the same block.
 *    `initial` can only be used with `code` blocks (raises error otherwise).
 *    `mandatory` can be used with: question, code, objects, attachment/attachments,
 *    data, data from code, objects from file.
 *
 * 6. CONTINUE BUTTON LABEL RESTRICTIONS
 *    `continue button label` cannot be used with yesno, noyes, yesnomaybe,
 *    noyesmaybe, or buttons question types.
 *    `resume button label` can only be used with review blocks.
 *    `skip undefined` can only be used with review blocks.
 *
 * 7. FIELD KEY IN DIFFERENT CONTEXTS
 *    In a buttons/choices/dropdown/combobox block: `field` is the variable to set.
 *    In a fields block: `field` is an ALIAS for `continue button field` when
 *    used without any of the multiple-choice directives.
 *    In a signature block: the `signature` key is the variable name (not `field`).
 *
 * 8. SECTION MODIFIER
 *    `section` can only appear on question blocks (requires `question`).
 *
 * 9. CSS CLASS AND TABLE CSS CLASS
 *    Both require `question` to be present in the same block.
 *
 * 10. TABLE BLOCK VALIDATION
 *     A table block requires ALL THREE of: `table`, `rows`, `columns`.
 *     Missing any one raises a DASourceError.
 *
 * 11. DATA BLOCK REQUIREMENTS
 *     Both `data` and `data from code` require `variable name` to be present.
 *
 * 12. ATTACHMENT FIELDS
 *     `fields` in an attachment can only be used with `pdf template file` or
 *     `docx template file`. Using both pdf and docx template files is an error.
 *
 * 13. ON CHANGE BLOCK
 *     An `on change` block must contain ONLY the `on change` key (no other keys).
 *
 * 14. ORDER BLOCK
 *     An `order` block must not be combined with question, code, attachment,
 *     attachments, or template.
 *
 * 15. LIST COLLECT
 *     `list collect` can only appear with a `fields` block.
 *
 * 16. GENERIC OBJECT MODIFIER
 *     The `generic object` and `generic list object` modifiers make a block
 *     respond to attribute lookups on objects of the named class.
 *     The placeholder variable `x` refers to the current object.
 *     Index variables `i`, `j`, `k`, `l`, `m`, `n` refer to list indices.
 *
 * 17. USEDEFS
 *     `usedefs` refers to `def` block names. All referenced `def` blocks
 *     must be defined BEFORE they are used.
 *
 * 18. REQUIRE BLOCK
 *     A `require` block requires an `orelse` block (a nested block dict).
 *     The `require` list contains Python expressions; if any is false,
 *     the `orelse` block is used. This is a legacy feature.
 *
 * 19. OBJECT LABELER / HELP GENERATOR / IMAGE GENERATOR
 *     These field modifiers are only valid with object datatypes.
 *     They must be Python expressions.
 *
 * 20. REVIEW BLOCK DATA
 *     In a review block, the `field` and `fields` keys have different
 *     semantics than in a `fields` block. The values are variables to
 *     re-visit (not variables to set). The label is what the user sees
 *     in the review list.
 *
 * VARIABLE NAME RULES
 * ====================
 * Variable names must match: [^\d][A-Za-z0-9_]*
 * They can include:
 *   - Attribute access: user.name.first
 *   - Integer index: items[0], items[i]
 *   - String index: data['key']
 * They cannot:
 *   - Start with a digit
 *   - Contain spaces
 *   - Contain punctuation other than `.`, `[`, `]`, `_`
 *   - Begin with `__` (double underscore attributes)
 *   - Be Python reserved words (for, while, in, etc.)
 *
 * MAKO TEMPLATE SYNTAX
 * ======================
 * Mako is used in most string fields. Key syntax:
 *   ${variable}          - insert variable value
 *   ${expr}              - insert expression result
 *   % if condition:      - conditional block start
 *   % elif condition:    - else-if
 *   % else:              - else
 *   % endif              - end conditional
 *   % for var in list:   - loop start
 *   % endfor             - loop end
 *   <%doc>text</%doc>    - documentation (not rendered)
 *   <%def name="name()"> - define reusable block
 *   <%include .../>      - include another template
 *
 * PACKAGE REFERENCES
 * ===================
 * Files from other packages are referenced as:
 *   "docassemble.packagename:data/questions/file.yml"
 *   "docassemble.packagename:data/templates/file.docx"
 *   "docassemble.packagename:data/static/image.png"
 * Files in the current package can be referenced by name alone:
 *   "file.yml"
 *
 * DOCX TEMPLATE JINJA2 SYNTAX
 * =============================
 * DOCX templates use Jinja2 (not Mako):
 *   {{ variable }}       - insert variable value
 *   {% if condition %}   - conditional
 *   {% endif %}
 *   {% for item in list %} - loop
 *   {% endfor %}
 *   {%p ... %}           - paragraph-level control
 *   {%tr ... %}          - table row level control
 *   {%tc ... %}          - table cell level control
 *
 * TRANSLATION FILES
 * ==================
 * Translation files (.xlsx, .xlf, .xliff) live in data/sources/ of a package.
 * XLIFF versions 1.2 and 2.0 are supported.
 */

export type {
  // Primitive types
  MakoString,
  PythonExpression,
  PythonCode,
  VariableName,
  BootstrapColor,
  MakoOrCode,
  BoolOrExpr,

  // Modifiers and shared structures
  CommonModifiers,
  ActionButtonSpec,
  ScreenTextFields,
  QuestionHelpSpec,
  TermItem,
  ShowIfSpec,
  GridSpec,
  ItemGridSpec,
  ListCollectSpec,

  // Choice structures
  ChoiceItem,
  ChoiceItemDict,
  ChoiceList,

  // Field structures
  FieldDatatype,
  FieldInputType,
  FieldSpec,
  ReviewFieldSpec,
  ReviewActionSpec,

  // Question block types
  YesNoBlock,
  NoYesBlock,
  YesNoMaybeBlock,
  NoYesMaybeBlock,
  ButtonsBlock,
  ChoicesBlock,
  DropdownBlock,
  ComboboxBlock,
  SignatureBlock,
  ContinueButtonFieldBlock,
  FieldsBlock,
  ReviewBlock,
  EventBlock,
  CodeBlock,
  TemplateBlock,
  TableBlock,
  ObjectsBlock,
  ObjectsFromFileBlock,
  DataBlock,
  DataFromCodeBlock,
  AttachmentBlock,
  AttachmentSpec,
  AttachmentOptionSpec,

  // Response block types
  ResponseBlock,
  ResponseFilenameBlock,
  RedirectBlock,
  BackgroundResponseBlock,
  ActionBlock,
  CommandBlock,
  RequireBlock,

  // Non-question blocks
  FeaturesBlock,
  FeaturesSpec,
  MetadataBlock,
  MetadataSpec,
  DefaultLanguageBlock,
  IncludeBlock,
  ModulesBlock,
  ImportsBlock,
  ResetBlock,
  ImageSetsBlock,
  ImagesBlock,
  DefBlock,
  InterviewHelpBlock,
  InterviewHelpSpec,
  DefaultScreenPartsBlock,
  DefaultValidationMessagesBlock,
  SectionsBlock,
  OnChangeBlock,
  MachineLearningStorageBlock,
  TranslationsBlock,
  StandaloneTermsBlock,
  StandaloneAutoTermsBlock,
  DefaultRoleBlock,
  AttachmentOptionsBlock,
  OrderBlock,
  CommentOnlyBlock,

  // Top-level union types
  AnyBlock,
  AnyQuestionBlock,
  InterviewFile,
};
