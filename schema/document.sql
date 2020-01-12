create table document 
(
    /* keys */
    document_id smallint primary key,
    platform_id smallint not null,
    archive_id smallint not null,

    /* required metadata */
    id_within_archive varchar(255) not null,
    id_within_archive_type varchar(255) not null comment 'NARA ID, ARK, ISBN, DOI, etc. Refer to DataCite Metadata Schema 4.2 relatedIdentifierType.',
    start_date date not null,
    end_date date not null,

    /* recommended metadata */
    contact_person varchar(255) null comment 'E-mail address of responsible human, usually the data provider.',
    /* standardized_region_list set('africa' , 'antarctica' , 'arabian_sea' , 'aral_sea' , 'arctic_ocean' , 'asia' , 'atlantic_arctic_ocean' , 'atlantic_ocean' , 'australia' , 'baltic_sea' , 'bering_sea' , 'bering_strait' , 'black_sea' , 'canadian_archipelago' , 'caribbean_sea' , 'caspian_sea' , 'central_america' , 'chukchi_sea' , 'davis_strait' , 'denmark_strait' , 'east_china_sea' , 'english_channel' , 'eurasia' , 'europe' , 'faroe_scotland_channel' , 'great_lakes' , 'greenland' , 'gulf_of_alaska' , 'gulf_of_mexico' , 'hudson_bay' , 'iceland_faroe_channel' , 'indian_ocean' , 'indian_pacific_ocean' , 'indonesian_throughflow' , 'indo_pacific_ocean' , 'irish_sea' , 'lake_baykal' , 'lake_chad' , 'lake_malawi' , 'lake_tanganyika' , 'lake_victoria' , 'mediterranean_sea' , 'mozambique_channel' , 'north_america' , 'north_sea' , 'norwegian_sea' , 'pacific_equatorial_undercurrent' , 'pacific_ocean' , 'persian_gulf' , 'red_sea' , 'ross_sea' , 'sea_of_japan' , 'sea_of_okhotsk' , 'south_america' , 'south_china_sea' , 'southern_ocean' , 'taiwan_luzon_straits' , 'weddell_sea' , 'windward_passage' , 'yellow_sea') comment 'See http://cfconventions.org/Data/standardized-region-list', */
    standardized_region_list set('north_atlantic', 'south_atlantic', 'north_pacific', 'south_pacific', 'north_indian', 'south_indian', 'antarctic', 'arctic', 'mediterranean', 'black_sea', 'baltic_sea', 'persian_gulf', 'red_sea') comment 'Steve Worley recommended this subset of the CF standardized regions list. See the full list here: http://cfconventions.org/Data/standardized-region-list.',
    type_of_record varchar(255) null comment 'RN logbook, UK Daily Weather Report, Todd Folio, etc.',
    rights_statement varchar(255) null comment 'A statement about the intellectual property rights (IPR) held in or over a Resource, a legal document giving official permission to do something with a resource, or a statement about access rights.',
    /* accession_to_archive_date date null, */

    /* optional metadata */
    colloquial_region_list varchar(1000) null comment 'Comma separated list of colloquial region names. Can include countries, cities, ports, sampling stations, etc.',
    notes varchar(1000) comment 'Free text',

    /* indices */
    foreign key (platform_id) references platform(platform_id) on delete restrict,
    foreign key (archive_id) references archive(archive_id) on delete restrict
) 
ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/* TODO */
/* Do we need "resolution" from observations_per_image? */
/* Should instrumental specifications and units be updated within each document? */
/* name varchar(100) generated always as (concat(platform.name ... */

/* testing */
insert into document 
(
    document_id,
    platform_id, 
    archive_id, 
    id_within_archive,
    id_within_archive_type,
    start_date,
    end_date,
    standardized_region_list,
    type_of_record,
    rights_statement
) 
values 
(
    0,
    0, 
    0, 
    "nara_id",
    122179482,
    20190101,
    20190501,
    "south_atlantic",
    "Ship logbook",
    "CC0"
)
