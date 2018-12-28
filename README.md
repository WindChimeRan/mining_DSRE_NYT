# Mining DSRE

## Overview

Data format:

```
[
    {
        "head": {
            "id": "/guid/9202a8c04000641f8000000000078105",
            "type": "/base/jewlib/topic,/common/topic,/user/narphorium/people/nndb_person,/freebase/apps/hosts/com/acre/juggle/juggle,/people/person,/book/author,/base/jewlib/original_owner,/user/narphorium/people/topic,/base/austria/topic,/film/writer,/people/deceased_person",
            "word": "Arthur Schnitzler"
        },
        "relation": "/people/person/place_of_birth",
        "sentence": "The Little Comedy , '' a mannered operetta based on a short story by Arthur Schnitzler set in fin-de-si \u00e8cle Vienna , opens the evening .",
        "tail": {
            "id": "/guid/9202a8c04000641f800000000006bea9",
            "type": "/location/administrative_division,/base/arthist/helynevek,/book/book_subject,/base/popstra/location,/people/place_of_interment,/location/citytown,/location/location,/base/popstra/topic,/government/governmental_jurisdiction,/base/popstra/sww_base,/user/carmenmfenn1/default_domain/cityscape,/travel/travel_destination,/location/statistical_region,/location/dated_location,/protected_sites/listed_site,/common/topic,/base/austria/topic,/user/brendan/default_domain/top_architectural_city",
            "word": "Vienna"
        }
    },
    ...
]
```

Each dict in the list is an instance.

Note that one entity mention may contain many entity types. That's very interesting.
## Relation labels

NYT contains 58 relation labels, 53 labels in trai set and 5 labels are exclusive in test set.

They are:

>>> * /business/company/industry
>>> * business/company_shareholder/major_shareholder_of
>>> * /sports/sports_team_location/teams
>>> * /people/ethnicity/includes_groups
>>> * /people/ethnicity/people

[^_^]: # (TODO draw a graph)

<img src="img/relation_overview.png" width = '800' div align=right />


##

