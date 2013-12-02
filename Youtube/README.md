# Youtube

## Description
Print a title of a web page to IRC.

It started as a Youtube title parser but ended up to a general link parser.
Naming of the script should be more convenient but oh well.

## Technical information
Saves fetched links to a database (change the path in file plugin.py and linkdb.py).

Will fetch title and update it to the database if link's title is older than a
week (86400seconds * 7).

## Dependencies

* py-SQLite3

