# 🎨 SmartFit CSS Review Scripts

These PowerShell scripts help review, reorganize, and replace CSS during the SmartFit frontend UI/UX polishing process.

## 📁 Folder Structure

```text
frontend/
└── scripts/
    ├── extract-css.ps1
    ├── replace-css.ps1
    ├── README.md
    └── css-review/
        └── CSS review and replacement files
```

The `css-review` folder is used for temporary CSS files created or used during the review process.

The scripts and this README remain directly inside the `scripts` folder.

---

## ▶️ Running the Scripts

The scripts are designed to be run from the **SmartFit project root**.

Example:

```text
SmartFit>
```

You do not need to change into the `frontend/scripts` directory.

---

# 1. Extract CSS

`extract-css.ps1` finds CSS rules related to a specific UI element and writes them to a separate review file.

This is useful when CSS for an element is spread across multiple stylesheets and needs to be reviewed before making changes.

### Usage

From the **SmartFit project root**:

```powershell
.\frontend\scripts\extract-css.ps1 `
    -Files "frontend\src\index.css","frontend\src\App.css" `
    -Element "navbar" `
    -Output "frontend\scripts\css-review\navbar-review.css"
```

### Example

To extract the existing Navbar CSS:

```powershell
.\frontend\scripts\extract-css.ps1 `
    -Files "frontend\src\index.css","frontend\src\App.css" `
    -Element "navbar" `
    -Output "frontend\scripts\css-review\navbar-review.css"
```

The script can identify selectors such as:

```css
.navbar
.navbar-brand
.navbar-links
.navbar-user
.navbar-logout
```

The original CSS files are **not modified** during extraction.

---

# 2. Review the Extracted CSS

After extraction, the review file will be placed inside:

```text
frontend/scripts/css-review/
```

For example:

```text
frontend/scripts/css-review/navbar-review.css
```

Review the existing CSS and prepare the improved version.

Save the improved version as:

```text
frontend/scripts/css-review/navbar-replacement.css
```

The `css-review` folder can therefore contain both:

```text
navbar-review.css
navbar-replacement.css
```

---

# 3. Replace CSS

`replace-css.ps1` replaces the existing CSS for a specific element with a new version.

It can also remove duplicate CSS for that element from other stylesheets.

### Usage

From the **SmartFit project root**:

```powershell
.\frontend\scripts\replace-css.ps1 `
    -TargetFile "frontend\src\index.css" `
    -CleanupFiles "frontend\src\App.css" `
    -Element "navbar" `
    -Replacement "frontend\scripts\css-review\navbar-replacement.css"
```

### What It Does

The replacement script:

1. Creates a backup of the target stylesheet.
2. Removes existing CSS for the specified element.
3. Inserts the replacement CSS.
4. Removes duplicate element-specific CSS from cleanup files.
5. Creates backups of modified cleanup files.
6. Leaves unrelated CSS unchanged.

For example:

```text
index.css
    ↓
Remove existing Navbar CSS
    ↓
Insert replacement Navbar CSS

App.css
    ↓
Remove duplicate Navbar CSS
    ↓
Keep global CSS
```

---

# 4. Recommended Workflow

For an element such as the Navbar, follow this workflow.

### Step 1 — Extract

Run from the SmartFit project root:

```powershell
.\frontend\scripts\extract-css.ps1 `
    -Files "frontend\src\index.css","frontend\src\App.css" `
    -Element "navbar" `
    -Output "frontend\scripts\css-review\navbar-review.css"
```

### Step 2 — Review

Open:

```text
frontend/scripts/css-review/navbar-review.css
```

Review the existing CSS.

### Step 3 — Prepare Replacement

Create:

```text
frontend/scripts/css-review/navbar-replacement.css
```

Place the improved CSS inside this file.

### Step 4 — Replace

Run:

```powershell
.\frontend\scripts\replace-css.ps1 `
    -TargetFile "frontend\src\index.css" `
    -CleanupFiles "frontend\src\App.css" `
    -Element "navbar" `
    -Replacement "frontend\scripts\css-review\navbar-replacement.css"
```

### Step 5 — Build

After replacing the CSS:

```powershell
cd frontend
npm run build
```

Then run the application and visually check the affected page.

---

# ⚠️ Important Notes

- Run both scripts from the **SmartFit project root**.
- Do not run the scripts from the `frontend/scripts` directory unless you have a specific reason to do so.
- `extract-css.ps1` does **not** modify the original CSS files.
- `replace-css.ps1` creates backups before modifying files.
- Do not use `-NoBackup` unless you deliberately do not want backups.
- Review extracted CSS before creating a replacement file.
- Only replace CSS for the element being polished.
- Always verify the frontend build after making CSS changes.
- The `css-review` folder is intended for CSS review and replacement files.
- These scripts are development utilities and are not part of the production application.

---

# 🎨 SmartFit CSS Organization

SmartFit uses the following CSS responsibility:

```text
App.css
└── Global application styling

index.css
└── Element and page-specific styling
```

The CSS review scripts help maintain this separation by allowing element-specific CSS to be extracted, reviewed, and reorganized without manually searching through large stylesheets.