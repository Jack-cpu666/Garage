# Python Version Fix for Render.com

## Problem

Render may default to Python 3.13, which is incompatible with gevent 23.9.1:
```
Error compiling Cython file: undeclared name not builtin: long
```

## Solution Applied

✅ **Updated gevent version** to 24.2.1 (Python 3.13 compatible)
✅ **Created `runtime.txt`** - Forces Python 3.11.9
✅ **Created `.python-version`** - Backup Python version specification
✅ **Updated `render.yaml`** - Sets PYTHON_VERSION environment variable

## Files Modified

1. **`requirements.txt`**
   ```
   gevent==24.2.1  # Updated from 23.9.1
   ```

2. **`runtime.txt`** (NEW)
   ```
   python-3.11.9
   ```

3. **`.python-version`** (NEW)
   ```
   3.11.9
   ```

4. **`render.yaml`**
   ```yaml
   envVars:
     - key: PYTHON_VERSION
       value: "3.11.0"
   ```

## Verification

When deploying to Render, check the build logs for:
```
Using Python version 3.11.9
```

If you still see Python 3.13, add this to your build command in `render.yaml`:
```yaml
buildCommand: |
  pyenv install 3.11.9
  pyenv global 3.11.9
  pip install --upgrade pip
  pip install -r requirements.txt
  ...
```

## Why Python 3.11?

- ✅ **Stable**: Well-tested with all dependencies
- ✅ **Compatible**: Works with gevent, Flask-SocketIO, Selenium
- ✅ **Render Support**: Fully supported on Render.com
- ⚠️ **Python 3.13**: Too new, some packages not yet compatible

## Local Development

This fix doesn't affect local development. You can use Python 3.11 or 3.12 locally.

The gevent 24.2.1 works on both Python 3.11, 3.12, and 3.13.
