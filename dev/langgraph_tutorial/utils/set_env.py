import getpass
import os
import sys

def is_this_active():
    """Se False, il terminale non è interattivo"""
    print("Terminal activity: ", sys.stdin.isatty())


def set_if_undefined(var: str):
    """Funziona solo se lanciato da cmd, altrimenti getpass resta bloccato."""
    counter = 0
    if not os.environ.get(var):
        print("###############")
        print("TEST")
        print("###############")
        user_input = input(f"Please provide your {var}: ")
        os.environ[var] = user_input
        counter = 1
    return counter


def verify_env(services: list[str]):
    dct_config = {
        "openai": "OPENAI_API_KEY",
        "tavily": "TAVILY_API_KEY"
    }

    results = {}
    for service in services:
        if service in dct_config:
            env_var = dct_config[service]
            results[service] = set_if_undefined(env_var)
        else:
            results[service] = f"Servizio '{service}' non riconosciuto"

    return results


verify_env(services=["openai", "tavily"])
