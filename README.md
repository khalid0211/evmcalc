# New Project Template

## Quick start
1. Ensure Python 3.13.7 is selected in VS Code.
2. (Optional) Install/refresh deps:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
3. Run the main script:
   ```bash
   python main.py
   ```
4. Run Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Notes
- Put datasets in `data/`, experiments in `notebooks/`, reusable code in `scripts/`.
- Add new packages with `pip install <pkg>` and update `requirements.txt` (`pip freeze > requirements.txt`) if you want a pinned snapshot.
