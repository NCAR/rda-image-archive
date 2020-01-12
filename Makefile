MYSQL_ARGS=--defaults-extra-file=user/mysql_args

read:
	mysql $(MYSQL_ARGS) images -e "drop table if exists observation"
	mysql $(MYSQL_ARGS) images -e "drop table if exists image"
	mysql $(MYSQL_ARGS) images -e "drop table if exists document"
	mysql $(MYSQL_ARGS) images -e "drop table if exists platform"
	mysql $(MYSQL_ARGS) images -e "drop table if exists archive"
	mysql $(MYSQL_ARGS) images < schema/archive.sql
	mysql $(MYSQL_ARGS) images < schema/platform.sql
	mysql $(MYSQL_ARGS) images < schema/document.sql
	mysql $(MYSQL_ARGS) images < schema/image.sql
	mysql $(MYSQL_ARGS) images < schema/observation.sql
api/head_date.txt:
	git document -1 --format="%ad" --date=format:"%Y-%m-%d" > "$@"

.PHONY: describe
describe:
	mysql $(MYSQL_ARGS) images -e "describe archive;"
	mysql $(MYSQL_ARGS) images -e "describe platform;"
	mysql $(MYSQL_ARGS) images -e "describe document;"
	mysql $(MYSQL_ARGS) images -e "describe image;"
	mysql $(MYSQL_ARGS) images -e "describe observation;"
