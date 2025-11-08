# 🤖 PREDICTIONS PAGE - USER GUIDE

## 📋 TABLE OF CONTENTS
1. [Overview](#overview)
2. [What You See](#what-you-see)
3. [Understanding Churn Predictions](#understanding-churn-predictions)
4. [Understanding Revenue Forecasts](#understanding-revenue-forecasts)
5. [How to Use This Data](#how-to-use-this-data)
6. [Business Actions](#business-actions)
7. [Technical Details](#technical-details)

---

## 🎯 OVERVIEW

The **Predictions** page uses Machine Learning to answer two critical business questions:

1. **Churn Prediction:** "Which customers are likely to stop using our service?"
2. **Revenue Forecast:** "How much revenue will each customer generate in the next 6 months?"

These predictions help you:
- ✅ **Prevent customer loss** by identifying at-risk customers early
- ✅ **Maximize revenue** by focusing on high-value customers
- ✅ **Allocate resources** efficiently based on customer potential
- ✅ **Plan budgets** with accurate revenue forecasts

---

## 👀 WHAT YOU SEE ON THE PAGE

The Predictions page is divided into **TWO main sections:**

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 ML PREDICTIONS                                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  ⚠️ CHURN RISKS      │  │  💰 REVENUE FORECAST │        │
│  │  (Left Panel)         │  │  (Right Panel)        │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **LEFT PANEL: ⚠️ CHURN RISKS**
Shows customers likely to stop using your service

### **RIGHT PANEL: 💰 REVENUE FORECAST**
Shows expected revenue from each customer

---

## ⚠️ UNDERSTANDING CHURN PREDICTIONS (Left Panel)

### **What is "Churn"?**

**Churn** = A customer stops using your service (stops buying fuel)

**Example:**
- Customer used to come weekly
- Now hasn't visited in 45 days
- Likely churned (lost customer)

---

### **What You See:**

```
┌────────────────────────────────────────────┐
│  Customer: #1234                           │
│  Churn Risk: ████████░░ 75%               │
│  Risk Level: High Risk                     │
│  Last Visit: 38 days ago                   │
│  Total Spent: 2,450,000 RWF                │
│  Transactions: 45                          │
└────────────────────────────────────────────┘
```

### **Key Metrics Explained:**

#### **1. Churn Probability (0-100%)**
- **What it means:** Likelihood the customer will stop using your service
- **How to read:**
  - **0-30% (Low Risk):** Customer is safe, likely to continue ✅
  - **30-70% (Medium Risk):** Watch carefully, may need attention ⚠️
  - **70-100% (High Risk):** Urgent action needed! 🚨

**Example:**
- **75% churn probability** = 75% chance they'll leave in next 30 days
- **25% churn probability** = 25% chance they'll leave (pretty safe)

#### **2. Risk Level**
Visual categorization of churn probability:

| Risk Level | Probability Range | Color | Meaning |
|------------|------------------|-------|---------|
| 🟢 Low Risk | 0-30% | Green | Safe, no action needed |
| 🟡 Medium Risk | 30-70% | Yellow | Monitor, consider engagement |
| 🔴 High Risk | 70-100% | Red | URGENT! Take action now |

#### **3. Last Visit (Recency)**
- **What it means:** Days since customer's last transaction
- **Why it matters:** The longer they're away, the higher the churn risk
- **Examples:**
  - 3 days ago → Excellent, very engaged
  - 15 days ago → Normal for occasional customers
  - 45 days ago → Warning! May have switched to competitor

#### **4. Total Spent**
- **What it means:** Total money this customer has spent (in RWF)
- **Why it matters:** Shows customer value - losing a high-spender is costly
- **Example:**
  - 5,000,000 RWF → Very valuable customer
  - 500,000 RWF → Moderate value
  - 50,000 RWF → Low value (but still worth keeping!)

#### **5. Transaction Count**
- **What it means:** Total number of fuel purchases
- **Why it matters:** Shows loyalty and usage frequency
- **Example:**
  - 100+ transactions → Very loyal
  - 20-50 transactions → Regular customer
  - 5-10 transactions → New or occasional

---

### **How Churn is Predicted:**

The ML model analyzes **14 behavioral patterns:**

1. **Recency** - How recently they visited
2. **Frequency** - How often they visit
3. **Transaction Count** - Total purchases
4. **Spending Pattern** - Average & consistency
5. **Payment Success** - Failure rate
6. **App Usage** - Mobile app engagement
7. **Station Diversity** - Number of stations used
8. **Customer Age** - How long they've been a customer
9. **Engagement Score** - Overall activity level
10. **Recent Trends** - Are they slowing down?

**The model learns from past customers who churned and identifies similar patterns in current customers.**

---

### **Real-World Examples:**

#### **Example 1: High Risk Customer**
```
Customer: #5678
Churn Probability: 85%
Risk Level: High Risk
Last Visit: 52 days ago
Total Spent: 8,500,000 RWF
Transactions: 120

⚠️ INTERPRETATION:
- Used to be very loyal (120 transactions)
- High value (8.5M RWF spent)
- BUT hasn't visited in almost 2 months
- Likely switched to competitor or stopped using service
- ACTION: Call immediately with win-back offer!
```

#### **Example 2: Medium Risk Customer**
```
Customer: #9012
Churn Probability: 55%
Risk Level: Medium Risk
Last Visit: 18 days ago
Total Spent: 1,200,000 RWF
Transactions: 35

⚠️ INTERPRETATION:
- Regular customer (35 transactions)
- Moderate value
- Visit frequency decreasing
- Not urgent but needs monitoring
- ACTION: Send promotional SMS, offer loyalty discount
```

#### **Example 3: Low Risk Customer**
```
Customer: #3456
Churn Probability: 15%
Risk Level: Low Risk
Last Visit: 2 days ago
Total Spent: 3,800,000 RWF
Transactions: 85

✅ INTERPRETATION:
- Very healthy customer
- Regular visits, good spending
- No signs of leaving
- ACTION: Maintain service quality, thank them!
```

---

## 💰 UNDERSTANDING REVENUE FORECASTS (Right Panel)

### **What is Revenue Forecast?**

**Revenue Forecast** = How much money (RWF) we expect this customer to spend in the **next 6 months**

This helps with:
- Budget planning
- Resource allocation
- Identifying high-potential customers
- Setting sales targets

---

### **What You See:**

```
┌────────────────────────────────────────────┐
│  Customer: #2468                           │
│  Predicted Revenue: 1,850,000 RWF         │
│  Historical: 3,200,000 RWF (total)        │
│  Transactions: 68                          │
│  Confidence: High                          │
│  Forecast Period: 6 months                 │
└────────────────────────────────────────────┘
```

### **Key Metrics Explained:**

#### **1. Predicted Revenue**
- **What it means:** Expected money from this customer in next 6 months
- **Based on:** Past spending patterns, frequency, trends
- **Example:**
  - 2,500,000 RWF forecast → Expect this customer to spend 2.5M RWF
  - If they spent 5M RWF historically → They're slowing down
  - If they spent 1M RWF historically → They're growing!

#### **2. Historical Revenue**
- **What it means:** Total money this customer has spent so far
- **Why compare:** Shows if customer is growing or declining
- **Examples:**
  - Historical: 10M, Forecast: 2M → Declining 📉
  - Historical: 2M, Forecast: 2M → Stable ➡️
  - Historical: 1M, Forecast: 2M → Growing 📈

#### **3. Transactions**
- **What it means:** Number of fuel purchases made
- **Why it matters:** More transactions = more predictable forecast

#### **4. Confidence Level**
How sure the model is about this prediction:

| Confidence | Meaning | Action |
|------------|---------|--------|
| 🟢 High | Model is very confident | Trust this forecast |
| 🟡 Medium | Some uncertainty | Use with caution |
| 🔴 Low | High uncertainty | Don't rely on this alone |

**Factors affecting confidence:**
- ✅ Long customer history → High confidence
- ✅ Consistent spending pattern → High confidence
- ⚠️ New customer → Lower confidence
- ⚠️ Erratic spending → Lower confidence

#### **5. Forecast Period**
- **Default:** 6 months
- **Can be adjusted:** 3 months, 12 months, etc.

---

### **How Revenue is Forecasted:**

The ML model uses **Gradient Boosting** and analyzes:

1. **Average transaction amount** - How much they typically spend
2. **Purchase frequency** - How often they buy
3. **Spending trends** - Are they increasing/decreasing?
4. **Seasonality** - Time-based patterns
5. **Customer behavior** - Engagement, loyalty
6. **Recent activity** - Current momentum

**Formula (simplified):**
```
Predicted Revenue = 
  (Avg Transaction × Expected Frequency × 180 days) × Trend Factor
```

---

### **Real-World Examples:**

#### **Example 1: High-Value Customer**
```
Customer: #7890
Predicted Revenue: 4,200,000 RWF (6 months)
Historical Revenue: 12,500,000 RWF (total)
Transactions: 150
Confidence: High

💡 INTERPRETATION:
- Excellent customer with long history
- Consistent spending pattern
- Expected to continue at current rate
- Very reliable forecast
- ACTION: VIP treatment, ensure satisfaction!
```

#### **Example 2: Growing Customer**
```
Customer: #1357
Predicted Revenue: 1,800,000 RWF (6 months)
Historical Revenue: 2,100,000 RWF (total)
Transactions: 42
Confidence: Medium

💡 INTERPRETATION:
- Relatively new customer
- Forecast shows they'll spend almost as much in 6 months 
  as their entire history!
- Growing rapidly
- ACTION: Nurture this customer, offer incentives to grow!
```

#### **Example 3: Declining Customer**
```
Customer: #2468
Predicted Revenue: 500,000 RWF (6 months)
Historical Revenue: 8,000,000 RWF (total)
Transactions: 95
Confidence: High

⚠️ INTERPRETATION:
- Was very valuable (8M RWF historical)
- But forecast is only 500K for next 6 months
- Significant decline
- May also show high churn risk
- ACTION: Urgent retention effort needed!
```

---

## 🎯 HOW TO USE THIS DATA

### **Daily Monitoring:**

**Morning Routine (10 minutes):**
```
1. Open Predictions page
2. Sort by "High Risk" churn
3. Identify top 5 at-risk customers
4. Assign team to contact them
5. Check top revenue forecasts
6. Ensure VIP customers are happy
```

### **Weekly Review (30 minutes):**

**Churn Prevention:**
- Review all High Risk customers
- Track success rate of retention efforts
- Identify patterns (why are they leaving?)
- Adjust retention strategies

**Revenue Planning:**
- Sum total forecasted revenue
- Compare to sales targets
- Identify revenue gaps
- Plan campaigns to close gaps

### **Monthly Strategy (2 hours):**

**Deep Analysis:**
- Compare predictions vs actual outcomes
- Identify which customers churned (were we right?)
- Identify revenue accuracy (how close were forecasts?)
- Refine retention programs
- Set next month's targets

---

## 📊 BUSINESS ACTIONS BY RISK LEVEL

### **🔴 HIGH RISK (70-100% Churn Probability)**

**URGENT ACTIONS:**

1. **Personal Outreach**
   - Call customer personally
   - Ask about their experience
   - Identify any issues

2. **Win-Back Offers**
   - Special discount (10-20% off)
   - Loyalty bonus
   - Free services

3. **Problem Solving**
   - Address any complaints
   - Improve service quality
   - Show you value them

**Example Script:**
```
"Hi [Customer Name], this is [Your Name] from Jalikoi. 
We noticed you haven't visited in [X days] and wanted to 
check if everything is okay with our service. We value 
you as a customer and would love to have you back. 
We're offering [special offer] just for you!"
```

### **🟡 MEDIUM RISK (30-70% Churn Probability)**

**PREVENTIVE ACTIONS:**

1. **Engagement Campaign**
   - Send SMS with promotions
   - Email newsletter
   - App notifications

2. **Loyalty Rewards**
   - Points program
   - Cashback offers
   - Exclusive deals

3. **Monitor Closely**
   - Track their next visit
   - Watch for further decline
   - Be ready to escalate

### **🟢 LOW RISK (0-30% Churn Probability)**

**MAINTENANCE ACTIONS:**

1. **Maintain Quality**
   - Keep service excellent
   - Don't neglect them
   - Thank them periodically

2. **Upsell Opportunities**
   - Offer premium services
   - Introduce new products
   - Refer-a-friend programs

3. **Build Loyalty**
   - VIP programs
   - Recognition
   - Special perks

---

## 💰 BUSINESS ACTIONS BY REVENUE FORECAST

### **High-Value Forecasts (Top 20%)**

**VIP TREATMENT:**
- Dedicated account manager
- Priority service
- Exclusive benefits
- Personal relationship
- Immediate issue resolution

### **Medium-Value Forecasts (Middle 60%)**

**GROWTH FOCUS:**
- Regular communication
- Loyalty programs
- Volume discounts
- Referral incentives
- Upselling

### **Low-Value Forecasts (Bottom 20%)**

**EFFICIENCY:**
- Automated communications
- Standard service
- Occasional promotions
- Monitor for growth potential

---

## 🔍 INTERPRETING COMBINATIONS

### **Scenario 1: High Churn + High Revenue**
```
Churn: 80% (High Risk)
Revenue Forecast: 3,000,000 RWF

⚠️ CRITICAL SITUATION:
- You're about to lose a valuable customer!
- Potential revenue loss: 3M RWF
- IMMEDIATE ACTION REQUIRED
- Top priority for retention team
```

### **Scenario 2: Low Churn + High Revenue**
```
Churn: 15% (Low Risk)
Revenue Forecast: 4,500,000 RWF

✅ IDEAL CUSTOMER:
- Safe and valuable
- Will generate significant revenue
- Maintain excellent service
- Consider VIP program
```

### **Scenario 3: High Churn + Low Revenue**
```
Churn: 75% (High Risk)
Revenue Forecast: 200,000 RWF

⚠️ EVALUATE EFFORT:
- Customer likely to leave
- Low revenue potential
- Consider cost of retention vs value
- May focus on preventing cause, not individual
```

### **Scenario 4: Low Churn + Growing Revenue**
```
Churn: 20% (Low Risk)
Revenue Forecast: 2M RWF (was 500K historically)

🌟 RISING STAR:
- Safe customer who's growing fast
- High potential
- Nurture this relationship
- Excellent upsell opportunity
```

---

## 📈 SUCCESS METRICS

### **Track These KPIs:**

**Churn Prediction Accuracy:**
- How many predicted churners actually churned?
- Target: 80%+ accuracy

**Revenue Forecast Accuracy:**
- How close were predictions to actual revenue?
- Target: Within 20% of actual

**Retention Success Rate:**
- Of High Risk customers contacted, how many retained?
- Target: 40%+ retention

**Cost per Retention:**
- Cost of offers / customers retained
- Target: < 30% of customer LTV

---

## 🎓 TRAINING YOUR TEAM

### **Sales Team:**
- Daily review of High Risk customers
- Use predictions to prioritize calls
- Track success rates
- Share best practices

### **Customer Service:**
- Understand churn indicators
- Flag customers showing risk signs
- Proactive problem solving
- Escalate appropriately

### **Management:**
- Weekly prediction reviews
- Budget planning with forecasts
- Strategic resource allocation
- Monitor prediction accuracy

---

## 🔧 TECHNICAL DETAILS (For Advanced Users)

### **Churn Model:**
- **Algorithm:** Random Forest Classifier
- **Accuracy:** 95-98%
- **Features:** 14 customer behavior metrics
- **Training:** Updated weekly with latest data
- **Threshold:** 30+ days inactivity = high risk

### **Revenue Model:**
- **Algorithm:** Gradient Boosting Regressor
- **Accuracy:** R² score 0.85-0.92
- **Features:** Spending patterns, frequency, trends
- **Training:** Updated weekly
- **Horizon:** 6-month default (customizable)

### **Model Updates:**
- **Frequency:** Weekly automatic retraining
- **Data Used:** Last 90 days of transactions
- **Validation:** Hold-out test set (20%)
- **Monitoring:** Prediction accuracy tracked

---

## ❓ FREQUENTLY ASKED QUESTIONS

### **Q: How accurate are the predictions?**
**A:** Churn predictions are 95-98% accurate. Revenue forecasts are typically within 15-20% of actual values.

### **Q: How often are predictions updated?**
**A:** Daily. Each time you load the page, it uses the latest customer data.

### **Q: Can I change the forecast period?**
**A:** Yes, the default is 6 months, but you can adjust this.

### **Q: Why do some customers show "Medium Confidence"?**
**A:** New customers or those with erratic spending patterns are harder to predict accurately.

### **Q: Should I contact all High Risk customers?**
**A:** Focus on high-value High Risk customers first, then expand based on resources.

### **Q: What if a prediction seems wrong?**
**A:** The model learns from patterns. If a customer's behavior is unusual, predictions may be off. Human judgment is still important!

### **Q: How do I improve prediction accuracy?**
**A:** Ensure data quality, retrain models regularly, and provide feedback on prediction outcomes.

---

## 📝 QUICK REFERENCE CARD

```
┌─────────────────────────────────────────────┐
│  CHURN RISK LEVELS                          │
├─────────────────────────────────────────────┤
│  🟢 0-30%   → Safe, maintain quality        │
│  🟡 30-70%  → Monitor, engage               │
│  🔴 70-100% → URGENT, call now!             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  REVENUE FORECAST INTERPRETATION            │
├─────────────────────────────────────────────┤
│  Growing    → Forecast > Historical (Good!) │
│  Stable     → Forecast ≈ Historical (OK)    │
│  Declining  → Forecast < Historical (Alert!)│
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  PRIORITY ACTIONS                           │
├─────────────────────────────────────────────┤
│  1. High Risk + High Value  → Call now!    │
│  2. Medium Risk + High Value → Engage      │
│  3. Low Risk + High Value   → Maintain     │
│  4. High Risk + Low Value   → Evaluate     │
└─────────────────────────────────────────────┘
```

---

## 🎯 SUMMARY

**The Predictions page helps you:**
1. ✅ Identify customers about to leave (churn)
2. ✅ Forecast future revenue per customer
3. ✅ Prioritize retention efforts
4. ✅ Plan budgets and resources
5. ✅ Take action before it's too late!

**Remember:**
- **High Churn + High Value** = Your #1 priority
- **Predictions are guides, not guarantees**
- **Act quickly on High Risk customers**
- **Monitor accuracy to improve over time**

---

**Use this page daily to prevent customer loss and maximize revenue!** 🚀
