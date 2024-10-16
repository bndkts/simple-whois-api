# simple-whois-api

# Domain Details API

This project provides a Flask-based API to retrieve domain details, including nameserver (NS) records, A records, hosting providers, and abuse contacts.

## Prerequisites

- Python 3.x
- Flask
- `dnspython` library
- [`ipwhois`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fworkspaces%2Fsimple-whois-api%2Fapp.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A2%2C%22character%22%3A5%7D%7D%5D%2C%227cdee693-cc7a-4ad3-ba9c-23bbd292aa17%22%5D "Go to definition") library

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

To run the Flask application, execute the following command:
```sh
python app.py
```

The application will start on `http://127.0.0.1:5000`.

## API Usage

### Endpoint: `/get-domain-details`

#### Method: [`POST`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fworkspaces%2Fsimple-whois-api%2Fapp.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A98%2C%22character%22%3A44%7D%7D%5D%2C%227cdee693-cc7a-4ad3-ba9c-23bbd292aa17%22%5D "Go to definition")

#### Description:
Retrieves NS records, A records, hosting providers, and abuse contacts for a given domain.

#### Request Body:
- [`domain`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fworkspaces%2Fsimple-whois-api%2Fapp.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A7%2C%22character%22%3A19%7D%7D%5D%2C%227cdee693-cc7a-4ad3-ba9c-23bbd292aa17%22%5D "Go to definition"): The domain name to query (string).

#### Example Request:
```sh
curl -X POST http://127.0.0.1:5000/get-domain-details -H "Content-Type: application/json" -d '{"domain": "example.com"}'
```

#### Example Response:
```json
{
    "HostingProviders": {
        "A": ["Provider A1", "Provider A2"],
        "NS": ["Provider NS1", "Provider NS2"]
    },
    "AbuseContacts": {
        "A": ["abuse@example.com"],
        "NS": ["abuse@ns-example.com"]
    }
}
```

#### Error Response:
If the domain is not provided in the request body, the API will return:
```json
{
    "error": "No domain provided"
}
```


