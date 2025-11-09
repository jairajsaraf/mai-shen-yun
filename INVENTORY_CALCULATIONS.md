# 📊 Inventory Management - Calculation Formulas

## Overview
This document explains how all inventory metrics are calculated in the Mai Shen Yun dashboard.

---

## 1️⃣ Current Stock
**Definition:** The current quantity of an ingredient in your inventory

**In Demo/Simulation:**
```python
current_stock = quantity_per_shipment × random(0.5 to 3.0)
```

**In Production:**
- Should come from your actual inventory management system
- Updated in real-time as items are used and received

**Example:**
- Beef gets shipments of 40 lbs
- Simulated current stock might be: 40 × 1.5 = **60 lbs**

---

## 2️⃣ Average Daily Usage
**Definition:** How much of an ingredient is consumed per day on average

**Formula:**
```python
avg_daily_usage = (quantity_per_shipment × num_shipments_per_month) / 30
```

**Example - Beef:**
- Quantity per shipment: 40 lbs
- Shipments per month: 3 (weekly = ~3 per month)
- Monthly consumption: 40 × 3 = 120 lbs
- **Daily usage: 120 / 30 = 4 lbs/day**

**Example - Rice:**
- Quantity per shipment: 50 lbs
- Shipments per month: 2 (biweekly)
- Monthly consumption: 50 × 2 = 100 lbs
- **Daily usage: 100 / 30 = 3.33 lbs/day**

---

## 3️⃣ Lead Time (Days)
**Definition:** Number of days between placing an order and receiving it

**Conversion Table:**
| Frequency | Lead Time | Days |
|-----------|-----------|------|
| Daily | Same day | 1 |
| Weekly | 1 week | 7 |
| Biweekly | 2 weeks | 14 |
| Monthly | 1 month | 30 |

**Why it matters:**
- Longer lead times = need more safety stock
- Must order before running out, accounting for delivery time

---

## 4️⃣ Reorder Point ⚠️
**Definition:** The inventory level that triggers a reorder

**Formula:**
```python
reorder_point = (lead_time_days × avg_daily_usage) + safety_stock

where:
    safety_stock = avg_daily_usage × 7  # 1 week buffer (default)
```

**Example - Beef (Weekly Delivery):**
1. Average daily usage: 4 lbs/day
2. Lead time: 7 days (weekly shipment)
3. Safety stock: 4 × 7 = 28 lbs
4. **Reorder point = (7 × 4) + 28 = 56 lbs**

**Meaning:** When beef inventory drops below 56 lbs, place an order immediately!

**Example - Rice (Biweekly Delivery):**
1. Average daily usage: 3.33 lbs/day
2. Lead time: 14 days (biweekly)
3. Safety stock: 3.33 × 7 = 23.3 lbs
4. **Reorder point = (14 × 3.33) + 23.3 = 69.9 lbs**

**Why it's calculated this way:**
- **Lead time portion:** Covers usage during delivery wait
- **Safety stock:** Buffer against unexpected demand or delays
- Together they prevent stockouts

---

## 5️⃣ Recommended Order Quantity
**Definition:** How much to order when restocking

**Formula:**
```python
recommended_order = (reorder_point - current_stock) + quantity_per_shipment
```

**Example - Beef:**
- Current stock: 30 lbs (⚠️ below reorder point!)
- Reorder point: 56 lbs
- Quantity per shipment: 40 lbs
- **Recommended = (56 - 30) + 40 = 66 lbs**
- This equals approximately **2 shipments** (66/40 ≈ 1.65)

**Logic:**
1. Calculate shortage: 56 - 30 = 26 lbs needed to reach reorder point
2. Add one standard shipment to build stock back up
3. Total order brings you above reorder point with buffer

---

## 6️⃣ Days of Stock
**Definition:** How many days until you run out (at current usage rate)

**Formula:**
```python
days_of_stock = current_stock / avg_daily_usage
```

**Example:**
- Current stock: 30 lbs
- Daily usage: 4 lbs/day
- **Days of stock = 30 / 4 = 7.5 days**

**Interpretation:**
- **< 7 days:** Critical - order immediately
- **7-14 days:** Low - order soon
- **14-30 days:** Normal - monitor
- **> 60 days:** Overstock - reduce orders

---

## 7️⃣ Status Classification

### 🔴 Low Stock (Urgent)
**Condition:**
```python
current_stock < reorder_point
```
**Action:** Reorder immediately!

### 🟢 Normal (Healthy)
**Condition:**
```python
reorder_point ≤ current_stock ≤ (avg_daily_usage × 60)
```
**Action:** Monitor regularly

### 🟡 Overstock (Excess)
**Condition:**
```python
current_stock > (avg_daily_usage × 60)
```
**Action:** Reduce future orders, check for waste

---

## 📊 Complete Example: Chicken

**Given Data:**
- Quantity per shipment: 40 lbs
- Number of shipments: 2 per month
- Frequency: Weekly
- Current stock: 45 lbs (simulated)

**Calculations:**
1. **Avg Daily Usage:**
   - Monthly: 40 × 2 = 80 lbs
   - Daily: 80 / 30 = **2.67 lbs/day**

2. **Lead Time:**
   - Weekly = **7 days**

3. **Safety Stock:**
   - 2.67 × 7 = **18.7 lbs**

4. **Reorder Point:**
   - (7 × 2.67) + 18.7 = **37.4 lbs**

5. **Days of Stock:**
   - 45 / 2.67 = **16.9 days**

6. **Status:**
   - 45 > 37.4 → **Normal** ✅

7. **Recommended Order:**
   - Not needed (above reorder point)
   - Next order when stock drops to 37 lbs

---

## 🎯 Best Practices

### For Weekly Deliveries:
- Safety stock = 7 days
- Reorder when you have ~2 weeks supply left

### For Biweekly Deliveries:
- Safety stock = 7 days
- Reorder when you have ~3 weeks supply left

### For Monthly Deliveries:
- Safety stock = 7-10 days
- Reorder when you have ~5 weeks supply left

---

## 📝 Notes

**Why Safety Stock = 7 days?**
- Covers unexpected demand spikes
- Protects against delivery delays
- Standard industry practice for restaurants
- Can be adjusted based on:
  - Ingredient perishability
  - Supplier reliability
  - Demand variability

**Adjusting Formulas:**
- More reliable supplier? Reduce safety stock
- Highly variable demand? Increase safety stock
- Perishable items? Reduce overstock threshold from 60 to 30 days

---

## 🔧 Implementation in Code

```python
# Calculate average daily usage
avg_daily_usage = (quantity_per_shipment * num_shipments) / 30

# Get lead time in days
lead_time_days = frequency_to_days(frequency)

# Calculate safety stock (7 days default)
safety_stock = avg_daily_usage * 7

# Calculate reorder point
reorder_point = (lead_time_days * avg_daily_usage) + safety_stock

# Determine status
if current_stock < reorder_point:
    status = "Low Stock"
elif current_stock > avg_daily_usage * 60:
    status = "Overstock"
else:
    status = "Normal"

# Calculate recommended order
if current_stock < reorder_point:
    recommended_order = (reorder_point - current_stock) + quantity_per_shipment
```

---

**Last Updated:** 2025-11-08
**Version:** 1.0
