# Step 1 — Data Exploration & Quality Assessment

## Objective

The goal of Step 1 was to perform a **first-pass exploration** of Voice of the Customer (VoC) datasets. This helps establish:

* What each dataset looks like (shape, features, timeframe).
* The quality of the feedback text (missingness, duplicates, language issues).
* A quick sentiment **proxy baseline** (from ratings, labels, or NPS).
* Early thematic signals (frequent words/phrases).
* Standardized KPIs that can be compared across datasets.

This foundation ensures later analysis (sentiment modeling, topic detection, predictive modeling) is built on reliable and well-understood data.

---

## Datasets Used

1. **Google Play Store Reviews**

   * User-generated app reviews with star ratings (1–5), review text, timestamps.
   * Used for **proxy sentiment (via stars)** and free-text exploration.



---

## Exploration Process

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

## Key Findings

*(replace with your real numbers once you run the notebook)*

* **Google Play Reviews:**

  * 12,495 rows of data
  * text average of 147 characters.
  * Sentiment proxy skewed positive (45% positive, 39% negative, 16% neutral).
  * Top negative themes: *delay, cannot use, doesn't work*.



---

## Step 1 Deliverables

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
  * NPS 

---

