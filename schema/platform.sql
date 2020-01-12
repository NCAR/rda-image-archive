create table platform 
(
    /* keys */
    platform_id smallint primary key,

    /* required metadata */
    name varchar(255) not null comment 'Name of platform (e.g., a ship or weather station) generating climate documents.'

    /* /1* recommended metadata *1/ */
    /* compass_type_of_instrument enum('gyro', 'magnetic', 'unknown'), */
    /* compass_units enum('degrees', 'cardinal directions'), */

    /* navigation_speed_type_of_instrument enum('chip log', 'patent log', 'pit log', 'electromagnetic log', 'propeller rpm'), */
    /* navigation_speed_units enum('knots', 'kilometers per second'), */

    /* scale_used_for_measuring_waves varchar(40), */
    /* scale_used_for_wind_speed enum('beaufort', 'meters per second'), */

    /* anemometer_instrument_make_and_number varchar(40), */
    /* anemometer_instrument_exposure varchar(40), */

    /* atmospheric_pressure_units enum('inches', 'hectopascals', 'millibars'), */ 
    /* atmospheric_pressure_type_of_instrument varchar(40), */
    /* atmospheric_pressure_instrument_make_and_number varchar(40), */
    /* atmospheric_pressure_instrument_exposure varchar(40), */

    /* temperature_units enum('celcius', 'fahrenheit'), */
    /* dry_bulb_thermometer_make_and_number varchar(40), */
    /* dry_bulb_thermometer_exposure varchar(40), */
    /* wet_bulb_thermometer_exposure varchar(40), */
    /* wet_bulb_thermometer_make_and_number varchar(40), */
    /* sea_temperature_type_of_instrument varchar(40), */
    /* sea_temperature_instrument_make_and_number varchar(40), */
    /* sea_temperature_instrument_exposure varchar(40), */

    /* /1* optional metadata *1/ */
    /* facility_description varchar(1000) comment 'E.g., port of registry, tonnage, measure, dimension.' */

    /* indices */
) 
ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/* TODO */
/* standardize (or convert) dimensional quantities */
/* standardize navigation speeds, see https://en.wikipedia.org/wiki/Pitometer_log */
/* Create virtual fields for `coverage_start_date` and `coverage_end_date` by querying document table. */
/* Compare to metadata vocabulary in WMO-No. 47 (Metadata Format Version 04). http://www.wmo.int/images/prog/www/ois/pub47/pub47-home.htm */
/* Implement units compatible with MetPy https://www.unidata.ucar.edu/blog/developer/en/entry/metpy-mondays-4-units-in */ 

insert into platform
(
    platform_id,
    name
    /* compass_type_of_instrument, */
    /* compass_units, */
    /* navigation_speed_type_of_instrument, */
    /* navigation_speed_units, */
    /* scale_used_for_wind_speed, */
    /* atmospheric_pressure_units, */
    /* temperature_units */
) 
values 
(
    0,
    "Test Ship"
    /* "gyro", */
    /* "degrees", */
    /* "patent log", */
    /* "knots", */
    /* "beaufort", */
    /* "inches", */
    /* "fahrenheit" */
);
