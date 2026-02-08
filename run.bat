@echo off
echo ---------------------------------------------------
echo 1. Installing Libraries explicitly for Python 3.12...
echo ---------------------------------------------------
"C:\Users\fhd6aha\AppData\Local\Programs\Python\Python312\python.exe" -m pip install streamlit google-generativeai pandas

echo.
echo ---------------------------------------------------
echo 2. Starting Bayan Pro...
echo ---------------------------------------------------
"C:\Users\fhd6aha\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run app.py
pause