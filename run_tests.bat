@echo off
echo Running Market Intelligence Bot Tests
python tests/run_tests.py %*
if %ERRORLEVEL% NEQ 0 (
    echo Tests failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
) else (
    echo All tests passed!
    exit /b 0
) 