from pathlib import Path
import json


def load_json_cases(filename: str) -> list[dict]:
    """

    Raises:
        IOError:
        json.JSONDecodeError
    """
    path = Path(__file__).parent / filename
    with open(path, 'r') as f:
        data = json.load(f)
    return data


online_score_invalid_requests = load_json_cases(
    'online_score_invalid_requests.json'
)
online_score_valid_requests = load_json_cases(
    'online_score_valid_requests.json'
)
clients_interests_invalid_requests = load_json_cases(
    'clients_interests_invalid_requests.json'
)
clients_interests_valid_requests = load_json_cases(
    'clients_interests_valid_requests.json'
)
auth_invalid_requests = load_json_cases('auth_invalid_requests.json')
method_invalid_requests = load_json_cases('method_invalid_requests.json')
