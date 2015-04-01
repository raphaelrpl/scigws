INSERT INTO geo_array (name, description, detail, crs, x_dim_name, x_min, x_max, x_resolution, y_dim_name, y_min, y_max, y_resolution, t_dim_name, t_min, t_max, t_resolution, t_unit_id)
     VALUES ('mcd43a4', 'Nadir BRDF-Adjusted Reflectance 16-Day L3 Global 500m', 'https://lpdaac.usgs.gov/products/modis_products_table/mcd43a4', '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs ', 'col_id', 21600, 35999, 500, 'row_id', 16800, 35999, 500, 'time_id', '2000-03-05', '2014-07-28', 16, 1);


INSERT INTO geo_array_attributes (array_id, name, description, range_min, range_max, scale, missing_value)
     VALUES (1, 'b1', 'Nadir_Reflectance_Band1', 0, 32766, 0.0001, 32767), 
            (1, 'b2', 'Nadir_Reflectance_Band2', 0, 32766, 0.0001, 32767),
            (1, 'b3', 'Nadir_Reflectance_Band3', 0, 32766, 0.0001, 32767),
            (1, 'b4', 'Nadir_Reflectance_Band4', 0, 32766, 0.0001, 32767),
            (1, 'b5', 'Nadir_Reflectance_Band5', 0, 32766, 0.0001, 32767),
            (1, 'b6', 'Nadir_Reflectance_Band6', 0, 32766, 0.0001, 32767),
            (1, 'b7', 'Nadir_Reflectance_Band7', 0, 32766, 0.0001, 32767);
