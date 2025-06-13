CREATE OR REPLACE VIEW "campaign_summary" AS 
SELECT
  campaign_id
, SUM(impressions) total_impressions
, SUM(clicks) total_clicks
, SUM(spend) total_spend
, SUM(conversions) total_conversions
, (CASE WHEN (SUM(impressions) > 0) THEN ((SUM(clicks) * 1E0) / SUM(impressions)) ELSE 0 END) campaign_ctr
, (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(spend) * 1E0) / SUM(clicks)) ELSE 0 END) campaign_cpc
, (CASE WHEN (SUM(impressions) > 0) THEN (((SUM(spend) * 1E0) / SUM(impressions)) * 1000) ELSE 0 END) campaign_cpm
, (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(conversions) * 1E0) / SUM(clicks)) ELSE 0 END) campaign_conversion_rate
FROM
  processed_campaign_data
GROUP BY campaign_id
