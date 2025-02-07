# Mawaqit Automation - Android

This project is intended for personal use only, but all Muslims can benefit InshaAllah. it is designed to automate the notification of prayer times for a specified mosque. It reads prayer times from a JSON file and sends notifications using the Termux API.

## why not Mawaqit app? 

Well, a touch of customization is missing in the Mawaqit app. e.g custom notification sounds or before prayer reminders .. 

## Requirements

- Termux 
- Termux:API
- Python 

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/mawaqit-automation.git
    cd mawaqit-automation
    ```

3. Ensure Termux API is installed on your device:
    ```sh
    pkg install termux-api
    ```

## Usage

1. Run the main script:
    ```sh
    python src/main.py
    ```

2. The script will read prayer times from `data/[mosque-id].json`, so you should get your closest mosque data and change script accordingly.

### Where to git mosque-id and json data from?

check out these sources:

- [text](https://mawaqit.net/en/)
- [text](https://mrsofiane.me/mawaqit-api/#/)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

