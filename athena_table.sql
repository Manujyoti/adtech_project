CREATE EXTERNAL TABLE `processed_campaign_data`(
  `campaign_id` string, 
  `ad_id` string, 
  `date` date, 
  `brand` string, 
  `country` string, 
  `state` string, 
  `city` string, 
  `zipcode` string, 
  `impressions` int, 
  `clicks` int, 
  `spend` double, 
  `conversions` int, 
  `ctr` double, 
  `cpc` double, 
  `cpm` double, 
  `conversion_rate` double)
PARTITIONED BY ( 
  `partition_date` string, 
  `partition_time` string)