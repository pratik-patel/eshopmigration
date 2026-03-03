---
name: webforms-discovery-ui-primitives
description: >
  Extracts evidence primitives and UI inventory primitives from ASP.NET Web Forms (System.Web) projects.
  Supports seam discovery (entrypoints, data access, tx scopes, dep edges) and UI inventory (pages/controls,
  server controls, validators, event wiring, navigation).
  Use with $ARGUMENTS specifying mode:
    - mode=discovery root=<path>
    - mode=ui root=<path>
user-invocable: false
allowed-tools: Read, Glob, Grep
disable-model-invocation: true
---

# ASP.NET Web Forms (System.Web) Discovery + UI Primitives

Output ONLY JSON. Do not write prose.

## Input
$ARGUMENTS must include:
- `mode=discovery` or `mode=ui`
- `root=<path>` absolute or relative root path

Example:
- `mode=discovery root=../MyWebFormsApp`
- `mode=ui root=../MyWebFormsApp`

If required arguments are missing, output JSON with empty arrays and a notes[] entry explaining what is missing.

---

# Common scanning rules

1) Discover candidate Web Forms artifacts under root:
- Pages: `**/*.aspx`
- User controls: `**/*.ascx`
- Master pages: `**/*.master`
- Code-behind: `*.aspx.cs`, `*.ascx.cs`, `*.master.cs`
- App start: `Global.asax` / `Global.asax.cs`
- Config: `web.config` (and transforms), `App_Start/**` (if present)
- HTTP Handlers/Modules: `IHttpHandler`, `IHttpModule` implementations
- Services: `*.asmx` (legacy SOAP), WCF `.svc` (sometimes in System.Web apps)

2) Ignore build output directories if possible:
- `**/bin/**`, `**/obj/**`, `**/.git/**`, `**/packages/**` (NuGet)

3) Evidence strings:
Every extracted item MUST include an `evidence` field describing the matched pattern and where it came from.

Confidence:
- high: direct extraction from ASPX markup or obvious code-behind signature
- medium: extracted from code patterns with some ambiguity
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

## 1) Entrypoints (delivery surfaces)
### A) Pages and user controls as UI entrypoints
- Each `.aspx` is a UI entry surface (Page).
- Each `.ascx` is a UI surface component (UserControl) and may be an entry to workflows via events.

Emit entrypoints:
- kind: "ui"
- subkind: "page" for .aspx, "user_control" for .ascx, "master_page" for .master (optional)
- symbol: page/control class name if discoverable, else file-based symbol (e.g., "Page:<path>")
- file: markup file path

How to find class name:
- In ASPX/ASCX directives:
  - `<%@ Page ... Inherits="Namespace.Type" ... %>`
  - `<%@ Control ... Inherits="Namespace.Type" ... %>`
Use Inherits value as symbol when present.

### B) App-level entrypoints
- `Global.asax` / `Global.asax.cs` methods: `Application_Start`, `Session_Start`, `Application_BeginRequest`, `Application_Error`
Emit:
- kind: "app"
- subkind: "global_asax"
- symbol: "Global.Application_Start" etc.

### C) HTTP Handlers/Modules
Detect in `.cs`:
- `class .* : IHttpHandler`
- `class .* : IHttpModule`
Emit:
- kind: "http"
- subkind: "handler" | "module"
- symbol: type name

### D) ASMX / SVC services (if present)
- `.asmx` / `.svc` as service endpoints
Emit:
- kind: "api"
- subkind: "asmx" | "svc"
- symbol: file-based if class not found

## 2) Data access (reads/writes)
Detect ADO.NET usage (commonly in Web Forms):
- `SqlConnection`, `SqlCommand`, `SqlDataReader`, `SqlDataAdapter`
- `ExecuteReader`, `ExecuteScalar`, `ExecuteNonQuery`
- `CommandType.StoredProcedure`
Detect EF usage (if present):
- `DbContext`, `DbSet<>`, `SaveChanges`, LINQ query patterns
Detect common connection string patterns:
- `ConfigurationManager.ConnectionStrings[...]`
- `<connectionStrings>` section in web.config

Heuristics:
- ExecuteNonQuery => write (high/medium)
- SaveChanges => write (medium)
- ExecuteReader/Scalar => read (medium)
If SQL text literals exist, attempt to extract:
- table: from `FROM <X>`, `UPDATE <X>`, `INSERT INTO <X>`
- stored proc: if `CommandType.StoredProcedure` and `CommandText = "ProcName"`

Emit data_access item:
- kind: "read"|"write"
- target: "table:<X>" | "sp:<Proc>" | "db:unknown"
- symbol: best effort enclosing method/type
- file, evidence, confidence

## 3) Transaction scope hints
Detect:
- `TransactionScope`
- `BeginTransaction` / `Commit` / `Rollback`
- `DbContext.Database.BeginTransaction`
Emit tx_scopes with kind "transaction" and evidence.

## 4) Dependency edges (coupling signals)
Emit dep_edges for:
- instantiation: `new <Type>(`
- static/global access: `<Type>.Current`, `<Type>.Instance`, `HttpContext.Current`, `HttpRuntime.Cache`, `Application[...]`, `Session[...]`
- reflection/dynamic: `Type.GetType`, `Activator.CreateInstance`, `InvokeMember`
- event subscription: `+=` to events
- cross-cutting web forms patterns:
  - `Server.Transfer`, `Response.Redirect` (navigation edge)
For dep_edges include:
- from_symbol, to_symbol (best effort), edge_type, evidence, file(s), confidence

## 5) Runtime signals (optional)
Detect hints for:
- correlation ids / trace ids in logs
- Application Insights / telemetry config
- `ActivitySource`, `DiagnosticSource` usage
Emit runtime_signals if found.

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

## 1) Screens
Each `.aspx` is a screen.
Each `.ascx` is a reusable UI component.
Optionally include `.master` as a shared layout.

For each screen, emit:
- type_name: class from Inherits, else "Page:<file>"
- framework: "webforms"
- kind: "page" | "user_control" | "master_page"
- file: markup file path
- designer_or_xaml: code-behind path if exists else "MISSING"
- title: extract from `<title>` in HTML head when present else UNKNOWN
- confidence_title: high if literal title found else low

## 2) Controls (server controls + important HTML inputs)
Extract control inventory from markup (best-effort):
- ASP.NET server controls with `runat="server"` and `ID="..."`
Examples:
- `<asp:TextBox ... ID="..." runat="server" />`
- `<asp:Button ... ID="..." runat="server" Text="..." OnClick="Handler" />`
- `<asp:DropDownList ... OnSelectedIndexChanged="..." AutoPostBack="true" />`
- `<asp:GridView ... OnRowCommand="..." />`
- `<asp:Repeater ... />`, `<asp:DataList ... />`

Also capture validators:
- `<asp:RequiredFieldValidator ... />`
- `<asp:RegularExpressionValidator ... />`
- `<asp:RangeValidator ... />`
Record them as controls with type "Validator" and capture their error message / pattern where literal.

For each control emit:
- name (ID)
- type (e.g., TextBox, Button, GridView, RequiredFieldValidator)
- text/label: from `Text="..."`, `HeaderText="..."`, `ErrorMessage="..."` when present, else UNKNOWN
- evidence + confidence

## 3) Grids / tables
Detect common data-bound controls:
- GridView, DetailsView, FormView, Repeater, DataList
Extract:
- column headers when explicitly declared:
  - `<asp:BoundField HeaderText="..." DataField="..." />`
  - `<asp:TemplateField HeaderText="..." />`
Set:
- dynamic_columns true if columns not declared (AutoGenerateColumns="true" or absent)
- unknown_remaining true if template fields without obvious header

## 4) Actions (wired events)
From markup, capture On* handler attributes:
- OnClick, OnCommand, OnRowCommand, OnSelectedIndexChanged, OnTextChanged, OnItemCommand, OnPageIndexChanging, OnSorting
Emit actions[]:
- control, event, handler, evidence, confidence=high

Also capture Page lifecycle handlers from code-behind if present:
- `Page_Load`, `Page_Init`, `Page_PreRender`
Emit as actions with control="(page)" event="Page_Load" etc.

## 5) Navigation / child screens
Detect navigation patterns:
- `<a href="...aspx">` links
- `Response.Redirect("...")`
- `Server.Transfer("...")`
Emit child_screens entries:
- child_type: target page path
- opened_via: handler if known else UNKNOWN
- modal: "unknown" (web is navigational)
- evidence + confidence

## 6) Unknown/dynamic UI
If markup uses heavy dynamic controls:
- `PlaceHolder.Controls.Add(...)`
- `LoadControl(...)`
- `FindControl(...)` patterns in code-behind
Add to unknowns:
- "dynamic controls created at runtime via PlaceHolder/LoadControl/FindControl"

### Notes
If you cannot resolve code-behind class names or handlers, add a notes[] entry and use UNKNOWN.

Return ONLY JSON.
