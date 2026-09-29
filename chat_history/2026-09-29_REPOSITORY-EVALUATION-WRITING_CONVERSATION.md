# Repository evaluation writing

- **Source URL:** [https://chatgpt.com/share/6abbf57a-3f24-83e8-beaa-ef2b95f0593f](https://chatgpt.com/share/6abbf57a-3f24-83e8-beaa-ef2b95f0593f)
- **Archived Date:** 2026-09-29
- **Total Turns:** 48

---

## Turn 1

### User

[Aaradhya-Dev-Tamrakar/md2pdf-desktop](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop)  eval this repo

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

# Repository Evaluation: `md2pdf-desktop`

<text color="secondary" size="sm">Reviewed September 29, 2026 · Public GitHub repository · Architecture, implementation, integration, and portfolio value</text>

**My overall assessment: this is a substantive engineering utility, not merely a Markdown-to-PDF script.** Its most interesting aspect is the combination of multiple document-rendering backends, a desktop interface, and an MCP server that lets AI coding agents invoke the same conversion capability.

Repository: [Aaradhya-Dev-Tamrakar/md2pdf-desktop](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop)

I inspected the README, shared conversion core, MCP server, dependency declarations, repository structure, and recent commit history. This is a source-level review; I have not run the application or verified the generated PDFs on your machine.

## 1. Evaluation at a glance

<box border radius="xl" padding={4} gap={3}>
  <row align="center" justify="between">
    <box gap={1}>
      <title size="xl">7.5/10</title>
      <text color="secondary" size="sm">Provisional engineering assessment</text>
    </box>
    <badge color="success">Useful real-world project</badge>
  </row>
  <divider color="subtle"/>
  <text color="secondary" size="sm">These are my qualitative review scores, not benchmark results or test coverage measurements.</text>
  <box gap={3}>
    {#each [{name:"Architecture and decomposition",score:8.0},{name:"Feature breadth",score:8.5},{name:"Integration potential",score:8.5},{name:"Documentation and usability",score:7.5},{name:"Reliability evidence",score:5.0},{name:"Distribution and portability",score:5.5}] as item}
      <box gap={1}>
        <row align="center" justify="between">
          <text>{item.name}</text>
          <title size="sm" color="default">{item.score.toFixed(1)}/10</title>
        </row>
        <box background="surface-tertiary" radius="full" height="6px" clip>
          <box background={item.score >= 8 ? "success-solid" : item.score >= 7 ? "info-solid" : "surface-inverted"} radius="full" height="6px" width={`${item.score*10}%`}/>
        </box>
      </box>
    {/each}
  </box>
</box>

The distinction that matters most is this: **the feature and architecture ambitions are ahead of the publicly demonstrated reliability.** That is fixable, and it is where I would concentrate the next engineering effort.

---

### Assistant

## 2. What you actually built

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="layers" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **A shared conversion engine**

      <text color="secondary" size="sm">`md2pdf/core.py`</text>

      The central module contains the rendering pipelines, dependency detection, Markdown preprocessing, and styling. Keeping this logic outside both the GUI and MCP server reduces duplication and gives the project a reusable core.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="file-text" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Multiple rendering backends**

      <text color="secondary" size="sm">`md2pdf/core.py`</text>

      - Sidebar: Pandoc, Chromium, KaTeX, and Mermaid.js.
      - LaTeX: Pandoc, `pdflatex`, and a custom LaTeX template.
      - Simple: Pandoc and `wkhtmltopdf`.
      - Auto: content detection to select an appropriate backend.

      This is more meaningful than wrapping one converter with a GUI because the rendering engines have different capabilities and dependencies.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="monitor" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Desktop Studio**

      <text color="secondary" size="sm">`md2pdf_app.py`</text>

      A Tkinter application with a document editor, toolchain status indicators, document metrics, file operations, and conversion controls. This makes the project usable as a standalone tool rather than only a developer library.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="workflow" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **MCP integration**

      <text color="secondary" size="sm">`mcp_server/server.py`</text>

      Exposes conversion, rendering-mode detection, and dependency-checking capabilities to compatible AI clients. This turns the converter into an operation that can be composed into automated documentation workflows.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="shield-check" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Development synchronization**

      <text color="secondary" size="sm">`sync.ps1`</text>

      Includes Git synchronization, secret scanning, and toolchain checks. This is a useful attempt to formalize development operations, although the existence of those checks does not by itself establish their effectiveness.
    </box>
  </row>
</box>

The repository's [README](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/README.md) documents these capabilities. The important architectural choice is the separation between the shared conversion core and its different user-facing entry points.

## 3. The strongest engineering decisions

### A. You designed for more than one interaction model

A user can convert a document through the desktop application, while an AI agent can request a conversion through MCP. Both are intended to use the same underlying engine.

That is a meaningful design pattern:

<box border radius="lg" padding={3} align="center" gap={2}>
  <box background="surface-secondary" radius="md" padding={3} width="100%" align="center">
    **Desktop GUI · MCP client**
  </box>
  <icon name="arrow-down" size="lg" color="secondary"/>
  <box border radius="md" padding={3} width="100%" align="center">
    **Shared conversion API**
  </box>
  <icon name="arrow-down" size="lg" color="secondary"/>
  <grid columns={3} gap={2}>
    <grid-item>
      <box background="surface" border radius="md" padding={2} align="center" gap={1}>
        <icon name="file-code" size="lg"/>
        <text weight="medium" textAlign="center" size="sm">Chromium</text>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface" border radius="md" padding={2} align="center" gap={1}>
        <icon name="sigma" size="lg"/>
        <text weight="medium" textAlign="center" size="sm">LaTeX</text>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface" border radius="md" padding={2} align="center" gap={1}>
        <icon name="file-text" size="lg"/>
        <text weight="medium" textAlign="center" size="sm">HTML PDF</text>
      </box>
    </grid-item>
  </grid>
  <caption>Intended architecture based on the repository's source and documentation.</caption>
</box>

This is the kind of design that transfers well to larger automation systems: several interfaces share one capability instead of implementing separate versions of the same operation.

### B. You considered document semantics, not just file conversion

Math notation, diagrams, callout blocks, tables, Unicode normalization, page breaks, and print styling are actual document-engineering problems. Supporting these features requires preprocessing, backend-specific handling, and output-quality decisions.

Your focus on mathematical and technical documents also gives the project a defined use case: engineering notes, study materials, technical reports, and generated documentation.

### C. You made the tool composable

The MCP server is particularly relevant to your broader engineering ecosystem. A document converter becomes more useful when another system can invoke it as a deterministic operation.

For example, a future workflow could be:

1. Generate a technical report from project artifacts.
2. Validate its Markdown structure.
3. Convert it to PDF using a selected rendering mode.
4. Check that the PDF exists and is readable.
5. Archive the PDF alongside its source and validation results.

The current repository provides pieces of this workflow, but the complete end-to-end sequence should be demonstrated and tested before claiming that it is reliable.

---

### Assistant

## 4. Important problems I found

These are the findings that most affect whether I would trust this project in a repeatable engineering workflow.

<box gap={3}>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">1. Auto mode is inconsistent across entry points</title>
      <badge color="danger">High priority</badge>
    </row>
    The shared `convert_auto()` function in [`md2pdf/core.py`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/md2pdf/core.py) attempts the Sidebar backend, catches failures, and can proceed to another backend.

    In contrast, [`mcp_server/server.py`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/mcp_server/server.py) implements its own auto-selection logic. It chooses a backend based on detected content and available tools, but does not provide the same general fallback behavior when the selected conversion fails.

    **Why it matters:** the GUI/core and MCP entry points may behave differently on the same input. An available toolchain does not guarantee a successful conversion.

    **Fix:** implement one shared conversion orchestrator that returns the actual backend, fallback history, and structured failure details. Have both interfaces call it.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">2. No visible reproducible test suite</title>
      <badge color="danger">High priority</badge>
    </row>
    The inspected root listing contains the application, core, MCP server, templates, and synchronization script, but no visible dedicated test directory or CI workflow.

    I cannot establish from this inspection whether manual testing or untracked tests exist.

    **Fix:** add automated tests for content detection, Markdown transformations, backend selection, missing dependencies, invalid output paths, conversion failures, and MCP tool contracts. Add integration tests that actually inspect generated PDFs.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">3. The README is not fully portable</title>
      <badge color="warning">Medium priority</badge>
    </row>
    The current [README](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/README.md) uses local Windows paths such as `file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/...` in links to source files. These are not portable repository links.

    **Fix:** replace them with relative GitHub-compatible links, such as `./md2pdf/core.py`. Add a clean-install walkthrough, sample input/output, screenshots, and a tested compatibility matrix.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">4. The dependency story needs tightening</title>
      <badge color="warning">Medium priority</badge>
    </row>
    [`requirements.txt`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/requirements.txt) declares the Python dependencies for the MCP server, but the actual conversion engines are external executables. The README documents several of those dependencies, with different requirements for each mode.

    The source also contains Windows-specific Chromium installation candidates alongside PATH-based discovery, so cross-platform behavior deserves explicit verification.

    **Fix:** document dependencies by mode, test executable discovery on Windows/Linux/macOS, and provide a dependency diagnostic that reports both availability and usable versions.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">5. Conversion failures need a stronger contract</title>
      <badge color="warning">Medium priority</badge>
    </row>
    The conversion code launches external processes, and Sidebar conversion uses a timeout. The MCP wrapper catches `RuntimeError` around conversion calls, but other exceptions from subprocess execution can escape that handler. In addition, checking whether an output file exists and is nonempty is not sufficient proof that it is a valid PDF.

    **Fix:** normalize process failures into structured results; distinguish missing dependencies, timeouts, rendering errors, and invalid output; and verify the produced PDF with a parser before reporting success.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">6. HTML and file-access boundaries deserve review</title>
      <badge color="warning">Hardening</badge>
    </row>
    Sidebar mode enables Pandoc's raw HTML reader extension and renders the resulting HTML in Chromium. The HTML wrapper loads JavaScript and stylesheets from external CDNs, while the browser invocation includes `--allow-running-insecure-content`.

    This is not proof of an exploitable vulnerability. It does mean that arbitrary or untrusted Markdown should not automatically be treated as harmless input.

    **Fix:** define a trust boundary for MCP inputs, sanitize or disable unsafe HTML where appropriate, restrict local-file access, avoid unnecessary insecure-content permissions, and consider how external resource loading affects reproducibility.
  </box>
</box>

## 5. What the recent commit history tells me

The latest five commits returned by GitHub were dated September 24, 2026. They show a concentrated round of work on the Sidebar renderer, desktop UI, light print styling, and README documentation.

<box border radius="lg" padding={3} gap={3}>
  <row align="start" gap={3}>
    <icon name="git-commit" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **Sidebar rendering and print styling**

      <text color="secondary" size="sm">September 24, 2026</text>

      The recent changes include the Chromium-based rendering path and making light paper styling the default.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <icon name="layout-dashboard" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **Desktop interface redesign**

      <text color="secondary" size="sm">September 24, 2026</text>

      A separate commit focuses on the Studio interface and its visual design.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <icon name="book-open" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **Documentation updated after implementation changes**

      <text color="secondary" size="sm">September 24, 2026</text>

      The README describes the new rendering engine, print theme, desktop UI, and MCP tools.
    </box>
  </row>
  <button block variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/commits/main")}>View commit history <icon name="arrow-up-right" size="xs" inline/></button>
</box>

The sequence shows feature development and documentation being updated together. However, the commits and README establish what was changed and intended, not whether all the features work consistently under clean installation, failure conditions, and different operating systems.

I would make the next phase about verification rather than adding another rendering feature.

## 6. The roadmap I would follow

{@body const tasks = [{phase:"P0",name:"Unify backend selection and fallback",detail:"One orchestration function used by the GUI, MCP, and any future CLI."},{phase:"P0",name:"Build a reproducible test suite",detail:"Unit tests, mocked process failures, MCP contract tests, and real PDF integration tests."},{phase:"P0",name:"Validate PDF outputs",detail:"Check file signatures, parseability, expected content, and page count where appropriate."},{phase:"P1",name:"Create a rendering regression corpus",detail:"Include equations, long tables, Mermaid diagrams, GFM alerts, Unicode, page breaks, and malformed input."},{phase:"P1",name:"Make installation reproducible",detail:"Document supported platforms, engine versions, setup steps, and dependency diagnostics."},{phase:"P2",name:"Demonstrate ecosystem composition",detail:"Publish one end-to-end workflow with retained source files, execution logs, output PDFs, and validation reports."}]}
{@body const [done,setDone] = DIL.useState([])}
<box border radius="xl" padding={3} gap={3}>
  <row align="center" justify="between">
    <title size="lg">Engineering backlog</title>
    <badge>{done.length} of {tasks.length} checked</badge>
  </row>
  <box background="surface-tertiary" radius="full" height="5px" clip>
    <box background="surface-inverted" height="5px" radius="full" width={`${done.length/tasks.length*100}%`}/>
  </box>
  {#each tasks as task}
    <checkbox key={task.name} checked={done.includes(task.name)} onChange={v=>setDone(old=>v?[...old,task.name]:old.filter(x=>x!==task.name))} lineThrough={false}>
      <box gap={1}>
        <row align="center" gap={2} wrap="wrap">
          <badge color={task.phase==="P0"?"danger":task.phase==="P1"?"warning":"secondary"}>{task.phase}</badge>
          <text weight="medium">{task.name}</text>
        </row>
        <text color="secondary" size="sm">{task.detail}</text>
      </box>
    </checkbox>
  {/each}
</box>

### The test corpus I would prioritize

| Input class | What to verify |
|---|---|
| Inline and display equations | Symbols, fractions, matrices, and delimiter handling |
| Mermaid flowcharts and sequences | Valid SVG rendering and page-fit behavior |
| Wide and multipage tables | Readability, overflow, and repeated headers where applicable |
| Unicode and Nepali text | Font coverage and missing-glyph behavior |
| GFM alerts and nested lists | Correct structure, styling, and content preservation |
| Missing tools and failed subprocesses | Clear errors, correct fallback, no false success |
| Untrusted HTML and local paths | Enforced input and filesystem boundaries |

Keep a set of known-good Markdown fixtures and compare rendered PDFs against expected properties. Visual snapshots can help, but they should complement—not replace—checks that the output is structurally valid and contains the expected text.

## 7. What this project demonstrates about your engineering direction

Given your wider work on `brainstorm`, I see a useful connection: `md2pdf-desktop` is a concrete example of turning a capability into something that other tools can invoke.

It demonstrates several distinct engineering activities:

- **Systems integration:** coordinating Python, Pandoc, Chromium, LaTeX, and other external programs.
- **Interface design:** providing both a desktop GUI and a machine-facing MCP interface.
- **Abstraction:** keeping rendering logic in a shared module rather than tying it entirely to one interface.
- **Workflow automation:** connecting conversion to AI-agent workflows and repository maintenance.

These are valuable skills for intelligent-systems engineering. They do not, by themselves, demonstrate that the implementation is fully robust or that every subsystem is understood in depth. The next step is to make the behavior observable and independently verifiable.

For your own learning, I would choose one complete path—Markdown input, backend selection, subprocess invocation, PDF validation—and be able to explain and debug each stage without relying on AI to make the diagnosis. That would convert a working AI-assisted prototype into a stronger demonstration of your own engineering capability.

## Final verdict

<box border radius="xl" padding={4} gap={3}>
  <title size="lg">A useful, composable engineering tool with a clear next step</title>
  `md2pdf-desktop` has a coherent purpose, multiple real rendering paths, a shared core, a desktop interface, and an MCP integration. Its strongest differentiator is the combination of document rendering with programmatic agent access.

  Its main weakness is not a lack of features. It is the gap between the documented capabilities and reproducible evidence that those capabilities work reliably together.

  **My recommendation:** prioritize shared orchestration, automated testing, and PDF validation before expanding the feature set. Those improvements would make the repository more credible as both a standalone utility and a component in your broader engineering ecosystem.
  <row gap={2} wrap="wrap">
    <button onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop")}>Open repository <icon name="arrow-up-right" size="xs" inline/></button>
    <button variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/main/md2pdf")}>Inspect conversion core</button>
    <button variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/main/mcp_server")}>Inspect MCP server</button>
  </row>
</box>

---

## Turn 2

### User

perform a deeper pass this time

### Assistant

I’m going one layer below the README this time: repository history, full file topology, shared core, GUI, MCP contract, sync engine, and failure paths. The goal is to separate “feature-rich” from “actually robust.”

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I hit one practical limitation: GitHub’s connector can read the repository, but the runtime cannot clone it directly. I’m compensating by inspecting the source through GitHub at line level rather than treating the README as ground truth.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Yes. I went substantially deeper this time, including the **actual current `main` tree as of September 29, 2026**, recent commit history, the full application flow, conversion core, MCP layer, templates, and the synchronization tooling.

One important correction from my previous pass: **the repository was updated today, September 29, with `sync.bat`**. The latest commit is `3ade282` and adds only that 14-line wrapper; the substantial rendering/UI work is still from September 24. The current tree contains 14 tracked paths, including a duplicated `templates/` directory. 

# Deep evaluation

## Overall: **7.2/10 engineering maturity**

But that number hides an important distinction:

| Dimension | Assessment |
|---|---|
| Product idea | **8.5/10** |
| Architecture | **8.0/10** |
| Feature implementation | **8.0/10** |
| Integration / composability | **8.5/10** |
| Error handling | **5.5/10** |
| Reproducibility | **5.0/10** |
| Testing / verification | **3.5/10** |
| Security / trust boundaries | **5.5/10** |
| Repository hygiene | **6.0/10** |
| Portfolio signal | **8.0/10** |

The key finding is:

> **The project has crossed the “interesting prototype” threshold. It has not yet crossed the “demonstrably reliable engineering tool” threshold.**

And the gap is surprisingly concentrated. You don't need another 10 features. You need **verification, determinism, and failure semantics**.

---

# 1. The architecture is genuinely better than it first appears

The repository is effectively:

```text
                    ┌──────────────────┐
                    │ Markdown source  │
                    └────────┬─────────┘
                             │
                     preprocessing
                             │
                    ┌────────▼─────────┐
                    │  md2pdf/core.py  │
                    └──────┬─┬─┬──────┘
                           │ │ │
             ┌─────────────┘ │ └─────────────┐
             ▼               ▼               ▼
        Chromium          LaTeX           wkhtmltopdf
        + KaTeX           + pdflatex       + HTML
        + Mermaid
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                            PDF

             ▲               ▲
             │               │
        Tkinter GUI       MCP server
             │               │
             └────── same core ──────────┘
```

This is a good architectural instinct.

The important part is not “it has three backends.”

It is:

**you extracted the capability into a reusable conversion core, then put different interfaces around it.**

That pattern generalizes well to larger engineering systems.

The MCP server and desktop application both import the core rather than reimplementing the rendering engines independently. That is one of the strongest aspects of this repository.

---

# 2. Your most interesting feature is actually MCP, not PDF conversion

The PDF converter itself is a useful utility.

The more strategically interesting part is:

```text
AI Agent
   ↓
MCP
   ↓
md2pdf tool
   ↓
shared conversion engine
   ↓
validated artifact
```

That changes the project's category.

It isn't merely:

> “I made a Markdown-to-PDF application.”

It can become:

> “I built a deterministic document-rendering capability that can be consumed interactively or programmatically by AI agents.”

That connects quite naturally with the architecture you're building elsewhere.

The current MCP layer exposes:

- conversion
- content detection
- environment/toolchain diagnostics

That's good composability.

The current repository therefore already contains the beginnings of a **tool-oriented engineering architecture**, rather than only a desktop application.

---

# 3. The biggest architectural weakness: there are actually multiple orchestrators

This is the most important design issue I found.

You have orchestration logic in at least three places:

### `md2pdf/core.py`

`convert_auto()`

### `mcp_server/server.py`

Its own `AUTO` selection logic.

### `md2pdf_app.py`

`_run_auto_detect()`

These do not behave identically.

For example:

### GUI

The GUI auto detector can change the selected mode to:

```text
sidebar_dark
sidebar_light
latex
```

and specifically sets **Sidebar Dark** when Sidebar is detected.

### MCP

The MCP server calls `convert_sidebar()` without exposing a theme parameter, so the default is **light**.

### Core

`convert_auto()` accepts a `theme` argument and has its own fallback chain.

Therefore:

```text
same Markdown
        ↓
GUI
        ↓
Sidebar Dark
```

versus:

```text
same Markdown
        ↓
MCP
        ↓
Sidebar Light
```

That directly conflicts with the README's claim that the surfaces provide identical behavior/output.

This is not a cosmetic issue.

It is an **orchestration ownership problem**.

## Better architecture

There should be exactly one canonical function:

```python
render_document(
    markdown,
    output_path,
    policy=...
)
```

and it should produce something like:

```python
ConversionResult(
    success=True,
    backend="sidebar",
    theme="light",
    fallbacks=[],
    warnings=[],
    output_path="...",
    output_size=...,
)
```

Then:

```text
GUI ───────┐
MCP ───────┼──> render_document()
CLI ───────┘
```

That would make the architecture considerably stronger.

---

# 4. There is a serious false-success problem

This is the most important implementation issue.

In Sidebar mode:

```python
p_res = subprocess.run(...)
if not os.path.isfile(save_path) or os.path.getsize(save_path) == 0:
    raise RuntimeError(...)
```

You don't actually check the Chromium process return code.

So the logic is effectively:

```text
Chromium says something went wrong
        ↓
output.pdf happens to exist
        ↓
application reports success
```

That is not a sufficient success criterion.

Even more importantly, there is no post-generation PDF validation.

A better contract is:

```text
process return code == 0
        AND
PDF exists
        AND
PDF parses successfully
        AND
PDF has >= 1 page
        AND
expected document content exists
```

For a document-processing application, that's much closer to what “successful conversion” should mean.

---

# 5. Sidebar rendering is not actually deterministic

This is a major issue that wasn't obvious from the README.

Your HTML wrapper loads:

```text
cdn.jsdelivr.net
```

for:

- KaTeX CSS
- KaTeX JS
- auto-render
- Mermaid.js

That means the conversion depends on an external network resource.

So the advertised pipeline:

```text
Markdown → Chromium → PDF
```

is really:

```text
Markdown
 ↓
Pandoc
 ↓
HTML
 ↓
Internet/CDN dependency
 ↓
KaTeX/Mermaid
 ↓
Chromium
 ↓
PDF
```

That means:

```text
offline machine
network outage
CDN outage
DNS failure
corporate proxy
changed CDN response
```

can potentially alter the rendering result.

For a document conversion utility, this is especially important because you describe the output as **publication-grade** and **vector**.

A stronger implementation would bundle the required JS/CSS locally:

```text
assets/
    katex.min.js
    katex.min.css
    mermaid.min.js
```

or generate the necessary resources into the temporary document.

Then:

```text
same input
+
same application version
+
same dependency versions
=
same rendering environment
```

That is a much stronger engineering story.

A current peer project in the same Chromium-based Markdown→PDF space explicitly emphasizes making the print document self-contained, including fonts, images, and diagrams. 

---

# 6. Your “smart page-break” claim is stronger than the implementation

This is a particularly clear documentation/code mismatch.

The README says Sidebar mode has smart page-break rules and describes preventing breaks inside:

- math
- tables
- code
- diagrams

But the CSS contains declarations such as:

```css
page-break-inside: auto;
break-inside: auto;
```

for those elements.

That is **not the same thing as preventing page breaks**.

Some browser pagination behavior may still produce acceptable results, but the source does not justify the stronger claim.

So I would change either:

### the implementation

to explicitly enforce the desired behavior,

or:

### the documentation

to accurately describe what Chromium actually guarantees.

This is exactly the kind of distinction an experienced reviewer notices.

---

# 7. The Markdown preprocessor is powerful, but too destructive

`clean_markdown_for_pdf()` is doing a lot:

- ASCII table conversion
- Unicode normalization
- emoji removal
- Mermaid transformation
- math symbol translation
- delimiter normalization

Conceptually, that's good.

Implementation-wise, it is overly global.

For example:

```python
text = text.replace('│', '|')
text = text.replace('─', '-')
text = text.replace('°', ' deg')
```

and:

```python
text = text.replace('∨', r' $\lor$ ')
```

operate on the entire Markdown document.

That means the converter can modify content that the user intended to preserve literally.

Imagine:

```markdown
```text
temperature °C
A │ B
x ∨ y
```
```

Your preprocessing is capable of altering that code block.

That's a semantic transformation.

The same problem exists with ASCII table detection: a fenced code block that happens to look like an ASCII table may be converted into a real Markdown table even when the user intended it as code.

## Better model

Parse by context:

```text
Markdown document
 ├── prose
 ├── code fence
 ├── math
 ├── HTML
 ├── Mermaid
 └── table
```

Then transform only the specific node types you intend to transform.

That means an AST-oriented approach is the natural next step.

Ironically, your README already calls these functions “AST sanitizers,” but most of the implementation is actually regex/string preprocessing rather than AST transformation.

That's another wording mismatch I'd fix.

---

# 8. `convert_auto()` hides too much

This function contains the pattern:

```python
try:
    convert_sidebar(...)
except Exception:
    pass
```

That makes the system resilient in one sense, but opaque in another.

You can end up with:

```text
Sidebar failed
     ↓
exception swallowed
     ↓
LaTeX attempted
     ↓
maybe Simple
     ↓
PDF produced
```

The caller may not know that the requested or automatically selected renderer failed.

For an engineering tool, fallback should be **observable**.

Something like:

```text
attempt 1:
    sidebar
    failed: Mermaid render timeout

attempt 2:
    latex
    skipped: unsupported Mermaid semantics

attempt 3:
    simple
    succeeded
```

would be much better.

This is especially important when an AI agent is consuming the tool.

An agent needs to know:

> “I produced the requested high-fidelity artifact.”

versus:

> “I produced a degraded fallback artifact.”

Those are materially different results.

---

# 9. MCP auto-mode contains a particularly important edge case

The server performs this logic:

```text
if Sidebar required and available
    → Sidebar

otherwise:
    detect LaTeX
    → LaTeX if available
    → otherwise Simple
```

But it does not perform the same comprehensive availability/failure handling as the core orchestrator.

The worst edge is:

```text
no Sidebar
no LaTeX
```

followed by selecting Simple without first establishing that both:

```text
pandoc
wkhtmltopdf
```

are actually usable.

The explicit Simple branch checks dependencies.

The automatic branch is less rigorous.

That's exactly the kind of bug that won't appear in normal development because the developer machine usually has all the tools installed.

---

# 10. The GUI isn't actually responsive during conversion

This is another source-level finding that matters.

`convert()` calls:

```python
convert_sidebar(...)
convert_latex(...)
convert_simple(...)
```

directly from the Tkinter event loop.

Those invoke external processes.

Sidebar even has a timeout of up to 60 seconds.

Therefore:

```text
Export
 ↓
Tkinter main thread blocked
 ↓
window stops responding
 ↓
conversion finishes
 ↓
UI resumes
```

So the interface can look polished while behaving synchronously.

The correct architecture would be:

```text
Tkinter UI thread
       │
       ├── enqueue conversion
       ▼
worker thread/process
       │
       ▼
converter
       │
       ▼
result queue
       │
       ▼
UI updates
```

Then you can actually provide:

- cancellation
- progress state
- asynchronous diagnostics
- responsive UI
- conversion timing

That would make the “Studio” concept much more credible.

---

# 11. Your timeouts are inconsistent

Sidebar:

```text
timeout=60
```

Simple:

no timeout

LaTeX:

no timeout

That means an accidental or broken external process can hang Simple or LaTeX indefinitely.

For a multi-backend system, subprocess lifecycle management should be centralized.

Something like:

```python
run_tool(
    command,
    timeout=...
)
```

would give all backends consistent behavior.

---

# 12. The LaTeX health check is useful—but narrower than advertised

`probe_latex_template()` is a good idea.

This is one of the better engineering touches in the repository.

But the probe is basically:

```text
# Probe

Hello $x^2$.
```

It therefore confirms roughly:

```text
Pandoc
+
pdflatex
+
basic template compilation
```

It does **not** demonstrate:

- Lua filter correctness
- callout box rendering
- long tables
- code wrapping
- Unicode behavior
- page breaks
- all packages
- complex math

So “template compiles” is supported.

“the LaTeX conversion pipeline is healthy” is a stronger claim.

The next step is to turn the probe into an actual fixture suite.

---

# 13. `sync.ps1` is much more ambitious—and more dangerous—than I initially gave it credit for

This is probably the most interesting non-PDF piece of the repository.

It contains:

- pull/rebase
- branch management
- push
- auto commit messages
- security scanning
- toolchain health
- status telemetry
- dry-run mode
- test mode

That is genuinely substantial scripting.

But I found several concerns.

## `Ensure-RemoteConfigured`

It hard-codes:

```text
https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop.git
```

and can change the `origin` URL.

That is surprising behavior for a generic synchronization script.

Someone clones the repository, changes `origin` to their fork, and the script can replace it.

For a personal workflow script this may be intentional.

For a public repository, I would not make it automatic.

---

## `-WhatIf` isn't completely read-only

The script does:

```text
git add -A
...
git reset --quiet
```

So it modifies the staging state during a supposedly dry-run operation.

If the user already had intentionally staged changes, this can disturb that state.

That's a real design flaw.

---

## The script can commit unrelated changes

The normal path performs:

```text
git add -A
git commit
```

That means:

```text
feature changes
+
unrelated personal edits
+
temporary tracked modifications
```

can become one commit.

For a personal “sync everything” workflow, perhaps intentional.

For a reusable engineering repository, dangerous.

---

## Secret scanning is useful but heuristic

The regex scanner catches several common token patterns, which is helpful.

But:

```text
pattern matching ≠ secret detection
```

It will have false positives and false negatives.

For your purpose, that's fine as an additional guard.

I wouldn't describe it as a complete security gate.

---

# 14. The new `sync.bat` is useful, but tiny relative to the rest of the engineering problem

Today's commit:

```text
3ade282
chore(scripts): add sync.bat
```

simply wraps `sync.ps1` and bypasses PowerShell execution policy using:

```text
-NoProfile -ExecutionPolicy Bypass
```

That is a convenience improvement for Windows users.

It does **not** meaningfully alter the engineering maturity of the core application.

The repository's recent development history is much more revealing:

```text
Sep 19
 ├── LaTeX fixes
 ├── sync.ps1
 ├── engine automation
 └── styling

Sep 24
 ├── Chromium renderer
 ├── UI overhaul
 ├── light print theme
 └── README rewrite

Sep 29
 └── sync.bat
```

You have had a very feature-dense period followed by a small workflow convenience commit.

What is missing in that sequence is:

```text
tests
validation
CI
fixtures
benchmarking
packaging
```

That's where I'd redirect the development energy now.

---

# 15. There is an odd repository hygiene issue: duplicated templates

The current repository tree contains both:

```text
templates/
    styled.latex
    callout-boxes.lua
```

and:

```text
md2pdf/templates/
    styled.latex
    callout-boxes.lua
```

The files have identical Git object SHAs.

But the application points to:

```python
PACKAGE_DIR / "templates"
```

inside `md2pdf`.

Therefore the root-level copy appears redundant.

This creates unnecessary ambiguity:

```text
Which templates are authoritative?
```

A future developer can modify:

```text
templates/styled.latex
```

and nothing changes.

That's a classic repository hygiene trap.

Remove the duplicate unless there is a deliberate packaging reason for it.

---

# 16. Packaging is missing

There is no visible:

```text
pyproject.toml
setup.cfg
setup.py
```

and no CLI entry point.

That means the project is currently more:

```text
"clone this repository and run these files"
```

than:

```text
"install this tool and use it"
```

For your own machine that's completely acceptable.

For a portfolio project, adding packaging would materially strengthen it.

For example:

```text
pipx install md2pdf-desktop
md2pdf ...
```

or a proper application release would push it toward software distribution rather than repository code.

---

# 17. Reproducibility is weak

`requirements.txt` says:

```text
mcp[cli]<2
pydantic>=2
```

The first is constrained.

The second is open-ended.

Meanwhile the important rendering dependencies are external:

```text
Pandoc
Chromium
Mermaid CDN
KaTeX CDN
wkhtmltopdf
pdflatex
LaTeX packages
```

That's a lot of environmental variance.

For deterministic document generation, dependency versions matter.

A strong release would document something like:

```text
Python
Pandoc
Chrome/Edge
KaTeX
Mermaid
TeX Live
wkhtmltopdf
```

and ideally test against known versions.

---

# 18. There is no evidence yet that “publication-grade” is reproducibly true

This is perhaps the most important philosophical point.

Your README uses language such as:

> publication-grade

and

> textbook-grade

Those are outcome claims.

At the source level, I can see serious effort toward those outcomes.

But I don't yet see:

```text
benchmark corpus
+
expected output
+
regression tests
+
PDF validation
+
visual regression
```

Therefore the repository currently demonstrates:

**engineering intent + substantial implementation**

rather than:

**demonstrated rendering quality under regression testing**

That's the distinction I'd want you to internalize.

---

# 19. What I would actually test

This project is unusually well suited to fixture-based testing.

Create:

```text
tests/
    fixtures/
        basic.md
        math.md
        tables.md
        mermaid.md
        gfm-alerts.md
        unicode.md
        code-heavy.md
        long-document.md
        adversarial.md
```

Then test:

```text
input
 ↓
detector
 ↓
selected backend
 ↓
conversion
 ↓
PDF parser
 ↓
assertions
```

For example:

```text
math.md
    → Sidebar
    → PDF exists
    → PDF parses
    → equation text exists

mermaid.md
    → Sidebar
    → PDF parses
    → SVG-derived content exists

plain.md
    → Simple

broken toolchain
    → structured error

invalid output directory
    → structured error

huge document
    → timeout rather than hang
```

That would do more for this repository than another visual redesign.

---

# 20. Your security boundary needs to be explicit

This matters particularly because you expose the functionality to AI agents.

The MCP tool can receive:

```text
output_path
```

and write to that filesystem location.

That is powerful.

Additionally, both HTML/PDF pipelines enable local resource access in places, and Sidebar rendering loads JavaScript.

For a personal local MCP server, this may be acceptable.

But architecturally I'd define:

```text
trusted local Markdown
```

versus:

```text
untrusted agent-generated Markdown
```

as two different threat models.

A future safe mode could restrict:

```text
output directory
local file references
HTML
external URLs
JavaScript
```

That would make the MCP capability much more defensible.

---

# 21. The GUI has several smaller quality issues

Some additional findings:

### Auto-detection behavior is inconsistent

When Sidebar content is detected, GUI auto-selection explicitly chooses:

```text
sidebar_dark
```

even though light is now your stated default print theme.

### Detection doesn't necessarily reset the mode

A document can transition:

```text
math → no math
```

while the selected engine remains LaTeX even after the detector says the document is now plain.

### Error handling is uneven

`paste_clipboard()` silently swallows all exceptions.

`open_file()` doesn't protect file-reading operations.

`open_output_folder()` doesn't verify subprocess success.

These aren't architectural failures, but they are exactly the polish you'd address before calling something production-ready.

---

# 22. What is actually excellent here

After going deeper, I would **increase** my assessment of several aspects.

### Shared-core extraction

Very good.

### MCP integration

Very good.

### Backend diversity

Strong.

### Dependency probing

Good engineering instinct.

### Dedicated LaTeX template

Good.

### Custom preprocessing

Ambitious and useful.

### Desktop + headless operation

Excellent product architecture.

### Synchronization automation

Technically substantial, although it needs safety refinement.

The project is definitely not “just a script.”

---

# 23. The bigger issue: your architecture is ahead of your verification

This is the central conclusion of the deeper pass.

You've already accumulated:

```text
GUI
+
MCP
+
multiple renderers
+
automatic detection
+
custom templates
+
preprocessing
+
toolchain detection
+
automation
+
sync tooling
```

That's a lot.

But the engineering evidence is still:

```text
implementation >> verification
```

I would reverse that relationship now.

For the next phase:

```text
implementation
      ↓
tests
      ↓
fixtures
      ↓
validation
      ↓
observability
      ↓
only then new features
```

---

# 24. What would move this to ~8.5+

I would make the next major version approximately:

```text
md2pdf/
    core/
        parser.py
        transforms.py
        detectors.py
        renderers/
            chromium.py
            latex.py
            simple.py
        orchestrator.py
        result.py
        validation.py

    assets/
        katex/
        mermaid/

tests/
    unit/
    integration/
    fixtures/
    regression/

scripts/
    sync.ps1
    sync.bat

pyproject.toml
LICENSE
CHANGELOG.md
```

Then the public contract becomes something like:

```text
Markdown
   ↓
parse
   ↓
normalize
   ↓
classify
   ↓
select renderer
   ↓
render
   ↓
validate PDF
   ↓
ConversionResult
```

That would be an appreciably more mature architecture.

---

# 25. Career/portfolio interpretation

This project gives me a somewhat different impression of your direction than a conventional student portfolio.

The interesting part isn't that you can write Python or Tkinter.

It's the pattern:

```text
messy real-world requirement
        ↓
multiple implementation constraints
        ↓
toolchain composition
        ↓
shared abstraction
        ↓
automation interface
        ↓
artifact generation
```

That pattern is much closer to **systems/integration engineering** than ordinary beginner application development.

It also fits particularly well with the direction you've been exploring in `brainstorm`: building infrastructure around AI-assisted engineering rather than only building isolated ML models.

But there's a trap here.

You could keep adding:

```text
another engine
another UI feature
another automation script
another MCP tool
another styling system
```

and become extremely good at **assembling increasingly complicated prototypes** without developing equivalent depth in verification and failure analysis.

This repository is actually an excellent place to break that pattern.

Take ownership of:

```text
Why did this renderer fail?
Why did auto-selection choose this backend?
Why did this PDF differ?
How do I prove the PDF is correct?
What is the trust boundary?
What happens under timeout?
What happens offline?
What happens with malformed Markdown?
```

Those questions will teach you considerably more engineering than adding another feature.

---

# Final assessment

## `md2pdf-desktop` is now a real engineering project, but its next evolution should be from **feature-rich** to **evidence-rich**.

The architecture is good enough to preserve.

I would **not** rewrite the project from scratch.

I would instead make five architectural corrections:

```text
1. One canonical renderer/orchestrator
2. Deterministic/self-contained rendering assets
3. Real PDF/output validation
4. Automated fixture + regression tests
5. Asynchronous GUI + structured failures
```

Then clean up:

```text
duplicate templates
hard-coded remote behavior
missing packaging
missing license
README/source mismatches
```

One especially encouraging fact is that the latest September 29 change was only a convenience wrapper, while the major September 24 work already established the core architecture. That means the repository is at a good **stabilization point** rather than needing another architectural explosion.

For comparison, current Markdown→PDF tooling is increasingly emphasizing self-contained rendering, deterministic pagination, and explicit document-processing pipelines rather than merely calling a browser to print HTML. 

urlOpen the current repositoryhttps://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop

I can next turn this exact audit into a **researcher-grade issue backlog with P0/P1/P2 findings mapped to specific files/functions and an implementation order**.

---


---

# 📎 Appendix: Repository evaluation writing (ChatGPT Session Continuation)

> **Source URL:** [https://chatgpt.com/share/6abc0262-f4f0-83e8-b92c-9228f4150ad3](https://chatgpt.com/share/6abc0262-f4f0-83e8-b92c-9228f4150ad3)
> **Appended:** 2026-09-30
> **Total Turns:** 343

---

## Turn 1

### User

[Aaradhya-Dev-Tamrakar/md2pdf-desktop](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop)  eval this repo

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

# Repository Evaluation: `md2pdf-desktop`

<text color="secondary" size="sm">Reviewed September 29, 2026 · Public GitHub repository · Architecture, implementation, integration, and portfolio value</text>

**My overall assessment: this is a substantive engineering utility, not merely a Markdown-to-PDF script.** Its most interesting aspect is the combination of multiple document-rendering backends, a desktop interface, and an MCP server that lets AI coding agents invoke the same conversion capability.

Repository: [Aaradhya-Dev-Tamrakar/md2pdf-desktop](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop)

I inspected the README, shared conversion core, MCP server, dependency declarations, repository structure, and recent commit history. This is a source-level review; I have not run the application or verified the generated PDFs on your machine.

## 1. Evaluation at a glance

<box border radius="xl" padding={4} gap={3}>
  <row align="center" justify="between">
    <box gap={1}>
      <title size="xl">7.5/10</title>
      <text color="secondary" size="sm">Provisional engineering assessment</text>
    </box>
    <badge color="success">Useful real-world project</badge>
  </row>
  <divider color="subtle"/>
  <text color="secondary" size="sm">These are my qualitative review scores, not benchmark results or test coverage measurements.</text>
  <box gap={3}>
    {#each [{name:"Architecture and decomposition",score:8.0},{name:"Feature breadth",score:8.5},{name:"Integration potential",score:8.5},{name:"Documentation and usability",score:7.5},{name:"Reliability evidence",score:5.0},{name:"Distribution and portability",score:5.5}] as item}
      <box gap={1}>
        <row align="center" justify="between">
          <text>{item.name}</text>
          <title size="sm" color="default">{item.score.toFixed(1)}/10</title>
        </row>
        <box background="surface-tertiary" radius="full" height="6px" clip>
          <box background={item.score >= 8 ? "success-solid" : item.score >= 7 ? "info-solid" : "surface-inverted"} radius="full" height="6px" width={`${item.score*10}%`}/>
        </box>
      </box>
    {/each}
  </box>
</box>

The distinction that matters most is this: **the feature and architecture ambitions are ahead of the publicly demonstrated reliability.** That is fixable, and it is where I would concentrate the next engineering effort.

---

### Assistant

## 2. What you actually built

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="layers" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **A shared conversion engine**

      <text color="secondary" size="sm">`md2pdf/core.py`</text>

      The central module contains the rendering pipelines, dependency detection, Markdown preprocessing, and styling. Keeping this logic outside both the GUI and MCP server reduces duplication and gives the project a reusable core.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="file-text" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Multiple rendering backends**

      <text color="secondary" size="sm">`md2pdf/core.py`</text>

      - Sidebar: Pandoc, Chromium, KaTeX, and Mermaid.js.
      - LaTeX: Pandoc, `pdflatex`, and a custom LaTeX template.
      - Simple: Pandoc and `wkhtmltopdf`.
      - Auto: content detection to select an appropriate backend.

      This is more meaningful than wrapping one converter with a GUI because the rendering engines have different capabilities and dependencies.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="monitor" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Desktop Studio**

      <text color="secondary" size="sm">`md2pdf_app.py`</text>

      A Tkinter application with a document editor, toolchain status indicators, document metrics, file operations, and conversion controls. This makes the project usable as a standalone tool rather than only a developer library.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="workflow" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **MCP integration**

      <text color="secondary" size="sm">`mcp_server/server.py`</text>

      Exposes conversion, rendering-mode detection, and dependency-checking capabilities to compatible AI clients. This turns the converter into an operation that can be composed into automated documentation workflows.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="shield-check" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Development synchronization**

      <text color="secondary" size="sm">`sync.ps1`</text>

      Includes Git synchronization, secret scanning, and toolchain checks. This is a useful attempt to formalize development operations, although the existence of those checks does not by itself establish their effectiveness.
    </box>
  </row>
</box>

The repository's [README](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/README.md) documents these capabilities. The important architectural choice is the separation between the shared conversion core and its different user-facing entry points.

## 3. The strongest engineering decisions

### A. You designed for more than one interaction model

A user can convert a document through the desktop application, while an AI agent can request a conversion through MCP. Both are intended to use the same underlying engine.

That is a meaningful design pattern:

<box border radius="lg" padding={3} align="center" gap={2}>
  <box background="surface-secondary" radius="md" padding={3} width="100%" align="center">
    **Desktop GUI · MCP client**
  </box>
  <icon name="arrow-down" size="lg" color="secondary"/>
  <box border radius="md" padding={3} width="100%" align="center">
    **Shared conversion API**
  </box>
  <icon name="arrow-down" size="lg" color="secondary"/>
  <grid columns={3} gap={2}>
    <grid-item>
      <box background="surface" border radius="md" padding={2} align="center" gap={1}>
        <icon name="file-code" size="lg"/>
        <text weight="medium" textAlign="center" size="sm">Chromium</text>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface" border radius="md" padding={2} align="center" gap={1}>
        <icon name="sigma" size="lg"/>
        <text weight="medium" textAlign="center" size="sm">LaTeX</text>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface" border radius="md" padding={2} align="center" gap={1}>
        <icon name="file-text" size="lg"/>
        <text weight="medium" textAlign="center" size="sm">HTML PDF</text>
      </box>
    </grid-item>
  </grid>
  <caption>Intended architecture based on the repository's source and documentation.</caption>
</box>

This is the kind of design that transfers well to larger automation systems: several interfaces share one capability instead of implementing separate versions of the same operation.

### B. You considered document semantics, not just file conversion

Math notation, diagrams, callout blocks, tables, Unicode normalization, page breaks, and print styling are actual document-engineering problems. Supporting these features requires preprocessing, backend-specific handling, and output-quality decisions.

Your focus on mathematical and technical documents also gives the project a defined use case: engineering notes, study materials, technical reports, and generated documentation.

### C. You made the tool composable

The MCP server is particularly relevant to your broader engineering ecosystem. A document converter becomes more useful when another system can invoke it as a deterministic operation.

For example, a future workflow could be:

1. Generate a technical report from project artifacts.
2. Validate its Markdown structure.
3. Convert it to PDF using a selected rendering mode.
4. Check that the PDF exists and is readable.
5. Archive the PDF alongside its source and validation results.

The current repository provides pieces of this workflow, but the complete end-to-end sequence should be demonstrated and tested before claiming that it is reliable.

---

### Assistant

## 4. Important problems I found

These are the findings that most affect whether I would trust this project in a repeatable engineering workflow.

<box gap={3}>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">1. Auto mode is inconsistent across entry points</title>
      <badge color="danger">High priority</badge>
    </row>
    The shared `convert_auto()` function in [`md2pdf/core.py`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/md2pdf/core.py) attempts the Sidebar backend, catches failures, and can proceed to another backend.

    In contrast, [`mcp_server/server.py`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/mcp_server/server.py) implements its own auto-selection logic. It chooses a backend based on detected content and available tools, but does not provide the same general fallback behavior when the selected conversion fails.

    **Why it matters:** the GUI/core and MCP entry points may behave differently on the same input. An available toolchain does not guarantee a successful conversion.

    **Fix:** implement one shared conversion orchestrator that returns the actual backend, fallback history, and structured failure details. Have both interfaces call it.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">2. No visible reproducible test suite</title>
      <badge color="danger">High priority</badge>
    </row>
    The inspected root listing contains the application, core, MCP server, templates, and synchronization script, but no visible dedicated test directory or CI workflow.

    I cannot establish from this inspection whether manual testing or untracked tests exist.

    **Fix:** add automated tests for content detection, Markdown transformations, backend selection, missing dependencies, invalid output paths, conversion failures, and MCP tool contracts. Add integration tests that actually inspect generated PDFs.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">3. The README is not fully portable</title>
      <badge color="warning">Medium priority</badge>
    </row>
    The current [README](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/README.md) uses local Windows paths such as `file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/...` in links to source files. These are not portable repository links.

    **Fix:** replace them with relative GitHub-compatible links, such as `./md2pdf/core.py`. Add a clean-install walkthrough, sample input/output, screenshots, and a tested compatibility matrix.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">4. The dependency story needs tightening</title>
      <badge color="warning">Medium priority</badge>
    </row>
    [`requirements.txt`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/main/requirements.txt) declares the Python dependencies for the MCP server, but the actual conversion engines are external executables. The README documents several of those dependencies, with different requirements for each mode.

    The source also contains Windows-specific Chromium installation candidates alongside PATH-based discovery, so cross-platform behavior deserves explicit verification.

    **Fix:** document dependencies by mode, test executable discovery on Windows/Linux/macOS, and provide a dependency diagnostic that reports both availability and usable versions.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">5. Conversion failures need a stronger contract</title>
      <badge color="warning">Medium priority</badge>
    </row>
    The conversion code launches external processes, and Sidebar conversion uses a timeout. The MCP wrapper catches `RuntimeError` around conversion calls, but other exceptions from subprocess execution can escape that handler. In addition, checking whether an output file exists and is nonempty is not sufficient proof that it is a valid PDF.

    **Fix:** normalize process failures into structured results; distinguish missing dependencies, timeouts, rendering errors, and invalid output; and verify the produced PDF with a parser before reporting success.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      <title size="md">6. HTML and file-access boundaries deserve review</title>
      <badge color="warning">Hardening</badge>
    </row>
    Sidebar mode enables Pandoc's raw HTML reader extension and renders the resulting HTML in Chromium. The HTML wrapper loads JavaScript and stylesheets from external CDNs, while the browser invocation includes `--allow-running-insecure-content`.

    This is not proof of an exploitable vulnerability. It does mean that arbitrary or untrusted Markdown should not automatically be treated as harmless input.

    **Fix:** define a trust boundary for MCP inputs, sanitize or disable unsafe HTML where appropriate, restrict local-file access, avoid unnecessary insecure-content permissions, and consider how external resource loading affects reproducibility.
  </box>
</box>

## 5. What the recent commit history tells me

The latest five commits returned by GitHub were dated September 24, 2026. They show a concentrated round of work on the Sidebar renderer, desktop UI, light print styling, and README documentation.

<box border radius="lg" padding={3} gap={3}>
  <row align="start" gap={3}>
    <icon name="git-commit" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **Sidebar rendering and print styling**

      <text color="secondary" size="sm">September 24, 2026</text>

      The recent changes include the Chromium-based rendering path and making light paper styling the default.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <icon name="layout-dashboard" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **Desktop interface redesign**

      <text color="secondary" size="sm">September 24, 2026</text>

      A separate commit focuses on the Studio interface and its visual design.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <icon name="book-open" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **Documentation updated after implementation changes**

      <text color="secondary" size="sm">September 24, 2026</text>

      The README describes the new rendering engine, print theme, desktop UI, and MCP tools.
    </box>
  </row>
  <button block variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/commits/main")}>View commit history <icon name="arrow-up-right" size="xs" inline/></button>
</box>

The sequence shows feature development and documentation being updated together. However, the commits and README establish what was changed and intended, not whether all the features work consistently under clean installation, failure conditions, and different operating systems.

I would make the next phase about verification rather than adding another rendering feature.

## 6. The roadmap I would follow

{@body const tasks = [{phase:"P0",name:"Unify backend selection and fallback",detail:"One orchestration function used by the GUI, MCP, and any future CLI."},{phase:"P0",name:"Build a reproducible test suite",detail:"Unit tests, mocked process failures, MCP contract tests, and real PDF integration tests."},{phase:"P0",name:"Validate PDF outputs",detail:"Check file signatures, parseability, expected content, and page count where appropriate."},{phase:"P1",name:"Create a rendering regression corpus",detail:"Include equations, long tables, Mermaid diagrams, GFM alerts, Unicode, page breaks, and malformed input."},{phase:"P1",name:"Make installation reproducible",detail:"Document supported platforms, engine versions, setup steps, and dependency diagnostics."},{phase:"P2",name:"Demonstrate ecosystem composition",detail:"Publish one end-to-end workflow with retained source files, execution logs, output PDFs, and validation reports."}]}
{@body const [done,setDone] = DIL.useState([])}
<box border radius="xl" padding={3} gap={3}>
  <row align="center" justify="between">
    <title size="lg">Engineering backlog</title>
    <badge>{done.length} of {tasks.length} checked</badge>
  </row>
  <box background="surface-tertiary" radius="full" height="5px" clip>
    <box background="surface-inverted" height="5px" radius="full" width={`${done.length/tasks.length*100}%`}/>
  </box>
  {#each tasks as task}
    <checkbox key={task.name} checked={done.includes(task.name)} onChange={v=>setDone(old=>v?[...old,task.name]:old.filter(x=>x!==task.name))} lineThrough={false}>
      <box gap={1}>
        <row align="center" gap={2} wrap="wrap">
          <badge color={task.phase==="P0"?"danger":task.phase==="P1"?"warning":"secondary"}>{task.phase}</badge>
          <text weight="medium">{task.name}</text>
        </row>
        <text color="secondary" size="sm">{task.detail}</text>
      </box>
    </checkbox>
  {/each}
</box>

### The test corpus I would prioritize

| Input class | What to verify |
|---|---|
| Inline and display equations | Symbols, fractions, matrices, and delimiter handling |
| Mermaid flowcharts and sequences | Valid SVG rendering and page-fit behavior |
| Wide and multipage tables | Readability, overflow, and repeated headers where applicable |
| Unicode and Nepali text | Font coverage and missing-glyph behavior |
| GFM alerts and nested lists | Correct structure, styling, and content preservation |
| Missing tools and failed subprocesses | Clear errors, correct fallback, no false success |
| Untrusted HTML and local paths | Enforced input and filesystem boundaries |

Keep a set of known-good Markdown fixtures and compare rendered PDFs against expected properties. Visual snapshots can help, but they should complement—not replace—checks that the output is structurally valid and contains the expected text.

## 7. What this project demonstrates about your engineering direction

Given your wider work on `brainstorm`, I see a useful connection: `md2pdf-desktop` is a concrete example of turning a capability into something that other tools can invoke.

It demonstrates several distinct engineering activities:

- **Systems integration:** coordinating Python, Pandoc, Chromium, LaTeX, and other external programs.
- **Interface design:** providing both a desktop GUI and a machine-facing MCP interface.
- **Abstraction:** keeping rendering logic in a shared module rather than tying it entirely to one interface.
- **Workflow automation:** connecting conversion to AI-agent workflows and repository maintenance.

These are valuable skills for intelligent-systems engineering. They do not, by themselves, demonstrate that the implementation is fully robust or that every subsystem is understood in depth. The next step is to make the behavior observable and independently verifiable.

For your own learning, I would choose one complete path—Markdown input, backend selection, subprocess invocation, PDF validation—and be able to explain and debug each stage without relying on AI to make the diagnosis. That would convert a working AI-assisted prototype into a stronger demonstration of your own engineering capability.

## Final verdict

<box border radius="xl" padding={4} gap={3}>
  <title size="lg">A useful, composable engineering tool with a clear next step</title>
  `md2pdf-desktop` has a coherent purpose, multiple real rendering paths, a shared core, a desktop interface, and an MCP integration. Its strongest differentiator is the combination of document rendering with programmatic agent access.

  Its main weakness is not a lack of features. It is the gap between the documented capabilities and reproducible evidence that those capabilities work reliably together.

  **My recommendation:** prioritize shared orchestration, automated testing, and PDF validation before expanding the feature set. Those improvements would make the repository more credible as both a standalone utility and a component in your broader engineering ecosystem.
  <row gap={2} wrap="wrap">
    <button onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop")}>Open repository <icon name="arrow-up-right" size="xs" inline/></button>
    <button variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/main/md2pdf")}>Inspect conversion core</button>
    <button variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/main/mcp_server")}>Inspect MCP server</button>
  </row>
</box>

---

## Turn 2

### User

perform a deeper pass this time

### Assistant

I’m going one layer below the README this time: repository history, full file topology, shared core, GUI, MCP contract, sync engine, and failure paths. The goal is to separate “feature-rich” from “actually robust.”

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I hit one practical limitation: GitHub’s connector can read the repository, but the runtime cannot clone it directly. I’m compensating by inspecting the source through GitHub at line level rather than treating the README as ground truth.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Yes. I went substantially deeper this time, including the **actual current `main` tree as of September 29, 2026**, recent commit history, the full application flow, conversion core, MCP layer, templates, and the synchronization tooling.

One important correction from my previous pass: **the repository was updated today, September 29, with `sync.bat`**. The latest commit is `3ade282` and adds only that 14-line wrapper; the substantial rendering/UI work is still from September 24. The current tree contains 14 tracked paths, including a duplicated `templates/` directory. 

# Deep evaluation

## Overall: **7.2/10 engineering maturity**

But that number hides an important distinction:

| Dimension | Assessment |
|---|---|
| Product idea | **8.5/10** |
| Architecture | **8.0/10** |
| Feature implementation | **8.0/10** |
| Integration / composability | **8.5/10** |
| Error handling | **5.5/10** |
| Reproducibility | **5.0/10** |
| Testing / verification | **3.5/10** |
| Security / trust boundaries | **5.5/10** |
| Repository hygiene | **6.0/10** |
| Portfolio signal | **8.0/10** |

The key finding is:

> **The project has crossed the “interesting prototype” threshold. It has not yet crossed the “demonstrably reliable engineering tool” threshold.**

And the gap is surprisingly concentrated. You don't need another 10 features. You need **verification, determinism, and failure semantics**.

---

# 1. The architecture is genuinely better than it first appears

The repository is effectively:

```text
                    ┌──────────────────┐
                    │ Markdown source  │
                    └────────┬─────────┘
                             │
                     preprocessing
                             │
                    ┌────────▼─────────┐
                    │  md2pdf/core.py  │
                    └──────┬─┬─┬──────┘
                           │ │ │
             ┌─────────────┘ │ └─────────────┐
             ▼               ▼               ▼
        Chromium          LaTeX           wkhtmltopdf
        + KaTeX           + pdflatex       + HTML
        + Mermaid
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                            PDF

             ▲               ▲
             │               │
        Tkinter GUI       MCP server
             │               │
             └────── same core ──────────┘
```

This is a good architectural instinct.

The important part is not “it has three backends.”

It is:

**you extracted the capability into a reusable conversion core, then put different interfaces around it.**

That pattern generalizes well to larger engineering systems.

The MCP server and desktop application both import the core rather than reimplementing the rendering engines independently. That is one of the strongest aspects of this repository.

---

# 2. Your most interesting feature is actually MCP, not PDF conversion

The PDF converter itself is a useful utility.

The more strategically interesting part is:

```text
AI Agent
   ↓
MCP
   ↓
md2pdf tool
   ↓
shared conversion engine
   ↓
validated artifact
```

That changes the project's category.

It isn't merely:

> “I made a Markdown-to-PDF application.”

It can become:

> “I built a deterministic document-rendering capability that can be consumed interactively or programmatically by AI agents.”

That connects quite naturally with the architecture you're building elsewhere.

The current MCP layer exposes:

- conversion
- content detection
- environment/toolchain diagnostics

That's good composability.

The current repository therefore already contains the beginnings of a **tool-oriented engineering architecture**, rather than only a desktop application.

---

# 3. The biggest architectural weakness: there are actually multiple orchestrators

This is the most important design issue I found.

You have orchestration logic in at least three places:

### `md2pdf/core.py`

`convert_auto()`

### `mcp_server/server.py`

Its own `AUTO` selection logic.

### `md2pdf_app.py`

`_run_auto_detect()`

These do not behave identically.

For example:

### GUI

The GUI auto detector can change the selected mode to:

```text
sidebar_dark
sidebar_light
latex
```

and specifically sets **Sidebar Dark** when Sidebar is detected.

### MCP

The MCP server calls `convert_sidebar()` without exposing a theme parameter, so the default is **light**.

### Core

`convert_auto()` accepts a `theme` argument and has its own fallback chain.

Therefore:

```text
same Markdown
        ↓
GUI
        ↓
Sidebar Dark
```

versus:

```text
same Markdown
        ↓
MCP
        ↓
Sidebar Light
```

That directly conflicts with the README's claim that the surfaces provide identical behavior/output.

This is not a cosmetic issue.

It is an **orchestration ownership problem**.

## Better architecture

There should be exactly one canonical function:

```python
render_document(
    markdown,
    output_path,
    policy=...
)
```

and it should produce something like:

```python
ConversionResult(
    success=True,
    backend="sidebar",
    theme="light",
    fallbacks=[],
    warnings=[],
    output_path="...",
    output_size=...,
)
```

Then:

```text
GUI ───────┐
MCP ───────┼──> render_document()
CLI ───────┘
```

That would make the architecture considerably stronger.

---

# 4. There is a serious false-success problem

This is the most important implementation issue.

In Sidebar mode:

```python
p_res = subprocess.run(...)
if not os.path.isfile(save_path) or os.path.getsize(save_path) == 0:
    raise RuntimeError(...)
```

You don't actually check the Chromium process return code.

So the logic is effectively:

```text
Chromium says something went wrong
        ↓
output.pdf happens to exist
        ↓
application reports success
```

That is not a sufficient success criterion.

Even more importantly, there is no post-generation PDF validation.

A better contract is:

```text
process return code == 0
        AND
PDF exists
        AND
PDF parses successfully
        AND
PDF has >= 1 page
        AND
expected document content exists
```

For a document-processing application, that's much closer to what “successful conversion” should mean.

---

# 5. Sidebar rendering is not actually deterministic

This is a major issue that wasn't obvious from the README.

Your HTML wrapper loads:

```text
cdn.jsdelivr.net
```

for:

- KaTeX CSS
- KaTeX JS
- auto-render
- Mermaid.js

That means the conversion depends on an external network resource.

So the advertised pipeline:

```text
Markdown → Chromium → PDF
```

is really:

```text
Markdown
 ↓
Pandoc
 ↓
HTML
 ↓
Internet/CDN dependency
 ↓
KaTeX/Mermaid
 ↓
Chromium
 ↓
PDF
```

That means:

```text
offline machine
network outage
CDN outage
DNS failure
corporate proxy
changed CDN response
```

can potentially alter the rendering result.

For a document conversion utility, this is especially important because you describe the output as **publication-grade** and **vector**.

A stronger implementation would bundle the required JS/CSS locally:

```text
assets/
    katex.min.js
    katex.min.css
    mermaid.min.js
```

or generate the necessary resources into the temporary document.

Then:

```text
same input
+
same application version
+
same dependency versions
=
same rendering environment
```

That is a much stronger engineering story.

A current peer project in the same Chromium-based Markdown→PDF space explicitly emphasizes making the print document self-contained, including fonts, images, and diagrams. 

---

# 6. Your “smart page-break” claim is stronger than the implementation

This is a particularly clear documentation/code mismatch.

The README says Sidebar mode has smart page-break rules and describes preventing breaks inside:

- math
- tables
- code
- diagrams

But the CSS contains declarations such as:

```css
page-break-inside: auto;
break-inside: auto;
```

for those elements.

That is **not the same thing as preventing page breaks**.

Some browser pagination behavior may still produce acceptable results, but the source does not justify the stronger claim.

So I would change either:

### the implementation

to explicitly enforce the desired behavior,

or:

### the documentation

to accurately describe what Chromium actually guarantees.

This is exactly the kind of distinction an experienced reviewer notices.

---

# 7. The Markdown preprocessor is powerful, but too destructive

`clean_markdown_for_pdf()` is doing a lot:

- ASCII table conversion
- Unicode normalization
- emoji removal
- Mermaid transformation
- math symbol translation
- delimiter normalization

Conceptually, that's good.

Implementation-wise, it is overly global.

For example:

```python
text = text.replace('│', '|')
text = text.replace('─', '-')
text = text.replace('°', ' deg')
```

and:

```python
text = text.replace('∨', r' $\lor$ ')
```

operate on the entire Markdown document.

That means the converter can modify content that the user intended to preserve literally.

Imagine:

```markdown
```text
temperature °C
A │ B
x ∨ y
```
```

Your preprocessing is capable of altering that code block.

That's a semantic transformation.

The same problem exists with ASCII table detection: a fenced code block that happens to look like an ASCII table may be converted into a real Markdown table even when the user intended it as code.

## Better model

Parse by context:

```text
Markdown document
 ├── prose
 ├── code fence
 ├── math
 ├── HTML
 ├── Mermaid
 └── table
```

Then transform only the specific node types you intend to transform.

That means an AST-oriented approach is the natural next step.

Ironically, your README already calls these functions “AST sanitizers,” but most of the implementation is actually regex/string preprocessing rather than AST transformation.

That's another wording mismatch I'd fix.

---

# 8. `convert_auto()` hides too much

This function contains the pattern:

```python
try:
    convert_sidebar(...)
except Exception:
    pass
```

That makes the system resilient in one sense, but opaque in another.

You can end up with:

```text
Sidebar failed
     ↓
exception swallowed
     ↓
LaTeX attempted
     ↓
maybe Simple
     ↓
PDF produced
```

The caller may not know that the requested or automatically selected renderer failed.

For an engineering tool, fallback should be **observable**.

Something like:

```text
attempt 1:
    sidebar
    failed: Mermaid render timeout

attempt 2:
    latex
    skipped: unsupported Mermaid semantics

attempt 3:
    simple
    succeeded
```

would be much better.

This is especially important when an AI agent is consuming the tool.

An agent needs to know:

> “I produced the requested high-fidelity artifact.”

versus:

> “I produced a degraded fallback artifact.”

Those are materially different results.

---

# 9. MCP auto-mode contains a particularly important edge case

The server performs this logic:

```text
if Sidebar required and available
    → Sidebar

otherwise:
    detect LaTeX
    → LaTeX if available
    → otherwise Simple
```

But it does not perform the same comprehensive availability/failure handling as the core orchestrator.

The worst edge is:

```text
no Sidebar
no LaTeX
```

followed by selecting Simple without first establishing that both:

```text
pandoc
wkhtmltopdf
```

are actually usable.

The explicit Simple branch checks dependencies.

The automatic branch is less rigorous.

That's exactly the kind of bug that won't appear in normal development because the developer machine usually has all the tools installed.

---

# 10. The GUI isn't actually responsive during conversion

This is another source-level finding that matters.

`convert()` calls:

```python
convert_sidebar(...)
convert_latex(...)
convert_simple(...)
```

directly from the Tkinter event loop.

Those invoke external processes.

Sidebar even has a timeout of up to 60 seconds.

Therefore:

```text
Export
 ↓
Tkinter main thread blocked
 ↓
window stops responding
 ↓
conversion finishes
 ↓
UI resumes
```

So the interface can look polished while behaving synchronously.

The correct architecture would be:

```text
Tkinter UI thread
       │
       ├── enqueue conversion
       ▼
worker thread/process
       │
       ▼
converter
       │
       ▼
result queue
       │
       ▼
UI updates
```

Then you can actually provide:

- cancellation
- progress state
- asynchronous diagnostics
- responsive UI
- conversion timing

That would make the “Studio” concept much more credible.

---

# 11. Your timeouts are inconsistent

Sidebar:

```text
timeout=60
```

Simple:

no timeout

LaTeX:

no timeout

That means an accidental or broken external process can hang Simple or LaTeX indefinitely.

For a multi-backend system, subprocess lifecycle management should be centralized.

Something like:

```python
run_tool(
    command,
    timeout=...
)
```

would give all backends consistent behavior.

---

# 12. The LaTeX health check is useful—but narrower than advertised

`probe_latex_template()` is a good idea.

This is one of the better engineering touches in the repository.

But the probe is basically:

```text
# Probe

Hello $x^2$.
```

It therefore confirms roughly:

```text
Pandoc
+
pdflatex
+
basic template compilation
```

It does **not** demonstrate:

- Lua filter correctness
- callout box rendering
- long tables
- code wrapping
- Unicode behavior
- page breaks
- all packages
- complex math

So “template compiles” is supported.

“the LaTeX conversion pipeline is healthy” is a stronger claim.

The next step is to turn the probe into an actual fixture suite.

---

# 13. `sync.ps1` is much more ambitious—and more dangerous—than I initially gave it credit for

This is probably the most interesting non-PDF piece of the repository.

It contains:

- pull/rebase
- branch management
- push
- auto commit messages
- security scanning
- toolchain health
- status telemetry
- dry-run mode
- test mode

That is genuinely substantial scripting.

But I found several concerns.

## `Ensure-RemoteConfigured`

It hard-codes:

```text
https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop.git
```

and can change the `origin` URL.

That is surprising behavior for a generic synchronization script.

Someone clones the repository, changes `origin` to their fork, and the script can replace it.

For a personal workflow script this may be intentional.

For a public repository, I would not make it automatic.

---

## `-WhatIf` isn't completely read-only

The script does:

```text
git add -A
...
git reset --quiet
```

So it modifies the staging state during a supposedly dry-run operation.

If the user already had intentionally staged changes, this can disturb that state.

That's a real design flaw.

---

## The script can commit unrelated changes

The normal path performs:

```text
git add -A
git commit
```

That means:

```text
feature changes
+
unrelated personal edits
+
temporary tracked modifications
```

can become one commit.

For a personal “sync everything” workflow, perhaps intentional.

For a reusable engineering repository, dangerous.

---

## Secret scanning is useful but heuristic

The regex scanner catches several common token patterns, which is helpful.

But:

```text
pattern matching ≠ secret detection
```

It will have false positives and false negatives.

For your purpose, that's fine as an additional guard.

I wouldn't describe it as a complete security gate.

---

# 14. The new `sync.bat` is useful, but tiny relative to the rest of the engineering problem

Today's commit:

```text
3ade282
chore(scripts): add sync.bat
```

simply wraps `sync.ps1` and bypasses PowerShell execution policy using:

```text
-NoProfile -ExecutionPolicy Bypass
```

That is a convenience improvement for Windows users.

It does **not** meaningfully alter the engineering maturity of the core application.

The repository's recent development history is much more revealing:

```text
Sep 19
 ├── LaTeX fixes
 ├── sync.ps1
 ├── engine automation
 └── styling

Sep 24
 ├── Chromium renderer
 ├── UI overhaul
 ├── light print theme
 └── README rewrite

Sep 29
 └── sync.bat
```

You have had a very feature-dense period followed by a small workflow convenience commit.

What is missing in that sequence is:

```text
tests
validation
CI
fixtures
benchmarking
packaging
```

That's where I'd redirect the development energy now.

---

# 15. There is an odd repository hygiene issue: duplicated templates

The current repository tree contains both:

```text
templates/
    styled.latex
    callout-boxes.lua
```

and:

```text
md2pdf/templates/
    styled.latex
    callout-boxes.lua
```

The files have identical Git object SHAs.

But the application points to:

```python
PACKAGE_DIR / "templates"
```

inside `md2pdf`.

Therefore the root-level copy appears redundant.

This creates unnecessary ambiguity:

```text
Which templates are authoritative?
```

A future developer can modify:

```text
templates/styled.latex
```

and nothing changes.

That's a classic repository hygiene trap.

Remove the duplicate unless there is a deliberate packaging reason for it.

---

# 16. Packaging is missing

There is no visible:

```text
pyproject.toml
setup.cfg
setup.py
```

and no CLI entry point.

That means the project is currently more:

```text
"clone this repository and run these files"
```

than:

```text
"install this tool and use it"
```

For your own machine that's completely acceptable.

For a portfolio project, adding packaging would materially strengthen it.

For example:

```text
pipx install md2pdf-desktop
md2pdf ...
```

or a proper application release would push it toward software distribution rather than repository code.

---

# 17. Reproducibility is weak

`requirements.txt` says:

```text
mcp[cli]<2
pydantic>=2
```

The first is constrained.

The second is open-ended.

Meanwhile the important rendering dependencies are external:

```text
Pandoc
Chromium
Mermaid CDN
KaTeX CDN
wkhtmltopdf
pdflatex
LaTeX packages
```

That's a lot of environmental variance.

For deterministic document generation, dependency versions matter.

A strong release would document something like:

```text
Python
Pandoc
Chrome/Edge
KaTeX
Mermaid
TeX Live
wkhtmltopdf
```

and ideally test against known versions.

---

# 18. There is no evidence yet that “publication-grade” is reproducibly true

This is perhaps the most important philosophical point.

Your README uses language such as:

> publication-grade

and

> textbook-grade

Those are outcome claims.

At the source level, I can see serious effort toward those outcomes.

But I don't yet see:

```text
benchmark corpus
+
expected output
+
regression tests
+
PDF validation
+
visual regression
```

Therefore the repository currently demonstrates:

**engineering intent + substantial implementation**

rather than:

**demonstrated rendering quality under regression testing**

That's the distinction I'd want you to internalize.

---

# 19. What I would actually test

This project is unusually well suited to fixture-based testing.

Create:

```text
tests/
    fixtures/
        basic.md
        math.md
        tables.md
        mermaid.md
        gfm-alerts.md
        unicode.md
        code-heavy.md
        long-document.md
        adversarial.md
```

Then test:

```text
input
 ↓
detector
 ↓
selected backend
 ↓
conversion
 ↓
PDF parser
 ↓
assertions
```

For example:

```text
math.md
    → Sidebar
    → PDF exists
    → PDF parses
    → equation text exists

mermaid.md
    → Sidebar
    → PDF parses
    → SVG-derived content exists

plain.md
    → Simple

broken toolchain
    → structured error

invalid output directory
    → structured error

huge document
    → timeout rather than hang
```

That would do more for this repository than another visual redesign.

---

# 20. Your security boundary needs to be explicit

This matters particularly because you expose the functionality to AI agents.

The MCP tool can receive:

```text
output_path
```

and write to that filesystem location.

That is powerful.

Additionally, both HTML/PDF pipelines enable local resource access in places, and Sidebar rendering loads JavaScript.

For a personal local MCP server, this may be acceptable.

But architecturally I'd define:

```text
trusted local Markdown
```

versus:

```text
untrusted agent-generated Markdown
```

as two different threat models.

A future safe mode could restrict:

```text
output directory
local file references
HTML
external URLs
JavaScript
```

That would make the MCP capability much more defensible.

---

# 21. The GUI has several smaller quality issues

Some additional findings:

### Auto-detection behavior is inconsistent

When Sidebar content is detected, GUI auto-selection explicitly chooses:

```text
sidebar_dark
```

even though light is now your stated default print theme.

### Detection doesn't necessarily reset the mode

A document can transition:

```text
math → no math
```

while the selected engine remains LaTeX even after the detector says the document is now plain.

### Error handling is uneven

`paste_clipboard()` silently swallows all exceptions.

`open_file()` doesn't protect file-reading operations.

`open_output_folder()` doesn't verify subprocess success.

These aren't architectural failures, but they are exactly the polish you'd address before calling something production-ready.

---

# 22. What is actually excellent here

After going deeper, I would **increase** my assessment of several aspects.

### Shared-core extraction

Very good.

### MCP integration

Very good.

### Backend diversity

Strong.

### Dependency probing

Good engineering instinct.

### Dedicated LaTeX template

Good.

### Custom preprocessing

Ambitious and useful.

### Desktop + headless operation

Excellent product architecture.

### Synchronization automation

Technically substantial, although it needs safety refinement.

The project is definitely not “just a script.”

---

# 23. The bigger issue: your architecture is ahead of your verification

This is the central conclusion of the deeper pass.

You've already accumulated:

```text
GUI
+
MCP
+
multiple renderers
+
automatic detection
+
custom templates
+
preprocessing
+
toolchain detection
+
automation
+
sync tooling
```

That's a lot.

But the engineering evidence is still:

```text
implementation >> verification
```

I would reverse that relationship now.

For the next phase:

```text
implementation
      ↓
tests
      ↓
fixtures
      ↓
validation
      ↓
observability
      ↓
only then new features
```

---

# 24. What would move this to ~8.5+

I would make the next major version approximately:

```text
md2pdf/
    core/
        parser.py
        transforms.py
        detectors.py
        renderers/
            chromium.py
            latex.py
            simple.py
        orchestrator.py
        result.py
        validation.py

    assets/
        katex/
        mermaid/

tests/
    unit/
    integration/
    fixtures/
    regression/

scripts/
    sync.ps1
    sync.bat

pyproject.toml
LICENSE
CHANGELOG.md
```

Then the public contract becomes something like:

```text
Markdown
   ↓
parse
   ↓
normalize
   ↓
classify
   ↓
select renderer
   ↓
render
   ↓
validate PDF
   ↓
ConversionResult
```

That would be an appreciably more mature architecture.

---

# 25. Career/portfolio interpretation

This project gives me a somewhat different impression of your direction than a conventional student portfolio.

The interesting part isn't that you can write Python or Tkinter.

It's the pattern:

```text
messy real-world requirement
        ↓
multiple implementation constraints
        ↓
toolchain composition
        ↓
shared abstraction
        ↓
automation interface
        ↓
artifact generation
```

That pattern is much closer to **systems/integration engineering** than ordinary beginner application development.

It also fits particularly well with the direction you've been exploring in `brainstorm`: building infrastructure around AI-assisted engineering rather than only building isolated ML models.

But there's a trap here.

You could keep adding:

```text
another engine
another UI feature
another automation script
another MCP tool
another styling system
```

and become extremely good at **assembling increasingly complicated prototypes** without developing equivalent depth in verification and failure analysis.

This repository is actually an excellent place to break that pattern.

Take ownership of:

```text
Why did this renderer fail?
Why did auto-selection choose this backend?
Why did this PDF differ?
How do I prove the PDF is correct?
What is the trust boundary?
What happens under timeout?
What happens offline?
What happens with malformed Markdown?
```

Those questions will teach you considerably more engineering than adding another feature.

---

# Final assessment

## `md2pdf-desktop` is now a real engineering project, but its next evolution should be from **feature-rich** to **evidence-rich**.

The architecture is good enough to preserve.

I would **not** rewrite the project from scratch.

I would instead make five architectural corrections:

```text
1. One canonical renderer/orchestrator
2. Deterministic/self-contained rendering assets
3. Real PDF/output validation
4. Automated fixture + regression tests
5. Asynchronous GUI + structured failures
```

Then clean up:

```text
duplicate templates
hard-coded remote behavior
missing packaging
missing license
README/source mismatches
```

One especially encouraging fact is that the latest September 29 change was only a convenience wrapper, while the major September 24 work already established the core architecture. That means the repository is at a good **stabilization point** rather than needing another architectural explosion.

For comparison, current Markdown→PDF tooling is increasingly emphasizing self-contained rendering, deterministic pagination, and explicit document-processing pipelines rather than merely calling a browser to print HTML. 

urlOpen the current repositoryhttps://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop

I can next turn this exact audit into a **researcher-grade issue backlog with P0/P1/P2 findings mapped to specific files/functions and an implementation order**.

---

## Turn 3

### User

can you provide me updated repo files

### Assistant

Yes. I’m going to turn the audit into a concrete stabilization update rather than just hand you recommendations: canonical orchestration, structured results, safer subprocess handling, validation, cleaner packaging, and regression tests.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I’ve prepared an updated version of your `md2pdf-desktop` repository on a separate GitHub branch, with a draft pull request for review. **Your `main` branch has not been changed.**

<box border radius="xl" padding={4} gap={3}>
  <row align="center" gap={2}>
    <icon name="git-pull-request" size="2xl"/>
    <box flex="1" gap={1}>
      <title size="lg">Stabilization pass</title>
      <text color="secondary" size="sm">September 29, 2026 · Pull request #1</text>
    </box>
    <badge color="warning">Draft</badge>
  </row>
  <title size="md">Stabilize conversion orchestration and PDF validation</title>
  The update focuses on reliability, consistent automatic backend selection, PDF integrity checks, automated tests, and more accurate documentation.
  <button block onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1")}>Review updated files and diff <icon name="arrow-up-right" size="sm" inline/></button>
  <button block variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/stabilization-pass-2026-09-29")}>Browse complete branch <icon name="github" size="sm" inline/></button>
</box>

## 1. Updated files

<box border radius="lg" gap={0}>
  {#each [{path:"md2pdf/core.py",desc:"Process timeouts, PDF integrity validation, and observable renderer fallback."},{path:"md2pdf/__init__.py",desc:"Exports the PDF validation helper."},{path:"mcp_server/server.py",desc:"Routes automatic conversion through the shared core orchestrator."},{path:"tests/test_core.py",desc:"Six regression tests for PDF validation and fallback behavior."},{path:".github/workflows/tests.yml",desc:"Automated tests on Python 3.10, 3.11, and 3.12."},{path:"README.md",desc:"Portable links, corrected rendering claims, and testing instructions."},{path:"docs/STABILIZATION_NOTES.md",desc:"Documents the changes, validation limits, and remaining risks."}] as file,i}
    {#if i>0}<divider color="subtle"/>{/if}
    <pressable padding={3} onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/stabilization-pass-2026-09-29/"+file.path)}>
      <row align="start" gap={2}>
        <icon name="file-code" size="lg" color="secondary"/>
        <box flex="1" gap={1}>
          <text weight="medium">{file.path}</text>
          <text color="secondary" size="sm">{file.desc}</text>
        </box>
        <icon name="arrow-up-right" size="sm" color="secondary"/>
      </row>
    </pressable>
  {/each}
</box>

## 2. What changed in the code

- **PDF validation:** rejects missing, truncated, empty, or obviously invalid PDF output.
- **Subprocess management:** introduces bounded execution and clearer errors for missing executables and timeouts.
- **Automatic fallback:** records which renderer failed and returns the backend that actually succeeded.
- **MCP consistency:** automatic conversion uses the shared orchestration logic instead of a separate selection implementation.
- **Documentation:** removes machine-specific file links and clarifies that browser pagination and rendering still require verification.

## 3. Test status

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle" color="success" size="lg"/>
    <box flex="1" gap={1}>
      **Initial CI run passed**
      <text color="secondary" size="sm">The regression suite completed successfully on an earlier branch revision.</text>
    </box>
    <button size="sm" variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/actions/runs/36605896964")}>View</button>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={2}>
    <icon name="clock" color="warning" size="lg"/>
    <box flex="1" gap={1}>
      **Latest verification pending**
      <text color="secondary" size="sm">A stricter PDF page-object check exposed a test-fixture issue. I corrected the regex and triggered new CI runs, but I haven't confirmed their final result yet.</text>
    </box>
  </row>
  <button block variant="outline" onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/actions")}>Check latest CI results <icon name="arrow-up-right" size="xs" inline/></button>
</box>

## 4. What remains unfinished

This is a targeted stabilization pass, not a claim that the application is production-ready. Remote CDN dependencies, global Markdown replacements, synchronous GUI conversion, and the synchronization script's staging behavior still need attention. These are recorded in the [stabilization notes](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/blob/stabilization-pass-2026-09-29/docs/STABILIZATION_NOTES.md).

**Recommended next step:** review the draft pull request, confirm the latest CI run is green, and then decide whether to merge. I have left the pull request in draft rather than merging unverified changes into `main`.

---

## Turn 4

### User

[Skip to content](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1#start-of-content)

1. [Aaradhya-Dev-Tamrakar](https://github.com/Aaradhya-Dev-Tamrakar)
2. [**md2pdf-desktop**](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop)

## Repository navigation

- [Code](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop)
- [Issues](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/issues)
- [**Pull requests**](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pulls)[ (1)](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pulls)
- [Agents](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/agents?author=Aaradhya-100)
- [Actions](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/actions)
- [Projects](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/projects)
- [Security and quality](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/security)
- [Insights](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pulse)
- [Settings](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/settings)

# **Stabilize conversion orchestration and PDF validation- #1**

**Pull requestDraft**

[**Aaradhya-100**](https://github.com/Aaradhya-100)wants to merge 11 commits into

[main](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/main)from

[stabilization-pass-2026-09-29](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/stabilization-pass-2026-09-29)

Lines changed: 306 additions & 54 deletions

[Conversation (0)](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1)[Commits (11)](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits)[Checks (6)](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/checks)[Files changed (7)](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/changes)

**Pull requestDraft**

## [**Stabilize conversion orchestration and PDF validation**](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1#top)**#1**

[**Aaradhya-100**](https://github.com/Aaradhya-100)**wants to merge 11 commits into**

[**main**](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/main)**from**

[**stabilization-pass-2026-09-29**](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/tree/stabilization-pass-2026-09-29)

## Conversation

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=80\&v=4))

### [**Aaradhya-100**](https://github.com/Aaradhya-100)commented[3 minutes ago](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1#issue-5634524902)

**Show options**

**Member**

## Summary

This stabilization pass addresses the highest-priority reliability findings from the repository audit.

### Changes

- Add bounded subprocess execution with normalized missing-executable, timeout, and OS errors.
- Validate generated PDFs for signature, EOF marker, and detectable page objects.
- Check Chromium's process return code before accepting output.
- Make automatic backend fallback observable and return the backend that actually succeeded.
- Route MCP auto mode through the shared core orchestrator.
- Add standard-library unit tests and Python 3.10–3.12 GitHub Actions coverage.
- Replace machine-local README links and qualify rendering/pagination claims.
- Document remaining limitations and follow-up work.

### Important limitations

This is not a complete production-hardening pass. Sidebar assets still load from CDNs, global Markdown replacements remain, and the Tkinter conversion path is still synchronous. The PDF validator is intentionally lightweight and does not prove visual correctness. See `docs/STABILIZATION_NOTES.md`.

### Verification

GitHub Actions runs are being triggered for the branch. Earlier runs for the test suite completed successfully; the latest commit's run is still queued at the time this PR was opened.

[**Aaradhya-100**](https://github.com/Aaradhya-100) added 11 commits [5 minutes ago](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1#commits-pushed-0ff48ec)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`fix(core): validate PDFs and make auto fallback observable`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/0ff48ec61a4f48eb279e3b771595fd28034ca406 "fix(core): validate PDFs and make auto fallback observable")

[`0ff48ec`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/0ff48ec61a4f48eb279e3b771595fd28034ca406)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`chore(api): export PDF validation helper`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/9a5b69bb3f57106f39bc93ba64980fe370105226 "chore(api): export PDF validation helper")

[`9a5b69b`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/9a5b69bb3f57106f39bc93ba64980fe370105226)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`fix(mcp): route auto mode through shared orchestrator`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/d36f445b0e3047eae40f529b0cc371245e2bf7a7 "fix(mcp): route auto mode through shared orchestrator")

[`d36f445`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/d36f445b0e3047eae40f529b0cc371245e2bf7a7)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`test(core): cover PDF validation and auto fallback`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/03e746dd3931c2a803b8255becdae0eac8681a0d "test(core): cover PDF validation and auto fallback")

[`03e746d`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/03e746dd3931c2a803b8255becdae0eac8681a0d)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`fix(core): scan large PDF outputs without loading whole file`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/dcce1d6526fa561b06b64bb1c4002660ec98d8fc "fix(core): scan large PDF outputs without loading whole file")

[`dcce1d6`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/dcce1d6526fa561b06b64bb1c4002660ec98d8fc)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`ci: run core regression tests on supported Python versions`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/7c360536c941688fffec4f88889181600b1b30aa "ci: run core regression tests on supported Python versions")

3 / 3 checks OK

[`7c36053`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/7c360536c941688fffec4f88889181600b1b30aa)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`docs: record stabilization changes and remaining risks`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/f717502e407d697112269aa9b5e8466e13549191 "docs: record stabilization changes and remaining risks")

3 / 3 checks OK

[`f717502`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/f717502e407d697112269aa9b5e8466e13549191)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`docs(readme): fix portable links and qualify rendering guarantees`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/98232797371c8a01687b6e37fa0785788de66b4a "docs(readme): fix portable links and qualify rendering guarantees")

3 / 3 checks OK

[`9823279`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/98232797371c8a01687b6e37fa0785788de66b4a)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`fix(core): distinguish page objects from page tree markers`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/6afc9f5cfa3480f5520ea09007f4d1b28a120466 "fix(core): distinguish page objects from page tree markers")

0 / 3 checks OK

[`6afc9f5`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/6afc9f5cfa3480f5520ea09007f4d1b28a120466)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`docs: align minimum Python version with type syntax`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/77cc91648d397b2fad6bfbac4e87d447823574de "docs: align minimum Python version with type syntax")

0 / 6 checks OK

[`77cc916`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/77cc91648d397b2fad6bfbac4e87d447823574de)

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=40\&v=4))

[`fix(core): correct PDF page-object detection regex`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/922d1885b3f9f9fe356f5626890384a35596ff03 "fix(core): correct PDF page-object detection regex")

6 / 6 checks OK

[`922d188`](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/commits/922d1885b3f9f9fe356f5626890384a35596ff03)

## Merge info

Not ready

### All checks have passed

6 successful checks

### No conflicts with base branch

Merging can be performed automatically.

### This pull request is still a work in progress

Draft pull requests cannot be merged.

You can also merge this with the command line. 

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=80\&v=4))

#### Add a comment

**Comment**

Remember, contributions to this repository should follow our [GitHub Community Guidelines](https://docs.github.com/articles/github-community-guidelines).

**ProTip!** Add comments to specific lines under [Files changed](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/1/files).

**Reviewers**

Suggestions

[@AaradhyaDT](https://github.com/AaradhyaDT) ([image](https://avatars.githubusercontent.com/u/118439108?s=40\&v=4))[**AaradhyaDT**](https://github.com/AaradhyaDT)

**Assignees**No one—

**Labels**

None yet

**Projects**

None yet

**Milestone**No milestone

**Development**

Successfully merging this pull request may close these issues.

None yet

**Notifications**

Customize

You’re receiving notifications because you authored the thread.

### 1 participant

[@Aaradhya-100](https://github.com/Aaradhya-100) ([image](https://avatars.githubusercontent.com/u/84552386?s=52\&v=4))

**Archive pull request**

## Footer

© 2026 GitHub, Inc.

### Footer navigation

- [Terms](https://docs.github.com/site-policy/github-terms/github-terms-of-service)
- [Privacy](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement)
- [Security](https://github.com/security)
- [Status](https://www.githubstatus.com/)
- [Community](https://github.community/)
- [Docs](https://docs.github.com/)
- [Contact](https://support.github.com/?tags=dotcom-footer)
- Manage cookies
- Do not share my personal information

### Assistant

Yes — this PR page confirms the stabilization pass is now **passing cleanly**.

### Current state

**PR #1:** `Stabilize conversion orchestration and PDF validation`

- **Draft:** yes
- **Merge conflicts:** none
- **Checks:** **6/6 passed**
- **Latest commit:** `922d188` — `fix(core): correct PDF page-object detection regex`
- **Latest CI result:** passed
- **Files changed:** 7
- **Changes:** +306 / −54

The progression is actually useful: the first implementation exposed a bad PDF-test fixture, CI caught it, we corrected the page-object detection logic, and the final revision passed all six checks. That is exactly the kind of feedback loop the repository previously lacked.

### One thing I would clean up before merging

The PR has **11 commits for a 7-file stabilization change**. Most of those commits exist because the GitHub file API committed each individual edit separately:

```text
0ff48ec   core reliability
9a5b69b   API export
d36f445   MCP orchestration
03e746d   tests
dcce1d6   large-PDF scan
7c36053   CI
f717502   notes
9823279   README
6afc9f5   validator correction
77cc916   Python version docs
922d188   regex correction
```

Technically valid, but for the final repository history I'd prefer something like:

```text
feat(core): add validated conversion orchestration
test(core): add renderer fallback regression suite
ci: add Python compatibility tests
docs: document reliability guarantees and limitations
```

or even one clean stabilization commit if this is intended as a single maintenance milestone.

### More importantly: the PR has accomplished what we wanted

The repository now has a documented and tested progression from:

```text
renderer exists
      ↓
renderer output may exist
      ↓
renderer output is checked
      ↓
automatic fallback is observable
      ↓
MCP uses the same orchestration
      ↓
CI continuously exercises the core
```

That materially improves the engineering quality of `md2pdf-desktop`.

The remaining issues are now clearly **second-phase work**, not blockers to the stabilization pass:

```text
CDN assets
AST-aware Markdown transformations
async Tkinter conversion
sync.ps1 safety
real renderer integration tests
full PDF parser validation
packaging/release
```

So the PR page you're seeing is essentially the outcome we were aiming for: **the reliability pass is now green; the next question is repository-history cleanup versus moving on to the next engineering phase.**

---

## Turn 5

### User

next phase now

### Assistant

Phase 2 should move the repo from “stabilized” to “productized”: safer document transforms, responsive desktop execution, installable packaging, and real regression coverage—without rewriting the renderer core.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I’m tightening the next layer now: code blocks will become protected regions during normalization, so the converter stops “fixing” literal code or examples accidentally. This is a safer transformation model without introducing a heavy parser dependency.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Phase 2 is underway in a separate draft PR, building on the stabilization branch rather than changing `main`.

<box border radius="lg" padding={4} gap={3}>
  <row align="center" gap={2}>
    <icon name="git-pull-request" size="xl" />
    <box flex="1" gap={1}>
      **Phase 2 — Productization**
      <text color="secondary" size="sm">PR #2 · Draft · Not merged</text>
    </box>
    <badge color="warning">Validation in progress</badge>
  </row>
  <button block onClick={() => GenUI.openUrl("https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/2")}>Open Phase 2 PR <icon name="arrow-up-right" size="sm" /></button>
</box>

The scope is now broader than adding features: make Markdown transformations safer, give the renderer a usable command-line interface, and establish regression tests before moving into more invasive GUI and rendering changes.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

## What has been implemented

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="terminal" size="xl" />
    </box>
    <box flex="1" gap={1}>
      **1. Command-line interface**
      <badge color="success">Added</badge>
      <text color="secondary" size="sm">New `md2pdf/cli.py`</text>
      Convert files with `auto`, `sidebar`, `latex`, or `simple` mode. Supports output paths, margins, and Sidebar themes, with explicit error exit codes.
    </box>
  </row>
  <divider color="subtle" />
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="package-check" size="xl" />
    </box>
    <box flex="1" gap={1}>
      **2. Installable Python package**
      <badge color="success">Added</badge>
      <text color="secondary" size="sm">New `pyproject.toml`</text>
      Defines Python 3.10+, the CLI entry point, and packaging rules for the LaTeX template and Lua filter.
    </box>
  </row>
  <divider color="subtle" />
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="shield-check" size="xl" />
    </box>
    <box flex="1" gap={1}>
      **3. Context-aware Markdown normalization**
      <badge color="success">Implemented</badge>
      Ordinary fenced code is now protected from global Unicode substitutions. Mermaid diagrams and explicitly labelled ASCII tables retain their special handling, and unclosed code fences are covered by the new protection logic.
    </box>
  </row>
  <divider color="subtle" />
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="test-tube" size="xl" />
    </box>
    <box flex="1" gap={1}>
      **4. Regression tests**
      <badge color="warning">Rerun needed</badge>
      Added tests for preserving code blocks, Mermaid conversion, and unclosed fences. The first CI run exposed two test failures caused by malformed newline fixtures; those fixtures were corrected, but I haven't verified a successful rerun.
    </box>
  </row>
</box>

## How to try the CLI after installing from the checkout

```powershell
python -m pip install .
md2pdf notes.md --mode auto --output notes.pdf
```

Pandoc and the selected external renderer must still be installed separately.

## What comes next

I would tackle these in order:

1. **Verify CI and packaging.** Confirm the full test matrix passes and that a built wheel contains the required templates.
2. **Make the desktop GUI responsive.** Move conversion into a worker thread, disable conflicting controls during conversion, and safely report completion or failure on the Tkinter main thread.
3. **Harden `sync.ps1`.** Prevent accidental staging of unrelated files and preserve pre-existing staged changes, especially in dry-run mode.
4. **Improve reproducibility.** Reduce CDN dependencies and add real-renderer integration tests that check generated PDFs, rather than relying only on mocked backends.
5. **Review release readiness.** Check dependency declarations, license status, installation instructions, and Windows packaging.

**Current status:** [Phase 2 PR #2](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/2) is open as a draft against the stabilization branch. It is not merged. I would keep it that way until the corrected tests pass and the packaging diff is reviewed.

---

### Assistant

The pasted PR snapshot shows a real regression: Phase 2 is currently blocked by **6 failing CI checks**, so I’m treating that as the next engineering task rather than advancing the feature set.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The CI failure is now isolated: the protection algorithm is fine, but the placeholder was written as the literal characters `\x00...` instead of an actual sentinel, so restoration never matched. I’m correcting that exact defect.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I found and fixed the actual Phase 2 blocker in PR #2.

The failure was not in the normalization idea itself: the fenced-block sentinel was emitted with the wrong escaping, so restoration never occurred. The latest commit corrects that and also fixes the indentation introduced while repairing it.

Current PR state:

- **PR #2:** Draft
- **Branch:** `phase2-productization-2026-09-29`
- **Latest commit:** `261938a`
- **Mergeable:** yes
- **CI:** newly triggered / not yet reported for the latest commit
- **Previous failing tests:** all three were the fenced-code tests; PDF validation and auto-orchestration were already passing. fileciteturn141file0L169-L202

The pasted PR page also confirms that earlier intermediate commits had passed their checks before the later fence changes introduced the regression. fileciteturn141file0L71-L167

[PR #2](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/2)

I would **not advance into the GUI async work yet** until this CI run turns green; otherwise we'd be stacking a second architectural change on top of an unverified core change.

---

## Turn 6

### User

all fail again

### Assistant

You’re right. I’m going back to the failing run itself and will fix the root cause rather than keep patching the tests around the symptoms.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I’ve corrected the source indentation error that caused all three Python versions to fail at import time. I’m independently syntax-checking and running the exact branch code before trusting another CI cycle.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Fixed. The **new CI run is green across all three supported Python versions**.

The previous failure shown in your pasted PR was an `IndentationError` in `md2pdf/core.py` at line 126, which prevented the test suite from importing at all. fileciteturn141file0L169-L200

I repaired the fenced-block scanner and pushed:

`4fc3b21` — `fix(core): repair fenced block scanner indentation`

Current GitHub Actions result:

| Python | Result |
|---|---|
| 3.10 | ✅ |
| 3.11 | ✅ |
| 3.12 | ✅ |

All **3/3 jobs passed**, including the complete regression suite.

So **PR #2 is no longer failing**. The Phase 2 core change is now technically validated.

[Open PR #2](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/2)

The next move should now be the **desktop GUI worker-thread refactor**, not another round of test patching.

---

## Turn 7

### User

okay do it

### Assistant

I’ll refactor the GUI conversion path so the Tkinter event loop stays responsive, while keeping all renderer logic in the shared core and preserving current UI behavior.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The conversion now runs in a daemon worker, while all Tk updates, dialogs, PDF launching, and button-state changes stay on the main thread. I’m adding a small regression around the worker result contract and updating the docs.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Done. The **desktop GUI worker-thread refactor is implemented and CI is green again**.

### What changed

`md2pdf_app.py` now:

- Runs PDF conversion in a background `threading.Thread`.
- Keeps the Tkinter main thread responsible for all UI operations.
- Uses a `queue.Queue` to pass worker results back safely.
- Polls the queue with `root.after(...)`, so the UI remains responsive.
- Disables the Export button during conversion and prevents duplicate conversions.
- Moves success/error dialogs back to the main thread.
- Moves PDF/folder launching into `_open_path()`.
- Preserves the existing renderer behavior for Sidebar, LaTeX, and Simple modes.

The README now documents responsive conversion, and I added regression tests covering both successful worker completion and renderer failure.

### Verification

Latest GitHub Actions run:

| Python | Result |
|---|---|
| 3.10 | ✅ |
| 3.11 | ✅ |
| 3.12 | ✅ |

**3/3 jobs passed.**

PR #2 remains a **draft** and is not merged.

[Open Phase 2 PR #2](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/2)

The next meaningful Phase 2 target is now **`sync.ps1` hardening + packaging verification**, followed by real renderer integration tests.

---

## Turn 8

### User

do that

### Assistant

I’ll harden `sync.ps1` first, then make packaging part of CI so the CLI and bundled templates are verified on every supported Python version. After that I’ll add a renderer smoke-test path that gracefully skips when the native toolchain is unavailable.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I found the next safety issue in `sync.ps1`: its `-WhatIf` mutates the Git index, and normal sync can mix pre-staged work with unrelated working-tree changes. I’m changing the script to fail safely on mixed staging and make dry-run completely read-only.

---

### Assistant

The edit itself hit a tooling-escaping issue before it touched the repository. I’m retrying with the same safety design but without PowerShell backticks inside the generated patch.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The repository is untouched by that workflow edit too; the failure was only JavaScript interpolation against GitHub’s `${{ ... }}` syntax. I’m applying it with literal strings now.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Packaging verification is now wired into the existing Python matrix. I’m adding one real end-to-end renderer test using Ubuntu’s available `pandoc` + `wkhtmltopdf` packages, so CI exercises the actual PDF pipeline rather than mocks.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The safety and packaging changes are in. One packaging detail also needed correction: the CLI smoke test must run outside the source checkout, otherwise Python could import the repository instead of the installed wheel. That is fixed too.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Done. This phase is now implemented and verified.

### What changed

**`sync.ps1` hardened**
- `-WhatIf` is now genuinely read-only; it no longer stages then resets the Git index.
- Mixed staged + unstaged/untracked work is rejected instead of silently combining unrelated changes.
- Existing staged work is preserved and committed as-is.
- `origin` is no longer silently rewritten. A missing/mismatched remote requires explicit `-RepairRemote`.
- Dry-run secret scanning now also examines untracked text files.
- `-Test` now runs the regression suite before the LaTeX probe.

**Packaging verification added**
- CI builds both sdist and wheel on Python 3.10, 3.11, and 3.12.
- CI inspects the wheel to ensure `styled.latex` and `callout-boxes.lua` are actually packaged.
- The installed CLI is smoke-tested **outside the repository checkout**, so the test proves the installed package rather than importing the source tree.

**Real renderer integration test added**
- New integration test invokes the actual `Pandoc → HTML → wkhtmltopdf → PDF` pipeline.
- CI installs those native tools and runs the real conversion.
- The resulting PDF is checked with the project's PDF validator.

### Current verification

Latest CI run is **4/4 green**:

| Check | Result |
|---|---|
| Python 3.10 unit/package | ✅ |
| Python 3.11 unit/package | ✅ |
| Python 3.12 unit/package | ✅ |
| Real renderer integration | ✅ |

The native integration uses `wkhtmltopdf`, which is available as an Ubuntu package alongside Pandoc. 

### Phase 2 status

PR #2 is still a **draft**, correctly so. The branch is now substantially stronger: core normalization is tested, the desktop conversion is asynchronous, packaging is exercised, synchronization is safer, and at least one renderer is tested end-to-end.

[Open PR #2](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/2)

The next engineering layer I'd put on this repo is **Sidebar/Chromium reproducibility**—especially removing the CDN dependency and making Mermaid/KaTeX rendering deterministic—because that is now the biggest remaining gap between “works” and a genuinely reproducible document tool.

---

## Turn 9

### User

ok do that

### Assistant

I’m taking the reproducibility pass now: first I’ll pin and vendor the exact browser-side assets, then make Sidebar fail clearly when assets are unavailable, and finally add an offline CI smoke test.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I verified the locked package sources before changing the renderer. I’m using exact npm package tarballs—KaTeX 0.16.11 and Mermaid 10.9.3—with SHA-512 integrity checks, rather than floating CDN URLs.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The local-cache path is in place. I’m tightening it one step further now: cached assets will carry a manifest and be re-hash-verified, so “local” also means “known, untampered bytes.”

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

I caught an integration gap before CI: `convert_sidebar()` was updated to call the new local-asset helper, but the helper itself wasn’t inserted. I’m fixing that now and adding direct tests so this class of omission cannot reach CI again.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The last write hit the same tooling-escaping trap because the test fixture itself contains Markdown backticks. I’m applying it as line arrays so the repository gets the intended content, not an escaped approximation.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Local assets and offline-mode CI are now wired. I’m updating the repository’s reproducibility contract and then I’ll watch the full matrix, including the new Sidebar end-to-end job.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The source changes are complete; the GitHub status probe briefly timed out. I’m rechecking the branch/PR directly rather than assuming the latest CI state.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

One final API cleanup before I call this phase complete: I’m exposing the asset provisioning helpers through the package namespace so the CLI, GUI, and future automation have one supported entry point.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The implementation is complete, but I found one documentation consistency issue: the stabilization notes still describe the GUI and sync engine as unresolved, although Phase 2 has already addressed both. I’m correcting that before the final status.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Done. The Sidebar reproducibility layer is now substantially upgraded on **Phase 2 / PR #2**.

### What changed

**Local browser assets**
`convert_sidebar()` no longer loads KaTeX or Mermaid from `cdn.jsdelivr.net` at render time.

It now uses a verified local asset cache containing:

- KaTeX **0.16.11**
- Mermaid **10.9.3**
- KaTeX CSS
- KaTeX JS
- KaTeX auto-render extension
- KaTeX font files
- Mermaid JS

KaTeX's own documentation supports hosting the distribution locally and explicitly requires its fonts alongside the stylesheet. 

**Integrity verification**

`md2pdf/web_assets.py` downloads the exact npm tarballs and verifies their SHA-512 integrity before extraction. The locked package metadata corresponds to KaTeX 0.16.11 and Mermaid 10.9.3. 

The extracted cache also gets a manifest containing SHA-256 hashes for the individual files. On subsequent runs, the cache is revalidated rather than blindly trusted.

**Offline mode**

You can now enforce zero network access during Sidebar rendering:

```powershell
$env:MD2PDF_OFFLINE="1"
python md2pdf_app.py
```

Or provision explicitly:

```powershell
python -m md2pdf.web_assets
python -m md2pdf.web_assets --offline
```

So the operational model is now:

`first provisioning → verify exact packages → local cache → offline rendering`

rather than:

`every render → remote CDN`.

**Chromium hardening**

The renderer now explicitly permits local file resources and no longer needs the previous insecure-content allowance.

**Tests**

Added coverage for:

- local `file://` asset generation
- version pinning
- integrity verification
- offline cache failures
- real Sidebar rendering with local KaTeX/Mermaid assets

CI now has a dedicated **Sidebar + Chromium integration job**, separate from the existing Pandoc/wkhtmltopdf integration job.

### One important distinction

This is **locally reproducible**, but not yet a completely self-contained source distribution: the first machine still needs network access to obtain the pinned npm archives. After that, the verified cache can operate offline.

That is a deliberate compromise because committing the complete Mermaid/KaTeX binary distributions—including fonts—would add substantial generated third-party payloads to the repository.

### Current branch

PR #2 remains draft and unmerged:

[Phase 2 PR #2](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/2)

The latest repository commit is `aafcf72`. GitHub has not surfaced a CI run for that final documentation-only commit through the connector yet, so I am **not** claiming the newest commit is green. The immediately preceding implementation CI had passed the Python matrix and real renderer jobs before the final documentation update.

The next logical step is now **PDF semantic validation + visual regression fixtures**, which would move the project from “renderer works and produces a structurally valid PDF” toward “the rendered document itself is automatically verified.”

---

## Turn 10

### User

first merge changes to main

### Assistant

I’ll merge the completed stabilization PR into `main` first, then rebase the Phase 2 work onto that new mainline so the history stays layered cleanly.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

PR #1 is now merged into `main` at `6b68872`. I’m switching PR #2’s base from the old stabilization branch to `main` so Phase 2 is now a clean incremental layer.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

Done.

### Mainline status

**PR #1 — Stabilization**
- ✅ Merged into `main`
- Merge commit: `6b688724fc82bae0272725f4161186d2b3bdc691`
- PR #1 is now closed/merged.
- `main` has advanced past the old `3ade282` baseline.

### Phase 2 status

PR #2 has been retargeted from the old stabilization branch to **`main`**.

- ✅ Base: `main`
- ✅ Base SHA: `6b68872…`
- ✅ Head: `aafcf72…`
- ✅ PR remains **Draft**
- ✅ Currently mergeable according to GitHub

So the repository history is now cleanly layered:

`main` ← **stabilization merged** ← **Phase 2 remains pending**

I did **not** merge Phase 2. That keeps the still-under-review productization/reproducibility work separate from the now-established stabilization baseline.

[View PR #2](https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop/pull/2)

---
