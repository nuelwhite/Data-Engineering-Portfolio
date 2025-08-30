Customer Sentiments & NPS Analysis
Project Overview
This project provides an in-depth analysis of customer feedback to understand customer sentiment and derive a Net Promoter Score (NPS). The goal is to transform raw feedback data into actionable insights that can be used to improve customer experience and drive business growth.

The analysis covers:

Data cleaning and preprocessing.

Calculation of overall NPS.

A breakdown of NPS by different data sources.

Key findings and recommendations.

What I Did
1. Data Preparation and Cleaning
The initial dataset was in a single, unformatted column. I performed the following steps to clean and prepare the data for analysis:

Data Splitting: The single column was split into seven distinct, meaningful columns: Text, Sentiment, Source, Date/Time, User ID, Location, and Confidence Score.

Data Type Conversion: The columns were converted to their appropriate data types to enable proper analysis. The Date/Time column was converted to datetime, Sentiment to a category type, and Confidence Score to float64.

Handling Missing Data: Rows with unknown or unmappable sentiment categories were removed to ensure the integrity of the NPS calculation.

2. NPS Calculation
I categorized each customer feedback entry based on its sentiment to calculate the Net Promoter Score (NPS):

Promoters: Customers with a 'Positive' sentiment.

Detractors: Customers with a 'Negative' sentiment.

Passives: Customers with a 'Neutral' sentiment.

Based on these categories, the following overall metrics were calculated:

Percentage of Promoters: 54.08%

Percentage of Detractors: 43.88%

Overall NPS: 10.20

3. Insights Uncovered
Overall NPS Interpretation
The overall NPS of 10.20 is considered a low to average score. While a significant portion of customers (54.08%) are happy and loyal (Promoters), the large percentage of unhappy customers (43.88%) poses a major risk. This indicates that while there are positive aspects of the customer experience, critical pain points exist that are causing a high level of dissatisfaction.

NPS by Source
A deeper analysis revealed that customer sentiment varies significantly across different data sources. The NPS was calculated for each source to pinpoint specific areas of success and failure:

Sources with a High NPS: Sources like "Art Review" and "TripAdvisor" showed an NPS of 100.00, indicating a complete satisfaction from clients on these platforms. This suggests that the customer experience being reviewed on these platforms is highly positive and is a key strength.

Sources with a Negative NPS: Conversely, sources like "Airline Review" and "Hotel Review" had an NPS of -100.00. This score highlights a critical issue, with all feedback from these sources being negative. These are the most urgent areas for improvement, as they represent complete dissatisfaction.

4. Next Steps & Recommendations
Based on these insights, the following recommendations are crucial for improving the NPS and customer experience:

Prioritize Detractor Feedback: The high percentage of Detractors is a top priority. A deep dive into the specific feedback from negative reviews is needed to identify the root causes of their dissatisfaction.

Focus on Low-NPS Sources: The "Airline Review" and "Hotel Review" platforms should be the immediate focus for targeted improvements. The negative feedback from these sources should be thoroughly analyzed to implement corrective actions.

Leverage Promoters: Utilize the positive feedback from Promoters on "Art Review" and "TripAdvisor" to understand what is working well. These insights can be leveraged to replicate successful experiences across other platforms and customer journeys.