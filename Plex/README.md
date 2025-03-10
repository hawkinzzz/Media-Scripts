# Plex scripts

Misc scripts and tools. Undocumented scripts probably do what I need them to but aren't finished yet.

## Setup

1. clone repo
1. Install requirements with `pip install -r requirements.txt` [I'd suggest doing this in a virtual environment]
1. Copy `.env.example` to `.env`
1. Edit .env to suit

All these scripts use the same `.env` and requirements.

### `.env` contents

```
TMDB_KEY=TMDB_API_KEY                        # https://developers.themoviedb.org/3/getting-started/introduction
TVDB_KEY=TVDB_V4_API_KEY                     # currently not used; https://thetvdb.com/api-information
PLEX_URL=https://plex.domain.tld             # URL for Plex; can be a domain or IP:PORT
PLEX_TOKEN=PLEX-TOKEN
PLEX_OWNER=yournamehere                      # account name of the server owner
TARGET_PLEX_URL=https://plex.domain2.tld     # As above, the target of apply_all_status
TARGET_PLEX_TOKEN=PLEX-TOKEN-TWO             # As above, the target of apply_all_status
TARGET_PLEX_OWNER=yournamehere               # As above, the target of apply_all_status
LIBRARY_MAP={"LIBRARY_ON_PLEX":"LIBRARY_ON_TARGET_PLEX", ...}
                                             # In apply_all_status, map libraries according to this JSON.
LIBRARY_NAMES=Movies,TV Shows,Movies 4K      # comma-separated list of libraries to act on
CAST_DEPTH=20                                # how deep to go into the cast for actor collections
TOP_COUNT=10                                 # how many actors to export
TARGET_LABELS=this label, that label         # comma-separated list of labels to remove posters from
REMOVE_LABELS=True                           # attempt to remove the TARGET_LABELs from items after resetting the poster
DELAY=1                                      # optional delay between items
CURRENT_POSTER_DIR=current_posters           # put downloaded current posters and artwork here
POSTER_DIR=extracted_posters                 # put downloaded posters here
POSTER_DEPTH=20                              # grab this many posters [0 grabs all]
POSTER_DOWNLOAD=False                        # generate a script rather than downloading
POSTER_CONSOLIDATE=True                      # posters are separated into folders by library
TRACK_RESET_STATUS=True                      # reset-posters-* keeps track of status and picks up where it left off
ARTWORK=True                                 # current background is downloaded with current poster
PLEX_PATHS=False
NAME_IN_TITLE=True
POSTER_NAME=poster
BACKGROUND_NAME=background
RESET_SEASONS=True                           # reset-posters-plex resets season artwork as well in TV libraries
RESET_EPISODES=True                          # reset-posters-plex resets episode artwork as well in TV libraries [requires RESET_SEASONS=True]
KEEP_COLLECTIONS=bing,bang                   # List of collections to keep
INCLUDE_COLLECTION_ARTWORK=1                 # should get-all-posters retrieve collection posters?
ONLY_COLLECTION_ARTWORK=0                    # should get-all-posters retrieve ONLY collection posters?
LOCAL_RESET_ARCHIVE=1                        # should reset-posters-tmdb keep a local archive of posters?
```

## Scripts:
1. [user-emails.py](#user-emailspy) - extract user emails from your shares
1. [reset-posters-tmdb.py](#reset-posters-tmdbpy) - reset all artwork in a library to TMDB default
1. [reset-posters-plex.py](#reset-posters-plexpy) - reset all artwork in a library to Plex default
1. [grab-current-posters.py](#grab-current-posterspy) - Grab currently-set posters and optionally background artwork
1. [grab-all-posters.py](#grab-all-posterspy) - grab some or all of the artwork for a library from plex
1. [grab-all-status.py](#grab-all-statuspy) - grab watch status for all users all libraries from plex
1. [apply-all-status.py](#apply-all-statuspy) - apply watch status for all users all libraries to plex from the file emitted by the previous script
1. [show-all-playlists.py](#show-all-playlistspy) - Show contents of all user playlists
1. [delete-collections.py](#delete-collectionspy) - delete most or all collections from one or more libraries
1. [refresh-metadata.py](#refresh-metadatapy) - Refresh metadata individually on items in a library

## user-emails.py

You want a list of email addresses for all the people you share with.

Here is a quick and dirty [emphasis on "quick" and "dirty"] way to do that.

### Usage
1. setup as above
2. Run with `python user-emails.py`

The script will loop through all the shared users on your acount and spit out username and email address.

```shell
connecting...
getting users...
looping over 26 users...
binguser - bing@gmail.com
mrbang - bang@gmail.com
boingster - boing@gmail.com
...
```

## reset-posters-tmdb.py

Perhaps you want to reset all the posters in a library

This script will set the poster for every series or movie to the default poster from TMDB/TVDB.  It also saves that poster under `./posters/[movies|shows]/<rating_key>.ext` in case you want to use them with PMM's overlay resets.

If there is a file already located at `./posters/[movies|shows]/<rating_key>.ext`, the script will use *that image* instead of retrieving a new one, so if you replace that local one with a poster of your choice, the script will use the custom one rather than the TMDB/TVDB default.

Script-specific variables in .env:
```
TRACK_RESET_STATUS=True                         # pick up where the script left off
TARGET_LABELS = Bing, Bang, Boing               # reset artwork on items with these labels
REMOVE_LABELS=True                              # remove labels when done [NOT RECOMMENDED]
RESET_SEASONS=True                           # reset-posters-plex resets season artwork as well in TV libraries
RESET_EPISODES=True                          # reset-posters-plex resets episode artwork as well in TV libraries [requires RESET_SEASONS=True]
LOCAL_RESET_ARCHIVE=True                        # keep a local archive of posters
```

If you set:
```
TRACK_RESET_STATUS=True
```
The script will keep track of where it is and will pick up at that point on subsequent runs.  This is useful in the event of a lost connection to Plex.

Once it gets to the end of the library successfully, the tracking file is deleted.

If you want to reset the progress tracking and start from the beginning for some reason, delete a file named something like `8c9d8955-b414-4f35-98a4-8f3f26d0249c.txt` in the same directory as this script.  The file name is the internal UUID of the library being processed.

If you specify a comma-separated list of labels in the env file:
```
TARGET_LABELS = This label, That label, Another label
```
The script will reset posters only on movies with those labels assigned.

If you also set:
```
REMOVE_LABELS=True
```
The script will *attempt* to remove those labels after resetting the poster.  I say "attempt" since in testing I have experienced an odd situation where no error occurs but the label is not removed.  My test library of 230 4K-Dolby Movies contains 47 that fail in this way; every run it goes through the 47 movies "removing labels" without error yet they still have the labels on the next run.

Besides that Heisenbug, I don't recommend using this [`REMOVE_LABELS`] since the label removal takes a long time [dozens of seconds per item].  Doing this through the Plex UI is much faster.

If you set:
```
LOCAL_RESET_ARCHIVE=False
```
The script will set the artwork by sending the TMDB URL to Plex, without downloading the file locally first.  This means a faster run compared to the initial run when downloading.

Example timings on a test library of 1140 TV Shows, resetting artwork for Show-Season-Episode level:

1. No downloading: 1 hour 25 minutes
1. With downloading: 2 hours 30 minutes
2. Second run with downloaded archive: 1 hours 10 minutes

That is on a system with a 1G connection up and down, so values are just relative ot each other.

The value of the local archive is that if you want to replace some of those images with your own, it provides a simple way to update all the posters in a library to custom posters of your own.  When teh script runs, it looks at that archive first, only downloading an image if one doesn't exist in the archive.

If you're just looking to reset as a one-off, that may not have value.

### Usage
1. setup as above
2. Run with `python reset-posters-tmdb.py`

```
tmdb config...
connecting to https://stream.BING.BANG...
getting items from [TV Shows - 4K]...
looping over 876 items...
[=---------------------------------------] 2.7% ... Age of Big Cats
```

At this time, there is no configuration aside from library name; it replaces all posters.  It does not delete any posters from Plex, just grabs a URL and uses the API to set the poster to the URL.

## reset-posters-plex.py

Script-specific variables in .env:
```
RESET_SEASONS=True                           # reset-posters-plex resets season artwork as well in TV libraries
RESET_EPISODES=True                          # reset-posters-plex resets episode artwork as well in TV libraries [requires RESET_SEASONS=True]
```

Same as `reset-posters-tmdb.py`, but it resets the artwork to the first item in Plex's own list of artwork, rather than downloading a new image from TMDB.

With `RESET_SEASONS=True`, if the season doesn't have artwork the series artwork will be used instead.

## grab-current-posters.py

Perhaps you want to get local copies of the currently-set posters [and maybe backgrounds] for everything in a library.

Script-specific variables in .env:
```
CURRENT_POSTER_DIR=current_posters           # put downloaded posters here
POSTER_DOWNLOAD=0                            # if set to 0, generate a script rather than downloading
POSTER_CONSOLIDATE=1                         # if set to 0, posters are separated into folders by library
ARTWORK=1                                    # if set to 1, background artwork is retrieved
PLEX_PATHS=1                                 # if set to 1, files are stored in a mirror of the plex folders rooted at CURRENT_POSTER_DIR
NAME_IN_TITLE=1                              # if set to 1, files will have the title added to the name: 13 Reasons Why (2017) {tvdb-323168}-SOMETHING.jpg
POSTER_NAME=poster                           # This is the SOMETHING in 13 Reasons Why (2017) {tvdb-323168}-SOMETHING.jpg for posters
BACKGROUND_NAME=background                   # This is the SOMETHING in 13 Reasons Why (2017) {tvdb-323168}-SOMETHING.jpg for backgrounds
INCLUDE_COLLECTION_ARTWORK=1                 # If set to 1, collection posters are retrieved
ONLY_COLLECTION_ARTWORK=0                    # If set to 1, ONLY collection posters are retrieved
```

If "POSTER_DOWNLOAD" is `0`, the script will build a shell script for each library to download the images at your convenience instead of downloading them as it runs, so you can run the downloads overnight or on a different machine with ALL THE DISK SPACE or something.

If "POSTER_CONSOLIDATE" is `1`, the script will store all the images in one directory rather than separating them by library name.  The idea is that Plex shows the same set of posters for "Star Wars" whether it's in your "Movies" or "Movies - 4K" or whatever other libraries, so there's no reason to pull the same set of posters multiple times.  There is an example below.

If "ARTWORK" is `1`, the script will also grab the background artwork.

If "PLEX_PATHS" is `1`, the script will store all the images in a mirror of your Plex library paths, under the Plex local asset names.  This overrides POSTER_CONSOLIDATE"

If "NAME_IN_TITLE" is `1`, files will have titles in their names:

`PLEX_PATHS=1`:
```
13 Reasons Why (2017) {tvdb-323168}-poster.jpg
13 Reasons Why (2017) {tvdb-323168}-background.jpg
```
`PLEX_PATHS=0`:
```
13 Reasons Why (2017) {tvdb-323168}-66788-323168-1791734-poster.jpg
13 Reasons Why (2017) {tvdb-323168}-66788-323168-1791734-background.jpg
```

Without NAME_IN_TITLE:

`PLEX_PATHS=1`:
```
poster.jpg
background.jpg
```
`PLEX_PATHS=0`:
```
66788-323168-1791734-poster.jpg
66788-323168-1791734-background.jpg
```

`POSTER_NAME` and `BACKGROUND_NAME` control the "-poster" and "-background" in those names.  Make sure they are different; if they are both blank and you want to download both poster and background; the second one won't get downloaded since hte file will already exist.

### Usage
1. setup as above
2. Run with `python grab-current-posters.py`

```
connecting to https://stream.BING.BANG...
getting items from [Movies - 4K]...
looping over 3254 items...
[----------------------------------------] 0.2% ... The 3 Worlds of Gulliver - DOWNLOADING 18974-36224-1841313-BG-Movies - 4K.png
```

The posters will be sorted by library [if enabled] with each poster getting an incremented number, like this:

The image names are: `TMDBID-TVDBID-RATINGKEY-INCREMENT.ext`

POSTER_CONSOLIDATE=1:
```
current_posters
└── all_libraries
    ├── 100402-Captain America The Winter Soldier
    │   ├── 100402-965-1456628-Movies - 4K.png
    │   └── 100402-965-1456628-BG-Movies - 4K.png
    └── 10061-Escape from L.A
        ├── 10061-2520-1985150-Movies - 4K.png
        └── 10061-2520-1985150-BG-Movies - 4K.png
...
```

POSTER_CONSOLIDATE=0:
```
CURRENT_posters
├── Movies - 4K
│   └── 100402-Captain America The Winter Soldier
│       ├── 100402-965-1456628.png
│       └── 100402-965-1456628-BG.png
└── Movies - 1080p
    └── 10061-Escape from L.A
        ├── 10061-2520-1985150.png
        └── 10061-2520-1985150-BG.png
...

```
PLEX_PATHS=1:
```
current_posters
└── mnt
    └── unionfs
        └── movies
            └── 4k
            │   └── Captain America The Winter Soldier (2014) {tmdb-100402}
            │       ├── background.jpg
            │       └── poster.png
            └── 1080
                └── Escape from L.A (1996) {tmdb-10061}
                    ├── background.jpg
                    └── poster.png
...
```

NEW: The script now downloads the image and examines it to find out its type before adding an extension.  This requires that "libmagic" be installed on the host system.

This is described [here](https://pypi.org/project/python-magic/) and reproduced below:

Debian/Ubuntu:
```
sudo apt-get install libmagic1
```

Windows:
You'll need DLLs for libmagic. @julian-r maintains a pypi package with the DLLs, you can fetch it with:

```
pip install python-magic-bin
```

OSX:
When using Homebrew: `brew install libmagic`
When using macports: `port install file`

If `libmagic` is not installed, the script will default to a jpg extension for all files.

## grab-all-posters.py

Perhaps you want to get local copies of some or all the posters Plex knows about for everything in a library.

Maybe you find it easier to look through a bunch of options in CoverFlow or something.

This script will download some or all the posters for every item in a given set of libraries.  It (probably) won't download the same thing more than once, so you can cancel it and restart it if need be.  I say "probably" because the script is assuming that the list of posters retireved from Plex is always in the same order [i.e. that new posters get appended to the end of the list].  On subsequent runs, the script checks only that a file exists at, for example, `extracted_posters/Movies - 4K DV/10 Cloverfield Lane/2273074-001.png`.  It doesn't pay any attention to whether the two [the one on disk vs. the one coming from Plex] are the same image.  I'll probably add a check to look at the image URL to attempt to ameliorate this at some point.

Script-specific variables in .env:
```
POSTER_DIR=extracted_posters                 # put downloaded posters here
POSTER_DEPTH=20                              # grab this many posters [0 grabs all]
POSTER_DOWNLOAD=0                            # if set to 0, generate a script rather than downloading
POSTER_CONSOLIDATE=1                         # if set to 0, posters are separated into folders by library
INCLUDE_COLLECTION_ARTWORK=1                 # If set to 1, collection posters are retrieved
ONLY_COLLECTION_ARTWORK=0                    # If set to 1, ONLY collection posters are retrieved
GRAB_SEASONS=1                               # grab season posters
GRAB_EPISODES=1                              # grab episode posters [requires GRAB_SEASONS]
GRAB_BACKGROUNDS=1                           # If set to 1, backgrounds are retrieved [into a folder `backgrounds`]
TRACK_URLS=1                                 # If set to 1, URLS are tracked and won't be downloaded twice
```

The point of "POSTER_DEPTH" is that sometimes movies have an insane number of posters, and maybe you don't want all 257 Endgame posters or whatever.  Or maybe you want to download them in batches.

If "POSTER_DOWNLOAD" is `0`, the script will build a shell script for each library to download the images at your convenience instead of downloading them as it runs, so you can run the downloads overnight or on a different machine with ALL THE DISK SPACE or something.

If "POSTER_CONSOLIDATE" is `1`, the script will store all the images in one directory rather than separating them by library name.  The idea is that Plex shows the same set of posters for "Star Wars" whether it's in your "Movies" or "Movies - 4K" or whatever other libraries, so there's no reason to pull the same set of posters multiple times.  There is an example below.

If "INCLUDE_COLLECTION_ARTWORK" is `1`, the script will grab artwork for all the collections in the target library.

If "ONLY_COLLECTION_ARTWORK" is `1`, the script will grab artwork for ONLY the collections in the target library; artwork for individual items [movies, shows] will not be grabbed.

If "TRACK_URLS" is `1`, the script will create a file named for the library and put every URL it downloads into the file.  On future runs, if a given URL is found in that file it won't be downloaded a second time.  This may save time if hte same URL appears multiple times in the list of posters from Plex.  THis file will be named for the library, including the uuid: `TV Shows-9ecacbf7-ad70-4ae2-bef4-3d183be4798b.txt`

If you delete the directory of extracted posters intending to download them again, be sure to delete these files, or nothing will be downloaded on that second pass.

Files are named following the pattern `S00E00-TITLE-PROVIDER-SOURCE.EXT`, with missing parts absent as seen in the lists below.  The ID in 

The "provider" is the original source of the image [tmdb, fanarttv, etc] and "source" will be "local" [downloaded from the plex server] or "remote" [downloaded from somewhere else].  A source of "none" means the image was uploaded to plex by a tool like PMM.  The remote URL can be found in the log.

### Usage
1. setup as above
2. Run with `python grab-all-posters.py`

```
tmdb config...
connecting to https://cp1.BING.BANG...
getting items from [Movies - 4K]...
looping over 754 items...
[==================================------] 84.7% ... The Sum of All Fears - 41 posters - 20
```

he posters will be sorted by library [if enabled] with each poster getting an incremented number, like this:

The image names are: `TMDBID-TVDBID-RATINGKEY-INCREMENT.ext`

POSTER_CONSOLIDATE=1:
```
extracted_posters/
└── all_libraries
    ├── 3 12 Hours-847208
    │   ├── 3 12 Hours-tmdb-local-001.jpg
    │   ├── 3 12 Hours-tmdb-remote-002.jpg
    │   └── backgrounds
    │       ├── background-tmdb-local-001.jpg
    │       └── background-tmdb-remote-002.jpg
    ├── 9-1-1 Lone Star-89393
    │   ├── 9-1-1 Lone Star-local-local-001.jpg
    │   ├── 9-1-1 Lone Star-tmdb-local-002.jpg
    │   ├── S01-Season 1
    │   │   ├── S01-Season 1-local-local-001.jpg
    │   │   ├── S01-Season 1-tmdb-local-002.jpg
    │   │   ├── S01E01-Pilot
    │   │   │   ├── S01E01-Pilot-local-local-001.jpg
    │   │   │   └── S01E01-Pilot-tmdb-remote-002.jpg
    │   │   └── backgrounds
    │   │       ├── background-fanarttv-remote-001.jpg
    │   │       └── background-fanarttv-remote-002.jpg
    │   └── backgrounds
    │       ├── background-local-local-001.jpg
    │       └── background-tmdb-remote-002.jpg
    ├── collection-ABC
    │   ├── ABC-None-local-001.jpg
    │   └── ABC-None-local-002.jpg
    └── collection-IMDb Top 250
        ├── IMDb Top 250-None-local-001.jpg
        └── IMDb Top 250-None-local-002.png
```

POSTER_CONSOLIDATE=0:
```
extracted_posters/
extracted_posters/
├── Movies
│   ├── 3 12 Hours-847208
│   │   ├── 3 12 Hours-tmdb-local-001.jpg
│   │   ├── 3 12 Hours-tmdb-remote-002.jpg
│   │   └── backgrounds
│   │       ├── background-tmdb-local-001.jpg
│   │       └── background-tmdb-remote-002.jpg
│   └── collection-IMDb Top 250
│       ├── IMDb Top 250-None-local-001.jpg
│       └── IMDb Top 250-None-local-002.png
└── TV Shows
    ├── 9-1-1 Lone Star-89393
    │   ├── 9-1-1 Lone Star-local-local-001.jpg
    │   ├── 9-1-1 Lone Star-tmdb-local-002.jpg
    │   ├── S01-Season 1
    │   │   ├── S01-Season 1-local-local-001.jpg
    │   │   ├── S01-Season 1-tmdb-local-002.jpg
    │   │   ├── S01E01-Pilot
    │   │   │   ├── S01E01-Pilot-local-local-001.jpg
    │   │   │   └── S01E01-Pilot-tmdb-remote-002.jpg
    │   │   └── backgrounds
    │   │       ├── background-fanarttv-remote-001.jpg
    │   │       └── background-fanarttv-remote-002.jpg
    │   └── backgrounds
    │       ├── background-local-local-001.jpg
    │       └── background-tmdb-remote-002.jpg
    └── collection-ABC
        ├── ABC-None-local-001.jpg
        └── ABC-None-local-002.jpg
```

## grab-all-status.py

Perhaps you want to move or restore watch status from one server to another [or to a rebuild]

This script will retrieve all watched items for all libraries on a given plex server.  It stores them in a tab-delimited file.

Script-specific variables in .env:
```
PLEX_OWNER=yournamehere                      # account name of the server owner
```

### Usage
1. setup as above
2. Run with `python grab-all-status.py`

```
onnecting to https://cp1.DOMAIN.TLD...
------------ chazlarson ------------
------------ Movies - 4K ------------
chazlarson      movie   Movies - 4K     It Comes at Night       2017    R
chazlarson      movie   Movies - 4K     Mad Max: Fury Road      2015    R
chazlarson      movie   Movies - 4K     Rio     2011    G
chazlarson      movie   Movies - 4K     Rocky   1976    PG
chazlarson      movie   Movies - 4K     The Witch       2015    R
------------ Movies - 4K DV ------------
chazlarson      movie   Movies - 4K DV  It Comes at Night       2017    R
chazlarson      movie   Movies - 4K DV  Mad Max: Fury Road      2015    R
...
```

The file contains one row per user/library/item:

```
chazlarson      movie   Movies - 4K     It Comes at Night       2017    R
chazlarson      movie   Movies - 4K     Mad Max: Fury Road      2015    R
chazlarson      movie   Movies - 4K     Rio     2011    G
chazlarson      movie   Movies - 4K     Rocky   1976    PG
chazlarson      movie   Movies - 4K     The Witch       2015    R
chazlarson      movie   Movies - 4K DV  It Comes at Night       2017    R
chazlarson      movie   Movies - 4K DV  Mad Max: Fury Road      2015    R
...
```

## apply-all-status.py

This script reads the file produces by the previous script and applies the watched status for each user/library/item

Script-specific variables in .env:
```
TARGET_PLEX_URL=https://plex.domain2.tld
TARGET_PLEX_TOKEN=PLEX-TOKEN-TWO
TARGET_PLEX_OWNER=yournamehere
LIBRARY_MAP={"LIBRARY_ON_PLEX":"LIBRARY_ON_TARGET_PLEX", ...}
```

These values are for the TARGET of this script; this is easier than requiring you to edit the PLEX_URL, etc, when running the script.

If the target Plex has different library names, you can map one to the other in LIBRARY_MAP.

For example, if the TV library on the source Plex is called "TV - 1080p" and on the target Plex it's "TV Shows on SpoonFlix", you'd map that with:

```
LIBRARY_MAP={"TV - 1080p":"TV Shows on SpoonFlix"}
```
And any records from the status.txt file that came from the "TV - 1080p" library on the source Plex would get applied to the "TV Shows on SpoonFlix" library on the target.

### Usage
1. setup as above
2. Run with `python apply-all-status.py`

```
connecting to https://cp1.DOMAIN.TLD...

------------ Movies - 4K ------------
Searching for It Comes at Night                                                      Marked watched for chazlarson
...
```

There might be a problem with special characters in titles.


## show-all-playlists.py

Perhaps you want to creep on your users and see what they have on their playlists

This script will list the contents of all playlists users have created [except the owner's, since you already have access to those].

Script-specific variables in .env:
```
NONE
```

****
### Usage
1. setup as above
2. Run with `python show-all-playlists.py`

```
connecting to https://cp1.DOMAIN.TLD...

------------ ozzy ------------
------------ ozzy playlist: Abbott Elementary ------------
episode - Abbott Elementary s01e01 Pilot
episode - Abbott Elementary s01e02 Light Bulb
episode - Abbott Elementary s01e03 Wishlist
episode - Abbott Elementary s01e04 New Tech
episode - Abbott Elementary s01e05 Student Transfer
episode - Abbott Elementary s01e06 Gifted Program
episode - Abbott Elementary s01e07 Art Teacher
------------ ozzy playlist: The Bear ------------
episode - The Bear s01e01 System
episode - The Bear s01e02 Hands
...
------------ tony ------------
------------ tony playlist: Specials ------------
movie   - Comedy Central Roast of James Franco
movie   - Comedy Central Roast of Justin Bieber
movie   - Comedy Central Roast of Bruce Willis
------------ tony playlist: Ted ------------
movie   - Ted
movie   - The Invisible Man
movie   - Ace Ventura: When Nature Calls
...
```

## delete_collections.py

Perhaps you want to delete all the collections in one or more libraries

This script will simply delete all collections from the libraries specified in the config, except those listed.

Script-specific variables in .env:
```
KEEP_COLLECTIONS=bing,bang                      # comma-separated list of collections to keep
```
****
### Usage
1. setup as above
2. Run with `python delete_collections.py`

```
39 collection(s) retrieved...****
Collection delete - Plex |█████████▎                              | ▂▄▆ 9/39 [23%] in 14s (0.6/s, eta: 27s)
-> deleting: 98 Best Action Movies Of All Time
```

## refresh-metadata.py

Perhaps you want to refresh metadata in one or more libraries; there are situations where refreshing the whole library doesn't work so you have to do it in groups, which can be tiring.

This script will simply loop through the libraries specified in the config, refreshing each item in the library.  It waits for the specified DELAY between each.

Script-specific variables in .env:
```
NONE
```
****
### Usage
1. setup as above
2. Run with `python refresh-metadata.py`

```
getting items from [TV Shows - 4K]...
looping over 1086 items...
[========================================] 100.1% ... Zoey's Extraordinary Playlist - DONE

getting items from [ TV Shows - Anime]...
looping over 2964 items...
[========================================] 100.0% ... Ōkami Shōnen Ken - DONE
```
