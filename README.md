# 📊 Step 1 — Data Exploration & Quality Assessment

## 🎯 Objective

The goal of Step 1 was to perform a **first-pass exploration** of Voice of the Customer (VoC) datasets. This helps establish:

* What each dataset looks like (shape, features, timeframe).
* The quality of the feedback text (missingness, duplicates, language issues).
* A quick sentiment **proxy baseline** (from ratings, labels, or NPS).
* Early thematic signals (frequent words/phrases).
* Standardized KPIs that can be compared across datasets.

This foundation ensures later analysis (sentiment modeling, topic detection, predictive modeling) is built on reliable and well-understood data.

---

## 📂 Datasets Used

1. **Google Play Store Reviews**

   * User-generated app reviews with star ratings (1–5), review text, timestamps.
   * Used for **proxy sentiment (via stars)** and free-text exploration.

2. **Twitter US Airline Sentiment**

   * Tweets labeled *positive / neutral / negative* with reasons for negativity.
   * Used as a **ground-truth labeled dataset** for sentiment benchmarking.

3. **NPS Survey (Financial Services)**

   * 0–10 customer satisfaction scores with free-text responses.
   * Used to compute **Net Promoter Score (NPS)** and categorize responses as *Promoters, Passives, Detractors*.

---

## 🔍 Exploration Process

### 1. Shape & Quality

* **Row/column counts** for each dataset.
* **Missingness** (e.g., blank text fields, missing ratings).
* **Duplicates** checked and removed if necessary.
* **Date ranges** confirmed (earliest to latest feedback).

### 2. Text Sanity Checks

* Character length and token length distributions.
* % empty or very short responses (≤3 tokens).
* Spot-check language (to confirm majority is English).

### 3. Sentiment Proxy

* **Reviews (stars):** mapped 1–2 = negative, 3 = neutral, 4–5 = positive.

  * Promoter (9–10)
  * Passive (7–8)
  * Detractor (0–6)
  * Computed **NPS = %Promoters − %Detractors**.

### 4. Early Themes

* Extracted **top unigrams and bigrams** with `CountVectorizer`.
* Highlighted recurring themes like *delivery delays, app crashes, pricing, customer support*.

---

## 📈 Key Findings

*(replace with your real numbers once you run the notebook)*

* **Google Play Reviews:**

  * \~500,000 rows, text avg \~120 characters.
  * Sentiment proxy skewed positive (65% positive, 20% negative, 15% neutral).
  * Top negative themes: *crash, bug, update*.

* **Twitter Airline Sentiment:**

  * \~15,000 tweets, avg \~20 tokens.
  * Labels: \~60% negative, \~20% neutral, \~20% positive.
  * Frequent complaints: *delays, cancellations, customer service*.

* **NPS Survey:**

  * \~10,000 responses, balanced across promoters/passives/detractors.
  * Computed NPS: +25.
  * Detractors focused on *fees, waiting times, app usability*.

---

## 📊 Step 1 Deliverables

* **Notebook:** `01_explore_data.ipynb`

  * Contains dataset loading, cleaning, profiling, and visualization.
* **Figures:** character/token length histograms, sentiment distributions.
* **KPI Table:** standardized summary across datasets with:

  * Row count, column count
  * Date range
  * Missing text %
  * Duplicate count
  * Avg char/token length
  * Empty/short text %
  * Sentiment distribution
  * NPS (if available)

---

