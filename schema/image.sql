create table image /* By "image" here is meant exactly one binary file obtained from a scanning the parent document. */
(
    /* keys */
    image_id char(32) primary key comment '32-char hexidecimal image UUID. Generated during image file import (by removing hyphens from 36-char UUID).',
    document_id smallint not null,

    /* required metadata */
    relative_order int(4) not null comment 'Format: 0000--9999. Describes the order of an image relative to other images in a given document.', 
    media_type enum('image/bmp', 'image/gif', 'image/jp2', 'image/jpeg', 'image/png', 'image/tiff') not null,
    filesize smallint,

    /* /1* optional metadata *1/ */
    /* local_start_date date comment 'format: "yyyy-mm-dd", or, numerically, yyyymmdd. local date at image start.', */
    /* local_start_time time default "00:00:00" comment 'format: "hh:mm:ss", or, numerically, hhmmss. local time at image start. should be entered as a postive value between "00:00" (or 000000) and "23:59" (or 235900).', */
    /* local_time_zone time comment 'format: should be entered as a signed value between "-12:00" (or -120000) and "12:00" (or 120000). the local timezone at image start is defined to be the (signed) hours and minutes from ut1 solar time to local time. for example, in timezone -03:30, the local time 15:00 refers to the ut1 time 18:30.', */

    /* /1* virtual metadata *1/ */
    /* ut1_start_datetime datetime generated always as */ 
    /*     ( */
    /*         date_sub(local_start_date, interval local_time_zone hour_second) */
    /*     ) */ 
    /*     comment 'UT1 datetime at image start.', */

    /* indices */
    index image_of_document (document_id, relative_order),
    foreign key (document_id) references document(document_id) on delete restrict
) 
ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/* testing */
insert into image 
(
    image_id,
    document_id,
    relative_order,
    media_type,
    filesize
)
values
(
    "testimage", 
    0,
    0, 
    "image/jpeg",
    32718
);

/* TODO save memory for indexing */
/* image_id binary(16) primary key comment '16-byte representation of 32-char hexidecimal image UUID. Generated during image file import (by removing hyphens from 36-char UUID).', */
/* image_id_hex char(32) generated always as (hex(image_id)), */
