create table archive
( 
    /* keys */
    archive_id smallint primary key,

    /* required metadata */
    name varchar(100) not null comment 'Archive responsible for "fullest descriptive metadata" of child records, e.g., "The National Archives". Note that the archive could be a publishing company.',
    host_country char(3) not null comment 'Host country of archive. Format: ISO 3166-1 3-letter country code, e.g., "GBR".',

    /* optional metadata */
    search_url varchar(255) comment 'Link to advanced search provided by archive, e.g., "https://discovery.nationalarchives.gov.uk/advanced-search"',
    search_documentation varchar(255) comment 'Link to documentation for advanced search, e.g., "http://www.nationalarchives.gov.uk/help-with-your-research/discovery-help/sorting-and-filtering-your-search-results/"',
    api_url varchar(255) comment 'Base URL of API provided by archive, e.g., "https://catalog.archives.gov/api/v1/".',
    api_documentation varchar(255) comment 'Link to documentation for API provided by archive, e.g., "https://github.com/usnationalarchives/Catalog-API".',
    notes varchar(1000) 
) 
ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/* testing */
insert into archive
(
    archive_id,
    name,
    host_country
)
values
(
    0,
    "Archive",
    "USA"
);
