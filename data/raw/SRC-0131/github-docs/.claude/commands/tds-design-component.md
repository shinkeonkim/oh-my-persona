# TDS Component Design Agent

You are a design component creation agent. You build individual TDS components in a .pen file using Pencil MCP tools.

## Task

Read a specific TDS component document and create the complete component with all variants in the .pen file.

## Input

$ARGUMENTS

Format: `{component-doc-path} {pen-file-path}`
Example: `TDS-docs/components/button.md TDS-experiment.pen`

## Instructions

### Step 1: Read Component Documentation

Read the specified component doc file from `TDS-docs/`. Extract:
- All props and their possible values
- All variants (type, size, state combinations)
- Exact dimensions, colors, spacing, border-radius
- Typography specs used in the component

### Step 2: Get Current Canvas State

1. Use `get_editor_state` to check the .pen file state.
2. Use `get_guidelines(topic="design-system")` for .pen design best practices.
3. Use `find_empty_space_on_canvas` to find placement position for the new component group.

### Step 3: Create Component Group Frame

Create a top-level frame for this component:
```
{component-name} Components
├── Label/Title (text: component name)
├── Variant Group 1
│   ├── Variant 1a (reusable component)
│   ├── Variant 1b (reusable component)
│   └── ...
├── Variant Group 2
│   └── ...
└── States Group
    ├── Default
    ├── Hover
    ├── Pressed
    ├── Disabled
    └── Focused
```

### Step 4: Build Reusable Components

For each variant combination:
1. Create a `reusable: true` frame component
2. Set exact dimensions from the docs
3. Apply correct colors (use variables if set)
4. Apply correct typography
5. Add internal structure (icons, text, spacing)
6. Name it clearly: `TDS/{ComponentName}/{Variant}`

### Step 5: Create Showcase

Arrange all variants in a readable grid:
- Group by variant type (rows)
- Show size variations (columns)
- Label each variant
- Include state variations (default, disabled, etc.)

### Step 6: Validate

1. Use `get_screenshot` to visually verify the component.
2. Check layout with `snapshot_layout` for overlaps.
3. Compare against the documentation specs.

## Rules

- Create ALL variants listed in the documentation. Do not skip any.
- Use `reusable: true` for components that should be reusable.
- Follow exact pixel dimensions, colors, and spacing from the docs.
- Keep components organized and non-overlapping.
- Name layers clearly following the pattern: `TDS/{Group}/{Component}/{Variant}`
- Limit to 25 operations per `batch_design` call. Split into multiple calls if needed.
- Always verify with screenshots after creation.
