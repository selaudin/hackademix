# hackademix
Repository to be using for BaselHack 2024 from Hackademix team working on MDPI challenge.

### Installation

1. Clone the repository
   ```bash
    git clone https://github.com/busymo/hackademix.git
   ```
2. Change current directory to project's directory
    ```bash
    cd hackademix
    ```
3. Copy *.example.env* to a *.env* file
    - For Windows <br />
      ``` copy .env.example .env```

    - For Linux or macOS <br />
      ``` cp .env.example .env```
4. Set API_KEY to your api key in the .env file
5. Install required dependencies
    ```bash
    pip install -r requirements.txt
    ```
6. Run the project
    ```bash
    streamlit run welcome.py
    ```
