# analyzeMasters

A webscraping tool that scrapes data from various platforms and accumulates a publicly available dataset of admit information to various universities in the US.

We then analyze the data to gain insights into the scores and background of the students admitted to these universities.

## Setup

1. Install the requirements
```bash
pip install -r requirements.txt
```

2. Define your credentials in config.py as:
```python
user = "<your_email>"
passw = "<your_password>"
```

3. Run the webscrapper:
```python
python app.py
```