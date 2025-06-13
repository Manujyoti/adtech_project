CREATE OR REPLACE VIEW "creative_performance" AS 
SELECT
  ad_id
, campaign_id
, brand
, country
, state
, city
, zipcode
, date
, SUM(impressions) total_impressions
, SUM(clicks) total_clicks
, SUM(conversions) total_conversions
, SUM(spend) total_spend
, (CASE WHEN (SUM(impressions) > 0) THEN ((SUM(clicks) * 1E0) / SUM(impressions)) ELSE 0 END) ctr
, (CASE WHEN (SUM(clicks) > 0) THEN (SUM(spend) / SUM(clicks)) ELSE 0 END) cpc
, (CASE WHEN (SUM(impressions) > 0) THEN (SUM(spend) / (SUM(impressions) / 1000)) ELSE 0 END) cpm
, (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(conversions) * 1E0) / SUM(clicks)) ELSE 0 END) conversion_rate
FROM
  adtech_db.processed_campaign_data
GROUP BY ad_id, campaign_id, brand, country, state, city, zipcode, date
