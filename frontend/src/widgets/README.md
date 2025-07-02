HiveWidget for MM App
====================

This is the official HiveOS widget for the MM App. It provides farm and rig management actions and status display for HiveOS users.

Installation
------------
1. Download the latest `hive.zip` from your trusted source or build it yourself (see below).
2. In the MM App admin panel, go to the Widget Manager and upload the `hive.zip` file.
3. The widget will appear in the available widgets list and can be enabled/added to your dashboard.

Widget Structure
----------------
The zip file should contain:

- `HiveWidget.vue` (the main widget component)
- `meta.json` (widget metadata)
- (optional) `README.md` (this file)

Example meta.json:
```json
{
  "name": "HiveOS Widget",
  "type": "hive",
  "description": "Manage and monitor your HiveOS farm and rigs.",
  "version": "1.0.0",
  "author": "Your Name or Org",
  "entry": "HiveWidget.vue"
}
```

Building the Zip
----------------
1. Place your `HiveWidget.vue` and `meta.json` in a folder named `hive`.
2. (Optional) Add a `README.md` for documentation.
3. Zip the contents of the `hive` folder (not the folder itself) so the zip root contains the files directly.

Example:
```
hive/
  HiveWidget.vue
  meta.json
  README.md
```

From inside the `hive` folder:
```bash
zip -r ../hive.zip *
```

Security Note
-------------
Only upload widgets from trusted sources. Widget code runs in the frontend and may access your API if not sandboxed.
