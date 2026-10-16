
import requests

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"


def get_pokemon_details(name):
    """Fetch detailed Pokémon information from PokéAPI."""

    pokemon_name = name.lower().strip().replace(" ", "-")
    url = f"{POKEAPI_BASE_URL}/pokemon/{pokemon_name}"

    response = requests.get(url, timeout=10)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    data = response.json()

    # Convert height and weight to readable metric units.
    height_m = data["height"] / 10
    weight_kg = data["weight"] / 10

    # Format base stats as a list for the frontend.
    stats = [
        {
            "name": item["stat"]["name"],
            "value": item["base_stat"],
            "base_stat": item["base_stat"],
        }
        for item in data["stats"]
    ]

    # Get official artwork, with a fallback to the regular sprite.
    sprites = data.get("sprites", {})
    artwork = (
        sprites.get("other", {})
        .get("official-artwork", {})
        .get("front_default")
        or sprites.get("front_default")
    )

    return {
        "id": data["id"],
        "name": data["name"].capitalize(),
        "height": height_m,
        "weight": weight_kg,
        "height_m": height_m,
        "weight_kg": weight_kg,
        "types": [
            item["type"]["name"]
            for item in data["types"]
        ],
        "abilities": [
            item["ability"]["name"]
            for item in data["abilities"]
        ],
        "stats": stats,
        "image": artwork,
        "url": f"{POKEAPI_BASE_URL}/pokemon/{data['name']}",
        "pokedex_url": (
            f"https://www.pokemon.com/us/pokedex/{data['name']}"
        ),
    }
