@echo off
echo Installing required Python packages...
pip install dash==2.14.2 dash-bootstrap-components==1.5.0 pandas==2.1.0 plotly==5.19.0 SQLAlchemy==2.0.25
if %ERRORLEVEL% EQU 0 (
    echo Installation completed successfully!
) else (
    echo Installation failed. Please check the error messages above.
)
pause
