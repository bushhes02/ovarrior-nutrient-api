"""
Nutrient Calculator API
Uses USDA SR Legacy database (2,382 foods) to calculate meal macros
Author: Bushra (G21318993)
Project: Ovarrior PCOS Wellness App
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════════════════════════════
#  LOAD DATABASE
# ═══════════════════════════════════════════════════════════════════════════

FOODS_DB = []

def load_database():
    """Load USDA nutrients database into memory"""
    global FOODS_DB
    
    db_path = 'usda_nutrients_clean.csv'
    
    if not os.path.exists(db_path):
        print(f"ERROR: {db_path} not found!")
        return
    
    with open(db_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            FOODS_DB.append({
                'fdc_id': row['fdc_id'],
                'food_name': row['food_name'].lower(),
                'category_id': int(row['category_id']),
                'calories': float(row['calories']),
                'carbs': float(row['carbs']),
                'protein': float(row['protein']),
                'fat': float(row['fat']),
                'fiber': float(row['fiber'])
            })
    
    print(f"✓ Loaded {len(FOODS_DB)} foods from USDA database")

# Load database when app starts
load_database()

# ═══════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def search_food(food_name):
    """
    Search for food in database (case-insensitive, partial match)
    Returns first match or None
    """
    food_name_lower = food_name.lower().strip()
    
    # Try exact match first
    for food in FOODS_DB:
        if food['food_name'] == food_name_lower:
            return food
    
    # Try partial match
    for food in FOODS_DB:
        if food_name_lower in food['food_name']:
            return food
    
    return None

def scale_nutrients(food_data, grams):
    """
    Scale nutrient values from per 100g to actual grams
    """
    multiplier = grams / 100.0
    
    return {
        'fdc_id': food_data['fdc_id'],
        'food_name': food_data['food_name'],
        'grams': grams,
        'calories': round(food_data['calories'] * multiplier, 1),
        'carbs': round(food_data['carbs'] * multiplier, 1),
        'protein': round(food_data['protein'] * multiplier, 1),
        'fat': round(food_data['fat'] * multiplier, 1),
        'fiber': round(food_data['fiber'] * multiplier, 1)
    }

# ═══════════════════════════════════════════════════════════════════════════
#  API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'nutrient-calculator',
        'foods_loaded': len(FOODS_DB)
    })

@app.route('/search-foods', methods=['GET'])
def search_foods():
    """
    Search for foods by name
    Query parameter: ?q=chicken
    Returns up to 10 matching foods
    """
    query = request.args.get('q', '').lower().strip()
    
    if not query or len(query) < 2:
        return jsonify({
            'success': False,
            'error': 'Query too short (minimum 2 characters)'
        }), 400
    
    # Find matching foods
    matches = []
    for food in FOODS_DB:
        if query in food['food_name']:
            matches.append({
                'fdc_id': food['fdc_id'],
                'food_name': food['food_name'],
                'category_id': food['category_id'],
                'calories_per_100g': food['calories'],
                'protein_per_100g': food['protein'],
                'carbs_per_100g': food['carbs'],
                'fat_per_100g': food['fat'],
                'fiber_per_100g': food['fiber']
            })
            
            if len(matches) >= 10:
                break
    
    return jsonify({
        'success': True,
        'query': query,
        'results': matches,
        'count': len(matches)
    })

@app.route('/calculate-nutrients', methods=['POST'])
def calculate_nutrients():
    """
    Calculate total nutrients for a meal
    
    Input JSON:
    {
        "foods": [
            {"food_name": "chicken breast cooked", "grams": 150},
            {"food_name": "broccoli cooked", "grams": 100}
        ]
    }
    
    Output JSON:
    {
        "success": true,
        "totals": {
            "calories": 283,
            "protein": 49.3,
            "carbs": 7.0,
            "fat": 5.8,
            "fiber": 2.6
        },
        "foods": [
            {
                "food_name": "chicken breast cooked",
                "grams": 150,
                "calories": 248,
                "protein": 46.5,
                ...
            }
        ],
        "not_found": []
    }
    """
    
    try:
        data = request.get_json()
        
        if not data or 'foods' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "foods" array in request'
            }), 400
        
        foods_input = data['foods']
        
        if not isinstance(foods_input, list) or len(foods_input) == 0:
            return jsonify({
                'success': False,
                'error': 'Foods must be a non-empty array'
            }), 400
        
        # Process each food
        foods_breakdown = []
        not_found = []
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        
        for item in foods_input:
            food_name = item.get('food_name')
            grams = item.get('grams')
            
            # Validate input
            if not food_name or grams is None:
                return jsonify({
                    'success': False,
                    'error': 'Each food must have "food_name" and "grams"'
                }), 400
            
            try:
                grams = float(grams)
                if grams <= 0:
                    return jsonify({
                        'success': False,
                        'error': f'Grams must be positive (got {grams})'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': f'Invalid grams value: {grams}'
                }), 400
            
            # Search for food
            food_data = search_food(food_name)
            
            if not food_data:
                not_found.append(food_name)
                continue
            
            # Scale nutrients to portion
            scaled = scale_nutrients(food_data, grams)
            foods_breakdown.append(scaled)
            
            # Add to totals
            total_calories += scaled['calories']
            total_protein += scaled['protein']
            total_carbs += scaled['carbs']
            total_fat += scaled['fat']
            total_fiber += scaled['fiber']
        
        # Return results
        return jsonify({
            'success': True,
            'totals': {
                'calories': round(total_calories, 1),
                'protein': round(total_protein, 1),
                'carbs': round(total_carbs, 1),
                'fat': round(total_fat, 1),
                'fiber': round(total_fiber, 1)
            },
            'foods': foods_breakdown,
            'not_found': not_found
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

# ═══════════════════════════════════════════════════════════════════════════
#  RUN SERVER
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
