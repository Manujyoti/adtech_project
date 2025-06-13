from flask import Flask, jsonify
from datetime import datetime
import random

app = Flask(__name__)

# Ad ID → Brand mapping
ad_brand_map = {
    101: "BrandA",
    102: "BrandB",
    103: "BrandC",
    104: "BrandD",
    105: "BrandE",
    106: "BrandF",
    107: "BrandG"
}

# Campaign → Ad mappings (many-to-many)
campaign_ad_map = {
    "A": [101, 102, 103],
    "B": [101, 104, 106],
    "C": [103, 105, 107]
}

# Location Data
geo_data = {
    "US": {
        "states": ["California", "Texas"],
        "cities": {
            "California": [("Los Angeles", "90001"), ("San Diego", "92101")],
            "Texas": [("Houston", "77001"), ("Dallas", "75001")]
        }
    },
    "CA": {
        "states": ["Ontario"],
        "cities": {
            "Ontario": [("Toronto", "M5A1A1"), ("Ottawa", "K1A0B1")]
        }
    },
    "IN": {
        "states": ["Maharashtra", "Karnataka"],
        "cities": {
            "Maharashtra": [("Mumbai", "400001"), ("Pune", "411001")],
            "Karnataka": [("Bengaluru", "560001"), ("Mysore", "570001")]
        }
    }
}

def maybe_null(value, null_chance=0.1):
    return value if random.random() > null_chance else None

@app.route('/campaign-data', methods=['GET'])
def get_campaign_data():
    today = datetime.now().strftime('%Y-%m-%d')
    data = []

    for _ in range(1000):
        # Select campaign and ad
        campaign_id = random.choice(list(campaign_ad_map.keys()))
        ad_id = random.choice(campaign_ad_map[campaign_id])
        brand = ad_brand_map[ad_id]

        # Select location
        country = random.choice(list(geo_data.keys()))
        state = random.choice(geo_data[country]["states"])
        city, zipcode = random.choice(geo_data[country]["cities"][state])

        # Metrics
        impressions = maybe_null(random.randint(5000, 15000))
        clicks = maybe_null(random.randint(0, impressions if impressions else 500))
        conversions = maybe_null(random.randint(0, clicks if clicks else 100))

        data.append({
            "campaign_id": maybe_null(campaign_id),
            "ad_id": maybe_null(ad_id),
            "brand": maybe_null(brand),
            "date": maybe_null(today),  # Now nullable
            "country": maybe_null(country),
            "state": maybe_null(state),
            "city": maybe_null(city),
            "zipcode": maybe_null(zipcode),
            "impressions": impressions,
            "clicks": clicks,
            "spend": maybe_null(round(random.uniform(100.0, 500.0), 2)),
            "conversions": conversions
        })

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)