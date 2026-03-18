# NUTRIENT CALCULATOR API - DEPLOYMENT GUIDE

## 📦 What You Have

**API:** Nutrient calculator for 2,382 USDA foods
**Endpoints:**
- `GET /health` - Health check
- `GET /search-foods?q=chicken` - Search foods
- `POST /calculate-nutrients` - Calculate meal macros

**Database:** `usda_nutrients_clean.csv` (2,382 foods)

---

## 🚀 Deploy to Render.com

### **Step 1: Prepare Files**

Create a new GitHub repository with these files:
```
nutrient-api/
├── nutrient_api.py
├── usda_nutrients_clean.csv
├── requirements.txt
├── Procfile
```

**File contents:**

**requirements.txt:**
```
Flask==2.3.0
flask-cors==4.0.0
gunicorn==20.1.0
```

**Procfile:**
```
web: gunicorn nutrient_api:app
```

---

### **Step 2: Create GitHub Repo**

1. Go to https://github.com/new
2. Name: `ovarrior-nutrient-api`
3. Create repository
4. Upload all 4 files

---

### **Step 3: Deploy to Render**

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Settings:
   - **Name:** `ovarrior-nutrient-api`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn nutrient_api:app`
5. Click "Create Web Service"
6. Wait 2-3 minutes for deployment

---

### **Step 4: Test Your API**

Your API will be at:
```
https://ovarrior-nutrient-api.onrender.com
```

**Test endpoints:**

**Health check:**
```
GET https://ovarrior-nutrient-api.onrender.com/health
```

**Search foods:**
```
GET https://ovarrior-nutrient-api.onrender.com/search-foods?q=chicken
```

**Calculate nutrients:**
```
POST https://ovarrior-nutrient-api.onrender.com/calculate-nutrients

Body:
{
  "foods": [
    {"food_name": "chicken breast cooked", "grams": 150},
    {"food_name": "broccoli cooked", "grams": 100}
  ]
}

Response:
{
  "success": true,
  "totals": {
    "calories": 283,
    "protein": 49.3,
    "carbs": 7.0,
    "fat": 5.8,
    "fiber": 2.6
  },
  "foods": [...],
  "not_found": []
}
```

---

## 🧪 Local Testing (Optional)

**Before deploying, test locally:**

1. Put all files in same folder
2. Install dependencies:
   ```bash
   pip install Flask flask-cors
   ```
3. Run:
   ```bash
   python nutrient_api.py
   ```
4. Test at: `http://localhost:5000/health`

---

## 📱 Flutter Integration

**Example API call:**

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<Map<String, dynamic>> calculateNutrients(List<Map<String, dynamic>> foods) async {
  final url = Uri.parse('https://ovarrior-nutrient-api.onrender.com/calculate-nutrients');
  
  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'foods': foods}),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to calculate nutrients');
  }
}

// Usage:
final result = await calculateNutrients([
  {'food_name': 'chicken breast cooked', 'grams': 150},
  {'food_name': 'broccoli cooked', 'grams': 100},
]);

print('Total calories: ${result['totals']['calories']}');
print('Total protein: ${result['totals']['protein']}g');
```

---

## 🔍 API Features

### **1. Food Search**
- Partial matching (e.g., "chick" finds "chicken breast cooked")
- Case-insensitive
- Returns up to 10 results

### **2. Nutrient Calculation**
- Scales from per-100g database values
- Returns per-item breakdown + totals
- Lists foods not found

### **3. Error Handling**
- Validates all inputs
- Returns clear error messages
- 400 for bad requests, 500 for server errors

---

## ⚠️ Important Notes

**Database Size:**
- CSV is 200KB (small enough for Render free tier)
- Loads into memory on startup
- Fast lookups (no database needed)

**Food Matching:**
- Searches for partial matches
- "chicken" will match "chicken breast cooked"
- Be specific for best results

**Render Free Tier:**
- Spins down after 15 min inactivity
- First request after sleep: 30-60 seconds
- Subsequent requests: instant

---

## 📊 Database Info

**Source:** USDA FoodData Central SR Legacy (April 2018)
**Foods:** 2,382 cooked foods + raw produce
**Nutrients:** Calories, Carbs, Protein, Fat, Fiber
**Values:** Per 100g (scaled automatically)

---

## ✅ Next Steps

After deploying this API:

1. **Test all endpoints** with Postman or curl
2. **Integrate with Flutter** meal logger
3. **Build GL analyzer API** separately (next phase)
4. **Optionally combine** both APIs later

---

**Need help? Check Render logs for errors!**
