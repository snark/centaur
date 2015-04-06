A Planet-like pluggable feed aggregator

Centaur takes a list of RSS and Atom feeds, filters them (if you want), and
generates a single aggregate feed. At the moment it only works from the command
line, and generates a new aggregated feed from scratch each time you call it.

Centaur has three main configuration directives:
- feeds: the feeds to aggregate
- filters: instead of simply taking all entries from the incoming feeds, you
  can filter them and only aggregate a subset
- aggregators: the formats in which to generate the output. At the moment,
  Centaur supports both simple templates (if you want an HTML version of the 
  aggregated feed) and Atom output

You must specify both a list of feeds and a list (with one or more elements) of
aggregators; filters are optional.

Filters and aggregators must be specified in a config file in JSON format. Feeds
can be specified in one of three ways: 

- via cli.py (using the '-f/--feed' option; to specify multiple feeds, pass
  the option multiple times. e.g. 'cli.py -f http://$SAMPLE_FEED_1 -f
  http://$SAMPLE_FEED_2')
- via a 'feeds' entry in the JSON config file
- via an OPML file

You can specify multiple config files. If the options specified in them can be
reconciled, centaur will do so; if you have conflicting actions, it will exit.

See config.json for an example of the various options and their formats.
