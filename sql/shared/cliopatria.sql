-- cliopatria
set search_path = gaz, public;
select distinct(name) from clio_polities; -- 1618
select distinct(name) from clio_polities where name like '(%' 
	order by name; 
-- 96 are in parens
select distinct(name) from clio_polities where name like '%Abbasid%' 
	order by name; 


-- ==== -- ==== -- ==== -- ==== -- ==== -- ==== 
ALTER TABLE gaz.clio_polities
  ALTER COLUMN geom TYPE geometry(MultiPolygon,4326) USING ST_Multi(geom);

CREATE INDEX clio_polities_gix
  ON gaz.clio_polities
  USING GIST (geom);

ANALYZE gaz.clio_polities;