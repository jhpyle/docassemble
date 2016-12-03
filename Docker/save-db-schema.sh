#! /bin/bash
su -c "psql -Atc \"select table_name, column_name, data_type, character_maximum_length, column_default from information_schema.columns where table_schema='public'\" docassemble" postgres
