---
name: winforms-discovery-ui-primitives
description: >
  Extracts evidence primitives and UI inventory primitives from Microsoft WinForms (.NET) projects.
  Supports seam discovery (entrypoints, data access, tx scopes, dep edges) and UI inventory (screens/controls,
  labels, grids, event wiring, child screen launches).
  Use with $ARGUMENTS specifying mode:
    - mode=discovery root=<path>
    - mode=ui root=<path>
user-invocable: false
allowed-tools: Read, Glob, Grep
disable-model-invocation: true
---

# WinForms (System.Windows.Forms) Discovery + UI Primitives

Output ONLY JSON. No prose.

## Input
$ARGUMENTS must include:
- `mode=discovery` or `mode=ui`
- `root=<path>` absolute or relative root path

Examples:
- `mode=discovery root=../MyWinFormsApp`
- `mode=ui root=../MyWinFormsApp`

If required arguments are missing, output JSON with empty arrays and a notes[] entry explaining what is missing.

---

# Common scanning rules

1) Discover candidate WinForms artifacts under root:
- C# sources: `**/*.cs`
- Projects: `**/*.csproj`
- Designer files: `**/*.Designer.cs`

2) Ignore build output directories if possible:
- `**/bin/**`, `**/obj/**`, `**/.git/**`, `**/packages/**`

3) Evidence strings:
Every extracted item MUST include an `evidence` field describing the matched pattern and where it came from.

Confidence:
- high: direct extraction from Designer.cs literal values or obvious signatures
- medium: extracted from clear code patterns with minor ambiguity
- low: naming-only inference (avoid; prefer UNKNOWN)

---

# Mode: discovery

When mode=discovery, output this JSON shape:

```json
{
  "entrypoints": [],
  "data_access": [],
  "tx_scopes": [],
  "dep_edges": [],
  "runtime_signals": [],
  "notes": []
}
```

## Discovery extraction rules

### 1) Entrypoints (delivery surfaces)

#### A) Application entry
Detect:
- `static void Main(` (Program.cs or any .cs)
- `Application.Run(`

Emit entrypoint:
- kind: "ui"
- subkind: "app_main"
- symbol: best effort (e.g., "Program.Main")
- file: where found
- evidence, confidence

#### B) Forms and UserControls
Detect types inheriting:
- `Form`
- `UserControl`
Also allow fully-qualified base types:
- `System.Windows.Forms.Form`
- `System.Windows.Forms.UserControl`

Patterns:
- `class <Name> : Form`
- `class <Name> : UserControl`

Emit entrypoint:
- kind: "ui"
- subkind: "form" | "user_control"
- symbol: "<TypeName>"
- file: source file
- evidence, confidence="high"

#### C) UI event triggers (workflow triggers)
Detect handler method names and/or wiring:
- Common suffix patterns: `_Click`, `_Load`, `_Shown`, `_Closing`, `_FormClosing`,
  `_SelectedIndexChanged`, `_TextChanged`, `_CheckedChanged`,
  `_CellValueChanged`, `_CellContentClick`,
  `_KeyDown`, `_KeyPress`, `_MouseDown`, `_MouseMove`, `_Tick`
- Wiring patterns:
  - `this.<control>.<Event> += new System.EventHandler(this.<Handler>);`
  - `this.<control>.<Event> += this.<Handler>;`
Emit entrypoint:
- kind: "ui"
- subkind: "event_handler"
- symbol: "<TypeName>.<MethodName>" (best effort)
- file, evidence
- confidence: high if wired in Designer.cs, else medium

Note: event handlers are NOT seams; they are workflow triggers used for clustering.

---

### 2) Data access (reads/writes)

Detect ADO.NET:
- `SqlConnection`, `SqlCommand`, `SqlDataReader`, `SqlDataAdapter`
- `ExecuteReader`, `ExecuteScalar`, `ExecuteNonQuery`
- `CommandType.StoredProcedure`
- `ConfigurationManager.ConnectionStrings`

Detect EF (EF6/EF Core):
- `DbContext`, `DbSet<>`, `SaveChanges`, `SaveChangesAsync`
- LINQ queries: `.Where(` `.Select(` `.ToList(` `.FirstOrDefault(`
- Raw SQL: `FromSqlRaw`, `SqlQuery`, `ExecuteSqlRaw`

Heuristics:
- `ExecuteNonQuery` => write (medium/high)
- `SaveChanges*` => write (medium)
- `ExecuteReader/Scalar` => read (medium)

Targets (best effort; avoid hallucination):
- If literal SQL contains `FROM <X>` => `table:<X>` (low/medium)
- If literal SQL contains `UPDATE <X>` / `INSERT INTO <X>` / `DELETE FROM <X>` => `table:<X>` (low/medium)
- If stored proc name literal exists => `sp:<name>` (medium)
Otherwise => `db:unknown`

Emit data_access item:
- kind: "read" | "write"
- target: "table:<X>" | "sp:<Proc>" | "db:unknown"
- symbol: best effort enclosing type/method
- file, evidence, confidence

---

### 3) Transaction scope hints
Detect:
- `TransactionScope`
- `BeginTransaction(` / `Commit(` / `Rollback(`
- `DbContext.Database.BeginTransaction(`

Emit tx_scopes:
- kind: "transaction"
- symbol: enclosing type/method (best effort)
- file, evidence, confidence

---

### 4) Dependency edges (coupling signals)

Emit dep_edges for:

#### A) Instantiation
Pattern: `new <TypeName>(`
- edge_type: "instantiates"
- from_symbol: enclosing type/method
- to_symbol: instantiated type
- evidence, confidence

#### B) Static/global/singleton access
Detect:
- `<Type>.Current`
- `<Type>.Instance`
- static classes with mutable state (best effort)
Emit:
- edge_type: "static_global"
- from_symbol / to_symbol best effort
- confidence medium unless clear singleton

#### C) Event subscription
Detect: `+=` to events in code-behind or Designer
Emit:
- edge_type: "subscribes_event"

#### D) External dependencies (interop)
Detect:
- `[DllImport]`, `[ComImport]`, `Marshal.`, `Interop.`
Emit:
- edge_type: "external_dependency"
- to_symbol: "PInvoke" | "COM" | "Interop"

---

### 5) Runtime signals (optional)
Detect hints for:
- `ActivitySource`, `DiagnosticSource`
- correlation IDs in logs (TraceId/CorrelationId)
- Application Insights config usage
Emit runtime_signals if found; else empty.

Return ONLY JSON.

---

# Mode: ui

When mode=ui, output this JSON shape:

```json
{
  "screens": [],
  "notes": []
}
```

## UI inventory extraction rules

Each `screen` must include:
- type_name
- framework: "winforms"
- kind: "form" | "user_control"
- file: code-behind file
- designer_or_xaml: Designer.cs path or "MISSING"
- title: literal title or "UNKNOWN"
- confidence_title: "high|medium|low"
- controls[], grids[], actions[], child_screens[], unknowns[]

### 1) Find screens
Find types inheriting `Form` or `UserControl` (same rules as discovery).
For each:
- record file
- locate `<TypeName>.Designer.cs` in same folder (best effort)

### 2) Extract from Designer.cs (highest confidence)
If Designer exists, parse `InitializeComponent()` via Grep patterns.

A) Controls
- `this.<name> = new System.Windows.Forms.<Type>();`
Record `controls[]` name/type.

B) Text/labels
Capture:
- `this.<name>.Text = "..."` (and `this.Text = "..."` for Form title)
- common label-like fields: `.HeaderText = "..."`, `.ToolTipText = "..."`
Update `controls[]` text when matched.

C) Event wiring
Capture:
- `this.<control>.<Event> += ... this.<Handler>`
Emit `actions[]`:
- control, event, handler, evidence, confidence="high"

### 3) Extract from code-behind (medium confidence)
A) Child form launches
Patterns:
- `new <Child>(...).ShowDialog()`
- `new <Child>(...).Show()`
Emit `child_screens[]` with modal/modeless.

B) Grid columns
Detect:
- DataGridView headers (`HeaderText`, `Columns.Add(...,"Header")`)
- SourceGrid headers (`new SourceGrid.Cells.ColumnHeader("Header")`)
Set:
- dynamic_columns=true if built in loops/metadata
- unknown_remaining=true when incomplete
Emit `grids[]`.

### 4) Unknown/dynamic UI
If evidence found:
- columns built in loops without literals
- dynamic control creation outside Designer
- reflection-based UI
Add to `unknowns[]` with evidence strings.

Return ONLY JSON.

