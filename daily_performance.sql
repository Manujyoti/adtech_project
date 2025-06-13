CREATE OR REPLACE VIEW "daily_performance" AS 
SELECT
  "date"
, campaign_id
, SUM(impressions) daily_impressions
, SUM(clicks) daily_clicks
, SUM(spend) daily_spend
, SUM(conversions) daily_conversions
, (CASE WHEN (SUM(impressions) > 0) THEN ((SUM(clicks) * 1E0) / SUM(impressions)) ELSE 0 END) daily_ctr
, (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(spend) * 1E0) / SUM(clicks)) ELSE 0 END) daily_cpc
, (CASE WHEN (SUM(impressions) > 0) THEN (((SUM(spend) * 1E0) / SUM(impressions)) * 1000) ELSE 0 END) daily_cpm
, (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(conversions) * 1E0) / SUM(clicks)) ELSE 0 END) daily_conversion_rate
FROM
  processed_campaign_data
GROUP BY "date", campaign_id
