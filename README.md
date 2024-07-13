# TennisCourtAvailabilityNotifier

This repository contains a Python script and GitHub Actions workflow to check the availability of tennis courts at Koganei Park. The script scrapes the reservation website for available slots on weekends between 13:00 and 19:00, and sends notifications via LINE if available slots are found.

## Features

- Scrapes the reservation website for tennis court availability.
- Checks for available slots on weekends (Saturday and Sunday) between 13:00 and 19:00.
- Sends notifications via LINE when available slots are found.
- Uses GitHub Actions to run the script periodically.

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/TennisCourtAvailabilityNotifier.git
    cd TennisCourtAvailabilityNotifier
    ```

2. Install the required Python packages:
    ```sh
    pip install requests beautifulsoup4
    ```

3. Obtain a LINE Notify token from [LINE Notify](https://notify-bot.line.me/en/).

4. Add the LINE Notify token to your GitHub repository secrets:
    - Go to your repository on GitHub.
    - Navigate to `Settings` > `Secrets` > `Actions`.
    - Add a new secret with the name `LINE_NOTIFY_TOKEN` and the value of your LINE Notify token.

## Usage

1. The script `your_script.py` scrapes the reservation website and checks for available slots.
2. GitHub Actions workflow `.github/workflows/check_availability.yml` runs the script every hour.

## GitHub Actions Workflow

The GitHub Actions workflow is defined in `.github/workflows/check_availability.yml`. It sets up the environment, installs the dependencies, and runs the script periodically.

## Contributing

Feel free to open issues or submit pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License.
