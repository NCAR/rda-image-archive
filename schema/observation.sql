create table observation 
( 
    /* keys */
    observation_id int primary key auto_increment,

    /* required metadata */
    image_id char(32) not null,
    is_cited_by_dataset_id char(255) not null comment 'E.g., 10.5065/D6ZS2TR3',
    is_cited_by_dataset_id_type char(32) not null comment 'E.g., DOI. See relatedIdentifierType in Datacite Schema 4.2.',

    /* recommended metadata */

    /* /1* optional metadata *1/ */
    /* time_after_image_start time null */ 
    /*     comment 'Format: a non-negative time entered as "HH:MM" (or HHMMSS). Defined as the displacement in hours and minutes from the start of the parent image (explicitly from `image.ut1_start_datetime`). Note: If `image.local_start_time` of the parent image takes its default value "00:00:00", then `time_after_image_start` for an observation would be given by the local time of this observation. If `image.local_start_time` is nonzero, say, "06:00:00", then an observation made at local time "18:00:00" would have `time_after_image_start` entered as "12:00" (or 120000).', */

    /*     /1* atmospheric pressure indicators *1/ */
    /*     atmospheric_pressure_indicator bool, */

    /*     /1* temperature indicators *1/ */
    /*     dry_bulb_temperature_indicator bool, */
    /*     wet_bulb_temperature_indicator bool, */
    /*     unspecified_air_temperature_indicator bool, */
    /*     sea_temperature_indicator bool, */

    /*     /1* wind speed indicators *1/ */
    /*     wind_direction_indicator bool, */
    /*     wind_speed_indicator bool, */

    /*     /1* cloud indicators *1/ */
    /*     cloud_form_indicator bool, */
    /*     cloud_direction_indicator bool, */
    /*     cloud_amount_indicator bool, */

    /* /1* optional metadata *1/ */

    /*     /1* platform position *1/ */
    /*     longitude float(10,6), */
    /*     latitude float(10,6), */
    /*     location_fix_indicator bool default 0 comment 'an indicator equal to 1 if longitude and latitude are "fixed" by georeference. else equal to 0, e.g., when location is unspecified or "dead-reckoned".', */

    /*     /1* platform course and speed *1/ */
    /*     local_course float(6,3) comment 'local course is defined as the direction of movement in degrees clockwise (e.g., convert ne to 315 and nne to 337.5) from "local north". this field should be entered verbatim, without correction for the compass type of instrument. true course thus depends on this field, the date, and the parent field `platform.compass_type_of_instrument`.', */
    /*     local_speed float(6,3) comment 'should be entered verbatim. this field depends on the parent field `platform.navigation_speed_units`.', */

    /* indices */
    foreign key (image_id) references image(image_id) on delete restrict
) 
ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/* TODO */
/* image_id binary(16) not null, */
/* Standardize indicators from Sec. 4.2.1 "Elements observed", WMO-No. 8 (2010 update). lwww.wmo.int/images/prog/www/IMOP/CIMO-Guide.html */
/* humidity indicators */
/* weather indicators */
/* visibility indicators */
/* precipitation indicators */
/* ocean sea waves and swell indicators */

insert into observation
(
    image_id,
    is_cited_by_dataset_id,
    is_cited_by_dataset_id_type
)
values
(
    "testimage",
    "10.5065/D6ZS2TR3",
    "DOI"
);
